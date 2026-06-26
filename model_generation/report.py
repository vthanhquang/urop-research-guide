# -*- coding: utf-8 -*-
"""
report.py — Generate formatted HTML / Markdown reports from monthly menu JSON.

Usage:
    python -m model_generation.report monthly_menu_20260626.json
    python -m model_generation.report -f html monthly_menu_20260626.json
    python -m model_generation.report -f md monthly_menu_20260626.json
    python -m model_generation.report -f both monthly_menu_20260626.json
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


# ─────────────────────────────────────────────────────────────────────────────
# Data loading
# ─────────────────────────────────────────────────────────────────────────────

def load_menu(path: str | Path) -> dict:
    with open(path, encoding="utf-8") as f:
        return json.load(f)


# ─────────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────────

_DAY_LABELS_VI = ["Thứ 2", "Thứ 3", "Thứ 4", "Thứ 5", "Thứ 6", "Thứ 7", "Chủ nhật"]

_MEAL_LABELS = {
    "breakfast": "Bữa sáng",
    "lunch": "Bữa trưa",
    "dinner": "Bữa tối",
}

_NUTRIENT_LABELS: dict[str, str] = {
    "kcal":       "Năng lượng (kcal)",
    "protein":    "Protein (g)",
    "fat":        "Lipid (g)",
    "carb":       "Glucid (g)",
    "fiber":      "Chất xơ (g)",
    "sodium":     "Natri (mg)",
    "potassium":  "Kali (mg)",
    "cholesterol":"Cholesterol (mg)",
}


def _pct_macro(protein_g: float, fat_g: float, carb_g: float) -> tuple[float, float, float]:
    ep = protein_g * 4
    el = fat_g * 9
    eg = carb_g * 4
    total = ep + el + eg
    if total <= 0:
        return 0.0, 0.0, 0.0
    return round(ep / total * 100, 1), round(el / total * 100, 1), round(eg / total * 100, 1)


def _ok(violations: list) -> str:
    return "OK" if not violations else "⚠️"


# ─────────────────────────────────────────────────────────────────────────────
# Section: nutrient table
# ─────────────────────────────────────────────────────────────────────────────

def _nutrient_row(name: str, value: float, target_lo: float | None,
                  target_hi: float | None, unit: str = "", fmt: str = ".0f") -> str:
    if target_lo is not None and target_hi is not None:
        if target_lo == target_hi:
            status = "OK" if target_lo - 1 <= value <= target_lo + 1 else "⚠️"
        else:
            status = "OK" if target_lo <= value <= target_hi else "⚠️"
    elif target_hi is not None:
        status = "OK" if value <= target_hi else "⚠️"
    elif target_lo is not None:
        status = "OK" if value >= target_lo else "⚠️"
    else:
        status = "—"
    val_str = f"{value:{fmt}}" if fmt == ".0f" else f"{value:.1f}"
    target_str = ""
    if target_lo is not None and target_hi is not None:
        if target_lo == target_hi:
            target_str = f"= {target_lo:.0f}"
        else:
            target_str = f"{target_lo:.0f}–{target_hi:.0f}"
    elif target_hi is not None:
        target_str = f"≤ {target_hi:.0f}"
    elif target_lo is not None:
        target_str = f"≥ {target_lo:.0f}"
    return f"| {name:<22} | {val_str:>8}{unit} | {target_str:>14} | {status:>4} |"


def _weekly_nutrient_table(week_data: dict, target: dict, group_id: str) -> str:
    t = week_data["plan_summary"]
    protein_avg = t["protein_avg"]
    fat_avg     = t["fat_avg"]
    carb_avg    = t["carb_avg"]
    p_pct, l_pct, g_pct = _pct_macro(protein_avg, fat_avg, carb_avg)

    rows = [
        "| Chỉ tiêu dinh dưỡng | Giá trị | Ngưỡng mục tiêu | Đạt |",
        "|:---|---:|---:|---:|",
        _nutrient_row("Năng lượng (kcal)",       t["kcal_avg"],        target.get("kcal_min"),  target.get("kcal_max")),
        _nutrient_row("Protein (g)",              protein_avg,           target.get("p_pct_range", [None, None])[0], target.get("p_pct_range", [None, None])[1], " g  "),
        _nutrient_row("  → Protein %",            p_pct,                 target.get("p_pct_range", [None, None])[0], target.get("p_pct_range", [None, None])[1], "%"),
        _nutrient_row("Lipid (g)",                fat_avg,               target.get("l_pct_range", [None, None])[0], target.get("l_pct_range", [None, None])[1], " g  "),
        _nutrient_row("  → Lipid %",             l_pct,                 target.get("l_pct_range", [None, None])[0], target.get("l_pct_range", [None, None])[1], "%"),
        _nutrient_row("Glucid (g)",               carb_avg,              target.get("g_pct_range", [None, None])[0], target.get("g_pct_range", [None, None])[1], " g  "),
        _nutrient_row("  → Glucid %",            g_pct,                 target.get("g_pct_range", [None, None])[0], target.get("g_pct_range", [None, None])[1], "%"),
        _nutrient_row("Chất xơ (g)",              t["fiber_avg"],        0, target.get("fiber_min", 0)),
        _nutrient_row("Natri (mg)",               t["sodium_avg"],       0, target.get("sodium_max")),
        _nutrient_row("Kali (mg)",                t["potassium_avg"],    target.get("potassium_min", 0), target.get("potassium_max", None)),
        _nutrient_row("Cholesterol (mg)",          t["cholesterol_avg"],  0, target.get("cholesterol_max")),
    ]
    return "\n".join(rows)


# ─────────────────────────────────────────────────────────────────────────────
# Section: day-by-day menu
# ─────────────────────────────────────────────────────────────────────────────

def _dish_cell(dish: Any) -> str:
    if dish is None:
        return "—"
    return str(dish)


def _day_row(day: dict) -> str:
    lunch = day.get("lunch") or {}
    dinner = day.get("dinner") or {}
    t = day.get("totals") or {}
    p_pct, l_pct, g_pct = _pct_macro(t.get("protein", 0), t.get("fat", 0), t.get("carb", 0))
    kcal = t.get("kcal", 0)

    return (
        f"| {day['label']:<12} "
        f"| {_dish_cell(day.get('breakfast')):<20} "
        f"| {_dish_cell(lunch.get('lunch_rice')):<12} "
        f"| {_dish_cell(lunch.get('lunch_protein')):<20} "
        f"| {_dish_cell(lunch.get('lunch_veg')):<18} "
        f"| {_dish_cell(dinner.get('dinner_rice')):<12} "
        f"| {_dish_cell(dinner.get('dinner_protein')):<20} "
        f"| {_dish_cell(dinner.get('dinner_veg')):<18} "
        f"| {kcal:>6.0f} "
        f"| {p_pct:>5.1f}% "
        f"| {l_pct:>5.1f}% "
        f"|"
    )


# ─────────────────────────────────────────────────────────────────────────────
# Full group report (Markdown)
# ─────────────────────────────────────────────────────────────────────────────

def report_group_md(group: dict) -> str:
    gid     = group["group_id"]
    label   = group["label"]
    tgt     = group.get("target") or {}
    weeks   = group.get("weeks") or []

    lines = [
        f"## {gid} — {label}\n",
        f"**Mã bệnh viện:** `{group.get('hospital_code', '—')}`  "
        f"**Ngày tạo:** {group.get('_generated_date', '—')}\n",
        f"### 1. Ngưỡng dinh dưỡng mục tiêu\n",
        f"| Chỉ tiêu | Giá trị |",
        f"|:---|---:|",
        f"| Năng lượng (kcal) | {tgt.get('kcal_min', '?')}–{tgt.get('kcal_max', '?')} kcal |",
        f"| Protein % | {tgt.get('p_pct_range', ['', ''])[0]}–{tgt.get('p_pct_range', ['', ''])[1]}% |",
        f"| Lipid % | {tgt.get('l_pct_range', ['', ''])[0]}–{tgt.get('l_pct_range', ['', ''])[1]}% |",
        f"| Glucid % | {tgt.get('g_pct_range', ['', ''])[0]}–{tgt.get('g_pct_range', ['', ''])[1]}% |",
        f"| Natri tối đa | {tgt.get('sodium_max', '?')} mg |",
        f"| Kali | {tgt.get('potassium_min', 0)}–{tgt.get('potassium_max', '?')} mg |",
        f"| Chất xơ tối thiểu | {tgt.get('fiber_min', 0)} g |",
    ]

    if tgt.get("added_sugar_max"):
        lines.append(f"| Đường tự do tối đa | {tgt['added_sugar_max']} g |")
    if tgt.get("cholesterol_max"):
        lines.append(f"| Cholesterol tối đa | {tgt['cholesterol_max']} mg |")

    lines.append("\n### 2. Kết quả tuần\n")
    for wk in weeks:
        wi = wk["week_index"]
        ps = wk["plan_summary"]
        violations = wk.get("violations") or []
        warn_count = len(wk.get("warnings") or [])

        p_pct, l_pct, g_pct = _pct_macro(ps["protein_avg"], ps["fat_avg"], ps["carb_avg"])

        lines.append(f"**Tuần {wi + 1}** — Điểm: {wk.get('score', '?'):.3f}  |  Cảnh báo: {warn_count}\n")
        lines.append(_weekly_nutrient_table(wk, tgt, gid))
        lines.append("")
        lines.append("| Ngày | Bữa sáng | Cơm (T) | Protein (T) | Rau (T) | Cơm (C) | Protein (C) | Rau (C) | kcal | P% | L% |")
        lines.append("|:---|:---|:---|:---|:---|:---|:---|:---|---:|---:|---:|")
        for d in wk.get("days") or []:
            lines.append(_day_row(d))
        if violations:
            for v in violations:
                lines.append(f"\n> ⚠️ **Vi phạm:** {v}")
        lines.append("\n---\n")

    return "\n".join(lines)


def report_group_html(group: dict) -> str:
    """Generate a self-contained HTML section for one group."""
    gid   = group["group_id"]
    label = group["label"]
    tgt   = group.get("target") or {}
    weeks = group.get("weeks") or []

    # Build daily rows for all weeks
    day_rows = ""
    for wk in weeks:
        for d in wk.get("days") or []:
            lunch = d.get("lunch") or {}
            dinner = d.get("dinner") or {}
            t = d.get("totals") or {}
            p_pct, l_pct, g_pct = _pct_macro(t.get("protein", 0), t.get("fat", 0), t.get("carb", 0))
            day_rows += (
                f"<tr>"
                f"<td>{d['label']}</td>"
                f"<td>{_dish_cell(d.get('breakfast'))}</td>"
                f"<td>{_dish_cell(lunch.get('lunch_rice'))}</td>"
                f"<td>{_dish_cell(lunch.get('lunch_protein'))}</td>"
                f"<td>{_dish_cell(lunch.get('lunch_veg'))}</td>"
                f"<td>{_dish_cell(dinner.get('dinner_rice'))}</td>"
                f"<td>{_dish_cell(dinner.get('dinner_protein'))}</td>"
                f"<td>{_dish_cell(dinner.get('dinner_veg'))}</td>"
                f"<td>{t.get('kcal', 0):.0f}</td>"
                f"<td>{p_pct:.1f}%</td>"
                f"<td>{l_pct:.1f}%</td>"
                f"</tr>\n"
            )

    # Nutrient summary
    avg = group.get("monthly_avg") or {}
    p_pct_m, l_pct_m, g_pct_m = _pct_macro(
        avg.get("protein", 0), avg.get("fat", 0), avg.get("carb", 0)
    )

    violations = group.get("violations") or []
    ok_class = "ok" if not violations else "warn"

    nut_rows = ""
    for key, label2, unit in [
        ("kcal", "Năng lượng", "kcal"),
        ("protein", "Protein", "g"),
        ("fat", "Lipid", "g"),
        ("carb", "Glucid", "g"),
        ("fiber", "Chất xơ", "g"),
        ("sodium", "Natri", "mg"),
        ("potassium", "Kali", "mg"),
        ("cholesterol", "Cholesterol", "mg"),
    ]:
        val = avg.get(key, 0)
        nut_rows += f"<tr><td>{label2}</td><td>{val:.0f} {unit}</td></tr>\n"

    viol_html = ""
    if violations:
        viol_html = "<div class='violations'><strong>Vi phạm:</strong><ul>"
        for v in violations:
            viol_html += f"<li>{v}</li>"
        viol_html += "</ul></div>"

    return f"""
<div class="group" id="{gid}">
  <h2>{gid} — {label}</h2>
  <span class="badge {ok_class}">{_ok(violations)}</span>
  <p><strong>Mã BV:</strong> {group.get('hospital_code', '—')}</p>
  <p><strong>Ngưỡng:</strong> {tgt.get('kcal_min','?')}–{tgt.get('kcal_max','?')} kcal, &nbsp;
     P={tgt.get('p_pct_range',[None,None])[0] or '?'}–{tgt.get('p_pct_range',[None,None])[1] or '?'}% &nbsp;
     L={tgt.get('l_pct_range',[None,None])[0] or '?'}–{tgt.get('l_pct_range',[None,None])[1] or '?'}% &nbsp;
     G={tgt.get('g_pct_range',[None,None])[0] or '?'}–{tgt.get('g_pct_range',[None,None])[1] or '?'}%</p>

  <h3>Tổng hợp</h3>
  <table class="summary-table">
    <tr><th>Chỉ tiêu</th><th>Giá trị</th></tr>
    {nut_rows}
    <tr><td>P%</td><td>{p_pct_m:.1f}%</td></tr>
    <tr><td>L%</td><td>{l_pct_m:.1f}%</td></tr>
    <tr><td>G%</td><td>{g_pct_m:.1f}%</td></tr>
  </table>
  {viol_html}

  <h3>Thực đơn 7 ngày</h3>
  <div class="table-scroll">
  <table>
    <thead>
      <tr>
        <th>Ngày</th><th>Bữa sáng</th>
        <th>Cơm (T)</th><th>Protein (T)</th><th>Rau (T)</th>
        <th>Cơm (C)</th><th>Protein (C)</th><th>Rau (C)</th>
        <th>kcal</th><th>P%</th><th>L%</th>
      </tr>
    </thead>
    <tbody>
      {day_rows}
    </tbody>
  </table>
  </div>
</div>
"""


# ─────────────────────────────────────────────────────────────────────────────
# Full report
# ─────────────────────────────────────────────────────────────────────────────

def report_menu_md(menu: dict) -> str:
    groups = menu.get("groups") or []
    lines = [
        "# THỰC ĐƠN THÁNG — BỆNH VIỆN\n",
        f"**Ngày tạo:** {menu.get('generated_date', '—')}  |  "
        f"**Nguồn:** {menu.get('source', '—')}  |  "
        f"**Số nhóm:** {len(groups)}\n",
        "---",
        "\n## Tóm tắt các nhóm\n",
        "| Mã | Nhóm | Kcal TB | P% | L% | G% | Natri(mg) | Kali(mg) | Status |",
        "|:---|:---|---:|---:|---:|---:|---:|---:|:---:|",
    ]

    for g in groups:
        avg = g.get("monthly_avg") or {}
        p_pct, l_pct, g_pct = _pct_macro(
            avg.get("protein", 0), avg.get("fat", 0), avg.get("carb", 0)
        )
        violations = g.get("violations") or []
        lines.append(
            f"| {g['group_id']} | {g['label']} | "
            f"{avg.get('kcal', 0):.0f} | {p_pct:.1f}% | {l_pct:.1f}% | {g_pct:.1f}% | "
            f"{avg.get('sodium', 0):.0f} | {avg.get('potassium', 0):.0f} | "
            f"{'OK' if not violations else '⚠️ '+str(len(violations))} |"
        )

    lines.append("\n---\n")
    for g in groups:
        lines.append(report_group_md(g))
        lines.append("\n")

    return "\n".join(lines)


def report_menu_html(menu: dict) -> str:
    groups_html = "\n".join(report_group_html(g) for g in (menu.get("groups") or []))

    return f"""<!DOCTYPE html>
<html lang="vi">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Thực đơn tháng — Bệnh viện</title>
<style>
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{ font-family: 'Segoe UI', Arial, sans-serif; background: #f4f6f9; color: #222; line-height: 1.6; }}
  header {{ background: #1a5c8a; color: #fff; padding: 24px 32px; }}
  header h1 {{ font-size: 1.6rem; }}
  header p {{ opacity: 0.85; font-size: 0.9rem; margin-top: 4px; }}
  nav {{ background: #e8f0f8; padding: 10px 32px; display: flex; flex-wrap: wrap; gap: 8px; }}
  nav a {{ color: #1a5c8a; text-decoration: none; padding: 4px 10px; border-radius: 4px; font-size: 0.85rem; }}
  nav a:hover {{ background: #1a5c8a; color: #fff; }}
  .container {{ max-width: 1100px; margin: 0 auto; padding: 20px 16px 60px; }}
  .group {{ background: #fff; border-radius: 10px; padding: 20px; margin-bottom: 24px;
             box-shadow: 0 2px 8px rgba(0,0,0,.08); }}
  .group h2 {{ color: #1a5c8a; border-bottom: 2px solid #1a5c8a; padding-bottom: 8px; margin-bottom: 10px; }}
  .badge {{ display: inline-block; padding: 2px 10px; border-radius: 12px; font-size: 0.8rem;
            font-weight: 600; margin-left: 8px; vertical-align: middle; }}
  .badge.ok {{ background: #d4edda; color: #155724; }}
  .badge.warn {{ background: #fff3cd; color: #856404; }}
  .violations {{ background: #fff3cd; border-left: 4px solid #ffc107; padding: 10px 14px;
                  border-radius: 4px; margin: 10px 0; }}
  .violations ul {{ margin: 6px 0 0 20px; }}
  table {{ width: 100%; border-collapse: collapse; margin: 10px 0; font-size: 0.85rem; }}
  th {{ background: #e8f0f8; padding: 8px 10px; text-align: left; border: 1px solid #c8d8e8; }}
  td {{ padding: 6px 10px; border: 1px solid #e0e8f0; vertical-align: top; }}
  tr:nth-child(even) td {{ background: #f9fbfe; }}
  .summary-table th, .summary-table td {{ padding: 5px 10px; }}
  .table-scroll {{ overflow-x: auto; }}
  table h3 {{ color: #1a5c8a; margin: 16px 0 6px; }}
  footer {{ text-align: center; padding: 20px; color: #888; font-size: 0.8rem; }}
</style>
</head>
<body>
<header>
  <h1>Thực đơn tháng — Bệnh viện</h1>
  <p>Ngày tạo: {menu.get('generated_date','—')} &nbsp;|&nbsp;
     Nguồn: {menu.get('source','—')} &nbsp;|&nbsp;
     {len(menu.get('groups') or [])} nhóm</p>
</header>
<nav>
  <span>Chuyển đến:</span>
  {"".join(f'<a href="#{g["group_id"]}">{g["group_id"]}</a>' for g in (menu.get("groups") or []))}
</nav>
<div class="container">
  {groups_html}
</div>
<footer>
  Được tạo tự động bởi model_generation/report.py &mdash;
  Nguồn: hospital-meal-planner &amp; urop-research-guide
</footer>
</body>
</html>
"""


# ─────────────────────────────────────────────────────────────────────────────
# CLI
# ─────────────────────────────────────────────────────────────────────────────

def main() -> None:
    p = argparse.ArgumentParser(description="Generate reports from monthly menu JSON")
    p.add_argument("json_file", nargs="?", help="Path to monthly_menu JSON")
    p.add_argument("-f", "--format", choices=["html", "md", "both"], default="html",
                   help="Output format (default: html)")
    p.add_argument("-o", "--output", help="Output path (default: stdout)")
    args = p.parse_args()

    # Resolve input
    if args.json_file:
        json_path = Path(args.json_file)
    else:
        out_dir = Path(__file__).parent / "output"
        candidates = sorted(out_dir.glob("monthly_menu_*.json"), reverse=True)
        if not candidates:
            print("No monthly_menu JSON found. Run: python run.py")
            sys.exit(1)
        json_path = candidates[0]

    menu = load_menu(json_path)
    basename = json_path.stem  # e.g. "monthly_menu_20260626"

    md_text  = report_menu_md(menu)
    html_text = report_menu_html(menu)

    if args.format in ("md", "both"):
        md_out = args.output or f"{basename}_report.md"
        Path(md_out).write_text(md_text, encoding="utf-8")
        print(f"Saved Markdown: {md_out}")

    if args.format in ("html", "both"):
        html_out = args.output or f"{basename}_report.html"
        Path(html_out).write_text(html_text, encoding="utf-8")
        print(f"Saved HTML:     {html_out}")

    if not args.output:
        print("\n--- Markdown preview (first 60 lines) ---\n")
        print("\n".join(md_text.splitlines()[:60]))


if __name__ == "__main__":
    main()
