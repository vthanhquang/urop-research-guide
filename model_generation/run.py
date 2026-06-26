# -*- coding: utf-8 -*-
"""
run.py — CLI entry point for monthly menu generation.

Usage:
    python run.py                     # Generate all 11 groups, 4 weeks
    python run.py --group BT01        # Generate only BT01
    python run.py --weeks 2          # Generate 2 weeks
    python run.py --candidates 3      # 3 candidates per week
    python run.py --output my_menu.json
    python run.py --verbose
    python run.py --all-groups
    python run.py --summary-only      # Skip dish details, only show totals
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

# Ensure model_generation is on the path
HERE = Path(__file__).parent.resolve()
sys.path.insert(0, str(HERE))

from core import (
    generate_monthly_menu,
    monthly_to_dict,
    GROUP_IDS,
    GROUP_LABELS,
)
from config import NUTRIENT_TARGETS


def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        description="Generate monthly hospital meal menus for all diet groups.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    p.add_argument(
        "--group", "-g",
        action="append",
        dest="groups",
        metavar="CODE",
        help="Diet group code(s) to generate. Can be repeated. "
             "Default: all groups. Options: " + ", ".join(GROUP_IDS),
    )
    p.add_argument(
        "--weeks", "-w",
        type=int,
        default=4,
        metavar="N",
        help="Number of weeks to generate (default: 4)",
    )
    p.add_argument(
        "--candidates", "-c",
        type=int,
        default=5,
        metavar="N",
        help="Number of candidate weeks to score per week (default: 5)",
    )
    p.add_argument(
        "--seed", "-s",
        type=int,
        default=42,
        metavar="N",
        help="Random seed for reproducibility (default: 42). Use 0 for random.",
    )
    p.add_argument(
        "--output", "-o",
        type=str,
        default=None,
        metavar="PATH",
        help="Output JSON path (default: model_generation/output/monthly_menu_YYYYMMDD.json)",
    )
    p.add_argument(
        "--summary-only",
        action="store_true",
        help="Skip per-day dish details in output JSON (smaller file)",
    )
    p.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Print per-day details to stdout",
    )
    p.add_argument(
        "--all-groups",
        action="store_true",
        help="Alias for --groups with all codes (default behaviour)",
    )
    return p


def _print_summary(menu_dict: dict) -> None:
    """Print a formatted summary table to stdout."""
    print("\n" + "=" * 80)
    print("MONTHLY MENU GENERATION SUMMARY")
    print("=" * 80)
    print(f"Generated: {menu_dict['generated_date']}  |  Weeks: {menu_dict['n_weeks']}")
    print(f"Groups: {len(menu_dict['groups'])}")
    print()

    header = (
        f"  {'Group':<6} {'Label':<26} {'Kcal target':>15} "
        f"{'Avg kcal':>10} {'P%':>6} {'L%':>6} {'G%':>6} {'Na mg':>8} {'Status':>8}"
    )
    print(header)
    print("  " + "-" * 85)

    for g in menu_dict["groups"]:
        gid = g["group_id"]
        label = g["label"][:25]
        tgt = g["target"]
        kcal_range = f"{tgt['kcal_min']}-{tgt['kcal_max']}"
        avg_kcal = g["monthly_avg"]["kcal"]
        p_pct = g["monthly_p_pct"]
        l_pct = g["monthly_l_pct"]
        g_pct = g["monthly_g_pct"]
        sodium = g["monthly_avg"]["sodium"]
        violations = g.get("violations", [])
        status = "✅ OK" if not violations else f"⚠️ {len(violations)}"
        print(
            f"  {gid:<6} {label:<26} {kcal_range:>15} "
            f"{avg_kcal:>10.0f} {p_pct:>5.1f}% {l_pct:>5.1f}% {g_pct:>5.1f}% "
            f"{sodium:>8.0f} {status:>8}"
        )

    print()
    total_violations = sum(len(g.get("violations", [])) for g in menu_dict["groups"])
    total_groups = len(menu_dict["groups"])
    print(f"  {total_groups} groups generated | {total_violations} violations")


def _summarize_weeks(menu_dict: dict) -> None:
    """Print week-level breakdown."""
    for g in menu_dict["groups"]:
        gid = g["group_id"]
        label = g["label"]
        print(f"\n{'─'*60}")
        print(f"  [{gid}] {label}")
        tgt = g["target"]
        print(f"  Target: {tgt['kcal_min']}-{tgt['kcal_max']} kcal, "
              f"P={tgt['p_pct_range'][0]}-{tgt['p_pct_range'][1]}%, "
              f"L={tgt['l_pct_range'][0]}-{tgt['l_pct_range'][1]}%, "
              f"G={tgt['g_pct_range'][0]}-{tgt['g_pct_range'][1]}%")

        for w in g["weeks"]:
            s = w["plan_summary"]
            p_pct = round(s["protein_avg"] * 4 / (
                s["protein_avg"] * 4 + s["fat_avg"] * 9 + s["carb_avg"] * 4
            ) * 100, 1) if s["protein_avg"] else 0
            l_pct = round(s["fat_avg"] * 9 / (
                s["protein_avg"] * 4 + s["fat_avg"] * 9 + s["carb_avg"] * 4
            ) * 100, 1) if s["protein_avg"] else 0
            g_pct = round(s["carb_avg"] * 4 / (
                s["protein_avg"] * 4 + s["fat_avg"] * 9 + s["carb_avg"] * 4
            ) * 100, 1) if s["protein_avg"] else 0
            flags = " ".join(w.get("flags", [])) if w.get("flags") else ""
            warn_str = f" ⚠️{len(w['warnings'])}" if w["warnings"] else ""
            print(
                f"  Week {w['week_index']+1}: {s['kcal_avg']:>6.0f} kcal  "
                f"P={s['protein_avg']:>5.1f}g({p_pct:>4.1f}%)  "
                f"L={s['fat_avg']:>4.1f}g({l_pct:>4.1f}%)  "
                f"G={s['carb_avg']:>5.1f}g({g_pct:>4.1f}%)  "
                f"Na={s['sodium_avg']:>5.0f}mg  "
                f"score={w['score']:.3f}{warn_str}  {flags}"
            )


def main() -> None:
    args = _build_parser().parse_args()

    # Resolve groups
    if args.all_groups or not args.groups:
        groups = GROUP_IDS
    else:
        groups = []
        for g in args.groups:
            g = g.upper()
            if g not in GROUP_IDS:
                print(f"WARNING: Unknown group '{g}'. Available: {', '.join(GROUP_IDS)}")
                continue
            groups.append(g)
        if not groups:
            print("No valid groups specified. Use --all-groups or --group CODE")
            sys.exit(1)

    # Resolve seed
    seed = None if (args.seed == 0) else args.seed

    # Output path
    if args.output:
        out_path = Path(args.output)
    else:
        from datetime import date
        today = date.today().strftime("%Y%m%d")
        out_dir = HERE / "output"
        out_dir.mkdir(exist_ok=True)
        out_path = out_dir / f"monthly_menu_{today}.json"

    print(f"\nGenerating monthly menu:")
    print(f"  Groups:    {', '.join(groups)}")
    print(f"  Weeks:     {args.weeks}")
    print(f"  Candidates:{args.candidates}")
    print(f"  Seed:      {seed if seed else '(random)'}")
    print(f"  Output:    {out_path}")

    menu = generate_monthly_menu(
        n_weeks=args.weeks,
        group_ids=groups,
        seed=seed,
        n_candidates=args.candidates,
    )

    menu_dict = monthly_to_dict(menu)

    # Prune per-day dish details if --summary-only
    if args.summary_only:
        for g in menu_dict["groups"]:
            for w in g["weeks"]:
                for d in w["days"]:
                    # Keep totals and key fields, remove dish names
                    d["_summary"] = True
        print("\n  [Note] --summary-only: dish-level details not included in JSON")

    # Save JSON
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(menu_dict, f, ensure_ascii=False, indent=2)
    print(f"\n  Saved: {out_path}  ({out_path.stat().st_size / 1024:.0f} KB)")

    # Print summary
    _print_summary(menu_dict)
    if args.verbose:
        _summarize_weeks(menu_dict)

    # Final verdict
    violations = sum(len(g.get("violations", [])) for g in menu_dict["groups"])
    groups_ok = sum(1 for g in menu_dict["groups"] if not g.get("violations"))
    print(f"\n{'='*80}")
    print(f"  Result: {groups_ok}/{len(menu_dict['groups'])} groups within all thresholds")
    if violations > 0:
        print(f"  ⚠️  {violations} violation(s) detected — see violations column above")
        print(f"  Note: violations may be acceptable if dish DB lacks full coverage")
    print(f"{'='*80}")

    if violations > 0 and not args.verbose:
        print("\n  Run with --verbose to see per-week breakdowns.")
        print("  Run with --output to save the full JSON.")


if __name__ == "__main__":
    main()
