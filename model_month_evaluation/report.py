# -*- coding: utf-8 -*-
"""
report.py — Báo cáo tổng hợp cho model_month_evaluation.

Tạo báo cáo HTML + Markdown từ:
  - rules_checker: kết quả kiểm tra ngưỡng
  - statistics: thống kê mô tả
  - compliance: tỷ lệ tuân thủ
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

_REPO = Path(__file__).parent.parent
sys.path.insert(0, str(_REPO))
sys.path.insert(0, str(_REPO / "model_generation"))

from model_month_evaluation.rules_checker import check_menu, results_to_json, results_to_markdown as rules_md
from model_month_evaluation.statistics import stats_to_markdown
from model_month_evaluation.compliance import compute_all_compliance, compliance_to_markdown

from model_generation.config import GROUP_LABELS


# ─────────────────────────────────────────────────────────────────────────────
# HTML formatters
# ─────────────────────────────────────────────────────────────────────────────

def _ok_cell(val: float) -> str:
    if val >= 90:
        return f"<td class='high'>{val:.0f}%</td>"
    elif val >= 71:
        return f"<td class='mid'>{val:.0f}%</td>"
    else:
        return f"<td class='low'>{val:.0f}%</td>"


def _violation_badge(violations: list) -> str:
    if not violations:
        return "<span class='badge ok'>✅ OK</span>"
    return f"<span class='badge warn'>⚠️ {len(violations)}</span>"


def _heatmap_html(menu: dict, compliance_results) -> str:
    nutrients = ["Tổng","Kcal","P%","L%","G%","Natri","Kali","Cholesterol"]
    rows_html = ""
    for r in compliance_results:
        matrix = {}
        # Re-compute inline via compute_all_compliance results
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

        def cell(cls, val):
            return f"<td class='{cls}'>{val:.0f}%</td>"

        row = f"<tr><td><strong>{r.group_id}</strong><br><small>{r.label}</small></td>"
        for n in nutrients:
            v = matrix.get(r.group_id, {}).get(n, 0)
            if v >= 90:
                row += f"<td class='high'>{v:.0f}%</td>"
            elif v >= 71:
                row += f"<td class='mid'>{v:.0f}%</td>"
            else:
                row += f"<td class='low'>{v:.0f}%</td>"
        row += "<td><strong>" + ("✅" if r.compliance_rate >= 90 else "⚠️") + f"</strong><br><small>{r.compliance_rate:.0f}%</small></td>"
        row += "</tr>\n"
        rows_html += row

    return f"""
<table class="heatmap">
  <thead>
    <tr><th>Nhóm</th>
      {"".join(f"<th>{n}</th>" for n in nutrients)}
      <th>Tuân thủ</th>
    </tr>
  </thead>
  <tbody>
    {rows_html}
  </tbody>
</table>
"""


def results_to_html(results, menu: dict, compliance_results) -> str:
    group_cards = ""
    for r in results:
        violations = r.violations
        hard_v = [v for v in violations if v.severity == "HARD"]
        soft_v = [v for v in violations if v.severity == "SOFT"]

        v_rows = ""
        if violations:
            for v in violations:
                cls = "hard-row" if v.severity == "HARD" else "soft-row"
                v_rows += (
                    f"<tr class='{cls}'>"
                    f"<td>[{v.severity}]</td>"
                    f"<td>{v.nutrient}</td>"
                    f"<td>{v.actual:.1f}</td>"
                    f"<td>{v.limit:.0f}" + (f"–{v.limit_hi:.0f}" if v.limit_hi else "") + f" {v.unit}</td>"
                    f"<td>{v.message}</td>"
                    f"</tr>\n"
                )
        else:
            v_rows = "<tr><td colspan='5' class='ok-row'>✅ Không có vi phạm</td></tr>"

        avg = {}
        for g in (menu.get("groups") or []):
            if g["group_id"] == r.group_id:
                avg = g.get("monthly_avg") or {}
                break
        p_pct = r.group_id  # placeholder
        for g in (menu.get("groups") or []):
            if g["group_id"] == r.group_id:
                from statistics import mean
                def mp(p, f, c):
                    ep, el, eg = p*4, f*9, c*4
                    t = ep+el+eg
                    return round(ep/t*100,1) if t else 0
                p_pct = mp(avg.get("protein",0), avg.get("fat",0), avg.get("carb",0))

        group_cards += f"""
<div class="group-card" id="{r.group_id}">
  <h2>{r.group_id} — {r.label} {_violation_badge(violations)}</h2>
  <table class="mini-table">
    <tr><td><strong>Năng lượng TB</strong></td><td>{avg.get('kcal',0):.0f} kcal</td></tr>
    <tr><td><strong>Protein TB</strong></td><td>{avg.get('protein',0):.0f} g</td></tr>
    <tr><td><strong>Lipid TB</strong></td><td>{avg.get('fat',0):.0f} g</td></tr>
    <tr><td><strong>Glucid TB</strong></td><td>{avg.get('carb',0):.0f} g</td></tr>
    <tr><td><strong>Natri TB</strong></td><td>{avg.get('sodium',0):.0f} mg</td></tr>
    <tr><td><strong>Kali TB</strong></td><td>{avg.get('potassium',0):.0f} mg</td></tr>
    <tr><td><strong>P%</strong></td><td>{p_pct:.1f}%</td></tr>
  </table>
  <h3>Vi phạm ngưỡng</h3>
  <table class="violations-table">
    <thead><tr><th>Severity</th><th>Chỉ tiêu</th><th>Thực tế</th><th>Ngưỡng</th><th>Mô tả</th></tr></thead>
    <tbody>{v_rows}</tbody>
  </table>
</div>
"""
    heatmap_html = _heatmap_html(menu, compliance_results)

    return f"""<!DOCTYPE html>
<html lang="vi">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Đánh giá thực đơn tháng</title>
<style>
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{ font-family: 'Segoe UI', Arial, sans-serif; background: #f4f6f9; color: #222; line-height: 1.6; }}
  header {{ background: #1a3c6e; color: #fff; padding: 20px 32px; }}
  header h1 {{ font-size: 1.5rem; }}
  nav {{ background: #e8f0f8; padding: 8px 32px; display:flex; gap:8px; flex-wrap:wrap; align-items:center; }}
  nav span {{ color:#666; font-size:0.85rem; }}
  nav a {{ color:#1a3c6e; text-decoration:none; padding:3px 10px; border-radius:4px; font-size:0.85rem; }}
  nav a:hover {{ background:#1a3c6e; color:#fff; }}
  .container {{ max-width:1100px; margin:0 auto; padding:16px; }}
  h1,h2,h3 {{ color:#1a3c6e; }}
  .badge {{ display:inline-block; padding:2px 10px; border-radius:12px; font-size:0.8rem; font-weight:600; margin-left:8px; }}
  .badge.ok {{ background:#d4edda; color:#155724; }}
  .badge.warn {{ background:#fff3cd; color:#856404; }}
  .group-card {{ background:#fff; border-radius:10px; padding:16px 20px; margin-bottom:20px;
                 box-shadow:0 2px 8px rgba(0,0,0,.08); }}
  .mini-table {{ width:auto; border-collapse:collapse; margin:8px 0 14px; font-size:0.88rem; }}
  .mini-table td {{ padding:4px 14px 4px 0; border-bottom:1px solid #eee; }}
  .mini-table td:first-child {{ color:#555; }}
  table {{ width:100%; border-collapse:collapse; margin:8px 0; font-size:0.85rem; }}
  th {{ background:#e8f0f8; padding:8px 10px; text-align:left; border:1px solid #c8d8e8; }}
  td {{ padding:6px 10px; border:1px solid #e0e8f0; }}
  tr:nth-child(even) td {{ background:#f9fbfe; }}
  .violations-table td {{ vertical-align:top; }}
  .hard-row td {{ background:#ffeaea; }}
  .soft-row td {{ background:#fffbea; }}
  .ok-row td {{ background:#eafaf1; color:#155724; }}
  .heatmap td {{ text-align:center; padding:6px; }}
  .heatmap .high {{ background:#d4edda; color:#155724; font-weight:600; }}
  .heatmap .mid  {{ background:#fff3cd; color:#856404; }}
  .heatmap .low  {{ background:#ffeaea; color:#9c2d2d; }}
  footer {{ text-align:center; padding:20px; color:#888; font-size:0.8rem; }}
</style>
</head>
<body>
<header>
  <h1>📊 Đánh giá thực đơn tháng — model_month_evaluation</h1>
</header>
<nav>
  <span>Chuyển đến:</span>
  {"".join(f'<a href="#{g["group_id"]}">{g["group_id"]}</a>' for g in (menu.get("groups") or []))}
  <a href="#heatmap">Heatmap</a>
</nav>
<div class="container">
  <h2>📐 Heatmap tuân thủ ngưỡng</h2>
  {heatmap_html}

  <h2 id="heatmap">Kết quả chi tiết theo nhóm</h2>
  {group_cards}
</div>
<footer>model_month_evaluation — tự động tạo bởi urop-research-guide</footer>
</body>
</html>
"""


def full_report_html(menu: dict) -> str:
    compliance_results = compute_all_compliance(menu)
    results = check_menu(menu)
    return results_to_html(results, menu, compliance_results)


def full_report_markdown(menu: dict) -> str:
    compliance_results = compute_all_compliance(menu)
    results = check_menu(menu)

    rules = rules_md(results)
    stats = stats_to_markdown(menu)
    comp  = compliance_to_markdown(compliance_results)

    return (
        "# BÁO CÁO ĐÁNH GIÁ THỰC ĐƠN THÁNG\n\n"
        f"Ngày tạo: {menu.get('generated_date','—')}  |  "
        f"Nguồn: {menu.get('source','—')}\n\n"
        "---\n\n"
        "## I. Kiểm tra ngưỡng QĐ 2879/QĐ-BYT\n\n"
        + rules +
        "\n\n---\n\n"
        "## II. Thống kê mô tả\n\n"
        + stats +
        "\n\n---\n\n"
        "## III. Tỷ lệ tuân thủ theo ngày\n\n"
        + comp +
        "\n"
    )


# ─────────────────────────────────────────────────────────────────────────────
# CLI
# ─────────────────────────────────────────────────────────────────────────────

def main() -> None:
    p = argparse.ArgumentParser(description="Tạo báo cáo đánh giá thực đơn tháng")
    p.add_argument("json_file", nargs="?", help="Đường dẫn file monthly_menu JSON")
    p.add_argument("-f", "--format", choices=["html", "md", "both"], default="html")
    p.add_argument("-o", "--output", help="Đường dẫn file output")
    args = p.parse_args()

    # Find input JSON
    if args.json_file:
        json_path = Path(args.json_file)
    else:
        mg_out = _REPO / "model_generation" / "output"
        candidates = sorted((mg_out).glob("monthly_menu_*.json"), reverse=True)
        if not candidates:
            print("Không tìm thấy file monthly_menu JSON. Chạy: python -m model_generation.run")
            sys.exit(1)
        json_path = candidates[0]

    menu = json.loads(json_path.read_text(encoding="utf-8"))
    basename = json_path.stem

    md_text  = full_report_markdown(menu)
    html_text = full_report_html(menu)

    if args.format in ("md", "both"):
        md_out = args.output or str((_REPO / "model_month_evaluation" / "output" / basename).with_suffix(".md"))
        Path(md_out).parent.mkdir(parents=True, exist_ok=True)
        Path(md_out).write_text(md_text, encoding="utf-8")
        print(f"Saved Markdown: {md_out}")

    if args.format in ("html", "both"):
        html_out = args.output or str((_REPO / "model_month_evaluation" / "output" / basename).with_suffix(".html"))
        Path(html_out).parent.mkdir(parents=True, exist_ok=True)
        Path(html_out).write_text(html_text, encoding="utf-8")
        print(f"Saved HTML:     {html_out}")
