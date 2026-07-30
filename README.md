# afya-medqol

Computes the Afya MedQoL Physician quality-of-life index from instrument
responses — practicing physicians (13 items, 3 domains) — with 100%
deterministic scoring (fixed quadrature, no random seed).

Calibration parameters are frozen in source code
([`parameters_physician.py`](src/afya_medqol/parameters_physician.py)) —
there is no external file (CSV/Excel) read at runtime.

## Installation

```bash
pip install afya-medqol
```

---

Three-dimensional Samejima GRM (Graded Response Model) with EAP (Expected A
Posteriori) scoring. Calibration frozen at **2024_2** (Gobbo Jr M et al.,
*BMJ Open* 2025;15:e102783), with independent domains (Σ = I): each domain
(F1, F2, F3) works as its own ruler — zeroing or excluding items from one
domain does not affect the others.

| Domain | Construct | Items |
|---|---|---|
| F1 | Quality of Life | 6 items (`F1_1_enjoymentoflife`, `F1_2_financialsufficiency`, `F1_3_accesstoinformation`, `F1_4_leisureopportunities`, `F1_5_mobilitypast2weeks`, `F1_6_accesstohealthservices`) |
| F2 | Institutional Support / Work Perception | 4 items (`F2_1_technicaltraining`, `F2_2_mentalhealthsupport`, `F2_3_coworkersupportnetwork`, `F2_4_educationalhandlingoferrors`) |
| F3 | Perceived Stress | 3 items (`F3_1_stresshurtsperformance`, `F3_2_stressledtoerrors`, `F3_3_stresshurtsrelationships`) |

The global score combines the three domains (F3 reversed only in this
composite) with weights proportional to each factor's discrimination
(Σ\|a\|).

### Library usage

```python
import pandas as pd
from afya_medqol import MedQoLPhysicianCalculator

df_responses = pd.read_csv("responses.csv")

calc = MedQoLPhysicianCalculator()
result = calc.score_batch(df_responses)

print(result[["theta_global", "T_score_global"]])
```

Scoring a single respondent:

```python
result = calc.score_physician({
    "F1_1_enjoymentoflife": 4,
    "F1_2_financialsufficiency": 3,
    # ... remaining items (see afya_medqol.ITENS_TODOS)
})
print(result["theta_global"], result["T_score_global"])
```

To look up the original questionnaire wording for any item, use
`ITEM_QUESTIONS` (a plain `dict` keyed by item, then by language code —
`"en"` or `"pt"`) or the `item_questions(lang="en")` method on a calculator
instance, which returns the flat `item -> text` dict for the requested
language (English by default):

```python
from afya_medqol import ITEM_QUESTIONS

print(ITEM_QUESTIONS["F1_1_enjoymentoflife"]["pt"])
print(calc.item_questions()["F1_1_enjoymentoflife"])            # English (default)
print(calc.item_questions(lang="pt")["F1_1_enjoymentoflife"])   # Portuguese
```

`MedQoLPhysicianCalculator` precomputes the quadrature grid and item probabilities
once at construction time — reuse the same instance when scoring multiple
batches.

### Command line

```bash
afya-medqol responses.csv
afya-medqol responses.csv --saida result.csv
```

### Output

- `theta1_quality_of_life`, `theta2_institutional_support`, `theta3_perceived_stress`, `theta_global`
- `T_score_global` (50 + 10·θ_global)

---

## License

Apache License 2.0 — see [LICENSE](LICENSE).
