# Stage A, Phase 2 — Rule Extraction Theoretical Framework

## 1. Purpose

Phase 2 transforms the validated municipal evidence collected in Phase 1 into a structured **town-level zoning-rule vector**.

The town is the primary analytic unit:

\[
t \in \mathcal{T}
\]

where:

\[
\mathcal{T}
=
\{
\text{Greenwich},
\text{Stamford},
\text{Norwalk},
\text{Westport},
\text{Darien},
\dots
\}
\]

Phase 1 produces district evidence bundles. Phase 2 uses those bundles to determine a single, transparent town-level value for each zoning variable.

The output is not a legal opinion. It is a traceable, structured policy-measurement record in which every extracted value links to:

- the controlling district-selection rule;
- the relevant ordinance excerpt or table cell;
- source page and document version;
- extraction method;
- model and regex confidence;
- conflict status; and
- human-review status.

---

## 2. Input from Phase 1

For town \(t\), the Phase 1 collection output is:

\[
\mathcal{E}_t
=
\{
(d, E_d, \mathcal{M}_d)
:
d \in \mathcal{D}_t
\}
\]

where:

- \(\mathcal{D}_t\) is the set of detected zoning districts in town \(t\);
- \(E_d\) is the evidence bundle for district \(d\); and
- \(\mathcal{M}_d\) is district metadata and provenance.

Each district evidence bundle is:

\[
E_d
=
T_d^{\text{primary}}
\cup
T_d^{\text{linked}}
\cup
T_d^{\text{tables}}
\cup
T_d^{\text{general}}
\cup
T_d^{\text{overlay}}
\]

where:

| Evidence component | Definition |
|---|---|
| \(T_d^{\text{primary}}\) | Direct district-specific ordinance text |
| \(T_d^{\text{linked}}\) | Resolved cross-referenced provisions |
| \(T_d^{\text{tables}}\) | Matched dimensional-table rows and cells |
| \(T_d^{\text{general}}\) | Explicitly applicable townwide provisions |
| \(T_d^{\text{overlay}}\) | Overlay evidence or conditional modifiers |

The town-level extraction pipeline uses only evidence with acceptable collection confidence and known source provenance.

---

## 3. Eight-variable schema

For each town \(t\), Phase 2 extracts the standardized zoning-rule vector:

\[
\mathbf{x}_t
=
\begin{bmatrix}
x_{t,1} \\
x_{t,2} \\
x_{t,3} \\
x_{t,4} \\
x_{t,5} \\
x_{t,6} \\
x_{t,7} \\
x_{t,8}
\end{bmatrix}
\]

where:

| \(k\) | Variable | Symbol | Data type | Direction before normalization |
|---:|---|---|---|---|
| 1 | Minimum lot size | \(x_{t,\text{lot}}\) | Continuous, square feet | Larger is generally more restrictive |
| 2 | Minimum lot width | \(x_{t,\text{width}}\) | Continuous, feet | Larger is generally more restrictive |
| 3 | Maximum building height | \(x_{t,\text{height}}\) | Continuous, feet | Smaller is generally more restrictive |
| 4 | Maximum lot coverage | \(x_{t,\text{coverage}}\) | Continuous, percent | Smaller is generally more restrictive |
| 5 | Summed minimum setbacks | \(x_{t,\text{setback}}\) | Continuous, feet | Larger is generally more restrictive |
| 6 | Minimum off-street parking | \(x_{t,\text{parking}}\) | Continuous, spaces per dwelling unit | Larger is generally more restrictive |
| 7 | Multifamily approval pathway | \(x_{t,\text{multifamily}}\) | Ordinal categorical | More discretionary/prohibitive is more restrictive |
| 8 | ADU permission pathway | \(x_{t,\text{ADU}}\) | Ordinal categorical | More restrictive/prohibitive is more restrictive |

The variable schema is fixed before statewide scoring.

A variable may be marked:

\[
\text{status}_{t,k}
\in
\{
\text{confirmed},
\text{review required},
\text{missing},
\text{not applicable}
\}
\]

A missing value is not treated as a restrictive value.

---

## 4. Dominant-district selection

### 4.1 Rationale

A town often contains multiple residential districts with different dimensional rules. Therefore, a town-level score requires an explicit district-collapse rule.

The default Phase 2 rule selects the **dominant residential district by verified developable residential land area**.

Let:

\[
\mathcal{D}^{\text{res}}_t
\subseteq
\mathcal{D}_t
\]

be the set of base residential districts in town \(t\).

Let:

\[
A_d^{\text{dev}}
\]

be the developable residential land area associated with district \(d\), after any documented removal of non-buildable water, rights-of-way, public parks, or other excluded land.

The dominant residential district is:

\[
d_t^*
=
\arg\max_{d \in \mathcal{D}^{\text{res}}_t}
A_d^{\text{dev}}
\]

The town-level value for rule \(k\) is then extracted from the evidence bundle of \(d_t^*\):

\[
x_{t,k}
=
\text{ExtractRule}(E_{d_t^*}, k)
\]

This means the town-level record represents the zoning standards applicable in the residential district covering the largest verified developable residential area.

### 4.2 Required district-selection metadata

Every town-level extraction record must retain:

\[
Z_t
=
\langle
d_t^*,
A_{d_t^*}^{\text{dev}},
\text{district area source},
\text{GIS join status},
\text{selection confidence}
\rangle
\]

At minimum, record:

- selected dominant district code;
- selected district name;
- district developable area;
- share of all residential developable area;
- geometry source;
- geometry ID;
- spatial confidence;
- whether overlays were considered;
- selection date; and
- selection-review status.

### 4.3 No-GIS fallback

If verified GIS geometry is unavailable, Phase 2 must not silently invent a dominant district.

Instead:

\[
d_t^*
=
\bot
\]

and town-level numerical extraction is marked:

\[
\text{status}_{t,k}
=
\text{review required}
\]

Permitted temporary fallback methods, in descending order of preference, are:

1. Manually verified official zoning-map area estimate.
2. Manually verified official planning/GIS district-area table.
3. Expert-reviewed proxy district selection, explicitly labeled as provisional.
4. No town score until a verified dominant district can be identified.

---

## 5. Candidate-evidence retrieval

For every target rule \(k\), Phase 2 first retrieves a constrained candidate set:

\[
C_{t,k}
=
\text{RetrieveCandidates}(E_{d_t^*}, k)
\]

Candidate evidence may include:

- matched dimensional table cells;
- district primary text;
- directly resolved references;
- explicitly applicable townwide provisions;
- verified overlay modifiers; and
- rule definitions needed to interpret the variable.

Candidate retrieval uses a rule-specific evidence map:

| Variable | Preferred evidence order |
|---|---|
| Minimum lot size | Matched dimensional table → district text → linked provision |
| Minimum lot width | Matched dimensional table → district text → linked provision |
| Maximum height | Matched dimensional table → district text → linked provision → verified overlay |
| Maximum lot coverage | Matched dimensional table → district text → linked provision |
| Summed setbacks | Matched dimensional table → district text → linked provision |
| Parking minimum | Explicitly applicable townwide parking provision → district text → linked provision |
| Multifamily pathway | District permitted-use text → use table → approval procedure → linked provision |
| ADU permission | Explicitly applicable ADU provision → district applicability clause → linked provision |

No evidence is retrieved solely because it is linguistically similar. It must remain linked to its source type and legal scope.

---

## 6. Regex and Legal-BERT ensemble

### 6.1 Ensemble objective

The extraction system combines:

1. deterministic regex and table parsing;
2. semantic Legal-BERT classification/ranking;
3. rule-specific normalization;
4. source-precedence checks; and
5. human review for uncertain results.

For candidate evidence item \(c \in C_{t,k}\), the ensemble estimates:

\[
P(y_{c,k} = 1)
=
f_{\text{ensemble}}
\left(
f_{\text{regex}}(c,k),
f_{\text{table}}(c,k),
f_{\text{LegalBERT}}(c,k),
f_{\text{scope}}(c,k),
f_{\text{source}}(c)
\right)
\]

where:

- \(y_{c,k}=1\) means candidate \(c\) governs rule \(k\);
- \(f_{\text{regex}}\) measures structured textual/numeric matching;
- \(f_{\text{table}}\) measures validated row-column-table structure;
- \(f_{\text{LegalBERT}}\) measures semantic relevance;
- \(f_{\text{scope}}\) measures applicability to \(d_t^*\); and
- \(f_{\text{source}}\) measures source authority and conflict status.

### 6.2 Regex responsibilities

Regex and deterministic parsers are responsible for high-precision tasks:

- statutory citations;
- district codes;
- numeric values;
- units;
- percentage values;
- table row labels;
- table column labels;
- modal legal terms;
- direct permission/prohibition terms;
- special-permit and site-plan terminology;
- applicability phrases; and
- exception markers.

Examples:

| Target | Illustrative deterministic signals |
|---|---|
| Minimum lot size | `minimum lot size`, `lot area`, `acre`, `sq. ft.` |
| Maximum height | `maximum height`, `height shall not exceed`, `feet` |
| Parking | `off-street parking`, `spaces per dwelling unit`, `parking requirement` |
| Multifamily | `multifamily`, `two-family`, `three-family`, `special permit`, `permitted use` |
| ADU | `accessory dwelling unit`, `ADU`, `accessory apartment`, `permitted`, `prohibited` |

### 6.3 Legal-BERT responsibilities

Legal-BERT is used to:

- classify whether a passage concerns one or more target variables;
- rank candidate passages retrieved from the evidence bundle;
- identify the most relevant supporting span;
- distinguish a legal requirement from a definition, example, exception, or citation;
- identify permission, prohibition, and discretionary-review language; and
- flag semantic disagreement with a deterministic extraction.

Legal-BERT does not independently establish a legal rule without source-linked evidence.

### 6.4 Ensemble decision states

For each rule \(k\), the ensemble produces:

\[
\hat{x}_{t,k}
=
\langle
v_{t,k},
u_{t,k},
s_{t,k},
e_{t,k},
c_{t,k},
r_{t,k}
\rangle
\]

where:

| Field | Meaning |
|---|---|
| \(v_{t,k}\) | Normalized rule value |
| \(u_{t,k}\) | Unit or category |
| \(s_{t,k}\) | Extracted legal status |
| \(e_{t,k}\) | Evidence provenance |
| \(c_{t,k}\) | Ensemble confidence |
| \(r_{t,k}\) | Review status |

The review status is:

\[
r_{t,k}
\in
\{
\text{auto accepted},
\text{review required},
\text{missing},
\text{not applicable}
\}
\]

---

## 7. Rule-specific extraction functions

### 7.1 Continuous dimensional rules

For continuous variables:

\[
k
\in
\{
\text{lot},
\text{width},
\text{height},
\text{coverage},
\text{setback},
\text{parking}
\}
\]

the extraction function returns:

\[
v_{t,k}
=
\text{NormalizeUnits}
\left(
\text{SelectAuthoritativeCandidate}(C_{t,k})
\right)
\]

All numerical outputs retain:

- raw source value;
- normalized value;
- original unit;
- normalized unit;
- source excerpt;
- table row and column, if applicable;
- page;
- section;
- extraction confidence; and
- review status.

#### Unit normalization

| Rule | Canonical unit |
|---|---|
| Minimum lot size | Square feet |
| Minimum lot width | Feet |
| Maximum height | Feet |
| Maximum lot coverage | Percent |
| Summed setbacks | Feet |
| Parking minimum | Spaces per dwelling unit |

Examples:

\[
1\text{ acre}
=
43{,}560\text{ square feet}
\]

\[
x_{t,\text{setback}}
=
x_{t,\text{front}}
+
x_{t,\text{side-left}}
+
x_{t,\text{side-right}}
+
x_{t,\text{rear}}
\]

If a code provides only one side-yard value for a symmetric requirement:

\[
x_{t,\text{setback}}
=
x_{t,\text{front}}
+
2x_{t,\text{side}}
+
x_{t,\text{rear}}
\]

If setbacks differ by building type, lot width, height, or other conditional facts, the system records the condition rather than forcing one universal number.

### 7.2 Multifamily approval pathway

Multifamily approval is converted from legal text into an ordinal policy category:

\[
x_{t,\text{multifamily}}
\in
\{0,1,2,3,4\}
\]

| Ordinal value | Category | Operational meaning |
|---:|---|---|
| 0 | Prohibited | Multifamily use is prohibited in the selected district |
| 1 | Discretionary legislative or rezoning pathway | Requires rezoning, amendment, planned-development approval, or similarly discretionary action |
| 2 | Special permit / special exception | Listed as potentially allowed but requires discretionary special approval |
| 3 | Site plan or administrative review | Allowed subject primarily to objective administrative or site-plan review |
| 4 | Permitted by right | Listed as permitted without discretionary use approval |

If multiple housing intensities exist, the pipeline records the exact use class:

\[
\text{MFType}
\in
\{
\text{two-family},
\text{three-family},
\text{multifamily},
\text{apartment},
\text{mixed-use residential}
\}
\]

A town-level multifamily value is not treated as confirmed unless the relevant dwelling type is explicitly identified.

### 7.3 ADU permission pathway

ADU status is likewise converted to an ordinal category:

\[
x_{t,\text{ADU}}
\in
\{0,1,2,3,4\}
\]

| Ordinal value | Category | Operational meaning |
|---:|---|---|
| 0 | Prohibited | ADUs are expressly prohibited or unavailable |
| 1 | Effectively unavailable | Allowed only through rezoning, legislative action, or an exceptional discretionary process |
| 2 | Conditional discretionary approval | Allowed through special permit, special exception, or similarly discretionary approval |
| 3 | Allowed subject to objective conditions | Allowed under documented size, owner-occupancy, parking, or design standards |
| 4 | Allowed by right | Allowed without discretionary use approval, subject to ordinary objective regulations |

The extraction record also retains conditions such as:

- owner occupancy;
- attached versus detached eligibility;
- lot-size threshold;
- parking requirement;
- maximum floor area;
- occupancy restrictions;
- deed restrictions; and
- approval pathway.

---

## 8. Source precedence and conflict policy

For a given rule \(k\), extracted candidate values may conflict.

The selection function is:

\[
\text{SelectAuthoritativeCandidate}
:
C_{t,k}
\rightarrow
\hat{x}_{t,k}
\cup
\{\text{manual review}\}
\]

The precedence policy is:

| Situation | Resolution |
|---|---|
| A general provision defines a term used by a district rule | Retain the definition as interpretation context; do not replace a district or table numeric value |
| District prose conflicts with a validated dimensional-table cell | Prefer the table cell for directly comparable dimensional values |
| District text conflicts with a linked general provision | Prefer the narrower and more specific provision if scope is explicit |
| Verified overlay modifies a base district rule | Store base value and overlay modifier separately; do not overwrite the base value |
| Multiple candidates remain equally plausible | Require manual review |
| Evidence is missing or scope is unclear | Mark missing/review required; do not infer a value |

A conflict must never be silently resolved merely because one candidate has a higher model confidence.

---

## 9. Confidence model

For rule \(k\), define component confidence:

\[
c_{t,k}
=
\alpha c_{\text{regex}}
+
\beta c_{\text{LegalBERT}}
+
\gamma c_{\text{source}}
+
\delta c_{\text{scope}}
+
\epsilon c_{\text{table}}
\]

subject to:

\[
\alpha+\beta+\gamma+\delta+\epsilon=1
\]

where unavailable components receive zero weight and the remaining weights are renormalized.

Illustrative confidence inputs:

| Component | Interpretation |
|---|---|
| \(c_{\text{regex}}\) | Exactness of structured pattern, value, and unit match |
| \(c_{\text{LegalBERT}}\) | Semantic relevance and supporting-span confidence |
| \(c_{\text{source}}\) | Reliability of source text, page quality, and conflict state |
| \(c_{\text{scope}}\) | Explicit applicability to dominant district |
| \(c_{\text{table}}\) | Table row-column integrity and district-row match confidence |

Auto-acceptance requires:

\[
\text{AutoAccept}(t,k)
=
\mathbf{1}
\left[
c_{t,k}\geq\tau_E
\land
\text{scope verified}
\land
\text{no unresolved conflict}
\land
\text{dominant district verified}
\right]
\]

All other extractions receive:

\[
r_{t,k}
=
\text{review required}
\]

---

## 10. Town-level extraction record

The Phase 2 output for town \(t\) is:

\[
R_t
=
\langle
t,
d_t^*,
\mathbf{x}_t,
\mathbf{c}_t,
\mathbf{e}_t,
\mathbf{r}_t,
Z_t
\rangle
\]

where:

- \(t\) is the town;
- \(d_t^*\) is the selected dominant residential district;
- \(\mathbf{x}_t\) contains the eight extracted rule values;
- \(\mathbf{c}_t\) contains the eight confidence values;
- \(\mathbf{e}_t\) contains source evidence;
- \(\mathbf{r}_t\) contains review status; and
- \(Z_t\) contains district-selection metadata.

The machine-readable row schema includes:

| Field group | Example fields |
|---|---|
| Town identity | `town`, `state`, `town_id` |
| Dominant district | `dominant_district_code`, `dominant_district_name`, `dominant_residential_area_acres`, `dominant_residential_area_share` |
| Rule value | `minimum_lot_size_sqft`, `maximum_height_ft`, `adu_status_ordinal` |
| Evidence | `source_excerpt`, `source_page`, `source_section`, `table_id`, `row_label`, `column_label` |
| Model result | `regex_confidence`, `legalbert_confidence`, `ensemble_confidence` |
| Review | `conflict_status`, `review_status`, `review_note` |
| Versioning | `document_hash`, `document_version_date`, `date_retrieved`, `pipeline_run_id` |

---

## 11. Phase 2 validation

### 11.1 Manual gold standard

For each pilot town:

1. Identify the dominant residential district using verified area data.
2. Manually extract all eight rule values.
3. Record supporting ordinance citations and excerpts.
4. Compare automated output with manual output.
5. Resolve every discrepancy before using the town for scoring.

### 11.2 Metrics

| Task | Metric |
|---|---|
| Dominant-district selection | Exact-match accuracy against manually verified district |
| Numeric extraction | Exact normalized-value match |
| Unit extraction | Exact unit match |
| Table matching | Exact district-row and column-label match |
| Categorical extraction | Accuracy and macro-F1 |
| Evidence retrieval | Recall of manually identified governing provision |
| Citation resolution | Precision and recall |
| Review routing | Recall of known ambiguous/conflicting cases |
| Overall town completeness | Share of eight variables confirmed without unresolved conflict |

For variable \(k\):

\[
\text{Accuracy}_k
=
\frac{
\#\{\text{correct confirmed town-level extractions}\}
}{
\#\{\text{manually labeled town-level cases}\}
}
\]

### 11.3 Score-eligibility rule

A town may enter Phase 3 scoring only if:

\[
\sum_{k=1}^{8}
\mathbf{1}
[
r_{t,k}
=
\text{confirmed}
]
\geq q_{\min}
\]

where \(q_{\min}\) is a predefined completeness threshold.

For the initial pilot:

\[
q_{\min}=8
\]

That is, all eight variables should be confirmed before publishing a composite town score.

---

## 12. Explicit limitations

Phase 2 does not:

- determine whether a zoning code is legally valid;
- substitute for legal counsel;
- infer district area without an identified source;
- assume a townwide rule applies without explicit scope;
- assume a missing rule is restrictive;
- treat low-confidence model output as a confirmed ordinance rule;
- treat overlays as townwide rules; or
- produce district-level rankings in Version 1.

District-level extraction and scoring remain an optional later refinement after town-level validation is complete.  