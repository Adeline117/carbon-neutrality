# Decentralized Rater Architecture (v0.4 design note)

*Design note. Not part of the workshop paper. Compares options for replacing the single-owner rater role in `CarbonCreditRating.sol` with a decentralized attestation layer. No code changes; implementation lands in v0.5 or v0.6 depending on expert feedback.*

## 1. Problem

The v0.4 reference contract uses a single-owner allowlist for rater access:

```solidity
// CarbonCreditRating.sol
modifier onlyRater() {
    if (!isRater[msg.sender]) revert NotRater();
    _;
}
```

This is deliberately simple for the workshop prototype, but it reintroduces exactly the trust problem the framework is meant to solve. A centralized rater in a "transparent, composable, on-chain rating" system is a contradiction in terms:

1. **Single point of failure.** The rater's private key controls the entire grade distribution. Compromise = total loss of framework integrity.
2. **Single point of capture.** The rater can be pressured, paid, or subpoenaed. Downstream DeFi protocols that gate pools on grades inherit that capture risk.
3. **No dispute.** A credit holder whose rating is lowered has no recourse beyond asking the single rater nicely.
4. **Trust regression vs. commercial agencies.** Sylvera, BeZero, and Calyx are already single-entity raters; the whole point of moving on-chain is to do better than that. A single-owner on-chain rater is strictly worse because it combines opaque trust with public composability.

The paper's §9 (Limitations, item 9) frames this as the main open governance question. This document compares four concrete options and picks one for v0.5 implementation.

## 2. Options

### 2.1 Option A — EAS (Ethereum Attestation Service)

**Mechanism.** Raters publish attestations to a shared EAS schema. The CarbonCreditRating contract reads the latest attestation for each `(creditToken, tokenId)` from a fixed schema ID via an adapter contract. The schema defines the field layout (seven dimension scores + disqualifier bitmap + methodology version + evidenceHash), and EAS handles the attestation storage, revocation, and queryability.

Who can attest? Two sub-variants:
- **A1 Permissionless**: anyone can attest; the adapter reads the most recent attestation from any address. Trust = whoever the reader trusts to be the "canonical" attester. In practice the adapter maintains a separate allowlist of trusted attester addresses and ignores attestations from outside the set. This is roughly equivalent to the v0.4 single-owner model distributed across multiple addresses with attestation provenance.
- **A2 Registry-allowlisted**: the adapter hardcodes (or token-gates on an allowlist updated by a slow multisig) a set of trusted attester addresses corresponding to the major registries (Verra, Gold Standard, Puro, Isometric, ICVCM). Only these can produce valid attestations; anyone can read them. This is the cleanest mapping of the real-world trust graph.

**Finality / latency.** Immediate. An EAS attestation is final as soon as it's on-chain. No challenge period.

**Gas cost.** EAS attestation ~80-150k gas depending on schema. On L2 (Base, Optimism, Arbitrum) this is ~$0.10-0.30 per attestation. Mainnet is prohibitive for high-volume rating.

**Composability.** Excellent. EAS is a standard; every major indexer and subgraph handles it. Downstream DeFi protocols can read either through the CarbonCreditRating adapter or directly.

**Dispute.** None by default. A wrong attestation must be revoked by the attester and re-attested. This is the same trust model as a single rater, just with audit trail.

**Off-chain dependencies.** The attester still needs access to verification reports, satellite imagery, etc., to produce per-dimension scores. EAS only handles the publication layer, not the input data.

**Works on.** Ethereum mainnet, Base, Optimism, Arbitrum, Scroll, Linea, Polygon. Broadest footprint of any option considered.

**Implementation precedent (discovered in v0.5 research).** The Hypercerts Foundation already operates an EAS-based evaluator registry with curated trusted attesters on Optimism, Base, and Celo. Their "Ecocerts" sub-project (with GainForest) builds EAS schemas specifically for ecological impact claims — structurally near-identical to our Option A2. Their evaluator registry contract pattern (roles controlling who can update the attester list) maps directly to our `isTrustedAttester` mapping. See `docs/research-on-chain-2025-2026.md` Finding 1 and Finding 12 for details. The Gold Standard + Hedera Guardian project (2025) demonstrates a working dMRV-to-blockchain pipeline for cookstove credits, validating the attestation model end-to-end.

### 2.2 Option B — UMA-style optimistic oracle

**Mechanism.** A rater *proposes* a rating and posts an economic bond. A challenge window (e.g., 48-72 hours) opens. Anyone can challenge the proposed rating by posting a counter-bond; if challenged, the dispute escalates to UMA's Data Verification Mechanism (DVM) where UMA token holders vote on the correct answer. Winners keep their bonds; losers forfeit them.

**Finality / latency.** Challenge window + (if disputed) ~48 hours DVM resolution. Effective latency 3-7 days for contentious ratings; immediate for uncontested ones (after the window).

**Gas cost.** ~200-300k gas per proposal. Challenge and DVM resolution add more. Bond size is economically meaningful ($100-$10,000 per rating depending on liability).

**Composability.** Fair. UMA is a mature oracle on Ethereum/L2s but has a smaller footprint than EAS. Integration requires an adapter contract that waits for oracle settlement before writing to `_ratings`.

**Dispute.** Yes, by design. This is the option's core strength: wrong ratings can be contested by anyone who is willing to post a bond. The DVM provides eventual correctness under honest-majority assumptions.

**Off-chain dependencies.** UMA DVM voters need to be able to verify ratings themselves, which is... hard. UMA voters are optimized for questions with clear empirical answers ("what was ETH's price at this timestamp?"); carbon credit quality is a multi-dimensional judgment call. The DVM is not a good fit for complex attestation disputes.

**Works on.** Ethereum mainnet, Optimism, Polygon, Arbitrum.

### 2.3 Option C — Multi-rater quorum (N-of-M allowlist)

**Mechanism.** A fixed set of M raters is allowlisted (e.g., M=5-7 representing a mix of registries, academic experts, and commercial agencies). Each rater independently submits a rating. The contract computes a quorum view: if ≥N of them agree on a per-dimension score within a tolerance (e.g., ±5 points per dimension), the median is accepted. Otherwise the rating is marked disputed and defaults to the previous valid rating (or "unrated" if none).

**Finality / latency.** Depends on coordination. If all M raters submit within a defined window (e.g., 7 days), resolution is immediate. Slow or missing raters block progress.

**Gas cost.** M × setRating ≈ M × 100-200k gas. For M=5 and L2 deployment this is ~$0.50-1.50 per full quorum rating.

**Composability.** Good for direct reads; the contract presents a single `ratingOf` view that downstream consumers can use exactly as in v0.4.

**Dispute.** Implicit — disagreement between raters is the dispute, and the tolerance threshold is the resolution mechanism. No explicit challenge period.

**Off-chain dependencies.** M independent raters each need their own access to data sources. Higher aggregate cost, better robustness to single-point compromise.

**Works on.** Any EVM chain. No external dependency.

### 2.4 Option D — Registry-attester with optimistic challenge

**Mechanism.** A hybrid of A2 and B. The primary attesters are the major carbon credit registries (Verra, Gold Standard, ACR, CAR, Puro, ICVCM — the same set that ICVCM has assessed for CCP eligibility). A registry's attestation becomes final after a challenge window (e.g., 7 days) unless a challenger posts a bond and proposes an alternative rating. If challenged, the dispute is resolved by a small expert panel (9-12 carbon market specialists) rather than a generic oracle. If the panel sides with the challenger, the challenger keeps the bond and the alternative rating becomes canonical; otherwise the original stands and the bond is forfeited to the rating DAO treasury.

**Finality / latency.** 7 days for uncontested ratings; 14-21 days for contested ones (challenge + panel convocation + resolution).

**Gas cost.** Similar to B on-chain (~200k gas per attestation + challenge/resolution costs). The expert panel adds significant off-chain coordination overhead.

**Composability.** Fair. The contract still exposes `ratingOf` and `meetsGrade`, but downstream consumers need to understand that "final" happens 7+ days after attestation. DeFi protocols gating pools on a fresh rating may need to wait.

**Dispute.** Yes, and with carbon-specific subject-matter expertise. This is the option's core advantage over B: the dispute resolver is not a generic oracle but a panel qualified to judge the dispute.

**Off-chain dependencies.** Registries as primary attesters, expert panel as dispute resolver. Both require sustained governance infrastructure — this is the most operationally demanding option.

**Works on.** Any EVM chain, but the expert panel is a meatspace dependency.

## 3. Trade-off matrix

| | **A2 EAS registry-allowlist** | **B UMA optimistic** | **C Multi-rater quorum** | **D Registry + expert challenge** |
|---|---|---|---|---|
| Trust model | Allowlisted registries | Economic bond + UMA DVM | N-of-M quorum | Registry primary + expert panel |
| Finality latency | Immediate | 3-7 days | Slowest-rater bounded (e.g., 7d) | 7-21 days |
| Gas cost per rating (L2) | $0.10-0.30 | $0.50-2.00 | $0.50-1.50 | $0.30-1.00 |
| Who pays | Attester | Proposer + bond | All M raters | Attester + bond from challenger |
| Dispute mechanism | None (revoke/re-attest) | Economic, via generic DVM | Implicit via quorum tolerance | Expert panel (carbon SMEs) |
| Subject-matter fit | Good | **Poor** (DVM is for empirical Qs) | Good | **Best** (panel has SMEs) |
| Composability with existing DeFi | **Excellent** (EAS standard) | Fair | Good | Fair |
| Operational complexity | **Low** | Medium | Medium-high | **High** (panel convocation) |
| Off-chain infrastructure | Attester + EAS | Bonders + DVM | M attesters | Registries + expert panel + DAO |
| Upgradability | Swap adapter to new schema | Swap oracle | Add/remove raters via multisig | Governance-heavy |
| Chains supported | **Broadest** (EAS mainnet + L2s) | Eth/Opt/Arb/Polygon | Any EVM | Any EVM |
| Replaces v0.4 single-owner cleanly? | **Yes** | Yes | Yes | Yes |

**Rows to pay attention to:**

- **Subject-matter fit**: Option B (UMA) is the weakest here, because carbon credit quality disputes are not questions UMA DVM voters are equipped to resolve. UMA works best for empirical questions with a single correct answer ("what was ETH's closing price?"). Carbon quality is a multi-dimensional judgment call; the DVM would do it badly.
- **Composability**: EAS has a structural advantage because it's already the attestation standard on Ethereum and L2s. Every indexer, subgraph, and integration library already speaks EAS. Any other option requires downstream consumers to adopt a bespoke integration.
- **Operational complexity**: Option D is the most ambitious but also the hardest to bootstrap. It needs a standing expert panel with real governance, honoraria, and dispute-resolution procedures. A workshop-level project cannot sustain that; it would need a dedicated foundation.
- **Finality**: Option A is the only option with immediate finality, which matters for DeFi composability — a protocol cannot gate deposits on a rating that won't be final for a week.

## 4. Recommendation

**Adopt Option A2 (EAS with a registry-allowlist) as the v0.5 default, with an explicit upgrade path to a D-style expert challenge mechanism in v0.6+ if expert consultation recommends it.**

Rationale:

1. **EAS is already the on-chain attestation standard.** Building on it maximizes downstream composability (the main reason the framework exists at all) and minimizes the operational burden of maintaining a custom attestation infrastructure.
2. **Registry-allowlist preserves the real-world trust graph.** In the actual voluntary carbon market, Verra / Gold Standard / Puro / Isometric / ICVCM are already the trust anchors. Encoding them as the allowlisted attesters in an EAS schema maps what exists rather than inventing a new trust relationship.
3. **Immediate finality is necessary for DeFi composability.** A quality-gated pool cannot wait 7-21 days for a rating to finalize. Options B and D both have this problem; Option A does not.
4. **Option B's mismatch is structural.** The UMA DVM is not designed for subjective multi-dimensional attestation disputes. Forcing it into that role would produce bad disputes and erode trust in the framework.
5. **Option C (multi-rater quorum) is a reasonable fallback** if EAS turns out to be unacceptable to any of the expert consultation participants in v0.5. It requires less infrastructure than D and more decentralization than A. Reject it only if consultation explicitly prefers A.
6. **Option D is the right endpoint but not the right starting point.** An expert challenge mechanism is ideal for a mature framework with real economic stakes and a standing foundation. For v0.5 it's premature; aim to migrate to D in v0.7+ once the framework has seen real adoption and someone is willing to underwrite the panel.

## 5. Interface sketch (no implementation)

The v0.5 adapter layer would look roughly like this. This is a sketch for discussion, not production code.

```solidity
// v0.5 adapter that plugs an EAS-based attestation layer into the v0.4 contract.
// The v0.4 CarbonCreditRating.sol is refactored so that `setRating` is protected
// by an adapter address instead of a rater allowlist.

interface IEASMinimal {
    function getAttestation(bytes32 uid) external view returns (
        bytes32 schema,
        uint64 time,
        uint64 expirationTime,
        uint64 revocationTime,
        bytes32 refUID,
        address recipient,
        address attester,
        bool revocable,
        bytes memory data
    );
}

contract CarbonCreditRatingEASAdapter {
    ICarbonCreditRating public immutable rating;
    IEASMinimal public immutable eas;
    bytes32 public immutable schemaId;

    // Allowlist of trusted attesters (registries). Updated by a slow multisig
    // with a minimum delay (e.g., 14 days).
    mapping(address => bool) public isTrustedAttester;

    error AttestationRevoked();
    error UntrustedAttester(address attester);
    error SchemaMismatch(bytes32 got, bytes32 want);

    /// @notice Pull an EAS attestation for (creditToken, tokenId) and write the
    ///         decoded rating to the underlying CarbonCreditRating contract.
    function relay(bytes32 attestationUid, address creditToken, uint256 tokenId)
        external
    {
        (
            bytes32 schema,
            ,
            uint64 expirationTime,
            uint64 revocationTime,
            ,
            ,
            address attester,
            ,
            bytes memory data
        ) = eas.getAttestation(attestationUid);

        if (schema != schemaId) revert SchemaMismatch(schema, schemaId);
        if (revocationTime != 0) revert AttestationRevoked();
        if (!isTrustedAttester[attester]) revert UntrustedAttester(attester);

        (
            ICarbonCreditRating.DimensionScores memory scores,
            ICarbonCreditRating.Disqualifiers memory flags,
            bytes32 evidenceHash
        ) = abi.decode(
            data,
            (ICarbonCreditRating.DimensionScores, ICarbonCreditRating.Disqualifiers, bytes32)
        );

        // Relay passes expirationTime through as the rating's expiresAt.
        rating.setRating(creditToken, tokenId, scores, flags, expirationTime, evidenceHash);
    }
}
```

The underlying `CarbonCreditRating.sol` changes minimally:
- `setRating` is gated on `msg.sender == adapter` instead of `isRater[msg.sender]`
- The `owner` role is retained only for swapping the adapter (e.g., pointing at a different EAS schema) under a timelock
- Everything else — the scoring logic, grade boundaries, disqualifier caps, freshness enforcement — is unchanged

This keeps v0.5 as a **pure governance change** layered on top of v0.4's methodology work. No new scoring logic, no new grade semantics, no new storage layout. The risk surface is contained to the adapter contract.

## 6. Migration path from v0.4

Three phases:

**Phase 1 — Adapter alongside (v0.5 release)**
1. Deploy `CarbonCreditRatingEASAdapter` pointing at the same `CarbonCreditRating` instance.
2. Add the adapter's address to the v0.4 rater allowlist. Keep the existing owner key active during this phase.
3. Migrate existing ratings (if any) from owner-signed to adapter-relayed. Each credit gets re-attested once under the EAS schema; the adapter relays the attestation to the existing contract. No storage migration.
4. Publish the EAS schema ID, allowlisted attester addresses, and onboarding docs for registries.

**Phase 2 — Decommission the owner key (v0.5.1 or v0.6)**
1. Remove all other raters from the `isRater` allowlist, leaving only the adapter.
2. Transfer ownership to a timelocked multisig whose only authority is swapping the adapter address.
3. Delete the owner key or rotate it to cold storage as a last-resort recovery.

**Phase 3 — Harden and expand (v0.6+)**
1. Expand the allowlisted attesters as new registries join ICVCM or demonstrate equivalent rigor.
2. Optionally add a challenge-and-dispute layer on top of the adapter (Option D) if expert consultation in v0.5 recommends it. This is a pure addition; the EAS layer underneath is unchanged.
3. Consider adding a rate limit or minimum inter-rating window per credit to prevent attester spam.

## 7. Open questions for v0.5 expert consultation

1. **Is EAS acceptable to the major registries?** Verra, Gold Standard, Puro, Isometric, ICVCM — would they actually attest via EAS, and under what conditions?
2. **What's the allowlist governance?** Who decides which registries are trusted attesters? A simple multisig is OK for v0.5 but not long-term.
3. **How often should ratings expire?** The v0.4 contract supports expiry but doesn't enforce a policy. Should it be 12 months (matching annual verification cycles), 18 months (to buffer verification delays), or methodology-specific (shorter for methodologies under active review)?
4. **Is the registry-only primary attester model sufficient**, or should independent raters (Sylvera-style commercial agencies, academic groups) also have a path to attest? If yes, how do we prevent rating-shopping (where a project solicits multiple raters and reports only the highest)?
5. **What happens when attestations conflict?** In Option A2 with multiple allowlisted attesters, if two registries produce different ratings for the same credit, which one wins? Proposed default: most recent attestation wins, with all historical attestations readable via EAS for audit. But a project that has been multi-rated with different grades needs a defined reconciliation rule.
6. **Does rating expiry reset on re-attestation from a different attester?** If Verra re-attests a credit that Puro originally attested, should the evidenceHash lineage be preserved, or treated as a fresh rating with a fresh lineage?

None of these questions block implementation of the EAS adapter — they can be answered during v0.5 consultation and encoded in the adapter's governance layer later. They are noted here so that v0.5 can structure its expert interviews around the right decision menu.

## 8. Non-goals

- **This document does not propose a new scoring methodology.** The v0.4 safeguards-gate mechanism (`docs/methodology-gate-v0.4.md`) is unchanged.
- **This document does not address dispute resolution for scoring disagreements within a single attester.** If Verra attests a credit at AA and an academic paper later argues it should be BB, that's a Verra-internal question, not a framework question.
- **This document does not cover retirement tracking.** Retirement is a separate DeFi primitive and belongs in a different design doc.
- **This document does not specify the off-chain attestation bundle format** (what should go into `evidenceHash`). That is a v0.5 question to discuss with registries during consultation.
