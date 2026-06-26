# -*- coding: utf-8 -*-
"""
run.py — Chạy đánh giá đầy đủ cho thực đơn tháng.

Usage:
    python -m model_month_evaluation.run                     # tất cả, cả HTML + Markdown
    python -m model_month_evaluation.run -f html          # chỉ HTML
    python -m model_month_evaluation.run -f md           # chỉ Markdown
    python -m model_month_evaluation.run monthly_menu_20260626.json
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

_REPO = Path(__file__).parent.parent
sys.path.insert(0, str(_REPO))
sys.path.insert(0, str(_REPO / "model_generation"))

from model_month_evaluation.rules_checker import check_menu, results_to_json
from model_month_evaluation.statistics import compute_all_stats, stats_to_markdown
from model_month_evaluation.compliance import compute_all_compliance, compliance_to_markdown


def main() -> None:
    p = argparse.ArgumentParser(description="Đánh giá thực đơn tháng (model_month_evaluation)")
    p.add_argument("json_file", nargs="?", help="File monthly_menu JSON")
    p.add_argument("-f", "--format", choices=["html", "md", "both"], default="both")
    p.add_argument("-o", "--output-dir", default=None,
                   help="Thư mục output (default: model_month_evaluation/output/)")
    args = p.parse_args()

    # Find input
    if args.json_file:
        json_path = Path(args.json_file)
    else:
        mg_out = _REPO / "model_generation" / "output"
        candidates = sorted((mg_out).glob("monthly_menu_*.json"), reverse=True)
        if not candidates:
            print("ERROR: Không tìm thấy file monthly_menu JSON.")
            print("Chạy trước: python -m model_generation.run")
            sys.exit(1)
        json_path = candidates[0]
        print(f"Dùng: {json_path.name}")

    menu = json.loads(json_path.read_text(encoding="utf-8"))
    basename = json_path.stem
    out_dir = Path(args.output_dir) if args.output_dir else _REPO / "model_month_evaluation" / "output"
    out_dir.mkdir(parents=True, exist_ok=True)

    print(f"\n{'='*60}")
    print(f"ĐÁNH GIÁ THỰC ĐƠN THÁNG")
    print(f"{'='*60}")
    print(f"  Input:  {json_path.name}")
    print(f"  Groups: {len(menu.get('groups', []))}")
    print(f"  Output: {out_dir}/")

    # ── 1. Rules check ──────────────────────────────────────────
    print(f"\n{'─'*40}")
    print("1. Kiểm tra ngưỡng QĐ 2879/QĐ-BYT")
    print(f"{'─'*40}")
    rule_results = check_menu(menu)
    hard_pass = soft_pass = 0
    for r in rule_results:
        hv = sum(1 for v in r.violations if v.severity == "HARD")
        sv = sum(1 for v in r.violations if v.severity == "SOFT")
        if not hv:
            hard_pass += 1
        if not sv:
            soft_pass += 1
        sym = "✅" if not hv and not sv else f"⚠️ H={hv} S={sv}"
        print(f"  [{r.group_id}] {r.label[:28]:<28} {sym}")
    print(f"\n  HARD: {hard_pass}/{len(rule_results)} nhóm đạt")
    print(f"  SOFT: {soft_pass}/{len(rule_results)} nhóm đạt")

    # ── 2. Compliance ───────────────────────────────────────────
    print(f"\n{'─'*40}")
    print("2. Tỷ lệ tuân thủ theo ngày")
    print(f"{'─'*40}")
    comp_results = compute_all_compliance(menu)
    comp_pass = 0
    for r in comp_results:
        sym = "✅" if r.compliance_rate >= 90 else f"⚠️ {r.compliance_rate:.0f}%"
        print(f"  [{r.group_id}] {r.label[:28]:<28} {sym}")
        if r.compliance_rate >= 90:
            comp_pass += 1
    print(f"\n  ≥90% tuân thủ: {comp_pass}/{len(comp_results)} nhóm")

    # ── 3. Statistics ────────────────────────────────────────────
    print(f"\n{'─'*40}")
    print("3. Thống kê mô tả")
    print(f"{'─'*40}")
    all_stats = compute_all_stats(menu)
    print(f"  {'Chỉ tiêu':<14} {'TB':>8} {'Min':>8} {'Max':>8} {'CV':>7}")
    print(f"  {'─'*14} {'─'*8} {'─'*8} {'─'*8} {'─'*7}")
    for s in all_stats[:6]:
        print(f"  {s['label']:<14} {s['all_groups_mean']:>8.0f} {s['all_groups_min']:>8.0f} "
              f"{s['all_groups_max']:>8.0f} {s['all_groups_cv']:>7.2f}")

    # ── 4. Save outputs ─────────────────────────────────────────
    rules_json_out = out_dir / f"{basename}_rules_check.json"
    rules_json_out.write_text(
        json.dumps(results_to_json(rule_results), ensure_ascii=False, indent=2),
        encoding="utf-8"
    )
    print(f"\n  Đã lưu: {rules_json_out.name}")

    stats_md = stats_to_markdown(menu)
    comp_md  = compliance_to_markdown(comp_results)
    rules_md = "\n".join([
        "# KIỂM TRA NGƯỠNG QĐ 2879/QĐ-BYT\n",
        "| Mã | Nhóm | HARD | SOFT | Vi phạm |",
        "|:---|:---|:---:|:---:|:---|",
    ] + [
        f"| {r.group_id} | {r.label} | "
        f"{'✅' if r.hard_passed else '❌'} | "
        f"{'✅' if r.soft_passed else '⚠️'} | "
        f"{len(r.violations)} |"
        for r in rule_results
    ] + [
        "\n### Chi tiết\n",
    ] + [
        f"**[{r.group_id}] {r.label}**: {r.summary}\n"
        + ("\n".join(f"- [{v.severity}] {v.message}" for v in r.violations) if r.violations else "(không có)\n")
        for r in rule_results
    ])

    if args.format in ("md", "both"):
        md_out = out_dir / f"{basename}_evaluation.md"
        md_out.write_text(f"# ĐÁNH GIÁ THỰC ĐƠN THÁNG\n\n"
                          f"Ngày: {menu.get('generated_date','—')}  |  Nguồn: {menu.get('source','—')}\n\n"
                          + rules_md + "\n\n---\n\n" + stats_md + "\n\n---\n\n" + comp_md,
                          encoding="utf-8")
        print(f"  Đã lưu: {md_out.name}  ({md_out.stat().st_size//1024} KB)")

    if args.format in ("html", "both"):
        from model_month_evaluation.report import full_report_html
        html_out = out_dir / f"{basename}_evaluation.html"
        html_out.write_text(full_report_html(menu), encoding="utf-8")
        print(f"  Đã lưu: {html_out.name}  ({html_out.stat().st_size//1024} KB)")

    print(f"\n{'='*60}")
    n_violations = sum(len(r.violations) for r in rule_results)
    n_groups_ok  = sum(1 for r in rule_results if not r.violations)
    print(f"  Kết quả: {n_groups_ok}/{len(rule_results)} nhóm không vi phạm")
    if n_violations:
        print(f"  Tổng cộng {n_violations} vi phạm ngưỡng")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    main()
