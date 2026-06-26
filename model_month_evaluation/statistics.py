# -*- coding: utf-8 -*-
"""
statistics.py — Thống kê mô tả cho thực đơn tháng.

Tính toán:
  - Trung bình, min, max, std, CV cho tất cả chất dinh dưỡng
  - Phân bố macro (P%, L%, G%) theo ngày và theo nhóm
  - Coefficient of Variation (CV) — đánh giá độ ổn định
  - Rangking nhóm theo từng chỉ tiêu
"""
from __future__ import annotations

import json
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional
from statistics import mean, stdev

_REPO = Path(__file__).parent.parent
sys.path.insert(0, str(_REPO / "model_generation"))
from model_generation.config import GROUP_LABELS

# ─────────────────────────────────────────────────────────────────────────────
# Nutrient definitions
# ─────────────────────────────────────────────────────────────────────────────

NUTRIENTS = [
    ("kcal",        "Năng lượng",   "kcal"),
    ("protein",     "Protein",       "g"),
    ("fat",         "Lipid",        "g"),
    ("carb",        "Glucid",       "g"),
    ("fiber",       "Chất xơ",      "g"),
    ("sodium",      "Natri",        "mg"),
    ("potassium",   "Kali",          "mg"),
    ("cholesterol", "Cholesterol",   "mg"),
]

MACRO_PCT_KEYS = ["p_pct", "l_pct", "g_pct"]


# ─────────────────────────────────────────────────────────────────────────────
# Data extractors
# ─────────────────────────────────────────────────────────────────────────────

def _extract_daily_nutrients(menu: dict) -> list[dict]:
    """Return flat list of all day-level nutrient dicts across all groups."""
    rows = []
    for g in (menu.get("groups") or []):
        gid = g["group_id"]
        for wk in (g.get("weeks") or []):
            for dt in (wk.get("daily_totals") or []):
                row = dict(dt)
                row["group_id"] = gid
                row["label"] = g.get("label", "")
                rows.append(row)
    return rows


def _group_daily_nutrients(menu: dict, group_id: str) -> list[dict]:
    """Daily nutrients for a specific group."""
    rows = []
    for g in (menu.get("groups") or []):
        if g["group_id"] != group_id:
            continue
        for wk in (g.get("weeks") or []):
            rows.extend(wk.get("daily_totals") or [])
    return rows


# ─────────────────────────────────────────────────────────────────────────────
# Core stats
# ─────────────────────────────────────────────────────────────────────────────

@dataclass
class NutrientStats:
    nutrient: str
    label: str
    unit: str
    mean: float
    min: float
    max: float
    std: float
    cv: float           # coefficient of variation = std/mean
    n: int             # number of days


def _stats(values: list[float], nutrient: str, label: str, unit: str) -> NutrientStats:
    n = len(values)
    m = mean(values) if values else 0.0
    lo = min(values) if values else 0.0
    hi = max(values) if values else 0.0
    s = stdev(values) if n > 1 else 0.0
    cv = s / m if m else 0.0
    return NutrientStats(
        nutrient=nutrient, label=label, unit=unit,
        mean=round(m, 1), min=round(lo, 1), max=round(hi, 1),
        std=round(s, 1), cv=round(cv, 3), n=n
    )


def compute_group_stats(menu: dict, group_id: str) -> list[NutrientStats]:
    rows = _group_daily_nutrients(menu, group_id)
    results = []
    for key, label, unit in NUTRIENTS:
        vals = [r.get(key, 0) or 0 for r in rows]
        results.append(_stats(vals, key, label, unit))
    return results


def compute_all_stats(menu: dict) -> list[dict]:
    """Compute stats for all groups, returned as dicts."""
    rows = _extract_daily_nutrients(menu)
    results = []
    for key, label, unit in NUTRIENTS:
        vals = [r.get(key, 0) or 0 for r in rows]
        s = _stats(vals, key, label, unit)
        results.append({
            "nutrient": key,
            "label": label,
            "unit": unit,
            "all_groups_mean": s.mean,
            "all_groups_min": s.min,
            "all_groups_max": s.max,
            "all_groups_std": s.std,
            "all_groups_cv": s.cv,
            "n_days": s.n,
            "per_group": {},
        })
    # Per-group breakdown
    for g in (menu.get("groups") or []):
        gid = g["group_id"]
        gr_stats = compute_group_stats(menu, gid)
        for gs in gr_stats:
            for r in results:
                if r["nutrient"] == gs.nutrient:
                    r["per_group"][gid] = {
                        "mean": gs.mean, "min": gs.min,
                        "max": gs.max, "std": gs.std, "cv": gs.cv,
                    }
    return results


# ─────────────────────────────────────────────────────────────────────────────
# Macro % distribution
# ─────────────────────────────────────────────────────────────────────────────

def macro_distribution(menu: dict) -> list[dict]:
    """Per-group and overall macro % (P%, L%, G%) daily distribution."""
    all_days: list[dict] = _extract_daily_nutrients(menu)
    rows = []
    for gid in GROUP_LABELS:
        grp_days = [d for d in all_days if d.get("group_id") == gid]
        if not grp_days:
            continue
        p_vals, l_vals, g_vals = [], [], []
        for d in grp_days:
            ep = (d.get("protein", 0) or 0) * 4
            el = (d.get("fat", 0) or 0) * 9
            eg = (d.get("carb", 0) or 0) * 4
            total = ep + el + eg
            if total > 0:
                p_vals.append(ep / total * 100)
                l_vals.append(el / total * 100)
                g_vals.append(eg / total * 100)
        rows.append({
            "group_id": gid,
            "label": GROUP_LABELS.get(gid, ""),
            "P%": {
                "mean": round(mean(p_vals), 1) if p_vals else 0,
                "min":  round(min(p_vals), 1) if p_vals else 0,
                "max":  round(max(p_vals), 1) if p_vals else 0,
            },
            "L%": {
                "mean": round(mean(l_vals), 1) if l_vals else 0,
                "min":  round(min(l_vals), 1) if l_vals else 0,
                "max":  round(max(l_vals), 1) if l_vals else 0,
            },
            "G%": {
                "mean": round(mean(g_vals), 1) if g_vals else 0,
                "min":  round(min(g_vals), 1) if g_vals else 0,
                "max":  round(max(g_vals), 1) if g_vals else 0,
            },
            "n_days": len(p_vals),
        })
    return rows


# ─────────────────────────────────────────────────────────────────────────────
# Rankings
# ─────────────────────────────────────────────────────────────────────────────

def rank_groups(menu: dict, nutrient: str) -> list[tuple[str, str, float, float]]:
    """Rank groups by mean nutrient value (higher first). Returns [(gid, label, mean, cv)]."""
    results = []
    for g in (menu.get("groups") or []):
        gid = g["group_id"]
        rows = _group_daily_nutrients(menu, gid)
        vals = [r.get(nutrient, 0) or 0 for r in rows]
        m = mean(vals) if vals else 0
        s = stdev(vals) if len(vals) > 1 else 0
        cv = s / m if m else 0
        results.append((gid, GROUP_LABELS.get(gid, ""), round(m, 1), round(cv, 3)))
    return sorted(results, key=lambda x: x[2], reverse=True)


# ─────────────────────────────────────────────────────────────────────────────
# Markdown output
# ─────────────────────────────────────────────────────────────────────────────

def stats_to_markdown(menu: dict) -> str:
    all_stats = compute_all_stats(menu)
    macro_dist = macro_distribution(menu)
    n_groups = len(menu.get("groups") or [])
    n_days = len(_extract_daily_nutrients(menu))

    lines = [
        "# THỐNG KÊ MÔ TẢ\n",
        f"| Số nhóm: {n_groups} | Số ngày (tổng): {n_days} |\n",
        "## 1. Tất cả nhóm gộp — chỉ tiêu dinh dưỡng\n",
        "| Chỉ tiêu | Đơn vị | Trung bình | Min | Max | Std | CV | N |",
        "|:---|:---|---:|---:|---:|---:|---:|---:|",
    ]
    for s in all_stats:
        lines.append(
            f"| {s['label']} | {s['unit']} | {s['all_groups_mean']:.0f} | "
            f"{s['all_groups_min']:.0f} | {s['all_groups_max']:.0f} | {s['all_groups_std']:.0f} | "
            f"{s['all_groups_cv']:.2f} | {s['n_days']} |"
        )

    lines.append("\n## 2. Phân bố Macro % theo ngày\n")
    lines.append("| Nhóm | P% TB | P% Min | P% Max | L% TB | L% Min | L% Max | G% TB | G% Min | G% Max | N |")
    lines.append("|:---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|")
    for r in macro_dist:
        lines.append(
            f"| {r['group_id']} | "
            f"{r['P%']['mean']:.1f} | {r['P%']['min']:.1f} | {r['P%']['max']:.1f} | "
            f"{r['L%']['mean']:.1f} | {r['L%']['min']:.1f} | {r['L%']['max']:.1f} | "
            f"{r['G%']['mean']:.1f} | {r['G%']['min']:.1f} | {r['G%']['max']:.1f} | "
            f"{r['n_days']} |"
        )

    lines.append("\n## 3. Bảng trung bình theo nhóm\n")
    for nut_key, nut_label, unit in NUTRIENTS:
        lines.append(f"\n### {nut_label} ({unit})\n")
        ranked = rank_groups(menu, nut_key)
        lines.append("| Hạng | Mã | Nhóm | Tr.bình | CV |")
        lines.append("|:---:|:---|:---|---:|---:|")
        for i, (gid, label, m, cv) in enumerate(ranked, 1):
            lines.append(f"| {i} | {gid} | {label} | {m:.0f} | {cv:.2f} |")

    return "\n".join(lines)
