# urop-research-guide

Research guide: Hospital meal plan analysis, diet group comparison, and nutritional rules.

## Project Structure

```
urop-research-guide/
├── monthly_plan_logic/
│   ├── data/
│   │   ├── weekly_meal_plan_85k.json   # Meal plan data (10 diet groups)
│   │   └── rules.txt                    # Extracted text from rules.pdf
│   ├── compare_diet_groups.py           # Script: diff each diet group vs baseline
│   ├── extract_rules.py                 # Script: extract PDF rules to text
│   └── ANALYSIS_diet_group_differences.md  # Analysis report
└── README.md
```

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

See `ANALYSIS_diet_group_differences.md` for full details with nutritional rules citations.

## Scripts

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
- `rules.pdf` — Hướng dẫn chế độ ăn bệnh viện (QĐ 2879/QĐ-BYT ngày 10/8/2006)
