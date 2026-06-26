# -*- coding: utf-8 -*-
"""
compliance.py — Tính tỷ lệ tuân thủ ngưỡng theo ngày.

Với mỗi nhóm và mỗi chỉ tiêu dinh dưỡng:
  compliance_rate = (số ngày đạt) / (tổng số ngày) × 100%

Biểu đồ: bảng nhiệt heatmap-style (ngày vs nhóm).
"""
from __future__ import annotations

import sys
from dataclasses import dataclass
from pathlib import Path
from statistics import mean

_REPO = Path(__file__).parent.parent
sys.path.insert(0, str(_REPO / "model_generation"))
from model_generation.config import GROUP_LABELS, NUTRIENT_TARGETS

# ─────────────────────────────────────────────────────────────────────────────
# Nutrient config for compliance check
# ─────────────────────────────────────────────────────────────────────────────

_COMPLIANCE_NUTRIENTS = [
    ("kcal",        "Năng lượng", "kcal"),
    ("sodium",      "Natri",       "mg"),
    ("potassium",   "Kali",        "mg"),
    ("cholesterol", "Cholesterol",  "mg"),
]


# ─────────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────────

def _pct_macro(p: float, f: float, c: float) -> tuple[float, float, float]:
    ep, el, eg = p * 4, f * 9, c * 4
    t = ep + el + eg
    if t <= 0:
        return 0.0, 0.0, 0.0
    return round(ep/t*100, 1), round(el/t*100, 1), round(eg/t*100, 1)


# ─────────────────────────────────────────────────────────────────────────────
# Day compliance
# ─────────────────────────────────────────────────────────────────────────────

@dataclass
class DayCompliance:
    day_index: int
    label: str
    compliant: bool
    kcal_ok: bool
    p_pct_ok: bool
    l_pct_ok: bool
    g_pct_ok: bool
    sodium_ok: bool
    potassium_ok: bool
    cholesterol_ok: bool
    score: float   # fraction of nutrients that passed (0-1)


@dataclass
class GroupCompliance:
    group_id: str
    label: str
    n_days: int
    n_passed: int
    compliance_rate: float   # 0-100
    kcal_rate: float
    sodium_rate: float
    potassium_rate: float
    cholesterol_rate: float
    p_pct_rate: float
    l_pct_rate: float
    g_pct_rate: float
    days: list[DayCompliance]


def _is_within(actual: float, lo: float | None, hi: float | None) -> bool:
    if hi is not None and actual > hi:
        return False
    if lo is not None and actual < lo:
        return False
    return True


def _check_day(
    day_totals: dict,
    tgt,
    group_id: str,
    day_index: int,
    label: str,
) -> DayCompliance:
    p = day_totals.get("protein", 0) or 0
    f = day_totals.get("fat", 0) or 0
    c = day_totals.get("carb", 0) or 0
    p_pct, l_pct, g_pct = _pct_macro(p, f, c)
    kcal = day_totals.get("kcal", 0) or 0
    sodium = day_totals.get("sodium", 0) or 0
    potassium = day_totals.get("potassium", 0) or 0
    cholesterol = day_totals.get("cholesterol", 0) or 0

    p_ok  = _is_within(p_pct, tgt.p_pct_min, tgt.p_pct_max)
    l_ok  = _is_within(l_pct, tgt.l_pct_min, tgt.l_pct_max)
    g_ok  = _is_within(g_pct, tgt.g_pct_min, tgt.g_pct_max)
    kcal_ok = _is_within(kcal, tgt.kcal_min, tgt.kcal_max)
    na_ok = sodium <= tgt.sodium_max if tgt.sodium_max else True
    k_ok  = _is_within(potassium, tgt.potassium_min, tgt.potassium_max)
    chol_ok = cholesterol <= tgt.cholesterol_max if tgt.cholesterol_max else True

    checks = [kcal_ok, p_ok, l_ok, g_ok, na_ok, k_ok, chol_ok]
    score = sum(checks) / len(checks) if checks else 0.0

    return DayCompliance(
        day_index=day_index,
        label=label,
        compliant=score >= 0.71,   # ≥5/7 pass → day compliant
        kcal_ok=kcal_ok,
        p_pct_ok=p_ok,
        l_pct_ok=l_ok,
        g_pct_ok=g_ok,
        sodium_ok=na_ok,
        potassium_ok=k_ok,
        cholesterol_ok=chol_ok,
        score=round(score * 100, 1),
    )


def compute_group_compliance(menu: dict, group_id: str) -> GroupCompliance | None:
    gid_found = None
    for g in (menu.get("groups") or []):
        if g["group_id"] == group_id:
            gid_found = g
            break
    if not gid_found:
        return None

    tgt = NUTRIENT_TARGETS.get(group_id)
    if not tgt:
        return None

    label = GROUP_LABELS.get(group_id, group_id)
    all_days: list[DayCompliance] = []

    for wk in (gid_found.get("weeks") or []):
        daily = wk.get("daily_totals") or []
        for di, dt in enumerate(daily):
            label_d = ["Thứ 2","Thứ 3","Thứ 4","Thứ 5","Thứ 6","Thứ 7","Chủ nhật"][di]
            all_days.append(_check_day(dt, tgt, group_id, di, label_d))

    n = len(all_days)
    n_passed = sum(1 for d in all_days if d.compliant)
    comp_rate = round(n_passed / n * 100, 1) if n else 0

    return GroupCompliance(
        group_id=group_id,
        label=label,
        n_days=n,
        n_passed=n_passed,
        compliance_rate=comp_rate,
        kcal_rate=round(mean([100 if d.kcal_ok else 0 for d in all_days]) or 0, 1),
        sodium_rate=round(mean([100 if d.sodium_ok else 0 for d in all_days]) or 0, 1),
        potassium_rate=round(mean([100 if d.potassium_ok else 0 for d in all_days]) or 0, 1),
        cholesterol_rate=round(mean([100 if d.cholesterol_ok else 0 for d in all_days]) or 0, 1),
        p_pct_rate=round(mean([100 if d.p_pct_ok else 0 for d in all_days]) or 0, 1),
        l_pct_rate=round(mean([100 if d.l_pct_ok else 0 for d in all_days]) or 0, 1),
        g_pct_rate=round(mean([100 if d.g_pct_ok else 0 for d in all_days]) or 0, 1),
        days=all_days,
    )


def compute_all_compliance(menu: dict) -> list[GroupCompliance]:
    results = []
    for gid in GROUP_LABELS:
        r = compute_group_compliance(menu, gid)
        if r:
            results.append(r)
    return results


# ─────────────────────────────────────────────────────────────────────────────
# Heatmap matrix
# ─────────────────────────────────────────────────────────────────────────────

def compliance_heatmap(menu: dict) -> dict:
    """
    Returns a matrix: heatmap[gid][nutrient] = compliance_rate (0-100)
    """
    results = compute_all_compliance(menu)
    matrix = {}
    for r in results:
        matrix[r.group_id] = {
            "Tổng": r.compliance_rate,
            "Kcal": r.kcal_rate,
            "Natri": r.sodium_rate,
            "Kali": r.potassium_rate,
            "Cholesterol": r.cholesterol_rate,
            "P%": r.p_pct_rate,
            "L%": r.l_pct_rate,
            "G%": r.g_pct_rate,
        }
    return matrix


# ─────────────────────────────────────────────────────────────────────────────
# Markdown output
# ─────────────────────────────────────────────────────────────────────────────

def compliance_to_markdown(results: list[GroupCompliance]) -> str:
    nutrients_checked = [
        ("Tổng", "Tổng hợp"),
        ("Kcal", "Năng lượng"),
        ("P%", "Protein %"),
        ("L%", "Lipid %"),
        ("G%", "Glucid %"),
        ("Natri", "Natri"),
        ("Kali", "Kali"),
        ("Cholesterol", "Cholesterol"),
    ]

    lines = [
        "# BÁO CÁO TUÂN THỦ NGƯỠNG\n",
        "Tỷ lệ tuân thủ = (số ngày đạt) / (tổng ngày) × 100%\n",
        "| Nhóm | Nhãn | Tổng | Kcal | P% | L% | G% | Natri | Kali | Cholesterol |",
        "|:---|:---|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for r in results:
        lines.append(
            f"| {r.group_id} | {r.label} | "
            f"{r.compliance_rate:.0f}% | "
            f"{r.kcal_rate:.0f}% | "
            f"{r.p_pct_rate:.0f}% | "
            f"{r.l_pct_rate:.0f}% | "
            f"{r.g_pct_rate:.0f}% | "
            f"{r.sodium_rate:.0f}% | "
            f"{r.potassium_rate:.0f}% | "
            f"{r.cholesterol_rate:.0f}% |"
        )

    lines.append("\n## Chi tiết theo ngày\n")
    for r in results:
        lines.append(f"\n### {r.group_id} — {r.label}\n")
        lines.append("| Ngày | Kcal | P% | L% | G% | Natri | Kali | Chol | Đạt |")
        lines.append("|:---|---:|---:|---:|---:|---:|---:|---:|:---:|")
        for d in r.days:
            sym = "✅" if d.compliant else "❌"
            lines.append(
                f"| {d.label} | "
                f"{'✅' if d.kcal_ok else '❌'} | "
                f"{'✅' if d.p_pct_ok else '❌'} | "
                f"{'✅' if d.l_pct_ok else '❌'} | "
                f"{'✅' if d.g_pct_ok else '❌'} | "
                f"{'✅' if d.sodium_ok else '❌'} | "
                f"{'✅' if d.potassium_ok else '❌'} | "
                f"{'✅' if d.cholesterol_ok else '❌'} | "
                f"{sym} |"
            )

    return "\n".join(lines)
