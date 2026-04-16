#!/usr/bin/env python3
"""Evidence pack builder for the LLM panel scale-up (Paper 1).

Takes a list of Verra/Gold-Standard project IDs and produces a standardized
JSON "evidence pack" per project that the LLM panel can score. Evidence packs
pull from:

  1. The structured metadata already present in this repo
     (data/depositor-analysis/project_classification_final.json,
      data/depositor-analysis/tco2_metadata.json,
      data/depositor-analysis/tco2_scores_final.json)
  2. Public project-detail pages on the registries themselves (Verra / GS / Puro)
     when reachable and we have scraping permission. These are fetched via
     WebFetch-compatible stubs that cache to disk.
  3. Any linked PDF (PDD, monitoring report, verification statement) when URL
     is discoverable. PDF bodies are cached as raw text.

The builder is intentionally resilient: if the public page is not reachable,
the pack falls back to the structured metadata already present and marks
`evidence_level: "metadata-only"`. This lets us run the full pipeline even
when the network is blocked (as it is in most CI environments).

Output schema per project (written to evidence-packs-cache/<registry>_<id>.json):

    {
      "evidence_pack_version": "0.1.0",
      "project_ref": {
        "registry": "VCS" | "GS" | "Puro" | "CAR" | ...,
        "project_id": "<string>",
        "canonical_url": "<string or null>",
        "name": "<string>"
      },
      "fields": {
        "methodology":             "<string or null>",
        "country":                 "<string or null>",
        "vintage":                 "<string or null>",  # may be range
        "description":             "<string or null>",  # 1-3 sentence archetype
        "claims":                  [<strings, optional>],
        "monitoring_approach":     "<string or null>",
        "vvb_history":             [<strings, optional>],
        "corrective_action_history":[<strings, optional>],
        "type_archetype":          "<string: REDD+ / ARR / Renewable / ...>",
        "tokenization":            "<string or null>"
      },
      "provenance": [
        {"source": "project_classification_final.json", "fetched_at": "<iso>"},
        {"source": "https://registry.verra.org/app/projectDetail/VCS/<id>",
         "fetched_at": "<iso>", "status": "ok" | "unreachable" | "rate-limited"}
      ],
      "evidence_level": "metadata-only" | "page-scraped" | "pdf-enriched"
    }

Usage:
    python3 evidence_pack_builder.py                       # build all 168 BCT projects
    python3 evidence_pack_builder.py --project-ids 10 1002 # build specific IDs
    python3 evidence_pack_builder.py --limit 20            # build first 20 only
    python3 evidence_pack_builder.py --online              # attempt live scraping
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import re
import sys
import time
from pathlib import Path
from typing import Any, Iterable

try:
    import urllib.request
    import urllib.error
except Exception:  # pragma: no cover
    urllib = None  # type: ignore

HERE = Path(__file__).resolve().parent
REPO = Path("/Users/adelinewen/carbon-neutrality")
MAIN_DATA = REPO / "data" / "depositor-analysis"
CACHE_DIR = HERE / "evidence-packs-cache"
CACHE_DIR.mkdir(parents=True, exist_ok=True)

CLASSIFICATION_FILE = MAIN_DATA / "project_classification_final.json"
METADATA_FILE = MAIN_DATA / "tco2_metadata.json"
SCORES_FILE = MAIN_DATA / "tco2_scores_final.json"

USER_AGENT = (
    "Mozilla/5.0 (compatible; CarbonQualityResearchBot/0.1; "
    "+https://github.com/adelinewen/carbon-neutrality)"
)

# ---------- archetype catalogue ----------
# Canonical short descriptions per project-type archetype. Used to seed the
# `description` field when we can't pull a page. This makes the evidence pack
# self-contained — an LLM scoring a "Renewable / Hydro / 2012 / China" credit
# has enough information to apply the rubric even without a live page.
ARCHETYPE_DESCRIPTIONS: dict[str, str] = {
    "Renewable": (
        "Grid-connected renewable energy project (hydro / wind / biomass / solar) "
        "claiming avoided-emissions credits by displacing fossil-fired grid electricity. "
        "Post-Paris additionality for utility-scale renewables is widely questioned in the "
        "literature (West et al. 2023, CMW 2023)."
    ),
    "Fossil switch": (
        "Fuel-switching project that claims emissions reductions by replacing a higher-"
        "carbon fossil fuel (e.g. diesel, coal) with a lower-carbon alternative (e.g. natural gas). "
        "Additionality and permanence of avoided emissions are methodology-sensitive; this "
        "archetype is not a carbon removal."
    ),
    "Waste/Methane": (
        "Methane capture or destruction project (landfill gas, wastewater, livestock manure). "
        "CH4 destruction has a strong physical rationale but baseline counterfactuals are "
        "sensitive to regulatory requirements in the host country."
    ),
    "REDD+": (
        "Reducing Emissions from Deforestation and forest Degradation project claiming avoided "
        "deforestation credits in a tropical forest. This archetype has been under sustained "
        "methodological criticism (West et al. 2023 Science, Guardian 2023): dynamic baselines "
        "and leakage-control are weak in most VM0007 vintages."
    ),
    "IFM": (
        "Improved Forest Management project claiming enhanced sequestration relative to a "
        "hypothetical logging baseline. Baseline construction (e.g. ARB IFM) is contested and "
        "over-crediting is documented in CAR/ARB IFM (Badgley et al. 2022)."
    ),
    "ARR": (
        "Afforestation, Reforestation, or Revegetation project. Archetype quality depends on "
        "species (native vs. monoculture), tenure security, and whether the planting is "
        "commercial timber. VM0047 is the current best-in-class methodology."
    ),
    "Agriculture": (
        "Soil-carbon or agricultural-management project. Permanence is low relative to "
        "engineered CDR; MRV typically relies on modelled outcomes rather than direct "
        "measurement."
    ),
    "Industrial": (
        "Industrial process efficiency or energy-recovery project (cement, steel, chemicals). "
        "Additionality depends on regulatory baselines and process-economics counterfactuals."
    ),
    "Industrial gas": (
        "Destruction of high-GWP industrial gases (HFC-23, SF6, N2O). Physically unambiguous "
        "abatement but the perverse-incentive literature (Wara 2007, Nature 2023) shows that "
        "HFC-23 projects have historically motivated additional HFC-22 production."
    ),
    "Cookstove": (
        "Improved-cookstove distribution project claiming avoided-biomass emissions. Recent "
        "work (Gill-Wiehl et al. 2024 Nature) has documented large over-crediting relative to "
        "measured stove-use and fuel-savings."
    ),
    "Energy efficiency": (
        "End-use energy efficiency (LED distribution, industrial motors, building envelope). "
        "Additionality hinges on whether the intervention would have happened anyway under a "
        "rising energy-price baseline."
    ),
}

# Per-archetype defaults for the "claims / monitoring_approach" fields when
# we only have metadata.
ARCHETYPE_CLAIMS: dict[str, list[str]] = {
    "Renewable": [
        "Displaces grid fossil generation",
        "Grid emission factor baseline",
    ],
    "Fossil switch": [
        "Reduced fuel carbon intensity",
        "Continued operation is counterfactual",
    ],
    "Waste/Methane": [
        "CH4 capture and combustion",
        "Landfill/wastewater baseline vented CH4",
    ],
    "REDD+": [
        "Avoided deforestation relative to regional baseline",
        "Community co-benefits",
    ],
    "IFM": [
        "Reduced harvest relative to business-as-usual",
        "Enhanced standing stock",
    ],
    "ARR": [
        "Net tree-cover increase on degraded land",
        "Above-ground biomass growth",
    ],
    "Agriculture": [
        "Soil organic carbon accumulation",
        "Reduced tillage / cover-cropping",
    ],
    "Industrial gas": [
        "Destruction of high-GWP gas (N2O / HFC-23)",
    ],
    "Industrial": [
        "Process efficiency improvement",
    ],
    "Cookstove": [
        "Replacement of baseline biomass stove",
        "Fraction of non-renewable biomass savings",
    ],
    "Energy efficiency": [
        "End-use energy saving vs. baseline appliance",
    ],
}

ARCHETYPE_MRV: dict[str, str] = {
    "Renewable": "Metered electrical output cross-checked against grid dispatch records.",
    "Fossil switch": "Fuel-consumption records and emission factors per IPCC 2006.",
    "Waste/Methane": "Flow-metered CH4 combustion, periodic composition tests.",
    "REDD+": "Remote-sensing forest-cover change + field plots.",
    "IFM": "Forest inventory re-measurement on fixed plots + permanence discount.",
    "ARR": "Allometric biomass estimation on permanent sample plots + remote sensing.",
    "Agriculture": "Modelled SOC change validated against sampled soil cores.",
    "Industrial gas": "Continuous emissions monitoring of destruction unit.",
    "Industrial": "Energy/material balance.",
    "Cookstove": "Surveys + KPT/CCT tests; recent methodologies require stove-use sensors.",
    "Energy efficiency": "Metered or stipulated savings depending on methodology.",
}


# ---------- load local data ----------

def load_local_data() -> tuple[dict, dict, dict]:
    classification = json.loads(CLASSIFICATION_FILE.read_text())
    metadata = json.loads(METADATA_FILE.read_text())
    scores = json.loads(SCORES_FILE.read_text())

    # Build project_id -> aggregated metadata
    by_project: dict[str, dict] = {}
    for addr, m in metadata.items():
        pid = m["project_id"]
        entry = by_project.setdefault(
            pid,
            {"registry": m.get("registry", "VCS"), "vintages": set(), "addresses": []},
        )
        v = m.get("vintage")
        if v:
            entry["vintages"].add(str(v))
        entry["addresses"].append(addr)
    for pid in by_project:
        by_project[pid]["vintages"] = sorted(by_project[pid]["vintages"])

    # Per-address grades from the on-chain scoring pipeline
    addr_to_score = scores

    return classification, by_project, addr_to_score


# ---------- scrapers (optional / online-only) ----------

def verra_detail_url(project_id: str) -> str:
    return f"https://registry.verra.org/app/projectDetail/VCS/{project_id}"


def gs_detail_url(project_id: str) -> str:
    return f"https://registry.goldstandard.org/projects/details/{project_id}"


def fetch_public_page(url: str, timeout: float = 10.0) -> dict[str, Any]:
    """Best-effort HTTP GET with a cache-friendly response envelope.

    Returns {"status": "ok"|"unreachable"|..., "text": <body or None>, "fetched_at": iso}.
    Never raises.
    """
    ts = dt.datetime.utcnow().isoformat() + "Z"
    if urllib is None:  # pragma: no cover
        return {"status": "no-urllib", "text": None, "fetched_at": ts, "url": url}
    try:
        req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            body = resp.read().decode("utf-8", errors="replace")
            return {"status": "ok", "text": body, "fetched_at": ts, "url": url}
    except urllib.error.HTTPError as e:  # type: ignore
        return {"status": f"http-{e.code}", "text": None, "fetched_at": ts, "url": url}
    except Exception as e:  # noqa: BLE001
        return {"status": f"error:{type(e).__name__}", "text": None, "fetched_at": ts, "url": url}


HTML_TAG_RE = re.compile(r"<[^>]+>")
WS_RE = re.compile(r"\s+")


def crude_text_from_html(html: str, max_chars: int = 4000) -> str:
    text = HTML_TAG_RE.sub(" ", html)
    text = WS_RE.sub(" ", text).strip()
    return text[:max_chars]


def extract_verra_fields(html: str) -> dict[str, Any]:
    """Very light heuristics for Verra project-detail pages. Returns empty dict
    on any failure; the fallback to metadata-only still produces a usable pack.
    """
    out: dict[str, Any] = {}
    plain = crude_text_from_html(html, max_chars=20_000)
    # Methodology often renders as: "Methodology VMxxxxx ..."
    m = re.search(r"Methodology[^\w]{0,3}(VM\d{4,5}|VCS\s*Methodology\s*\w+)", plain, re.I)
    if m:
        out["methodology"] = m.group(1)
    # Country
    m = re.search(r"Country/Area[^A-Za-z]{0,3}([A-Z][A-Za-z ,.'-]{2,40})", plain)
    if m:
        out["country"] = m.group(1).strip()
    # Estimated annual emission reductions
    m = re.search(r"Estimated Annual Emission Reductions[^\d]{0,5}([\d,]+)", plain, re.I)
    if m:
        out["annual_reductions_tCO2e"] = int(m.group(1).replace(",", ""))
    return out


# ---------- evidence pack assembly ----------

def build_pack(
    project_id: str,
    cls_entry: dict,
    proj_meta: dict,
    addr_to_score: dict,
    online: bool = False,
) -> dict:
    ts = dt.datetime.utcnow().isoformat() + "Z"
    registry = proj_meta.get("registry", "VCS")
    canonical_url = verra_detail_url(project_id) if registry == "VCS" else None

    provenance: list[dict[str, Any]] = [
        {"source": "project_classification_final.json", "fetched_at": ts},
        {"source": "tco2_metadata.json", "fetched_at": ts},
        {"source": "tco2_scores_final.json", "fetched_at": ts},
    ]

    type_arch = cls_entry.get("type", "Unknown")
    description = ARCHETYPE_DESCRIPTIONS.get(type_arch, "Unclassified archetype.")
    claims = list(ARCHETYPE_CLAIMS.get(type_arch, []))
    monitoring = ARCHETYPE_MRV.get(type_arch, "Methodology-specified MRV.")

    fields: dict[str, Any] = {
        "methodology": None,
        "country": None,
        "vintage": ",".join(proj_meta.get("vintages", [])) or None,
        "description": description,
        "claims": claims,
        "monitoring_approach": monitoring,
        "vvb_history": [],
        "corrective_action_history": [],
        "type_archetype": type_arch,
        "tokenization": "Toucan TCO2 (BCT-eligible)" if proj_meta.get("addresses") else None,
        "on_chain_addresses": proj_meta.get("addresses", []),
    }

    evidence_level = "metadata-only"

    if online and canonical_url is not None:
        fetched = fetch_public_page(canonical_url)
        provenance.append({
            "source": canonical_url,
            "fetched_at": fetched["fetched_at"],
            "status": fetched["status"],
        })
        if fetched["status"] == "ok" and fetched.get("text"):
            extracted = extract_verra_fields(fetched["text"])
            if extracted:
                fields.update({k: v for k, v in extracted.items() if v})
                evidence_level = "page-scraped"

    # Pull per-address on-chain composite if available (for internal reference /
    # ground-truth correlation, not for the LLM).
    on_chain_refs = []
    for addr in proj_meta.get("addresses", []):
        sc = addr_to_score.get(addr)
        if sc:
            on_chain_refs.append({
                "address": addr,
                "internal_composite": sc.get("composite"),
                "internal_grade": sc.get("grade"),
                "vintage": sc.get("vintage"),
            })

    pack = {
        "evidence_pack_version": "0.1.0",
        "project_ref": {
            "registry": registry,
            "project_id": project_id,
            "canonical_url": canonical_url,
            "name": cls_entry.get("name", ""),
        },
        "fields": fields,
        "provenance": provenance,
        "on_chain_internal_scores": on_chain_refs,
        "evidence_level": evidence_level,
        "built_at": ts,
    }
    return pack


def pack_cache_path(registry: str, project_id: str) -> Path:
    safe = re.sub(r"[^A-Za-z0-9_-]", "_", f"{registry}_{project_id}")
    return CACHE_DIR / f"{safe}.json"


def build_all(
    project_ids: Iterable[str] | None = None,
    limit: int | None = None,
    online: bool = False,
    force: bool = False,
) -> list[Path]:
    classification, by_project, addr_to_score = load_local_data()

    if project_ids is None:
        ids = list(classification.keys())
    else:
        ids = list(project_ids)

    if limit is not None:
        ids = ids[:limit]

    written: list[Path] = []
    n_scraped = 0
    for pid in ids:
        cls_entry = classification.get(pid, {"type": "Unknown", "name": f"VCS {pid}"})
        proj_meta = by_project.get(pid, {"registry": "VCS", "vintages": [], "addresses": []})
        out_path = pack_cache_path(proj_meta.get("registry", "VCS"), pid)
        if out_path.exists() and not force:
            written.append(out_path)
            continue
        pack = build_pack(pid, cls_entry, proj_meta, addr_to_score, online=online)
        out_path.write_text(json.dumps(pack, indent=2))
        written.append(out_path)
        if pack["evidence_level"] == "page-scraped":
            n_scraped += 1
        if online:
            time.sleep(0.5)  # polite to Verra
    print(f"Wrote {len(written)} packs to {CACHE_DIR} ({n_scraped} page-scraped)")
    return written


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--project-ids", nargs="+", help="Specific project IDs")
    p.add_argument("--limit", type=int, default=None)
    p.add_argument("--online", action="store_true", help="Attempt live scraping")
    p.add_argument("--force", action="store_true", help="Re-build even if cached")
    args = p.parse_args()

    build_all(
        project_ids=args.project_ids,
        limit=args.limit,
        online=args.online,
        force=args.force,
    )


if __name__ == "__main__":
    main()
