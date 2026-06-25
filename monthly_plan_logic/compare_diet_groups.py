# -*- coding: utf-8 -*-
"""
Compare each diet group (pages 2-11) against the base standard menu (page 1).

For every (day, meal, slot, item_index) cell, report:
  - UNCHANGED  — dish matches the base
  - CHANGED    — slot occupied but dish differs
  - ADDED      — extra item in this group (item_index > base max)
  - REMOVED    — base has an item this group skips
"""
import json
import sys
from pathlib import Path

# Force UTF-8 output so Vietnamese characters render correctly in the console.
sys.stdout.reconfigure(encoding="utf-8")

HERE = Path(__file__).parent.resolve()
JSON_PATH = HERE / "data" / "weekly_meal_plan_85k.json"


def flatten_page(data, page_num):
    """Return dict[day_key][meal][slot][item_index] -> dish_name (str or None)."""
    groups = {g["page"]: g for g in data["groups"]}
    g = groups[page_num]
    result = {}  # day_key -> meal -> slot -> item_index -> dish_name

    for day in g["days"]:
        dk = day["key"]
        result[dk] = {}
        for meal in ("breakfast", "lunch", "dinner"):
            result[dk][meal] = {}
            slot_data = day.get(meal)
            if not slot_data:
                continue
            if meal == "breakfast":
                bf = slot_data
                result[dk][meal]["main"] = {}
                result[dk][meal]["main"][1] = (bf["name"] or "") if bf else ""
            else:
                for slot in ("rice", "vegetable", "protein", "soup"):
                    result[dk][meal][slot] = {}
                    items = slot_data.get(slot, [])
                    if isinstance(items, list):
                        for idx, item in enumerate(items, 1):
                            result[dk][meal][slot][idx] = item or ""
                    else:
                        result[dk][meal][slot][1] = items or ""
    return result


def compare_pages(base, other):
    """Compare 'other' against 'base', return list of diff entries."""
    diffs = []
    for dk in sorted(base.keys()):
        if dk not in other:
            continue
        for meal in ("breakfast", "lunch", "dinner"):
            if meal not in base[dk] or meal not in other[dk]:
                continue
            for slot in base[dk][meal]:
                base_items = base[dk][meal].get(slot, {})
                other_items = other[dk][meal].get(slot, {})

                all_indices = set(base_items.keys()) | set(other_items.keys())
                for idx in sorted(all_indices):
                    b_val = base_items.get(idx, "")
                    o_val = other_items.get(idx, "")

                    b_name = b_val.strip()
                    o_name = o_val.strip()

                    if o_name and b_name and o_name != b_name:
                        diffs.append({
                            "day": dk,
                            "meal": meal,
                            "slot": slot,
                            "idx": idx,
                            "status": "CHANGED",
                            "base": b_name,
                            "other": o_name,
                        })
                    elif o_name and not b_name:
                        diffs.append({
                            "day": dk,
                            "meal": meal,
                            "slot": slot,
                            "idx": idx,
                            "status": "ADDED",
                            "base": b_name,
                            "other": o_name,
                        })
                    elif not o_name and b_name:
                        diffs.append({
                            "day": dk,
                            "meal": meal,
                            "slot": slot,
                            "idx": idx,
                            "status": "REMOVED",
                            "base": b_name,
                            "other": o_name,
                        })
    return diffs


def summarize_page(base, other_flat, page_num, label):
    diffs = compare_pages(base, other_flat)

    changed = [d for d in diffs if d["status"] == "CHANGED"]
    added   = [d for d in diffs if d["status"] == "ADDED"]
    removed = [d for d in diffs if d["status"] == "REMOVED"]

    print(f"\n{'='*70}")
    print(f"  Page {page_num}: {label}")
    print(f"  CHANGED: {len(changed)}  |  ADDED: {len(added)}  |  REMOVED: {len(removed)}")
    print(f"{'='*70}")

    # Group by meal
    for meal in ("breakfast", "lunch", "dinner"):
        meal_changed = [d for d in changed if d["meal"] == meal]
        meal_added   = [d for d in added   if d["meal"] == meal]
        meal_removed = [d for d in removed if d["meal"] == meal]
        if not (meal_changed or meal_added or meal_removed):
            continue

        print(f"\n  [{meal.upper()}]")
        if meal_added:
            print(f"    + ADDED   ({len(meal_added)}):")
            for d in meal_added:
                print(f"        {d['day']:>3}  [{d['slot']}] item#{d['idx']}  \"{d['other']}\"")
        if meal_changed:
            print(f"    ~ CHANGED ({len(meal_changed)}):")
            for d in meal_changed:
                print(f"        {d['day']:>3}  [{d['slot']}] item#{d['idx']}")
                print(f"            base:  \"{d['base']}\"")
                print(f"            this:  \"{d['other']}\"")
        if meal_removed:
            print(f"    - REMOVED ({len(meal_removed)}):")
            for d in meal_removed:
                print(f"        {d['day']:>3}  [{d['slot']}] item#{d['idx']}  \"{d['base']}\"")


def main():
    with open(JSON_PATH, encoding="utf-8") as f:
        data = json.load(f)

    base_flat = flatten_page(data, page_num=1)

    # Summary table
    print(f"\n{'='*70}")
    print("  TỔNG HỢP SO SÁNH CÁC NHÓM BỆNH VỚI THỰC ĐƠN CHUẨN (Page 1)")
    print(f"{'='*70}")
    print(f"\n  {'Page':<6} {'Nhóm bệnh':<35} {'Changed':>8} {'Added':>7} {'Removed':>8}")
    print(f"  {'-'*6}  {'-'*35}  {'-'*8}  {'-'*7}  {'-'*8}")

    for g in data["groups"]:
        if g["page"] == 1:
            continue
        other_flat = flatten_page(data, page_num=g["page"])
        diffs = compare_pages(base_flat, other_flat)
        changed = sum(1 for d in diffs if d["status"] == "CHANGED")
        added   = sum(1 for d in diffs if d["status"] == "ADDED")
        removed = sum(1 for d in diffs if d["status"] == "REMOVED")
        label = (g["label"] or g["code"] or f"page {g['page']}")[:35]
        print(f"  {g['page']:<6}  {label:<35}  {changed:>8}  {added:>7}  {removed:>8}")

    print(f"\n  {'TOTAL changes across all groups:'}")
    total_changed = total_added = total_removed = 0
    for g in data["groups"]:
        if g["page"] == 1:
            continue
        other_flat = flatten_page(data, page_num=g["page"])
        diffs = compare_pages(base_flat, other_flat)
        total_changed += sum(1 for d in diffs if d["status"] == "CHANGED")
        total_added   += sum(1 for d in diffs if d["status"] == "ADDED")
        total_removed += sum(1 for d in diffs if d["status"] == "REMOVED")
    print(f"  {'Changed:':<40} {total_changed}")
    print(f"  {'Added (extra dishes):':<40} {total_added}")
    print(f"  {'Removed (dishes skipped):':<40} {total_removed}")

    # Detailed output per page
    for g in data["groups"]:
        if g["page"] == 1:
            continue
        other_flat = flatten_page(data, page_num=g["page"])
        summarize_page(base_flat, other_flat, g["page"], g["label"] or g["code"])


if __name__ == "__main__":
    main()
