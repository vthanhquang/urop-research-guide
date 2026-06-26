# -*- coding: utf-8 -*-
"""
rules_checker.py — Kiểm tra tuân thủ ngưỡng QĐ 2879/QĐ-BYT cho từng nhóm.

Ngưỡng được chia làm 3 cấp:
  HARD  — Vi phạm bắt buộc phải sửa (e.g. Natri > max, Kali < min với CKD)
  SOFT  — Vi phạm khuyến cáo (e.g. Protein% ngoài ±3% range)
  INFO  — Thông tin bổ sung

Ngưỡng cụ thể theo nhóm (dựa trên QĐ 2879/QĐ-BYT và tài liệu phân tích):
"""
from __future__ import annotations

import json
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

_REPO = Path(__file__).parent.parent
sys.path.insert(0, str(_REPO / "model_generation"))

from model_generation.config import (
    GROUP_LABELS,
    HOSPITAL_CODE_MAP,
    NUTRIENT_TARGETS,
    BREAKFAST_TYPES,
)


# ─────────────────────────────────────────────────────────────────────────────
# Severity levels
# ─────────────────────────────────────────────────────────────────────────────

class Severity:
    HARD = "HARD"    # Must fix
    SOFT = "SOFT"    # Advisory
    INFO = "INFO"    # Informational


# ─────────────────────────────────────────────────────────────────────────────
# Threshold definitions per group
# ─────────────────────────────────────────────────────────────────────────────

@dataclass
class NutrientLimit:
    name: str
    value: float
    unit: str
    direction: str          # "max", "min", "range"
    hi: Optional[float] = None
    severity: str = Severity.HARD
    note: str = ""


@dataclass
class GroupRules:
    group_id: str
    label: str
    hospital_code: str
    limits: list[NutrientLimit] = field(default_factory=list)
    hard_notes: list[str] = field(default_factory=list)
    soft_notes: list[str] = field(default_factory=list)


def _build_rules() -> dict[str, GroupRules]:
    """Build all group rules from config + QĐ 2879 annotations."""
    rules = {}
    for gid in GROUP_LABELS:
        tgt = NUTRIENT_TARGETS.get(gid)
        limits = []
        if tgt:
            limits = [
                NutrientLimit("kcal", tgt.kcal_min, "kcal", "range",
                              hi=tgt.kcal_max, severity=Severity.SOFT,
                              note="Trung bình tuần"),
                NutrientLimit("P%",
                              tgt.p_pct_min, "%", "range",
                              hi=tgt.p_pct_max, severity=Severity.SOFT),
                NutrientLimit("L%",
                              tgt.l_pct_min, "%", "range",
                              hi=tgt.l_pct_max, severity=Severity.SOFT),
                NutrientLimit("G%",
                              tgt.g_pct_min, "%", "range",
                              hi=tgt.g_pct_max, severity=Severity.SOFT),
                NutrientLimit("Natri",
                              tgt.sodium_max, "mg", "max",
                              severity=Severity.SOFT,
                              note=f"QĐ 2879: ≤{tgt.sodium_max} mg"),
                NutrientLimit("Kali",
                              tgt.potassium_min, "mg", "range",
                              hi=tgt.potassium_max, severity=Severity.INFO),
                NutrientLimit("Chất xơ",
                              tgt.fiber_min, "g", "min",
                              severity=Severity.INFO),
            ]
            if tgt.added_sugar_max:
                limits.append(NutrientLimit("Đường tự do",
                              tgt.added_sugar_max, "g", "max",
                              severity=Severity.SOFT))
            if tgt.cholesterol_max:
                limits.append(NutrientLimit("Cholesterol",
                              tgt.cholesterol_max, "mg", "max",
                              severity=Severity.SOFT))
        rules[gid] = GroupRules(
            group_id=gid,
            label=GROUP_LABELS[gid],
            hospital_code=HOSPITAL_CODE_MAP.get(gid, "—"),
            limits=limits,
        )
    return rules


_ALL_RULES = _build_rules()


# ─────────────────────────────────────────────────────────────────────────────
# Checker
# ─────────────────────────────────────────────────────────────────────────────

@dataclass
class Violation:
    nutrient: str
    actual: float
    limit: float
    limit_hi: Optional[float]
    unit: str
    direction: str
    severity: str
    message: str


@dataclass
class GroupCheckResult:
    group_id: str
    label: str
    violations: list[Violation] = field(default_factory=list)
    hard_passed: bool = True
    soft_passed: bool = True
    summary: str = ""


def _check_limit(actual: float, limit: NutrientLimit) -> Violation | None:
    d = limit.direction
    tol_pct = 0.10  # 10% tolerance for SOFT
    tol_abs = limit.value * tol_pct

    if d == "max":
        threshold = limit.value * (1 + tol_pct) if limit.severity == Severity.SOFT else limit.value
        if actual > threshold:
            return Violation(
                nutrient=limit.name, actual=actual,
                limit=limit.value, limit_hi=None,
                unit=limit.unit, direction=d,
                severity=limit.severity,
                message=f"{limit.name} = {actual:.1f}{limit.unit} "
                        f"(max cho phép: {limit.value:.0f}{limit.unit})"
                        + (f"  [{limit.note}]" if limit.note else "")
            )
    elif d == "min":
        threshold = limit.value * (1 - tol_pct) if limit.severity == Severity.SOFT else limit.value
        if actual < threshold:
            return Violation(
                nutrient=limit.name, actual=actual,
                limit=limit.value, limit_hi=None,
                unit=limit.unit, direction=d,
                severity=limit.severity,
                message=f"{limit.name} = {actual:.1f}{limit.unit} "
                        f"(tối thiểu: {limit.value:.0f}{limit.unit})"
            )
    elif d == "range":
        lo = limit.value
        hi = limit.hi or limit.value
        lo_t = lo * (1 - tol_pct) if limit.severity == Severity.SOFT else lo
        hi_t = hi * (1 + tol_pct) if limit.severity == Severity.SOFT else hi
        if actual < lo_t or actual > hi_t:
            return Violation(
                nutrient=limit.name, actual=actual,
                limit=lo, limit_hi=hi,
                unit=limit.unit, direction=d,
                severity=limit.severity,
                message=f"{limit.name} = {actual:.1f}{limit.unit} "
                        f"(ngưỡng: {lo:.0f}–{hi:.0f}{limit.unit})"
            )
    return None


def check_group(group_data: dict) -> GroupCheckResult:
    gid = group_data["group_id"]
    gr = _ALL_RULES.get(gid)
    avg = group_data.get("monthly_avg") or {}
    p_pct = group_data.get("monthly_p_pct", 0)
    l_pct = group_data.get("monthly_l_pct", 0)
    g_pct = group_data.get("monthly_g_pct", 0)

    # Build actuals dict
    actuals = {
        "kcal":        avg.get("kcal", 0),
        "P%":          p_pct,
        "L%":          l_pct,
        "G%":          g_pct,
        "Natri":       avg.get("sodium", 0),
        "Kali":        avg.get("potassium", 0),
        "Chất xơ":     avg.get("fiber", 0),
        "Cholesterol": avg.get("cholesterol", 0),
        "Đường tự do": 0,   # not tracked in current output
    }

    violations: list[Violation] = []
    if gr:
        for lim in gr.limits:
            actual = actuals.get(lim.name, 0)
            v = _check_limit(actual, lim)
            if v:
                violations.append(v)

    hard_passed = not any(v.severity == Severity.HARD for v in violations)
    soft_passed  = not any(v.severity == Severity.SOFT for v in violations)

    result = GroupCheckResult(
        group_id=gid,
        label=gr.label if gr else group_data.get("label", ""),
        violations=violations,
        hard_passed=hard_passed,
        soft_passed=soft_passed,
    )

    # Build summary text
    hard_v = [v for v in violations if v.severity == Severity.HARD]
    soft_v = [v for v in violations if v.severity == Severity.SOFT]
    info_v = [v for v in violations if v.severity == Severity.INFO]

    if not hard_v and not soft_v:
        result.summary = "✅ Đạt tất cả ngưỡng HARD và SOFT."
    else:
        parts = []
        if hard_v:
            parts.append(f"❌ {len(hard_v)} HARD: " + "; ".join(v.message for v in hard_v))
        if soft_v:
            parts.append(f"⚠️  {len(soft_v)} SOFT: " + "; ".join(v.message for v in soft_v))
        result.summary = "  |  ".join(parts)

    return result


def check_menu(menu_data: dict) -> list[GroupCheckResult]:
    results = []
    for g in (menu_data.get("groups") or []):
        results.append(check_group(g))
    return results


# ─────────────────────────────────────────────────────────────────────────────
# Output formatters
# ─────────────────────────────────────────────────────────────────────────────

def results_to_markdown(results: list[GroupCheckResult]) -> str:
    lines = [
        "# BÁO CÁO KIỂM TRA QUY TẮC — QĐ 2879/QĐ-BYT\n",
        "| Mã | Nhóm | HARD | SOFT | Tổng |",
        "|:---|:---|:---:|:---:|:---:|",
    ]
    for r in results:
        hv = sum(1 for v in r.violations if v.severity == Severity.HARD)
        sv = sum(1 for v in r.violations if v.severity == Severity.SOFT)
        hard_sym = "✅" if r.hard_passed else f"❌{hv}"
        soft_sym = "✅" if r.soft_passed else f"⚠️{sv}"
        lines.append(
            f"| {r.group_id} | {r.label} | {hard_sym} | {soft_sym} | {hv+sv} |"
        )
    lines.append("\n---\n")
    for r in results:
        hv = sum(1 for v in r.violations if v.severity == Severity.HARD)
        sv = sum(1 for v in r.violations if v.severity == Severity.SOFT)
        lines.append(f"## {r.group_id} — {r.label}\n")
        lines.append(f"**{r.summary}**\n")
        if r.violations:
            for v in r.violations:
                sev_badge = f"[{v.severity}]"
                lines.append(f"- {sev_badge} {v.message}\n")
        lines.append("\n")
    return "\n".join(lines)


def results_to_json(results: list[GroupCheckResult]) -> list[dict]:
    return [
        {
            "group_id": r.group_id,
            "label": r.label,
            "hard_passed": r.hard_passed,
            "soft_passed": r.soft_passed,
            "summary": r.summary,
            "violations": [
                {
                    "nutrient": v.nutrient,
                    "actual": round(v.actual, 2),
                    "limit": v.limit,
                    "limit_hi": v.limit_hi,
                    "unit": v.unit,
                    "direction": v.direction,
                    "severity": v.severity,
                    "message": v.message,
                }
                for v in r.violations
            ],
        }
        for r in results
    ]
