# urop-research-guide

Research guide: Hospital meal plan analysis, diet group comparison, and nutritional validation.

## Project Structure

```
urop-research-guide/
├── monthly_plan_logic/
│   ├── data/
│   │   ├── weekly_meal_plan_85k.json   # Meal plan data (10 diet groups)
│   │   ├── VTN_FCT_2007_food_composition.csv  # Vietnamese FCT 2007 (2077 entries)
│   │   ├── sp_thuong_mai.csv          # Supplemental market foods
│   │   └── rules.txt                  # Extracted text from rules.pdf
│   ├── validate_nutrition.py            # Main: parse + FCT lookup + validation
│   ├── extract_rules.py                # Extract PDF rules to text
│   ├── compare_diet_groups.py          # Diff each diet group vs baseline
│   ├── parse_85k_weekly.py            # Parse raw meal plan CSV → JSON
│   ├── special_case.md                 # FCT mapping decisions & known gaps
│   └── ANALYSIS_*.md                   # Analysis & validation reports
└── README.md                          # (this file)
```

## Meal Plan Validation Pipeline

```
Input: weekly_meal_plan_85k.json + VTN_FCT_2007_food_composition.csv
  │
  ├─ parse_85k_weekly.py       → weekly_meal_plan_85k.json (one-time)
  │
  └─ validate_nutrition.py     → validation_summary.json
       │
       ├─ parse_breakfast_detail()   Parse breakfast: sữa + thực phẩm
       ├─ parse_items()              Parse rice/veg/soup lines
       ├─ parse_proteins()           Parse protein section (with compound dishes)
       ├─ parse_compound_dish()      Split multi-ingredient dishes into components
       ├─ FCT_NAMES{}                Manual name → FCT entry mapping
       ├─ resolve()                  Name + weight → {kcal, P, L, G}
       ├─ build_fct()                Load & cache FCT + sp_thuong_mai
       ├─ calc_day()                 Sum 5 sections → daily totals + %
       └─ validate()                 Compare vs diet-group rules → ⚠️/✅
```

Run:
```bash
python monthly_plan_logic/validate_nutrition.py
```

See `monthly_plan_logic/special_case.md` for FCT mapping decisions and known gaps.

---

## Analysis

### What was analyzed

The weekly meal plan (`weekly_meal_plan_85k.json`) contains **10 diet groups** across **7 days × 3 meals** with 4 slots each (rice, vegetable, protein, soup) + breakfast (main + milk):

- **Page 1**: Standard menu (BT01-CƠM) — baseline
- **Pages 2–11**: 10 diet groups adjusted for specific conditions

### Key findings

| Diet group | Changes | Main pattern |
|---|---|---|
| Phẫu thuật (P2) | 0 | Identical to baseline |
| Sản khoa (P3) | 27 | Breakfast → porridge; rau cải → đậu/bí |
| Bệnh thận (P4) | 4 | Swap high-K rau củ for low-K alternatives |
| Tim mạch (P5) | 0 | Identical to baseline |
| Đái tháo đường (P6) | 29 | Rice 150→100g; rau 200→230g |
| Gan mật (P7) | 0 | Identical to baseline |
| Ung thư (P8) | 0 | Identical to baseline |
| Gút (P9) | 0 | Identical to baseline |
| Kiêng i-ốt (P10) | 35 | Gạo Lào→Thái; bỏ rau cải |
| Người nhà (P11) | 0 | Identical to baseline |

See `monthly_plan_logic/REPORT_nutrition_validation.md` for full validation report and FCT mapping decisions.

## Scripts

### `validate_nutrition.py` (primary)
Parses the meal plan, resolves every dish against FCT, computes daily kcal/protein/fat/carb, and validates against diet-group rules.

```bash
python monthly_plan_logic/validate_nutrition.py
```

### `compare_diet_groups.py`
Compares each diet group (pages 2–11) against the baseline standard menu (page 1).

```bash
python monthly_plan_logic/compare_diet_groups.py
```

### `extract_rules.py`
Extracts text from `rules.pdf` into `rules.txt` for analysis.

```bash
python monthly_plan_logic/extract_rules.py
```

## Data Sources

- `weekly_meal_plan_85k.json` — Thực đơn cơm tháng 5/2026, mức ăn 85.680đ (10 nhóm bệnh)
- `VTN_FCT_2007_food_composition.csv` — Bảng thành phần dinh dưỡng thực phẩm Việt Nam 2007 (2077 entries)
- `sp_thuong_mai.csv` — Thành phần dinh dưỡng thực phẩm thương mại Việt Nam (bổ sung)
- `rules.pdf` — Hướng dẫn chế độ ăn bệnh viện (QĐ 2879/QĐ-BYT ngày 10/8/2006)

