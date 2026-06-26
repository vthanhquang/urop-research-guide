# -*- coding: utf-8 -*-
"""
Nutritional validation: calculate kcal/P/L/G from FCT data
and compare against values recorded in weekly_meal_plan_85k.json.

Usage:
    python validate_nutrition.py
"""
import csv
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).parent.resolve()
FCT_PATH  = HERE / "data" / "VTN_FCT_2007_food_composition.csv"
MEAL_PATH = HERE / "data" / "weekly_meal_plan_85k.json"

# ── Helpers ──────────────────────────────────────────────────────────────────

def to_float(v):
    try:
        return float(v)
    except (ValueError, TypeError):
        return 0.0

# ── FCT lookup ─────────────────────────────────────────────────────────────────

def build_fct() -> dict:
    """
    Build a lookup dict keyed by vietnamese_name lowercase.
    Each entry: {kcal, protein, fat, carb, fiber} per 100g.
    """
    fct = {}
    with open(FCT_PATH, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            name = row["vietnamese_name"].strip()
            if not name:
                continue
            entry = {
                "kcal":    to_float(row["energy_kcal"]),
                "protein": to_float(row["protein_g"]),
                "fat":     to_float(row["fat_g"]),
                "carb":    to_float(row["carbohydrate_g"]),
                "fiber":   to_float(row["fiber_g"]),
                "group":   row["group_name_vi"].strip(),
                "code":    row["code"].strip(),
            }
            # Also index by raw and english names
            for n in [name, row["vietnamese_name_raw"].strip(), row["english_name"].strip()]:
                if n:
                    fct[n.lower()] = entry
            fct[row["code"]] = entry
    return fct


def lookup(name: str, fct: dict) -> dict | None:
    """
    Fuzzy FCT lookup: try exact match first, then substring match.
    Returns {kcal, protein, fat, carb} PER 100g, or None.
    """
    key = name.lower().strip()
    if key in fct:
        return fct[key]
    # Substring match: look for key inside FCT name or vice versa
    candidates = []
    for fname, entry in fct.items():
        if not isinstance(fname, str) or len(fname) < 3:
            continue
        if key in fname or fname in key:
            candidates.append((len(fname), fname, entry))
    if candidates:
        # Prefer shortest match (most specific)
        candidates.sort()
        return candidates[0][2]
    return None


# ── Food name → FCT name mapping ───────────────────────────────────────────────

# Priority: manually curated → fallback to fuzzy FCT lookup
# Keys are lowercase, Values are FCT vietnamese_name lowercase
FCT_NAMES: dict[str, str] = {

    # ── Cereals & starches ──
    "gạo tám lào":          "gạo tẻ máy",
    "gạo tám thái":         "gạo tẻ máy",
    "gạo tẻ":               "gạo tẻ máy",
    "bún":                   "bún",
    "bánh phở":              "bánh phở",
    "phở":                   "bánh phở",
    "bánh cuốn":             "bánh phở",
    "bánh bao":              "bánh bao nhân thịt",

    # ── Soups ──
    "canh cải xanh":         "cải xanh",
    "canh cải bắp":          "cải bắp",
    "canh cải ngọt":         "cải ngọt",
    "canh mồng tơi":         "mồng tơi",
    "canh bí xanh":          "bí xanh",
    "canh khoai tây":        "khoai tây",
    "canh cà chua":          "cà chua",

    # ── Vegetables (raw/boiled) ──
    "củ cải":                "củ cải trắng",
    "củ cải trắng":          "củ cải trắng",
    "cải chíp":               "cải bắp",
    "cải bắp":                "cải bắp",
    "cải xanh":               "cải xanh",
    "cải ngọt":               "cải ngọt",
    "mồng tơi":               "mồng tơi",
    "bí xanh":                "bí xanh",
    "bí đỏ":                  "bí đỏ",
    "khoai tây":              "khoai tây",
    "khoai lang":             "khoai lang",
    "cà rốt":                 "cà rốt",
    "hành tây":               "hành tây",
    "đậu cove":               "đậu cô ve",
    "đậu cô ve":              "đậu cô ve",
    "cà chua":                 "cà chua",
    "bông cải xanh":          "bông cải",
    "cà chua":                "cà chua",
    "ớt":                      "ớt",
    "hành lá":                 "hành lá",
    "rau mùi":                 "rau mùi",

    # ── Proteins (raw weight, after cooking adjustments) ──
    # Weights in the plan are cooked weights → use raw FCT values but note the caveat
    "thịt bò":                "thịt bò",
    "thịt lợn":               "thịt lợn",
    "thịt nạc":                "thịt lợn nạc",
    "thịt ngan":               "thịt ngan",
    "ức gà":                  "thịt gà",
    "thịt gà":                 "thịt gà",
    "cá trắm":                 "cá trắm",
    "cá thu":                  "cá thu",
    "cá basa":                  "cá basa",
    "cá rô":                   "cá rô",
    "cá lóc":                  "cá lóc",
    "cá hồi":                  "cá hồi",
    "cá thát lát":              "cá thát lát",
    "tôm":                      "tôm đông lạnh",
    "mực":                      "mực",
    "chả cá":                   "chả cá",
    "chả lá lốt":               "thịt lợn",
    "lạc":                      "lạc hạt",
    "đậu phụ":                  "đậu phụ",
    "đậu phụ rán":              "đậu phụ",
    "trứng":                    "trứng gà",
    "xương ống":                "xương",   # soup base, minimal nutrition

    # ── Cooking oils / seasonings (minimal, not in FCT) ──
    "dầu ăn":                   None,
    "gia vị":                    None,
    "hành":                     "hành lá",
    "hẹ":                       None,
    "tiêu":                     None,
    "mắm":                      None,
    "bột ngọt":                 None,
    "đường":                    "đường",
}


def resolve(name: str, weight_g: float, fct: dict) -> dict:
    """
    Resolve a food name + weight to nutrition.
    Returns {kcal, protein, fat, carb} scaled to weight_g.
    Returns zeros if food is excluded (seasonings/oils) or not found.
    """
    # Check manual map
    key = name.lower().strip()
    fct_name = FCT_NAMES.get(key)

    if fct_name is None and key in FCT_NAMES:
        # Explicitly excluded (seasonings)
        return {"kcal": 0.0, "protein": 0.0, "fat": 0.0, "carb": 0.0}

    # Try manual map first, then fuzzy
    entry = None
    if fct_name and fct_name in fct:
        entry = fct[fct_name]
    if entry is None:
        entry = lookup(key, fct)

    if entry is None:
        return {"kcal": 0.0, "protein": 0.0, "fat": 0.0, "carb": 0.0}

    scale = weight_g / 100.0
    return {
        "kcal":    round(entry["kcal"]    * scale, 2),
        "protein": round(entry["protein"] * scale, 2),
        "fat":     round(entry["fat"]     * scale, 2),
        "carb":    round(entry["carb"]    * scale, 2),
    }


# ── Ingredient string parser ────────────────────────────────────────────────────

def parse_items(raw: str) -> list[tuple[str, float]]:
    """
    Parse a meal-plan ingredient line into (name, weight_g) pairs.

    Handles formats like:
      "Gạo tám Lào: 150g"
      "Cá trắm rán xốt cà chua: 140g, 20g"
      "Thịt lợn xào hành tây, cà rốt: 70g, 10g, 10g"
      "Canh cải xanh nấu thịt nạc: 20g, 10g"
      "Phở: 150g, thịt bò: 50g, xương ống: 20g, hành lá, rau mùi, gia vị"

    Returns list of (ingredient_name, weight_g). Items without explicit weight
    get weight=0 (resolved by resolve() using default or lookup).
    """
    if not raw or not isinstance(raw, str):
        return []

    items = []
    # Split by comma, but handle compound dishes carefully
    segments = re.split(r",\s*", raw)

    for seg in segments:
        seg = seg.strip()
        if not seg:
            continue

        # Try to extract: name: NNNg, NNg, ...
        # Pattern: "dish name: 100g, 20g, 10g" → first number = main ingredient weight
        m = re.search(r":\s*(\d+(?:[.,]\d+)?)\s*g\b", seg)
        if m:
            weight = float(m.group(1).replace(",", "."))
            # Remove all :NNNg patterns to get the name(s)
            name_part = re.sub(r":\s*\d+(?:[.,]\d+)?\s*g\b", "", seg).strip()
            name_part = re.sub(r":\s*$", "", name_part).strip()
            if name_part:
                # Split name_part by comma for compound names
                # e.g. "Cá trắm rán xốt cà chua" → split ingredients
                for sub in re.split(r",\s*", name_part):
                    sub = sub.strip()
                    if sub:
                        items.append((sub, weight))
        else:
            # No weight → e.g. "hành lá", "rau mùi" — weight=0 (resolve will handle)
            seg = seg.strip()
            if seg and len(seg) > 1:
                items.append((seg, 0.0))

    return items


def parse_proteins(raw_list: list) -> list[tuple[str, float]]:
    """Parse a list of protein dish strings."""
    all_items = []
    for item in raw_list:
        all_items.extend(parse_items(item))
    return all_items


def parse_breakfast_detail(raw: str) -> list[tuple[str, float]]:
    """
    Parse breakfast detail strings like:
    "Phở: 150g, thịt bò: 50g, xương ống: 20g, hành lá, rau mùi, gia vị"
    The first segment "Phở: 150g" → phở (bánh phở) 150g
    Other segments have their own weights.
    """
    return parse_items(raw)


# ── Daily nutrition calculator ─────────────────────────────────────────────────

def calc_day(day: dict, fct: dict) -> dict:
    """Calculate total kcal/P/L/G for one day."""
    totals = {"kcal": 0.0, "protein": 0.0, "fat": 0.0, "carb": 0.0}
    unfound = []

    # ── Breakfast ──
    bf = day.get("breakfast")
    if bf:
        detail = bf.get("detail") or ""
        for name, weight in parse_breakfast_detail(detail):
            if weight <= 0:
                weight = 50  # default estimate for unweighed items
            n = resolve(name, weight, fct)
            if n["kcal"] == 0 and name.lower() not in ("gia vị", "hành lá", "rau mùi"):
                unfound.append(name)
            for k in totals:
                totals[k] += n[k]

    # ── Lunch & Dinner ──
    for meal_key in ("lunch", "dinner"):
        meal = day.get(meal_key, {})
        if not meal:
            continue

        # Rice
        rice_raw = meal.get("rice") or ""
        for name, weight in parse_items(rice_raw):
            if weight <= 0:
                weight = 150
            n = resolve(name, weight, fct)
            if n["kcal"] == 0 and name.lower() not in ("gia vị", "hành lá"):
                unfound.append(name)
            for k in totals:
                totals[k] += n[k]

        # Vegetable
        veg_raw = meal.get("vegetable") or ""
        for name, weight in parse_items(veg_raw):
            if weight <= 0:
                weight = 200
            n = resolve(name, weight, fct)
            if n["kcal"] == 0:
                unfound.append(name)
            for k in totals:
                totals[k] += n[k]

        # Proteins
        for name, weight in parse_proteins(meal.get("proteins") or []):
            if weight <= 0:
                weight = 80
            n = resolve(name, weight, fct)
            if n["kcal"] == 0 and name.lower() not in ("gia vị", "hành lá", "cà rốt", "hành tây"):
                unfound.append(name)
            for k in totals:
                totals[k] += n[k]

        # Soup
        soup_raw = meal.get("soup") or ""
        for name, weight in parse_items(soup_raw):
            if weight <= 0:
                weight = 20  # base (soup is mostly water + small amount of veg/meat)
            n = resolve(name, weight, fct)
            if n["kcal"] == 0:
                unfound.append(name)
            for k in totals:
                totals[k] += n[k]

    return {**totals, "unfound": unfound}


def calc_pcts(totals: dict) -> dict:
    """Calculate P/L/G percentages from gram totals."""
    e_p = totals["protein"] * 4
    e_l = totals["fat"]     * 9
    e_g = totals["carb"]    * 4
    total_e = e_p + e_l + e_g
    if total_e <= 0:
        return {"p_pct": 0, "l_pct": 0, "g_pct": 0}
    return {
        "p_pct": round(e_p / total_e * 100, 1),
        "l_pct": round(e_l / total_e * 100, 1),
        "g_pct": round(e_g / total_e * 100, 1),
    }


# ── Rules thresholds ────────────────────────────────────────────────────────────

RULES: dict[str, dict] = {
    # BT01: 1800-1900 kcal, P 12-14%, L 15-25%, G 340-440g
    "BT01": {"kcal_min": 1700, "kcal_max": 2000, "p_min": 12, "p_max": 15,
              "l_min": 15, "l_max": 28, "g_min": 330, "g_max": 450},
    # DD (đái tháo đường): 1500-1700 kcal, P 15-20%, G 200-280g
    "DD":   {"kcal_min": 1400, "kcal_max": 1750, "p_min": 15, "p_max": 20,
              "l_min": 20, "l_max": 32, "g_min": 190, "g_max": 290,
              "fiber_min": 20},
    # SK (sản khoa - cho con bú): 2600-2700 kcal, P 12-14%, G 390-470g
    "SK":   {"kcal_min": 2450, "kcal_max": 2800, "p_min": 11, "p_max": 15,
              "l_min": 18, "l_max": 28, "g_min": 380, "g_max": 480},
    # TN (bệnh thận): 1800-1900 kcal, P 12-14%, G 300-360g
    "TN":   {"kcal_min": 1700, "kcal_max": 2000, "p_min": 11, "p_max": 15,
              "l_min": 18, "l_max": 28, "g_min": 290, "g_max": 370},
    # TM (tim mạch): 1800-1900 kcal
    "TM":   {"kcal_min": 1700, "kcal_max": 2000, "p_min": 12, "p_max": 15,
              "l_min": 15, "l_max": 28, "g_min": 330, "g_max": 440,
              "natri_max": 2400},
    # GM (gan mật): 1500-1700 kcal, L lower
    "GM":   {"kcal_min": 1400, "kcal_max": 1800, "p_min": 12, "p_max": 16,
              "l_min": 10, "l_max": 18, "g_min": 300, "g_max": 370},
    # PT (phẫu thuật hồi phục): 1800-1900 kcal
    "PT":   {"kcal_min": 1700, "kcal_max": 2000, "p_min": 12, "p_max": 15,
              "l_min": 15, "l_max": 28, "g_min": 270, "g_max": 340},
    # GU (gút): 1800-1900 kcal
    "GU":   {"kcal_min": 1700, "kcal_max": 2000, "p_min": 12, "p_max": 15,
              "l_min": 15, "l_max": 28, "g_min": 330, "g_max": 440},
    # UT (ung thư): 1800-1900 kcal
    "UT":   {"kcal_min": 1700, "kcal_max": 2000, "p_min": 12, "p_max": 15,
              "l_min": 15, "l_max": 28, "g_min": 330, "g_max": 440},
    # IOD (kiêng i-ốt): similar to BT
    "IOD":  {"kcal_min": 1650, "kcal_max": 2000, "p_min": 12, "p_max": 15,
              "l_min": 15, "l_max": 28, "g_min": 330, "g_max": 440},
    # DEFAULT: BT
    "DEFAULT": {"kcal_min": 1700, "kcal_max": 2000, "p_min": 12, "p_max": 15,
                "l_min": 15, "l_max": 28, "g_min": 330, "g_max": 440},
}


def rules_key_for(code: str, label: str) -> str:
    """Map diet group to rules key."""
    c = (code or "").upper()
    l = (label or "").upper()
    if "BT01" in c and "CƠM THƯỜNG" in l:
        return "BT01"
    if "ĐĐ" in c or "ĐÁI THÁO" in l:
        return "DD"
    if "SẢN" in c or "SẢN KHOA" in l:
        return "SK"
    if "TN" in c or "THẬN" in l:
        return "TN"
    if "TM" in c or "TIM MẠCH" in l or "TĂNG HUYẾT" in l:
        return "TM"
    if "GM" in c or "GAN MẬT" in l:
        return "GM"
    if "PT" in c or "PHẪU" in l:
        return "PT"
    if "GU" in c or "GÚT" in l:
        return "GU"
    if "UT" in c or "UNG THƯ" in l:
        return "UT"
    if "IOD" in c or "KIÊNG" in l:
        return "IOD"
    return "DEFAULT"


# ── Main ──────────────────────────────────────────────────────────────────────

def validate():
    print("=" * 72)
    print("NUTRITIONAL VALIDATION REPORT")
    print("  Meal plan: weekly_meal_plan_85k.json")
    print("  FCT source: VTN_FCT_2007_food_composition.csv")
    print("=" * 72)

    fct = build_fct()
    print(f"\nLoaded FCT: {len(fct)} entries")

    with open(MEAL_PATH, encoding="utf-8") as f:
        plan = json.load(f)

    summary = []

    for group in plan["groups"]:
        code  = group.get("code") or ""
        label = group.get("label") or ""
        rec_kcal = group.get("kcal") or 0
        rec_plg  = group.get("plgG") or ""
        rec_pct  = group.get("plgPct") or ""

        # Parse recorded P:L:G (g)
        rec_p, rec_l, rec_g = 0.0, 0.0, 0.0
        if rec_plg:
            parts = re.split(r":", rec_plg.replace("g", "").strip())
            if len(parts) >= 3:
                try:
                    rec_p = float(parts[0].strip())
                    rec_l = float(parts[1].strip())
                    rec_g = float(parts[2].strip())
                except ValueError:
                    pass

        print(f"\n{'─' * 72}")
        print(f"GROUP : {label}")
        print(f"  Code : {code}")
        print(f"  Rec  : {rec_kcal} kcal | P={rec_p:.0f}g L={rec_l:.0f}g G={rec_g:.0f}g | {rec_pct}")

        # Calculate per-day
        days_result = []
        for day in group.get("days") or []:
            day_tot = calc_day(day, fct)
            pcts = calc_pcts(day_tot)
            days_result.append({**day_tot, **pcts, "day": day.get("key", "?")})

        if not days_result:
            print("  ⚠️  No days found")
            continue

        # Average
        n = len(days_result)
        avg_kcal = sum(d["kcal"]    for d in days_result) / n
        avg_p    = sum(d["protein"] for d in days_result) / n
        avg_l    = sum(d["fat"]     for d in days_result) / n
        avg_g    = sum(d["carb"]    for d in days_result) / n

        # Average percentages
        avg_e_p  = avg_p * 4
        avg_e_l  = avg_l * 9
        avg_e_g  = avg_g * 4
        total_e  = avg_e_p + avg_e_l + avg_e_g
        avg_p_pct = round(avg_e_p / total_e * 100, 1) if total_e else 0
        avg_l_pct = round(avg_e_l / total_e * 100, 1) if total_e else 0
        avg_g_pct = round(avg_e_g / total_e * 100, 1) if total_e else 0

        # Diff
        diff_kcal = round(avg_kcal - rec_kcal, 0)
        diff_p    = round(avg_p    - rec_p,    1)
        diff_l    = round(avg_l    - rec_l,    1)
        diff_g    = round(avg_g    - rec_g,    1)

        # Collect all unfound items
        all_unfound = set()
        for d in days_result:
            all_unfound.update(d.get("unfound", []))

        print(f"  Calc : {avg_kcal:.0f} kcal | P={avg_p:.0f}g L={avg_l:.0f}g G={avg_g:.0f}g")
        print(f"  %    : P={avg_p_pct}% L={avg_l_pct}% G={avg_g_pct}%")
        print(f"  Diff : kcal={diff_kcal:+.0f} P={diff_p:+.0f}g L={diff_l:+.0f}g G={diff_g:+.0f}g")
        if all_unfound:
            print(f"  ?     : Not in FCT: {', '.join(sorted(all_unfound))}")

        # Rules check
        rk = rules_key_for(code, label)
        r  = RULES.get(rk, RULES["DEFAULT"])
        issues = []
        if avg_kcal < r["kcal_min"]:
            issues.append(f"kcal LOW ({avg_kcal:.0f} < {r['kcal_min']})")
        if avg_kcal > r["kcal_max"]:
            issues.append(f"kcal HIGH ({avg_kcal:.0f} > {r['kcal_max']})")
        if avg_p_pct < r["p_min"]:
            issues.append(f"P% LOW ({avg_p_pct}% < {r['p_min']}%)")
        if avg_p_pct > r["p_max"]:
            issues.append(f"P% HIGH ({avg_p_pct}% > {r['p_max']}%)")
        if avg_l_pct < r["l_min"]:
            issues.append(f"L% LOW ({avg_l_pct}% < {r['l_min']}%)")
        if avg_l_pct > r["l_max"]:
            issues.append(f"L% HIGH ({avg_l_pct}% > {r['l_max']}%)")
        if avg_g < r["g_min"]:
            issues.append(f"G(g) LOW ({avg_g:.0f}g < {r['g_min']}g)")
        if avg_g > r["g_max"]:
            issues.append(f"G(g) HIGH ({avg_g:.0f}g > {r['g_max']}g)")

        if issues:
            print(f"  Rules ({rk}): {' | '.join(issues)} ⚠️")
        else:
            print(f"  Rules ({rk}): ✅ Within thresholds")

        # Pass/fail: allow ±200 kcal, ±20g P, ±15g L, ±40g G as "pass"
        kcal_ok = abs(diff_kcal) < 200
        p_ok    = abs(diff_p)    < 20
        l_ok    = abs(diff_l)    < 15
        g_ok    = abs(diff_g)    < 40
        overall_ok = kcal_ok and p_ok and l_ok and g_ok
        status = "✅ PASS" if overall_ok else "⚠️  REVIEW"
        print(f"  Status: {status}")

        summary.append({
            "code": code,
            "label": label,
            "rec_kcal": rec_kcal,
            "calc_kcal": round(avg_kcal),
            "diff_kcal": round(diff_kcal),
            "rec_p": rec_p, "rec_l": rec_l, "rec_g": rec_g,
            "calc_p": round(avg_p), "calc_l": round(avg_l), "calc_g": round(avg_g),
            "diff_p": round(diff_p), "diff_l": round(diff_l), "diff_g": round(diff_g),
            "p_pct": avg_p_pct, "l_pct": avg_l_pct, "g_pct": avg_g_pct,
            "unfound": sorted(all_unfound),
            "rules_key": rk,
            "rules_issues": issues,
            "status": "PASS" if overall_ok else "REVIEW",
        })

    # ── Summary ────────────────────────────────────────────────────────────────
    print("\n" + "=" * 72)
    print("SUMMARY TABLE")
    print("=" * 72)
    print(f"{'Code':<18} {'Label':<22} {'Rec kcal':>8} {'Cal kcal':>8} "
          f"{'Δkcal':>6} {'P%':>5} {'L%':>5} {'G%':>5} {'Status':>6}")
    print("-" * 90)
    for s in summary:
        label_short = s["label"][:21] if s["label"] else ""
        print(f"{s['code'][:17]:<18} {label_short:<22} {s['rec_kcal']:>8} "
              f"{s['calc_kcal']:>8} {s['diff_kcal']:>+6.0f} "
              f"{s['p_pct']:>5.1f} {s['l_pct']:>5.1f} {s['g_pct']:>5.1f} "
              f"{s['status']:>6}")

    pass_count   = sum(1 for s in summary if s["status"] == "PASS")
    review_count = sum(1 for s in summary if s["status"] == "REVIEW")
    print(f"\n{pass_count} PASS | {review_count} REVIEW")

    # Per-day detail for groups with issues
    print("\n" + "=" * 72)
    print("PER-DAY BREAKDOWN (all groups)")
    print("=" * 72)
    for group in plan["groups"]:
        code  = group.get("code") or ""
        label = group.get("label") or ""
        print(f"\n[{code[:18]}] {label}")
        for day in group.get("days") or []:
            day_tot = calc_day(day, fct)
            pcts    = calc_pcts(day_tot)
            e_p = day_tot["protein"] * 4
            e_l = day_tot["fat"]     * 9
            e_g = day_tot["carb"]    * 4
            total_e = e_p + e_l + e_g
            pp = round(e_p / total_e * 100, 1) if total_e else 0
            lp = round(e_l / total_e * 100, 1) if total_e else 0
            gp = round(e_g / total_e * 100, 1) if total_e else 0
            unf = day_tot.get("unfound", [])
            unf_str = f" ?{len(unf)}" if unf else ""
            print(f"  {day.get('label',''):<10} {day_tot['kcal']:>6.0f} kcal  "
                  f"P={day_tot['protein']:>5.1f}g L={day_tot['fat']:>4.1f}g G={day_tot['carb']:>5.1f}g  "
                  f"P%={pp:>4.1f}% L%={lp:>4.1f}% G%={gp:>4.1f}%{unf_str}")

    # Save JSON summary
    out_path = HERE / "data" / "validation_summary.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)
    print(f"\nSaved: {out_path}")


if __name__ == "__main__":
    validate()
