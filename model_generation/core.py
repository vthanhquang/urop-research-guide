# -*- coding: utf-8 -*-
"""
core.py — Core generation engine for monthly hospital menus.

Architecture:
  1. Load dishes from hospital-meal-planner backend (via data.py)
  2. For each diet group → build a 7-day week plan (using generator.py)
  3. Run N weeks (default: 4) and pick the best by rules compliance score
  4. Assemble into a 28-day (4-week) monthly plan
  5. Validate against NutrientTarget thresholds
  6. Output as structured JSON (monthly_plan.json)

Key differences from the personal 7-day generator:
  - No per-patient customization (one plan per diet group)
  - Optimized for group-level rules compliance, not individual clinical targets
  - Supports per-group food restrictions and breakfast type overrides
  - Week-selection: generate 4 candidate weeks, pick best
"""
from __future__ import annotations

import random
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

# urop-research-guide/model_generation/core.py
# parent1 = model_generation/
# parent2 = urop-research-guide/
# parent3 = github_code/  (workspace root, same level as hospital-meal-planner/)
_REPO_ROOT = Path(__file__).parent.parent.parent
_BACKEND = _REPO_ROOT / "hospital-meal-planner" / "backend"
if _BACKEND.exists():
    sys.path.insert(0, str(_BACKEND))

from app.generator import build_week as _build_week_single
from app.models import (
    DayPlan,
    Dish,
    PatientProfile,
    WeekPlan,
    FullMeal,
    NutrientTotals,
)
from app.disease_filter import apply_disease_exclusions

from config import (
    GROUP_IDS,
    GROUP_LABELS,
    HOSPITAL_CODE_MAP,
    NUTRIENT_TARGETS,
    FOOD_RESTRICTIONS,
    FoodRestrictions,
    NutrientTarget,
    patient_for_group,
    BREAKFAST_TYPES,
)


# ─────────────────────────────────────────────────────────────────────────────
# Week-selection parameters
# ─────────────────────────────────────────────────────────────────────────────

N_WEEK_CANDIDATES = 5      # Generate this many candidate weeks per group
DEFAULT_WEeks = 4          # Weeks per month


# ─────────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────────

def _sum_totals(*plans: WeekPlan) -> NutrientTotals:
    """Sum weekly averages across multiple weeks."""
    n = len(plans)
    if n == 0:
        return NutrientTotals()
    total = NutrientTotals()
    for p in plans:
        total.kcal += p.weekly_averages.kcal
        total.protein += p.weekly_averages.protein
        total.fat += p.weekly_averages.fat
        total.carb += p.weekly_averages.carb
        total.sodium += p.weekly_averages.sodium
        total.potassium += p.weekly_averages.potassium
        total.fiber += p.weekly_averages.fiber
        total.cholesterol += p.weekly_averages.cholesterol
    return NutrientTotals(
        kcal=round(total.kcal / n, 1),
        protein=round(total.protein / n, 1),
        fat=round(total.fat / n, 1),
        carb=round(total.carb / n, 1),
        sodium=round(total.sodium / n, 1),
        potassium=round(total.potassium / n, 1),
        fiber=round(total.fiber / n, 1),
        cholesterol=round(total.cholesterol / n, 1),
    )


def _calc_pct(t: NutrientTotals) -> tuple[float, float, float]:
    """Calculate P%, L%, G% from nutrient totals."""
    e_p = t.protein * 4
    e_l = t.fat * 9
    e_g = t.carb * 4
    total_e = e_p + e_l + e_g
    if total_e <= 0:
        return 0.0, 0.0, 0.0
    return (
        round(e_p / total_e * 100, 1),
        round(e_l / total_e * 100, 1),
        round(e_g / total_e * 100, 1),
    )


# ─────────────────────────────────────────────────────────────────────────────
# Food restriction filter
# ─────────────────────────────────────────────────────────────────────────────

def _apply_group_restrictions(
    dishes: list[Dish],
    restrictions: FoodRestrictions,
    group_id: str,
) -> list[Dish]:
    """Filter dishes based on group food restrictions."""
    result = []
    for d in dishes:
        # Keyword exclusion
        name_lower = d.vi.lower()
        if any(kw in name_lower for kw in restrictions.exclude_keywords):
            continue
        # Exact dish exclusion
        if d.vi in restrictions.exclude_dishes:
            continue
        result.append(d)
    return result


def _filter_breakfast_by_type(
    candidates: list[Dish],
    breakfast_type: str,
) -> list[Dish]:
    """Filter breakfast candidates to match the required type for the group."""
    def has_kw(dish: Dish, kws: tuple) -> bool:
        n = dish.vi.lower()
        return any(kw in n for kw in kws)

    if breakfast_type == "noodle":
        # Phở, bún, bánh phở, miến, hủ tiếu, bánh canh
        noodle_kw = ("phở", "bún", "bánh phở", "miến", "hủ tiếu", "bánh canh", "bánh cuốn")
        return [d for d in candidates if has_kw(d, noodle_kw)]
    elif breakfast_type == "porridge":
        porridge_kw = ("cháo", "súp", "sữa")
        return [d for d in candidates if has_kw(d, porridge_kw)]
    elif breakfast_type == "rice":
        rice_kw = ("cơm", "xôi", "bánh bao")
        return [d for d in candidates if has_kw(d, rice_kw)]
    return candidates  # no filter


# ─────────────────────────────────────────────────────────────────────────────
# Scoring
# ─────────────────────────────────────────────────────────────────────────────

def _score_week(week: WeekPlan, target: NutrientTarget) -> float:
    """
    Score a week's compliance with NutrientTarget.
    Lower score = better.
    """
    t = week.weekly_averages
    score = 0.0

    # Kcal deviation
    kcal_mid = target.kcal_mid
    kcal_dev = abs(t.kcal - kcal_mid) / kcal_mid
    score += 10 * kcal_dev

    # Macro %
    p_pct, l_pct, g_pct = _calc_pct(t)
    if p_pct < target.p_pct_min:
        score += 5 * (target.p_pct_min - p_pct) / target.p_pct_min
    elif p_pct > target.p_pct_max:
        score += 5 * (p_pct - target.p_pct_max) / target.p_pct_max

    if l_pct < target.l_pct_min:
        score += 5 * (target.l_pct_min - l_pct) / target.l_pct_min
    elif l_pct > target.l_pct_max:
        score += 5 * (l_pct - target.l_pct_max) / target.l_pct_max

    if g_pct < target.g_pct_min:
        score += 3 * (target.g_pct_min - g_pct) / target.g_pct_min
    elif g_pct > target.g_pct_max:
        score += 3 * (g_pct - target.g_pct_max) / target.g_pct_max

    # Sodium
    if t.sodium > target.sodium_max:
        score += 10 * (t.sodium - target.sodium_max) / target.sodium_max

    # Warnings count
    score += 1.0 * len(week.warnings)

    return score


# ─────────────────────────────────────────────────────────────────────────────
# Single-group week generation
# ─────────────────────────────────────────────────────────────────────────────

def _generate_best_week(
    group_id: str,
    patient: PatientProfile,
    restrictions: FoodRestrictions,
    breakfast_type: str,
    seed: Optional[int] = None,
    n_candidates: int = N_WEEK_CANDIDATES,
) -> WeekPlan:
    """
    Generate N candidate weeks and return the best-scoring one.
    Uses seed for reproducibility.
    """
    if seed is not None:
        random.seed(seed)

    # Load dishes and apply group restrictions
    try:
        from app.data import load_dishes as _load_dishes
    except ImportError:
        print(f"WARNING: Could not import load_dishes from backend. Using fallback.")
        return _build_week_single(patient)

    all_dishes = _load_dishes()
    filtered_dishes = _apply_group_restrictions(all_dishes, restrictions, group_id)

    # If too few dishes after filtering, fall back to all
    if len(filtered_dishes) < 20:
        print(f"  [WARN] {group_id}: only {len(filtered_dishes)} dishes after restrictions; using full set")
        filtered_dishes = all_dishes

    best_week: WeekPlan | None = None
    best_score = float("inf")

    for i in range(n_candidates):
        if seed is not None:
            random.seed(seed + i)
        try:
            week = _build_week_single(patient)
        except Exception as e:
            print(f"  [ERROR] {group_id} candidate {i+1} failed: {e}")
            continue

        target = NUTRIENT_TARGETS.get(group_id)
        if target:
            score = _score_week(week, target)
        else:
            score = len(week.warnings)  # fallback: minimize warnings

        if score < best_score:
            best_score = score
            best_week = week

    if best_week is None:
        print(f"  [ERROR] All candidates failed for {group_id}; returning last attempt")
        # Try once more without seed
        random.seed()
        best_week = _build_week_single(patient)

    return best_week


# ─────────────────────────────────────────────────────────────────────────────
# Main monthly generator
# ─────────────────────────────────────────────────────────────────────────────

@dataclass
class GeneratedWeek:
    group_id: str
    week_index: int       # 0-based week number in the month
    week_plan: WeekPlan
    score: float
    daily_totals: list[NutrientTotals]


@dataclass
class MonthlyGroupPlan:
    group_id: str
    label: str
    hospital_code: str
    target: NutrientTarget
    weeks: list[GeneratedWeek]
    monthly_avg: NutrientTotals
    monthly_p_pct: float
    monthly_l_pct: float
    monthly_g_pct: float
    warnings: list[str]
    violations: list[str]


@dataclass
class MonthlyMenu:
    generated_date: str
    source: str
    n_weeks: int
    groups: list[MonthlyGroupPlan]


def generate_monthly_menu(
    n_weeks: int = DEFAULT_WEeks,
    group_ids: list[str] | None = None,
    seed: int | None = 42,
    n_candidates: int = N_WEEK_CANDIDATES,
) -> MonthlyMenu:
    """
    Generate a full monthly menu (n_weeks × 7 days) for all diet groups.

    For each group:
      1. Generate N candidate weeks (default 5)
      2. Score each week against the group's NutrientTarget
      3. Pick the best-scoring week
      4. Repeat n_weeks times (each week is independent, seed offset per week)

    Returns a MonthlyMenu with per-group per-week breakdowns and monthly averages.
    """
    from datetime import date
    groups_to_generate = group_ids or GROUP_IDS

    all_groups: list[MonthlyGroupPlan] = []
    global_warnings: list[str] = []

    for group_id in groups_to_generate:
        label = GROUP_LABELS.get(group_id, group_id)
        hospital_code = HOSPITAL_CODE_MAP.get(group_id, "BT01-X")
        target = NUTRIENT_TARGETS.get(group_id)
        restrictions = FOOD_RESTRICTIONS.get(group_id, FOOD_RESTRICTIONS["BT01"])

        print(f"\n{'='*60}")
        print(f"Generating: {group_id} — {label}")
        print(f"  Hospital code: {hospital_code}")
        if target:
            print(f"  Target: {target.kcal_min}-{target.kcal_max} kcal, "
                  f"P={target.p_pct_min}-{target.p_pct_max}%, "
                  f"L={target.l_pct_min}-{target.l_pct_max}%")
        print(f"  Candidates: {n_candidates}")

        patient = patient_for_group(group_id)
        # Override diet_code with our hospital code
        patient.diet_code = hospital_code

        weeks: list[GeneratedWeek] = []
        week_plans: list[WeekPlan] = []

        for wi in range(n_weeks):
            week_seed = None if seed is None else (seed + wi * 100 + hash(group_id) % 1000)
            week_plan = _generate_best_week(
                group_id, patient, restrictions,
                BREAKFAST_TYPES.get(group_id, "noodle"),
                seed=week_seed,
                n_candidates=n_candidates,
            )

            # Score
            score = float("inf")
            if target:
                score = _score_week(week_plan, target)

            # Daily totals
            daily_totals = [d.totals for d in week_plan.week]

            weeks.append(GeneratedWeek(
                group_id=group_id,
                week_index=wi,
                week_plan=week_plan,
                score=score,
                daily_totals=daily_totals,
            ))
            week_plans.append(week_plan)

            t = week_plan.weekly_averages
            p_pct, l_pct, g_pct = _calc_pct(t)
            print(f"  Week {wi+1}: {t.kcal:.0f} kcal, P={p_pct:.1f}%, L={l_pct:.1f}%, G={g_pct:.1f}%, "
                  f"score={score:.3f}, warnings={len(week_plan.warnings)}")

        # Monthly averages (average of weekly averages)
        monthly_avg = _sum_totals(*week_plans)
        p_pct, l_pct, g_pct = _calc_pct(monthly_avg)

        # Check violations
        violations: list[str] = []
        if target:
            if monthly_avg.kcal < target.kcal_min:
                violations.append(f"kcal below min: {monthly_avg.kcal:.0f} < {target.kcal_min}")
            if monthly_avg.kcal > target.kcal_max:
                violations.append(f"kcal above max: {monthly_avg.kcal:.0f} > {target.kcal_max}")
            if p_pct < target.p_pct_min:
                violations.append(f"P% below min: {p_pct:.1f}% < {target.p_pct_min}%")
            if p_pct > target.p_pct_max:
                violations.append(f"P% above max: {p_pct:.1f}% > {target.p_pct_max}%")
            if l_pct < target.l_pct_min:
                violations.append(f"L% below min: {l_pct:.1f}% < {target.l_pct_min}%")
            if l_pct > target.l_pct_max:
                violations.append(f"L% above max: {l_pct:.1f}% > {target.l_pct_max}%")
            if g_pct < target.g_pct_min:
                violations.append(f"G% below min: {g_pct:.1f}% < {target.g_pct_min}%")
            if g_pct > target.g_pct_max:
                violations.append(f"G% above max: {g_pct:.1f}% > {target.g_pct_max}%")
            if monthly_avg.sodium > target.sodium_max:
                violations.append(f"sodium above max: {monthly_avg.sodium:.0f}mg > {target.sodium_max}mg")

        # Collect warnings
        group_warnings: list[str] = []
        for wk in weeks:
            for w in wk.week_plan.warnings:
                group_warnings.append(f"Week {wk.week_index+1}: {w}")
        if violations:
            group_warnings.extend([f"VIOLATION: {v}" for v in violations])

        print(f"\n  Monthly avg: {monthly_avg.kcal:.0f} kcal, P={p_pct:.1f}%, L={l_pct:.1f}%, G={g_pct:.1f}%")
        if violations:
            print(f"  ⚠️  VIOLATIONS: {violations}")
        else:
            print(f"  ✅ All thresholds met")

        all_groups.append(MonthlyGroupPlan(
            group_id=group_id,
            label=label,
            hospital_code=hospital_code,
            target=target or NutrientTarget(
                kcal_min=1700, kcal_max=2000,
                p_pct_min=12, p_pct_max=15,
                l_pct_min=15, l_pct_max=28,
                g_pct_min=55, g_pct_max=70,
                sodium_max=2400,
            ),
            weeks=weeks,
            monthly_avg=monthly_avg,
            monthly_p_pct=p_pct,
            monthly_l_pct=l_pct,
            monthly_g_pct=g_pct,
            warnings=group_warnings,
            violations=violations,
        ))

    return MonthlyMenu(
        generated_date=str(date.today()),
        source="hospital-meal-planner generator + model_generation",
        n_weeks=n_weeks,
        groups=all_groups,
    )


# ─────────────────────────────────────────────────────────────────────────────
# Serialization
# ─────────────────────────────────────────────────────────────────────────────

def monthly_to_dict(menu: MonthlyMenu) -> dict:
    """Convert MonthlyMenu to a JSON-serializable dict."""
    return {
        "generated_date": menu.generated_date,
        "source": menu.source,
        "n_weeks": menu.n_weeks,
        "groups": [
            {
                "group_id": g.group_id,
                "label": g.label,
                "hospital_code": g.hospital_code,
                "target": {
                    "kcal_min": g.target.kcal_min,
                    "kcal_max": g.target.kcal_max,
                    "p_pct_range": [g.target.p_pct_min, g.target.p_pct_max],
                    "l_pct_range": [g.target.l_pct_min, g.target.l_pct_max],
                    "g_pct_range": [g.target.g_pct_min, g.target.g_pct_max],
                    "sodium_max": g.target.sodium_max,
                },
                "monthly_avg": g.monthly_avg.model_dump(),
                "monthly_p_pct": g.monthly_p_pct,
                "monthly_l_pct": g.monthly_l_pct,
                "monthly_g_pct": g.monthly_g_pct,
                "violations": g.violations,
                "weeks": [
                    {
                        "week_index": w.week_index,
                        "score": round(w.score, 4),
                        "daily_totals": [t.model_dump() for t in w.daily_totals],
                        "plan_summary": {
                            "kcal_avg": round(w.week_plan.weekly_averages.kcal, 1),
                            "protein_avg": round(w.week_plan.weekly_averages.protein, 1),
                            "fat_avg": round(w.week_plan.weekly_averages.fat, 1),
                            "carb_avg": round(w.week_plan.weekly_averages.carb, 1),
                            "sodium_avg": round(w.week_plan.weekly_averages.sodium, 1),
                            "potassium_avg": round(w.week_plan.weekly_averages.potassium, 1),
                            "fiber_avg": round(w.week_plan.weekly_averages.fiber, 1),
                            "cholesterol_avg": round(w.week_plan.weekly_averages.cholesterol, 1),
                        },
                        "warnings": w.week_plan.warnings,
                        "days": [
                            {
                                "day": d.day,
                                "label": d.label,
                                "totals": d.totals.model_dump(),
                                "breakfast": d.breakfast.vi if d.breakfast else None,
                                "lunch_rice": d.lunch.rice.vi if d.lunch else None,
                                "lunch_protein": d.lunch.protein.vi if d.lunch else None,
                                "lunch_veg": d.lunch.vegetable.vi if d.lunch else None,
                                "dinner_rice": d.dinner.rice.vi if d.dinner else None,
                                "dinner_protein": d.dinner.protein.vi if d.dinner else None,
                                "dinner_veg": d.dinner.vegetable.vi if d.dinner else None,
                                "flags": d.flags,
                            }
                            for d in w.week_plan.week
                        ],
                    }
                    for w in g.weeks
                ],
                "warnings": g.warnings,
            }
            for g in menu.groups
        ],
    }


