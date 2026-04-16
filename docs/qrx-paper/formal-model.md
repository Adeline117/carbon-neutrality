# QRX Formal Model — Notation, Setup, and Proof Obligations

*Status: scaffolding. Sections marked [CO-AUTHOR PLACEHOLDER] require the
game-theorist co-author to complete the equilibrium proofs. All mechanism
definitions, payoff equations, and proof obligations are fixed here.*

---

## 1. Players and information structure

Let there be a finite set of carbon-credit **depositors** $D = \{1, \ldots, n\}$
and a competitive population of **buyers**. Each depositor $i \in D$ privately
observes a quality type
$$q_i \in Q = \{\text{B}, \text{BB}, \text{BBB}, \text{A}, \text{AA}, \text{AAA}\}$$
drawn from a common-prior distribution $\pi \in \Delta(Q)$. Grades are
totally ordered with rank $r : Q \to \{0, 1, 2, 3, 4, 5\}$.

The MRV (measurement / reporting / verification) process is modelled as a
stochastic oracle that at any time $t \geq t_{\text{deposit}}$ produces a
**certified grade** $\hat q_i \in Q$. We treat $\hat q_i = q_i$ in the
baseline model (perfect ex-post verification); Section 4 relaxes this to
$\Pr(\hat q_i = q_i) = 1 - \varepsilon$ for small $\varepsilon$.

At deposit time, each depositor chooses an action
$$a_i = (\hat c_i, b_i) \in Q \times \mathbb{R}_{\geq 0}$$
where $\hat c_i$ is the **claimed grade** and $b_i \geq 0$ is the **bond
posted**. The mechanism requires
$$b_i \geq B(\hat c_i, x_i) := \beta_{\hat c_i} \cdot x_i, \qquad \beta_{\text{B}} < \beta_{\text{BB}} < \cdots < \beta_{\text{AAA}},$$
where $x_i$ is the deposit tonnage (treated as exogenous for simplicity) and
$\beta \in \mathbb{R}^6_{>0}$ is the **bond rate schedule**.

After deposit, any agent may issue a challenge, which is adjudicated by an
oracle with cost $\kappa \geq 0$ to the challenger and expected reward
$\rho \cdot \text{slash}$ if the challenge succeeds (where $\rho =
\texttt{challengerBountyBps}/10000$; default $\rho = 0.5$).

Let $p \in [0, 1]$ denote the equilibrium probability that an overclaim is
challenged and resolved truthfully. Under $p$-detection, the **expected
slash** of a claim $\hat c$ by a true-quality-$q$ depositor is
$$\mathbb{E}[\text{slash} \mid \hat c, q] = p \cdot b \cdot \frac{\max(0, r(\hat c) - r(q))}{5}.$$

## 2. Buyer behaviour and prices

Buyers are risk-neutral and pay a grade-conditional willingness-to-pay
$$W : Q \to \mathbb{R}_{\geq 0}, \qquad W(\text{B}) < W(\text{BB}) < \cdots < W(\text{AAA}).$$
Following the VCM literature (Macinante 2022; CCQI 2023; Ecosystem Marketplace
2024) we assume $W$ is convex-increasing: the marginal WTP for one grade
improvement rises as quality rises. Section 4 shows that all results survive
a linear $W$.

A pool operating under QRX advertises, for each depositId, the claimed grade
$\hat c_i$. Buyers price credits based on $\hat c_i$ **before** the challenge
window closes, anticipating that some fraction of claims will be invalidated
post-hoc; for the baseline analysis we assume buyers pay $W(\hat c_i)$ per
tonne immediately (as they do for BCT today).

## 3. Depositor payoffs

Write $C(q) \geq 0$ for the depositor's reservation price per tonne
(opportunity cost of not selling off-pool). The depositor's expected payoff
per tonne from action $(\hat c, b)$ given true type $q$ is
$$u(\hat c, b \mid q) = W(\hat c) - C(q) - p \cdot \beta_{\hat c} \cdot \frac{\max(0, r(\hat c) - r(q))}{5} - \phi(b),$$
where $\phi(b) \geq 0$ is the opportunity cost of the bond capital over the
expected challenge window (reference deployment: $\phi(b) \approx r_f \cdot b
\cdot \tau$ for $\tau$ the window length and $r_f$ the risk-free rate).

We assume $\phi$ is strictly increasing and convex. Under the minimum-bond
contract $b = \beta_{\hat c} \cdot x_i$, $\phi$ is a strict increasing
function of $\hat c$ for any fixed $q$.

## 4. Equilibrium concept and proof obligations

We study Perfect Bayesian Equilibria (PBE) of the deposit game in which
buyers' beliefs $\mu(\cdot \mid \hat c)$ are consistent with depositor
strategies and each depositor best-responds given $\mu$.

### Proposition 1 (truthful-reporting dominates overclaiming)

> **[CO-AUTHOR PLACEHOLDER]** Under assumptions (A1)–(A3):
>
> **(A1)** $W$ and $C$ are bounded, monotone, and satisfy the single-crossing
>  property in $(q, \hat c)$.
>
> **(A2)** $\beta$ is strictly increasing and chosen so that for all $q' > q$,
>  $$p \cdot \beta_{q'} \cdot \frac{r(q') - r(q)}{5} > W(q') - W(q).$$
>  (The expected slash exceeds the WTP gain from one-step overclaim.)
>
> **(A3)** Challenging is sequentially rational: any profitable overclaim is
>  detected with probability $p$ at least as large as the threshold in (A2).
>
> Then truthful reporting ($\hat c_i = q_i$) with minimum bond
> $b_i = \beta_{q_i} x_i$ is a best response for every depositor.
>
> **Proof obligation**: Show that any deviation $\hat c \neq q$ strictly
> reduces $u$. The bond-cost term is weakly higher when $\hat c > q$ and the
> slash term is strictly higher; conversely, underclaim $\hat c < q$ strictly
> reduces $W(\hat c) - W(q)$ while weakly decreasing the bond cost (Section
> 5 of the paper handles the underclaim case with a tie-breaking assumption).

### Proposition 2 (separating equilibrium exists)

> **[CO-AUTHOR PLACEHOLDER: Prove separating equilibrium exists under assumptions X, Y, Z.]**
>
> Concrete formulation to prove:
> There exist bond rates $\beta^*$ such that the strategy profile $\sigma^*$
> with $\sigma^*_i(q) = (q, \beta^*_q \cdot x_i)$ and buyer beliefs
> $\mu^*(\hat c) = \delta_{\hat c}$ (a Dirac mass on the claimed grade) forms
> a PBE.
>
> Sketch of the argument we expect:
>   1. Show (A2) can be satisfied for all adjacent grade pairs simultaneously
>      because $\beta$ is strictly increasing.
>   2. Show that the IC constraints chain (from B up to AAA) as in Spence
>      (1973).
>   3. Show the IR constraint $u(q, b^* \mid q) \geq 0$ holds for sufficiently
>      small $\phi$ or equivalently sufficiently short challenge windows.

### Proposition 3 (Akerlof pooling equilibrium is eliminated)

> **[CO-AUTHOR PLACEHOLDER: Show Akerlof's pooling equilibrium is eliminated.]**
>
> Concrete formulation to prove:
> The strategy profile $\sigma^P$ in which every type claims AAA with
> minimum bond $\beta_{\text{AAA}} x_i$ and buyers pay
> $\mathbb{E}_\pi[W(q)]$ is **not** a PBE of the QRX game, for any
> non-degenerate prior $\pi$ with positive mass on $q < \text{AAA}$.
>
> Sketch:
>   1. Under pooling, buyers' Bayesian-consistent belief is $\mu(\cdot \mid
>      \text{AAA}) = \pi$.
>   2. A $\text{B}$-type's deviation to $\hat c = \text{B}$ with bond
>      $\beta_{\text{B}} x_i$ yields payoff $W(\text{B}) - C(\text{B}) -
>      \phi(\beta_{\text{B}} x_i)$ and no slash.
>   3. The pooling payoff is $\mathbb{E}_\pi[W(q)] - C(\text{B}) - p \cdot
>      \beta_{\text{AAA}} \cdot \frac{r(\text{AAA}) - r(\text{B})}{5} x_i -
>      \phi(\beta_{\text{AAA}} x_i)$.
>   4. Under (A2), the slash term dominates the WTP term; the $\text{B}$-type
>      strictly prefers the separating action. Hence pooling is not PBE.
>
> This is the **paper's core theorem** — it is the formal analogue of Akerlof
> (1970) Proposition 1, inverted.

### Proposition 4 (robustness to imperfect MRV)

> **[CO-AUTHOR PLACEHOLDER]** Let $\varepsilon = \Pr(\hat q_i \neq q_i)$ be
> the MRV error rate. Propositions 1–3 continue to hold when $\beta$ is
> rescaled by $1 / (1 - 2\varepsilon)$ for $\varepsilon < 1/2$.
>
> The intuition is that the certified grade is a consistent-in-expectation
> estimator of $q$, so slash expectations scale linearly with
> $1 - 2\varepsilon$. Detailed proof uses a Chernoff bound over the
> challenge window.

## 5. Mechanism-design desiderata (stated, not proved)

  * **Budget balance (ex post).** Slashed bonds are redistributed between
    challenger, treasury, and (in extensions) affected buyers. QRX does not
    subsidise the mechanism from outside; all slash revenue stays within
    the system.
  * **Individual rationality.** Each type's equilibrium payoff is
    non-negative when $W(q) - C(q) \geq \phi(\beta_q x)$.
  * **Incentive compatibility.** Propositions 1 and 2 together imply that
    truthful reporting is a dominant strategy for each type — the standard
    IC result for separating equilibria under single-crossing.
  * **Sybil resistance.** Because $B$ is linear in $x$, a depositor cannot
    reduce total slash by splitting one deposit into $K$ smaller deposits
    (proved in `contracts/test/QRX.t.sol::test_sybilResistance_*`).
  * **Collusion resistance.** See paper §Discussion for informal analysis of
    challenger–depositor collusion (mitigated by anyone being allowed to
    challenge plus the 50% challenger bounty).

## 6. Calibration requirements

The counterfactual (`data/qrx/counterfactual_replay.py`) shows that the
reference bond schedule requires $\sim 20\times$ amplification relative to
the illustrative on-chain values to satisfy (A2) under $p \approx 1$ and
a $\$50$/t-per-grade WTP gap. That is, for BCT-scale deposits the AAA
bond rate must be $\sim\$300$/t to deter overclaim with near certainty.

The policy question is whether $\$300$/t of capital-locked bond is affordable
to CDR suppliers; at $r_f = 5\%$ and a 30-day window this is $\sim\$1.25$/t
in lost interest, well below the $\$50$/t WTP gap. QRX is economically
feasible at realistic parameters.

## Closing note

The contract, tests, counterfactual, and paper draft are complete. The four
proof obligations above — Propositions 1, 2, 3, 4 — are the scope of the
game-theorist co-author's contribution. Once those are written, the paper is
ready for submission to VLDB (systems track) or CCS (security track), with
the formal-methods and mechanism-design co-author a prerequisite for the
latter venue.
