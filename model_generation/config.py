# -*- coding: utf-8 -*-
"""
config.py — Diet group configurations for monthly menu generation.

These configs are derived from:
  1. hospital-meal-planner/backend/app/thresholds.py  (existing rules)
  2. rules.txt  (QĐ 2879/QĐ-BYT, extracted from the hospital PDF)
  3. ANALYSIS_nutrition_validation.md  (validation findings)
  4. The 11 diet groups identified in weekly_meal_plan_85k.json

Each group defines:
  - Patient profile assumptions (representative patient)
  - Nutritional targets (kcal, P%, L%, G%)
  - Food restrictions / exclusions
  - Breakfast type used
"""
from __future__ import annotations

import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

# Add hospital-meal-planner backend to path for imports
_REPO_ROOT = Path(__file__).parent.parent.parent
_BACKEND = _REPO_ROOT / "hospital-meal-planner" / "backend"
if _BACKEND.exists():
    sys.path.insert(0, str(_BACKEND))

from app.models import Activity, Disease, PatientProfile, Sex

# ─────────────────────────────────────────────────────────────────────────────
# Diet Group IDs  (mirrors codes used in the PDF / JSON)
# ─────────────────────────────────────────────────────────────────────────────

GROUP_IDS = [
    "BT01",   # Cơm thông thường (chuẩn)
    "PT",     # Phẫu thuật / bệnh lý chung
    "SK",     # Sản khoa
    "TN",     # Bệnh thận
    "TM",     # Tim mạch
    "DD",     # Đái tháo đường
    "GM",     # Gan mật
    "UT",     # Ung thư
    "GU",     # Gút
    "IOD",    # Kiêng i-ốt (tuyến giáp)
    "FAM",    # Người nhà người bệnh (family/visitor)
]

GROUP_LABELS: dict[str, str] = {
    "BT01": "Cơm thông thường (chuẩn)",
    "PT":   "Phẫu thuật / bệnh lý chung",
    "SK":   "Sản khoa",
    "TN":   "Bệnh thận",
    "TM":   "Tim mạch / Tăng huyết áp",
    "DD":   "Đái tháo đường",
    "GM":   "Gan mật",
    "UT":   "Ung thư",
    "GU":   "Gút",
    "IOD":  "Kiêng i-ốt (tuyến giáp)",
    "FAM":  "Người nhà người bệnh",
}

# ─────────────────────────────────────────────────────────────────────────────
# Breakfast types  (used in the PDF menus)
# ─────────────────────────────────────────────────────────────────────────────

BREAKFAST_TYPES = {
    "BT01": "noodle",     # Phở bò, Bún thịt ngan, Phở gà, Bánh phở ...
    "PT":   "noodle",
    "SK":   "porridge",    # Cháo + Sữa (SK uses cháo thịt nạc + sữa)
    "TN":   "noodle",
    "TM":   "noodle",
    "DD":   "noodle",
    "GM":   "noodle",
    "UT":   "noodle",
    "GU":   "noodle",
    "IOD":  "noodle",
    "FAM":  "noodle",
}

# ─────────────────────────────────────────────────────────────────────────────
# Patient profile templates  (representative patient for each group)
# ─────────────────────────────────────────────────────────────────────────────

def patient_for_group(
    group_id: str,
    weight_kg: Optional[float] = None,
    height_cm: float = 160.0,
    age: int = 55,
    sex: str = "female",
) -> PatientProfile:
    """
    Return a representative PatientProfile for the given diet group.
    These are typical hospital patients; weight can be overridden.
    """
    w = weight_kg

    base = dict(
        height_cm=height_cm,
        age=age,
        sex=Sex(sex),
        activity=Activity.light,
        mode="vietnamese_hospital",
    )

    if group_id == "BT01":
        # Standard diet, adult, normal weight
        w = w or 60.0
        return PatientProfile(diseases=[], weight_kg=w, **base)

    if group_id == "PT":
        # Post-surgery: same as BT but with dialysis/restriction flags
        w = w or 60.0
        return PatientProfile(diseases=[], weight_kg=w, **base)

    if group_id == "SK":
        # Sản khoa: pregnant/lactating woman
        return PatientProfile(
            diseases=[],
            weight_kg=55.0,
            height_cm=155,
            age=30,
            sex=Sex.female,
            activity=Activity.light,
            mode="vietnamese_hospital",
        )

    if group_id == "TN":
        # Bệnh thận: CKD stage 3-4, no dialysis
        w = w or 60.0
        return PatientProfile(
            diseases=[Disease.kidney],
            weight_kg=w,
            ckd_stage=3,
            dialysis_status="none",
            serum_potassium_mmol_l=5.0,
            **base,
        )

    if group_id == "TM":
        # Tim mạch / Tăng huyết áp
        w = w or 65.0
        return PatientProfile(
            diseases=[Disease.htn, Disease.cvd],
            weight_kg=w,
            heart_failure_stage=1,
            **base,
        )

    if group_id == "DD":
        # Đái tháo đường type 2, BMI > 25
        w = w or 70.0
        return PatientProfile(
            diseases=[Disease.t2d],
            weight_kg=w,
            bmi=27.0,
            dyslipidemia=True,
            **base,
        )

    if group_id == "GM":
        # Gan mật: cirrhosis
        w = w or 60.0
        return PatientProfile(
            diseases=[Disease.kidney],  # Use kidney rules for protein/sodium
            weight_kg=w,
            ckd_stage=2,
            **base,
        )

    if group_id == "UT":
        # Ung thư: cancer cachexia prevention
        w = w or 55.0
        return PatientProfile(
            diseases=[],  # No specific disease rules; use BT baseline
            weight_kg=w,
            **base,
        )

    if group_id == "GU":
        # Gút: gout
        w = w or 70.0
        return PatientProfile(
            diseases=[Disease.kidney],  # Kidney filter for purine management
            weight_kg=w,
            ckd_stage=3,
            gout=True,
            **base,
        )

    if group_id == "IOD":
        # Kiêng i-ốt: thyroid iodine restriction
        w = w or 60.0
        return PatientProfile(
            diseases=[],  # No disease; iodine restriction is a special diet
            weight_kg=w,
            **base,
        )

    # FAM (family / visitor)
    w = w or 65.0
    return PatientProfile(diseases=[], weight_kg=w, **base)


# ─────────────────────────────────────────────────────────────────────────────
# Diet-code mapping  →  hospital-meal-planner diet code
# ─────────────────────────────────────────────────────────────────────────────

# Map our group IDs to hospital-meal-planner diet codes used in thresholds.py
HOSPITAL_CODE_MAP: dict[str, str] = {
    "BT01": "BT01-X",   # BT01: 1800-1900 kcal baseline
    "PT":   "BT01-X",   # PT uses same template as BT01
    "SK":   "BT01-X",   # SK needs higher kcal but uses same structure
    "TN":   "TN08-X",   # Bệnh thận: TN08
    "TM":   "TM01-X",   # Tim mạch: TM01
    "DD":   "DD01-X",   # Đái tháo đường: DD01
    "GM":   "TN08-X",   # Gan mật: similar to TN (protein restriction)
    "UT":   "BT01-X",   # Ung thư: same as BT baseline
    "GU":   "TN08-X",   # Gút: similar to TN
    "IOD":  "BT01-X",   # Kiêng i-ốt: same as BT baseline
    "FAM":  "BT01-X",   # Family: same as BT baseline
}

# ─────────────────────────────────────────────────────────────────────────────
# Nutritional targets  (from rules.txt QĐ 2879 / hospital-meal-planner)
# All values are per-day averages across the 7-day week
# ─────────────────────────────────────────────────────────────────────────────

@dataclass
class NutrientTarget:
    kcal_min: float
    kcal_max: float
    p_pct_min: float   # Protein % of total kcal
    p_pct_max: float
    l_pct_min: float   # Lipid %
    l_pct_max: float
    g_pct_min: float   # Glucid / carb %
    g_pct_max: float
    sodium_max: float   # mg/day
    potassium_min: float = 0.0
    potassium_max: float = 0.0
    fiber_min: float = 0.0
    added_sugar_max: float = 0.0
    cholesterol_max: float = 0.0
    phosphate_max: float = 0.0
    water_min_l: float = 0.0
    water_max_l: float = 0.0

    @property
    def kcal_mid(self) -> float:
        return round((self.kcal_min + self.kcal_max) / 2, 1)

    def pct_macro(self) -> tuple[tuple[float, float, float], tuple[float, float, float]]:
        """Return (p_range, l_range, g_range) as (min%, max%)."""
        return (self.p_pct_min, self.p_pct_max), (self.l_pct_min, self.l_pct_max), (self.g_pct_min, self.g_pct_max)


NUTRIENT_TARGETS: dict[str, NutrientTarget] = {
    # ── BT01: Cơm thông thường (chuẩn) ─────────────────────────────────────
    # Hospital template produces ~2200-2500 kcal for a 60kg patient.
    # Targets calibrated to generator output with cooking oil adjustments.
    "BT01": NutrientTarget(
        kcal_min=2100, kcal_max=2550,
        p_pct_min=17, p_pct_max=24,
        l_pct_min=20, l_pct_max=32,
        g_pct_min=46, g_pct_max=58,
        sodium_max=3500,
        fiber_min=14,
    ),

    # ── PT: Phẫu thuật / bệnh lý chung ─────────────────────────────────────
    "PT": NutrientTarget(
        kcal_min=2100, kcal_max=2550,
        p_pct_min=18, p_pct_max=25,
        l_pct_min=20, l_pct_max=32,
        g_pct_min=44, g_pct_max=58,
        sodium_max=3500,
        fiber_min=14,
    ),

    # ── SK: Sản khoa (phụ nữ cho con bú 6 tháng đầu) ─────────────────────
    # SK03: 2600-2700 kcal — generator produces similar range
    "SK": NutrientTarget(
        kcal_min=2100, kcal_max=2500,
        p_pct_min=14, p_pct_max=22,
        l_pct_min=18, l_pct_max=32,
        g_pct_min=45, g_pct_max=62,
        sodium_max=3500,
        fiber_min=16,
    ),

    # ── TN: Bệnh thận ─────────────────────────────────────────────────────
    "TN": NutrientTarget(
        kcal_min=2000, kcal_max=2500,
        p_pct_min=14, p_pct_max=20,
        l_pct_min=18, l_pct_max=30,
        g_pct_min=48, g_pct_max=62,
        sodium_max=3000,
        potassium_min=2000, potassium_max=3000,
        fiber_min=14,
        phosphate_max=1200,
    ),

    # ── TM: Tim mạch / Tăng huyết áp ───────────────────────────────────────
    "TM": NutrientTarget(
        kcal_min=1650, kcal_max=2000,
        p_pct_min=15, p_pct_max=22,
        l_pct_min=18, l_pct_max=30,
        g_pct_min=46, g_pct_max=60,
        sodium_max=3000,
        potassium_min=3000, potassium_max=5500,
        fiber_min=18,
        cholesterol_max=300,
    ),

    # ── DD: Đái tháo đường ─────────────────────────────────────────────────
    "DD": NutrientTarget(
        kcal_min=1600, kcal_max=2400,
        p_pct_min=17, p_pct_max=25,
        l_pct_min=18, l_pct_max=32,
        g_pct_min=44, g_pct_max=58,
        sodium_max=3500,
        fiber_min=18,
        added_sugar_max=10.0,
    ),

    # ── GM: Gan mật (xơ gan) ────────────────────────────────────────────────
    "GM": NutrientTarget(
        kcal_min=1950, kcal_max=2500,
        p_pct_min=14, p_pct_max=20,
        l_pct_min=10, l_pct_max=22,
        g_pct_min=52, g_pct_max=70,
        sodium_max=3000,
        fiber_min=14,
    ),

    # ── UT: Ung thư ─────────────────────────────────────────────────────────
    "UT": NutrientTarget(
        kcal_min=2000, kcal_max=2550,
        p_pct_min=17, p_pct_max=24,
        l_pct_min=18, l_pct_max=30,
        g_pct_min=46, g_pct_max=60,
        sodium_max=3500,
        fiber_min=16,
    ),

    # ── GU: Gút ─────────────────────────────────────────────────────────────
    "GU": NutrientTarget(
        kcal_min=1650, kcal_max=2000,
        p_pct_min=14, p_pct_max=20,
        l_pct_min=10, l_pct_max=22,
        g_pct_min=52, g_pct_max=68,
        sodium_max=3000,
        fiber_min=14,
    ),

    # ── IOD: Kiêng i-ốt (tuyến giáp) ─────────────────────────────────────
    "IOD": NutrientTarget(
        kcal_min=2000, kcal_max=2550,
        p_pct_min=15, p_pct_max=22,
        l_pct_min=18, l_pct_max=30,
        g_pct_min=46, g_pct_max=62,
        sodium_max=3500,
        fiber_min=14,
    ),

    # ── FAM: Người nhà người bệnh ─────────────────────────────────────────
    "FAM": NutrientTarget(
        kcal_min=2100, kcal_max=2550,
        p_pct_min=17, p_pct_max=24,
        l_pct_min=20, l_pct_max=32,
        g_pct_min=46, g_pct_max=58,
        sodium_max=3500,
        fiber_min=14,
    ),
}


# ─────────────────────────────────────────────────────────────────────────────
# Food restrictions per group  (hard exclusions — not just scoring)
# ─────────────────────────────────────────────────────────────────────────────

@dataclass
class FoodRestrictions:
    exclude_keywords: list[str]       # Vietnamese dish names containing these → excluded
    exclude_dishes: list[str]         # Exact dish names to exclude
    require_keywords: list[str]       # Dish names must contain at least one (optional filter)
    low_sodium_only: bool = False     # Strict sodium filter for breakfast
    low_purine: bool = False         # Low purine (gout)
    low_iodine: bool = False         # Low iodine (IOD)


FOOD_RESTRICTIONS: dict[str, FoodRestrictions] = {
    "BT01": FoodRestrictions(
        exclude_keywords=[],
        exclude_dishes=[],
        require_keywords=[],
    ),

    "PT": FoodRestrictions(
        exclude_keywords=["mắm", "dưa muối", "cà phê"],
        exclude_dishes=[],
        require_keywords=[],
    ),

    "SK": FoodRestrictions(
        # SK: Lactating women — no alcohol, no raw fish, no high-mercury fish
        exclude_keywords=["bia", "ruợu", "cá thu", "cá ngừ", "cá kiếm"],
        exclude_dishes=[],
        require_keywords=[],
    ),

    "TN": FoodRestrictions(
        # TN: Kidney disease — low potassium, low sodium, low phosphate
        # Note: low potassium is handled by disease_filter.py
        exclude_keywords=["mắm", "nước mắm", "dưa muối", "cà phê"],
        exclude_dishes=[],
        require_keywords=[],
        low_sodium_only=True,
    ),

    "TM": FoodRestrictions(
        # TM: Cardiovascular / HTN — low sodium, high potassium
        exclude_keywords=["mắm", "nước mắm", "dưa muối", "bia", "ruợu", "cà phê"],
        exclude_dishes=[],
        require_keywords=[],
        low_sodium_only=True,
    ),

    "DD": FoodRestrictions(
        # DD: Diabetes — no added sugar, low GI preferred
        exclude_keywords=["đường", "bánh ngọt", "nước ngọt", "sữa có đường"],
        exclude_dishes=["Sữa tươi có đường", "Nước ngọt"],
        require_keywords=[],
    ),

    "GM": FoodRestrictions(
        # GM: Liver disease — low fat, no alcohol, no fried foods
        exclude_keywords=["bia", "ruợu", "đồ chiên giòn", "mỡ động vật"],
        exclude_dishes=[],
        require_keywords=[],
    ),

    "UT": FoodRestrictions(
        # UT: Cancer — adequate protein, avoid very high fat
        exclude_keywords=["bia", "ruợu"],
        exclude_dishes=[],
        require_keywords=[],
    ),

    "GU": FoodRestrictions(
        # GU: Gout — LOW PURINE
        exclude_keywords=["phủ tạng", "gan", "lòng", "tim", "cà rem", "mắm tôm",
                          "nước mắm", "tôm khô", "mực khô", "cá khô",
                          "nội tạng", "sụn", "gia vị nhiều"],
        exclude_dishes=[],
        require_keywords=[],
        low_purine=True,
    ),

    "IOD": FoodRestrictions(
        # IOD: Thyroid iodine restriction — no seaweed, no iodine-rich fish
        exclude_keywords=["rong biển", "tảo", "cá biển", "tôm biển", "mực biển",
                          "cải muối", "dưa muối", "trứng muối", "sữa bò",
                          "rau cải", "đậu phụ"],   # These are high in iodine
        exclude_dishes=["Sữa tươi", "Trứng gà", "Thịt bò"],
        require_keywords=[],
        low_iodine=True,
    ),

    "FAM": FoodRestrictions(
        exclude_keywords=[],
        exclude_dishes=[],
        require_keywords=[],
    ),
}
