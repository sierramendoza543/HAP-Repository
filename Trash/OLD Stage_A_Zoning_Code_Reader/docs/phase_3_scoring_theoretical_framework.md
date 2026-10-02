# Stage A, Phase 3 — Town-Level Zoning Restrictiveness Scoring Framework

## 1. Purpose

Phase 3 converts the eight validated town-level zoning variables produced in Phase 2 into an interpretable statewide comparative score.

The unit of analysis is the town:

\[
t \in \mathcal{T}_{CT}
\]

where:

\[
\mathcal{T}_{CT}
=
\{
t_1,t_2,\dots,t_N
\}
\]

is the Connecticut comparison population, initially informed by the Connecticut Zoning Atlas reference dataset.

The central output is a town-level zoning restrictiveness score:

\[
R_t \in [0,100]
\]

where a higher value means the town's dominant residential zoning rules are more restrictive relative to the statewide reference population.

The score is a comparative policy indicator. It is not a legal determination, a housing-production forecast, or a causal estimate of a town's housing supply.

---

## 2. Inputs

For each town \(t\), Phase 2 produces:

\[
R_t^{\text{extract}}
=
\langle
d_t^*,
\mathbf{x}_t,
\mathbf{c}_t,
\mathbf{e}_t,
\mathbf{r}_t
\rangle
\]

where:

- \(d_t^*\) is the verified dominant residential district;
- \(\mathbf{x}_t\) is the eight-variable town rule vector;
- \(\mathbf{c}_t\) is the extraction-confidence vector;
- \(\mathbf{e}_t\) is the source-evidence vector; and
- \(\mathbf{r}_t\) is the review-status vector.

The scoring population also requires a reference dataset:

\[
\mathcal{A}
=
\{
\mathbf{a}_j
:
j = 1,\dots,N
\}
\]

where \(\mathbf{a}_j\) is the standardized zoning-variable record for reference town \(j\), drawn from the Connecticut Zoning Atlas or a documented harmonized statewide dataset.

---

## 3. Score eligibility

A town may be scored only if all required rule values are confirmed:

\[
\text{Eligible}(t)
=
\mathbf{1}
\left[
\bigwedge_{k=1}^{8}
r_{t,k}
=
\text{confirmed}
\right]
\]

For Version 1:

\[
\text{Eligible}(t)=0
\implies
R_t=\text{Not Published}
\]

This avoids converting unknown legal rules into a misleading numerical score.

A town may still appear in a pipeline-status dashboard with:

- number of confirmed variables;
- number of variables requiring review;
- missing-data reasons;
- document version;
- source hash; and
- date of last validation.

---

## 4. Variable orientation

All variables must be oriented so higher normalized values represent greater zoning restrictiveness.

Let:

\[
x_{t,k}
\]

be the raw extracted value for town \(t\), variable \(k\).

Define the oriented variable:

\[
x'_{t,k}
=
g_k(x_{t,k})
\]

where \(g_k\) reverses the direction of variables for which larger raw values are generally less restrictive.

| Variable | Raw interpretation | Restrictiveness orientation |
|---|---|---|
| Minimum lot size | Larger lots required | Larger = more restrictive |
| Minimum lot width | Larger width required | Larger = more restrictive |
| Maximum height | Taller buildings permitted | Smaller = more restrictive |
| Maximum lot coverage | More site coverage permitted | Smaller = more restrictive |
| Summed setbacks | More land reserved around buildings | Larger = more restrictive |
| Parking minimum | More spaces required per dwelling unit | Larger = more restrictive |
| Multifamily pathway | More discretionary/prohibitive approval | Larger ordinal value = more restrictive after recoding |
| ADU pathway | More restrictive/prohibitive permission | Larger ordinal value = more restrictive after recoding |

For maximum height and maximum lot coverage, orient using an inverse transform before percentile ranking:

\[
x'_{t,\text{height}}
=
-x_{t,\text{height}}
\]

\[
x'_{t,\text{coverage}}
=
-x_{t,\text{coverage}}
\]

The negative sign is only an orientation device. The raw value remains visible in all public outputs.

---

## 5. Categorical-variable recoding

### 5.1 Multifamily restrictiveness

Phase 2 extracts a permission-oriented score:

\[
m_t
\in
\{0,1,2,3,4\}
\]

where larger values are more permissive.

Convert it to a restrictiveness scale:

\[
x'_{t,\text{multifamily}}
=
4-m_t
\]

| Permission category | Permission score \(m_t\) | Restrictiveness score \(x'_{t,\text{multifamily}}\) |
|---|---:|---:|
| Permitted by right | 4 | 0 |
| Administrative/site-plan approval | 3 | 1 |
| Special permit/special exception | 2 | 2 |
| Rezoning or legislative pathway | 1 | 3 |
| Prohibited | 0 | 4 |

### 5.2 ADU restrictiveness

Phase 2 extracts a permission-oriented ADU score:

\[
a_t
\in
\{0,1,2,3,4\}
\]

where larger values are more permissive.

Convert it to a restrictiveness scale:

\[
x'_{t,\text{ADU}}
=
4-a_t
\]

| Permission category | Permission score \(a_t\) | Restrictiveness score \(x'_{t,\text{ADU}}\) |
|---|---:|---:|
| Allowed by right | 4 | 0 |
| Allowed under objective conditions | 3 | 1 |
| Conditional discretionary approval | 2 | 2 |
| Effectively unavailable | 1 | 3 |
| Prohibited | 0 | 4 |

The original categorical category and supporting ordinance text remain part of the published score record.

---

## 6. Statewide percentile normalization

For each oriented variable \(x'_{t,k}\), compare town \(t\) to the statewide reference distribution for variable \(k\).

Let:

\[
\mathcal{A}_k
=
\{
a'_{1,k},
a'_{2,k},
\dots,
a'_{N,k}
\}
\]

be the oriented statewide reference distribution.

The percentile rank is:

\[
P_{t,k}
=
100
\cdot
\frac{
\#\{j : a'_{j,k} < x'_{t,k}\}
+
0.5
\cdot
\#\{j : a'_{j,k}=x'_{t,k}\}
}{
N
}
\]

where:

\[
P_{t,k}\in[0,100]
\]

Interpretation:

- \(P_{t,k}=0\): among the least restrictive values in the reference population;
- \(P_{t,k}=50\): near the statewide median;
- \(P_{t,k}=100\): among the most restrictive values in the reference population.

Percentile normalization is preferable to direct arithmetic comparison because lot sizes, setback units, and approval categories operate on different scales.

---

## 7. Reference-data harmonization

Before percentile ranking, the Phase 2 output and Atlas/reference data must be harmonized.

For each variable \(k\), define:

\[
H_k
:
\text{Phase 2 schema}
\leftrightarrow
\text{reference schema}
\]

The harmonization log must document:

- reference field name;
- unit conversion;
- directionality;
- categorical recoding;
- treatment of missing values;
- date/version of reference dataset;
- reference-population size; and
- known definitional differences.

A reference field may not be used for scoring if it is not conceptually comparable to the Phase 2 variable.

For example, a minimum lot-size comparison is valid only if both values refer to comparable residential zoning contexts and are measured in compatible units.

---

## 8. Composite town score

The Version 1 town score is an equal-weighted average of the eight percentile ranks:

\[
R_t
=
\frac{1}{8}
\sum_{k=1}^{8}
P_{t,k}
\]

Equivalently:

\[
R_t
=
\sum_{k=1}^{8}
w_kP_{t,k}
\]

with:

\[
w_k=\frac{1}{8}
\]

and:

\[
\sum_{k=1}^{8}w_k=1
\]

The published score is:

\[
\text{TownScore}_t
=
100 \cdot
\left(
\frac{1}{8}
\sum_{k=1}^{8}
\frac{P_{t,k}}{100}
\right)
=
R_t
\]

Thus:

\[
\text{TownScore}_t \in [0,100]
\]

A high score means the town's dominant residential district is comparatively restrictive across the selected rule set.

### 8.1 Why equal weights in Version 1

Equal weighting is the default because:

- it is transparent;
- it avoids pretending that the project has validated causal weights;
- it prevents an unreviewed subjective judgment from dominating the score;
- each of the eight rules is explicitly part of the policy framework; and
- sensitivity analysis can show how rankings change under alternatives.

Equal weights do not imply that all rules have identical real-world effects on housing production. They are a Version 1 transparency choice.

---

## 9. Score decomposition

Every published town score must be accompanied by its full component vector:

\[
\mathbf{P}_t
=
\begin{bmatrix}
P_{t,\text{lot}} \\
P_{t,\text{width}} \\
P_{t,\text{height}} \\
P_{t,\text{coverage}} \\
P_{t,\text{setback}} \\
P_{t,\text{parking}} \\
P_{t,\text{multifamily}} \\
P_{t,\text{ADU}}
\end{bmatrix}
\]

The score display must include:

| Field | Description |
|---|---|
| Town score | Equal-weight composite \(R_t\) |
| Raw rule value | Directly extracted town-level rule value |
| Oriented rule value | Value after restrictiveness orientation |
| Statewide percentile | \(P_{t,k}\) |
| Dominant district | District from which the town-level rule was derived |
| Evidence excerpt | Exact ordinance sentence or table cell |
| Source page/section | Provenance pointer |
| Confidence | Phase 2 extraction confidence |
| Review status | Confirmed / review required / missing |
| Reference-data field | Atlas/reference counterpart used for percentile rank |

A user must be able to answer:

\[
\text{Why did town } t \text{ receive score } R_t?
\]

without needing to inspect model internals.

---

## 10. Confidence and uncertainty reporting

The composite score should never hide uncertainty.

Let:

\[
c_{t,k}
\in [0,1]
\]

be Phase 2 confidence for rule \(k\).

Define descriptive town-level extraction confidence:

\[
C_t
=
\frac{1}{8}
\sum_{k=1}^{8}
c_{t,k}
\]

This confidence value is not a substitute for eligibility. A town must still meet the confirmed-variable rule before receiving a published composite score.

The published score record includes:

\[
\langle
R_t,
C_t,
\mathbf{P}_t,
\mathbf{r}_t
\rangle
\]

where \(\mathbf{r}_t\) records review status for all eight components.

---

## 11. Sensitivity analysis

The system must report whether town rankings depend strongly on modeling choices.

### 11.1 Alternative district-collapse rule

The primary method is:

\[
d_t^*
=
\arg\max_{d\in\mathcal{D}^{\text{res}}_t}
A_d^{\text{dev}}
\]

A sensitivity scenario may instead use:

\[
x_{t,k}^{\text{restrictive}}
=
\max_{d\in\mathcal{D}^{\text{res}}_t}
x'_{d,k}
\]

where the most restrictive district rule is selected for each variable.

This scenario is reported as a sensitivity analysis only. It is not the default published score because a small district should not automatically define a whole town.

### 11.2 Alternative score weights

For a set of alternative weights:

\[
\mathbf{w}^{(s)}
=
\{
w_1^{(s)},
\dots,
w_8^{(s)}
\}
\]

calculate:

\[
R_t^{(s)}
=
\sum_{k=1}^{8}
w_k^{(s)}P_{t,k}
\]

Potential scenarios include:

| Scenario | Weighting rule |
|---|---|
| Version 1 baseline | Equal weights |
| Dimensional emphasis | Higher total weight on lot size, setbacks, height, and coverage |
| Housing-type emphasis | Higher total weight on multifamily and ADU pathways |
| Parking sensitivity | Higher parking weight |
| Leave-one-out | Omit one variable at a time |

Rank stability is summarized using:

\[
\Delta \text{Rank}_t^{(s)}
=
\text{Rank}_t^{(s)}
-
\text{Rank}_t^{\text{baseline}}
\]

and rank correlation:

\[
\rho_s
=
\text{SpearmanCorr}
\left(
\text{Rank}^{(s)},
\text{Rank}^{\text{baseline}}
\right)
\]

### 11.3 Interpretation

If rankings change sharply under plausible scenarios, the dashboard should state that the town's comparative placement is **weight-sensitive**.

---

## 12. Missing-data policy

No missing rule is assigned an arbitrary restrictive or permissive value.

For Version 1:

\[
\exists k:
r_{t,k}
\neq
\text{confirmed}
\implies
R_t=\text{Not Published}
\]

A future research version may calculate a provisional partial score:

\[
R_t^{\text{partial}}
=
\frac{
\sum_{k \in K_t^{\text{confirmed}}}
w_k P_{t,k}
}{
\sum_{k \in K_t^{\text{confirmed}}}
w_k
}
\]

but it must be visibly labeled:

\[
\text{PROVISIONAL — INCOMPLETE VARIABLE COVERAGE}
\]

The Version 1 public comparison should avoid partial-score ranking.

---

## 13. Change tracking over time

For each town \(t\), let:

\[
F_t^{(\tau)}
\]

denote the versioned ordinance document collected at time \(\tau\).

When the ordinance source changes:

\[
F_t^{(\tau)}
\neq
F_t^{(\tau-1)}
\]

the system computes a document change signal:

\[
\Delta F_t^{(\tau)}
=
\text{Diff}
\left(
F_t^{(\tau)},
F_t^{(\tau-1)}
\right)
\]

If the change affects evidence relevant to any target variable, rerun Phase 2 and Phase 3:

\[
\mathbf{x}_t^{(\tau)}
\rightarrow
\mathbf{P}_t^{(\tau)}
\rightarrow
R_t^{(\tau)}
\]

Store a score history:

\[
\mathcal{H}_t
=
\{
(
\tau,
R_t^{(\tau)},
\mathbf{x}_t^{(\tau)},
\mathbf{P}_t^{(\tau)},
\text{document hash}^{(\tau)}
)
\}
\]

The system must distinguish:

- ordinance change;
- extraction-model change;
- reference-dataset update;
- scoring-methodology change; and
- manual correction.

A ranking change should never be presented as a zoning-policy change unless the cause is documented.

---

## 14. Validation

### 14.1 Manual ordinance validation

For each pilot town:

1. Manually identify the dominant residential district.
2. Manually verify all eight extracted variables.
3. Confirm all source excerpts, table cells, and citations.
4. Compare automated and manual values.
5. Review all discrepancies.
6. Approve the town only after all eight variables are confirmed.

### 14.2 Reference-data validation

Where the Connecticut Zoning Atlas contains comparable town-level fields:

\[
\text{Validate}(x_{t,k}, a_{t,k})
\]

Report:

- exact agreement;
- normalized-unit agreement;
- definitional mismatch;
- reference-data missingness;
- Atlas coding date; and
- explanation for disagreement.

Disagreement does not automatically prove either source wrong. It is a review trigger because ordinance versions, coding definitions, and district-selection methods may differ.

### 14.3 Ranking validation

Before publication:

- inspect component percentile values;
- identify outlier towns;
- verify raw ordinance evidence for extreme percentile results;
- test sensitivity to weighting choices;
- test sensitivity to dominant-district selection;
- confirm that score directionality is correct; and
- ensure that missing values are excluded from scoring.

---

## 15. Published town score record

The final town-level score record is:

\[
S_t
=
\langle
t,
d_t^*,
\mathbf{x}_t,
\mathbf{P}_t,
R_t,
C_t,
\mathbf{e}_t,
\mathbf{r}_t,
\mathcal{H}_t
\rangle
\]

The public-facing schema includes:

| Category | Required fields |
|---|---|
| Identity | Town, state, town ID |
| Score | Town score, statewide rank, percentile interpretation |
| Components | Eight raw values, oriented values, and percentiles |
| Dominant district | Code, name, residential area, district-area share |
| Provenance | Document title, version date, retrieval date, source URL, SHA-256 hash |
| Evidence | Source excerpts, pages, sections, table coordinates |
| Quality | Extraction confidence, conflict status, review status |
| Method | Reference-data version, percentile method, weighting scenario |
| Time | Pipeline run date, score effective date, prior-score comparison |

---

## 16. Explicit Version 1 scope

Version 1 includes:

- town-level zoning-rule extraction;
- dominant-residential-district selection;
- eight-variable scoring;
- statewide percentile comparison;
- equal-weight composite score;
- evidence-linked audit records;
- sensitivity analysis; and
- document-version tracking.

Version 1 does not include:

- district-level public scorecards;
- parcel-level development-capacity modeling;
- housing-production causal prediction;
- probability-of-reform prediction;
- hand-selected causal weights;
- unverified GIS district-area inference;
- scoring of incomplete towns; or
- legal advice or formal legal determinations.

District-level scoring remains a possible Version 2 extension:

\[
R_d
=
\frac{1}{8}
\sum_{k=1}^{8}
P_{d,k}
\]

but it is not required for the town-level Version 1 system.
