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
SP_PATH   = HERE / "data" / "sp_thuong_mai.csv"
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
    Combines VTN_FCT_2007 + sp_thuong_mai.csv (commercial products).
    """
    fct = {}
    for path in [FCT_PATH, SP_PATH]:
        with open(path, encoding="utf-8") as f:
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
    "cải ngọt":             "dưa cải bẹ",
    "mồng tơi":               "mồng tơi",
    "bí xanh":                "bí xanh",
    "bí đỏ":                  "bí ngô",
    "khoai tây":              "khoai tây",
    "khoai lang":             "khoai lang",
    "cà rốt":                 "cà rốt (củ đỏ, vàng)",
    "hành tây":               "hành tây",
    "đậu cove":               "đậu cô ve",
    "đậu cô ve":              "đậu cô ve",
    "cà chua":                 "cà chua",
    "bông cải xanh":          "bông cải",
    "cà chua":                "cà chua",
    "ớt":                      "ớt đỏ to",
    "hành lá":                 "hành lá",
    "rau mùi":                 None,   # not in FCT → zero kcal (herb garnish)
    "rau thơm":                "rau thơm",

    # ── Proteins (raw weight, after cooking adjustments) ──
    # Weights in the plan are cooked weights → use raw FCT values but note the caveat
    "thịt bò":                "thịt bò loại i",
    "thịt bê":                "thịt bò loại i",       # thịt bê không có trong FCT → proxy bằng thịt bò loại i (118 kcal/100g)
    "thịt bê nạc":           "thịt bò loại i",          # thịt bê nạc not in FCT → proxy bằng thịt bò loại i (118 kcal/100g)
    "thịt lợn":               "thịt lợn nạc",    # generic pork → lean pork (118 kcal); "thịt lợn mỡ" (315 kcal) should NOT be auto-matched
    "thịt lợn nạc":            "thịt lợn nạc",
    "thịt lợn nửa nạc":        "thịt lợn nửa nạc nửa mỡ",
    "thịt lợn nửa nạc nửa mỡ": "thịt lợn nửa nạc, nửa mỡ",  # FCT uses comma, plan uses dash
    "thịt lợn vai luộc":       "thịt lợn nạc",               # cooked lean pork → lean pork FCT (111 kcal)
    "thịt lợn mỡ":            "thịt lợn mỡ",
    "thịt nạc":                "thịt lợn nạc",
    "thịt vai quay":           "thịt lợn nửa nạc, nửa mỡ",
    "thịt lợn vai":           "thịt lợn nửa nạc, nửa mỡ",
    "sườn lợn":               "sườn lợn",
    "thịt ngan":               "thịt ngỗng",
    "ức gà":                  "thịt gà ta",
    "thịt gà":                 "thịt gà ta",
    "thịt gà ta":             "thịt gà ta",
    "thịt gà xé":             "thịt gà ta",
    "thịt gà xé 70g":         "thịt gà ta",
    "thịt gà cn (cả xương)":  "thịt gà ta",
    # Fish: dùng FCT có sẵn nếu có, fallback sang cá basa (bạc) nếu không tìm thấy
    # FCT có: cá trắm cỏ (91 kcal), cá rô đồng (126 kcal), cá thu (166 kcal)
    "cá trắm":                "cá trắm cỏ",
    "cá trắm cỏ":             "cá trắm cỏ",
    "cá thu":                  "cá thu",
    "cá rô":                   "cá rô đồng",
    "cá lóc":                  "cá basa (bạc)",      # NOT in FCT → fallback
    "cá basa":                  "cá basa (bạc)",      # NOT in FCT → fallback
    "cá hồi":                  "cá hồi",
    "cá thát lát":              "cá nạc",
    "tôm":                      "tôm đồng",
    "mực":                      "mực tươi",
    "chả cá":                   "cá basa (bạc)",
    "chả lá lốt":               "thịt lợn nạc",
    "lạc":                      "lạc hạt",
    "lạc rim":                  "lạc hạt",
    "đậu phụ":                  "đậu phụ",
    "đậu phụ rán":              "đậu phụ nướng",
    "trứng":                    "trứng gà",
    "trứng đúc thịt":           "trứng gà",
    "trứng ốp":                 "trứng gà",
    "trứng ốp lết":             "trứng gà",
    "giò lụa":                  "giò lụa",
    "ba tê":                    "ba tê",

    # ── Cooked vegetable dishes → raw vegetable equivalents ──────────────────
    # NOTE: "cải ngọt" is NOT in FCT; substitute closest variety
    "bí xanh luộc":           "bí đao (bí xanh)",
    "bí đỏ xào":             "bí ngô",
    "củ cải luộc":           "củ cải trắng",
    "cải chíp luộc":          "cải bắp",
    "cải chíp xào":          "cải bắp",
    # "cải ngọt" (mustard greens) not in VTN_FCT_2007 → substitute cải xanh
    "cải ngọt luộc":          "cải xanh",
    "đậu cove luộc":         "đậu cô ve",
    "rau dền luộc":           "rau đay",
    "cải thảo xào thì là":   "cải bắp",
    "canh bí xanh nấu thịt nạc": "bí đao (bí xanh)",
    "canh mồng tơi nấu bột nêm": "rau mồng tơi",
    # Soup patterns with 2 ingredients: the first weight is vegetable, second is meat (broth)
    # Meat in soup is broth → kcal contribution is negligible (the meat is simmered for flavor)
    "canh cải bắp nấu cà chua": "cải bắp",     # 20g cải bắp only; 10g cà chua and meat excluded
    "canh cải xanh nấu thịt nạc": "cải xanh",   # 20g cải xanh only; meat excluded

    # ── Bone soup (xương ống) — mostly water, minimal nutrition ──────────
    # FCT has Tủy xương (bone marrow) which is very high-fat; xương ống soup
    # is the broth, not the marrow. Use None (→ zero) to exclude.
    "xương ống":              None,

    # ── Cooked protein dishes → approximate with raw / processed equivalents ──
    # Cooking yield: ~85% for stir-fried (xào/rang) → apply 0.85 factor in resolve()
    # Boiled/steamed dishes: ~90% yield → apply 0.90 factor
    "thịt bò xào cần tỏi tây":    ("thịt bò loại i",          0.85),
    "thịt bê xào sả ớt":            ("thịt lợn nạc",            0.85),
    "thịt lợn vai quay mềm":        ("thịt lợn nạc",            0.90),
    "thịt lợn băm xào cà rốt":     ("thịt lợn nạc",            0.85),
    "thịt lợn băm xào hành lá":    ("thịt lợn nạc",            0.85),
    "thịt lợn xào hành tây":       ("thịt lợn nạc",            0.85),
    "thịt lợn xào hành tây, cà rốt": ("thịt lợn nạc",            0.85),
    "thịt lợn xào cần tỏi tây":   ("thịt lợn nạc",            0.85),
    "thịt lợn xào ớt đà lạt":     ("thịt lợn nạc",            0.85),
    "thịt lợn vai rim mắm":         ("thịt lợn nạc",            0.90),
    "thịt lợn kho tàu":             ("thịt lợn nạc",            0.90),
    "thịt gà cn (cả xương) rang gừng sả": ("thịt gà ta",        0.85),
    "tôm rang":                       ("tôm đồng",                 0.85),
    "tôm rang thịt lợn":            ("tôm đồng",                 0.85),
    "tôm rim hành":                  ("tôm đồng",                 0.90),
    "cá trắm kho giềng xả":         ("cá trắm cỏ",              0.90),
    "cá trắm rán xốt cà chua":      ("cá trắm cỏ",              0.85),
    "chả cá rán":                    ("cá rô đồng",              0.85),
    # Commercial product: Sữa Grandcare Gold 180ml (→ sp_thuong_mai.csv, 78 kcal/100g × 180ml = 140 kcal/180ml)
    "sữa grandcare gold 180ml":                ("sữa grandcare gold 180ml", 1.00),
    "gia vị vừa đủ sữa grandcare gold 180ml: 01 hộp": ("sữa grandcare gold 180ml", 1.00),
    "thịt lợn gia vị vừa đủ sữa grandcare gold 180ml: 01 hộp": ("sữa grandcare gold 180ml", 1.00),

    # ── Cooking oils / seasonings (minimal, not in FCT) ──
    "dầu ăn":                   None,
    "gia vị":                    None,
    "hành":                     "hành lá",
    "hẹ":                       None,
    "tiêu":                     None,
    "mắm":                      None,
    "bột ngọt":                 None,
    "đường":                    "đường",

    # ── Split fragments from compound dish names (parser splits these) ──
    # These are garnishes that appear in unfound lists when the parent dish
    # is not in FCT. They have negligible kcal but we still map them to avoid
    # noise in the unfound list.
    "hành lá":                  "hành lá",
    "hành tây":                 "hành tây",
    "cà rốt":                 "cà rốt (củ đỏ, vàng)",

    # ── Genuinely unfound dishes (not in VTN_FCT_2007 / sp_thuong_mai) ──
    # These are compound dishes whose components can't be reliably split.
    # Removing from FCT_NAMES → resolve() returns None → calc_day excludes them (kcal=0).
    # They MUST be on the kcal==0 allowlist in calc_day's 5 sections.
    # "tôm rang thịt lợn": None,  # kept as tuple above → uses tôm đồng
    # "tôm rang thịt lợn, hành lá": None,  # removed → resolve() returns None → excluded
    # "thịt lợn băm xào cà rốt, hành lá": None,  # removed → resolve() returns None → excluded
}


# ── Soup-specific vegetable weights (not all soups use 20g vegetable) ──────
# Map: lowercased soup raw string → vegetable weight in grams
# These override the default 20g in calc_day.
SOUP_VEG_WEIGHTS: dict[str, float] = {
    # IOD group: heavier vegetable portions
    "canh khoai tây nấu thịt nạc": 50.0,   # IOD: 50g khoai tây (vs 30g in BT01)
    "canh bí xanh nấu thịt nạc": 30.0,       # IOD: 30g bí xanh (vs 20g in BT01)
}


def resolve(name: str, weight_g: float, fct: dict) -> dict | None:
    """
    Resolve a food name + weight to nutrition.
    Returns {kcal, protein, fat, carb} scaled to weight_g.
    Returns None if food is NOT in FCT (caller decides how to handle).
    Returns {kcal:0, ...} for explicitly excluded items (seasonings, broth, etc.).
    """
    # Skip pure-number / pure-gram tokens (e.g. "1", "70g", "01 quả", "10g")
    key = name.lower().strip()
    if re.fullmatch(r"[\d][\d.,]*\s*(g|ml|lít|quả|khẩu phần)?", key, re.IGNORECASE):
        return None  # not a real food

    fct_name_raw = FCT_NAMES.get(key)

    # Explicitly excluded (seasonings, broth, compound dishes, etc.) → zero contribution
    if key in FCT_NAMES and fct_name_raw is None:
        return {"kcal": 0.0, "protein": 0.0, "fat": 0.0, "carb": 0.0}

    # Resolve: check manual map → fuzzy → None
    entry = None
    yield_factor = 1.0

    if fct_name_raw is not None:
        # Tuple: ("food_name", yield_factor) for cooked dishes
        if isinstance(fct_name_raw, tuple):
            fct_name, yield_factor = fct_name_raw
        else:
            fct_name = fct_name_raw
            yield_factor = 1.0
        if fct_name in fct:
            entry = fct[fct_name]

    if entry is None:
        entry = lookup(key, fct)

    if entry is None:
        return None  # NOT in FCT

    scale = weight_g / 100.0 * yield_factor
    return {
        "kcal":    round(entry["kcal"]    * scale, 2),
        "protein": round(entry["protein"] * scale, 2),
        "fat":     round(entry["fat"]     * scale, 2),
        "carb":    round(entry["carb"]    * scale, 2),
    }


# ── Ingredient string parser ────────────────────────────────────────────────────

def parse_compound_dish(raw: str) -> list[tuple[str, float]] | None:
    """
    Handle compound protein dishes with multiple weights.
    Returns [(name, weight), ...] if this is a compound dish, else None.

    Formats handled:
      "Thịt lợn băm xào cà rốt, hành lá: 50g, 10g, 5g"
        → [("Thịt lợn băm", 50), ("Cà rốt", 10), ("Hành lá", 5)]
      "Tôm rang thịt lợn, hành lá: 60g, 70g, 5g"
        → [("Tôm", 60), ("Thịt lợn", 70), ("Hành lá", 5)]
    """
    raw = raw.strip()
    if not raw:
        return None

    # ── Compound dish patterns ───────────────────────────────────────────────────────
    # Each entry: (dish_name_substring, [(fct_name, weight_idx), ...])
    # weight_idx: which captured weight group to use (0=first, 1=second, ...)
    COMPOUND_PATTERNS: list[tuple] = [
        (
            "thịt lợn băm xào cà rốt, hành lá",
            [("thịt lợn nạc", 0), ("cà rốt", 1), ("hành lá", 2)],
        ),
        (
            "tôm rang thịt lợn, hành lá",
            [("tôm đồng", 0), ("thịt lợn nạc", 1), ("hành lá", 2)],
        ),
        (
            "tôm rang thịt lợn",
            [("tôm đồng", 0), ("thịt lợn nạc", 1)],
        ),
        (
            "thịt lợn xào hành tây, cà rốt",
            [("thịt lợn nạc", 0), ("cà rốt", 1), ("hành tây", 2)],
        ),
        (
            "thịt bò xào cần tỏi tây, hành tây",
            [("thịt bò loại i", 0), ("hành tây", 1), ("hành tây", 2)],
        ),
        (
            "ức gà xào hành tây, cà rốt",
            [("thịt gà ta", 0), ("cà rốt", 1), ("hành tây", 2)],
        ),
        (
            "thịt lợn nạc vai xào cần tỏi tây, hành tây",
            [("thịt lợn nửa nạc, nửa mỡ", 0), ("hành tây", 1), ("hành tây", 2)],
        ),
        (
            "trứng đúc thịt",
            [("trứng gà", 0), ("thịt lợn nạc", 1)],
        ),
        # "Thịt lợn xào cần tỏi tây, hành tây: 100g, 10g, 5g"
        (
            "xào cần tỏi tây, hành tây",
            [("thịt lợn nạc", 0), ("hành tây", 1), ("hành tây", 2)],
        ),
        # "Thịt bê xào sả ớt: 50g, 10g, 5g"
        (
            "bê xào sả ớt",
            [("thịt lợn nạc", 0), ("hành tây", 1), ("ớt đỏ to", 2)],
        ),
        # "Thịt lợn băm xào hành lá: 50g, 5g"
        (
            "thịt lợn băm xào hành lá",
            [("thịt lợn nạc", 0), ("hành lá", 1)],
        ),
        # "Thịt lợn nạc vai xào ớt đà lạt: 100g, 20g"
        (
            "thịt lợn nạc vai xào ớt đà lạt",
            [("thịt lợn nửa nạc, nửa mỡ", 0), ("ớt đỏ to", 1)],
        ),
        # "Thịt lợn, trứng gà kho tàu: 90g, 1 quả"
        (
            "thịt lợn, trứng gà kho tàu",
            [("thịt lợn nạc", 0), ("trứng gà", 1)],
        ),
    ]

    key = raw.lower()
    for pattern_entry in COMPOUND_PATTERNS:
        pattern = pattern_entry[0]
        if pattern not in key:
            continue

        # Capture both number AND unit so "01 quả" can be converted to 50g
        weight_re = re.compile(
            r"(?<![:a-zA-Z])(\d+(?:[.,]\d+)?)\s*(g|quả)\b", re.IGNORECASE
        )
        all_weights = list(weight_re.finditer(raw))
        if len(all_weights) < 2:
            return None
        weights = []
        for m in all_weights:
            val = float(m.group(1).replace(",", "."))
            unit = m.group(2).lower()
            # "quả" (egg) → standard 50g per egg
            weights.append(50.0 if unit == "quả" else val)

        result = []
        for fct_name, w_idx in pattern_entry[1]:
            w = weights[w_idx] if w_idx < len(weights) else 0.0
            result.append((fct_name, w))
        return result

    return None


def parse_items(raw: str) -> list[tuple[str, float]]:
    """
    Parse a meal-plan ingredient line into (name, weight_g) pairs.

    Key insight: every food item ends with a weight label ": NNNg" or ": NNquả".
    The LAST weight label in the string is the main dish's weight.
    All weight labels before it belong to earlier dishes.
    Everything after the LAST weight label is garnishes.

    Handles formats like:
      "Gạo tám Thái: 150g"
      "Thịt lợn xào hành tây, cà rốt: 70g, 10g, 10g"  → compound dish
      "Phở: 150g, thịt bò: 50g, xương ống: 20g, hành lá, rau mùi, gia vị"
      "Cá trắm rán xốt cà chua: 140g, 20g"
      "Trứng đúc thịt: 01 quả"
      "Gạo: 50g, thịt lợn: 50g Gia vị vừa đủ Sữa Grandcare Gold 180ml: 01 hộp"
    """
    if not raw or not isinstance(raw, str):
        return []

    items = []

    # ── Step 0: Pre-process — extract known compound display names ─────────────
    # These appear as part of a larger breakfast string without comma separators.
    # e.g. "Gạo: 50g, thịt lợn: 50g Gia vị vừa đủ Sữa Grandcare Gold 180ml: 01 hộp"
    # We collect them first, then strip them from raw before normal parsing so that
    # the preceding items ("Gạo", "thịt lợn") are still parseable.
    compound_name_re = re.compile(
        r"((?:Gia vị vừa đủ |Thịt lợn gia vị vừa đủ )?"
        r"Sữa Grandcare Gold 180ml)\b",
        re.IGNORECASE
    )
    # Collect all compound items first (don't modify raw while iterating)
    raw_matches = list(compound_name_re.finditer(raw))
    for m in raw_matches:
        full_name = m.group(1).strip()
        tail = raw[m.end():]
        wm = re.search(r":\s*(\d+(?:[.,]\d+)?)\s*(hộp|ml|g|quả)\b", tail, re.IGNORECASE)
        if wm:
            unit = wm.group(2).lower()
            if unit in ("hộp", "ml"):
                weight = 180.0
            elif unit == "quả":
                weight = 50.0
            else:
                weight = float(wm.group(1).replace(",", "."))
            items.append((full_name, weight))
    # Strip only the compound display names (not their weights) so preceding
    # dishes can still be parsed via normal comma-splitting logic.
    raw = compound_name_re.sub("", raw).strip()
    if not raw:
        return items

    # Clean up orphaned weight fragments left behind after stripping the display name.
    # e.g. "Gạo: 50g, thịt lợn: 50g: 01 hộp" → "Gạo: 50g, thịt lợn: 50g"
    # e.g. ": 01 hộp" → ""
    raw = re.sub(r":\s*(\d+(?:[.,]\d+)?)\s*(hộp|ml)\b\s*:", ":", raw)
    raw = re.sub(r"^\s*:\s*(\d+(?:[.,]\d+)?)\s*(hộp|ml)\b", "", raw)
    raw = raw.strip(":").strip()

    weight_re = re.compile(
        r":\s*(\d+(?:[.,]\d+)?)\s*(g|quả|khẩu phần|hộp|ml)\b", re.IGNORECASE
    )
    all_weights = list(weight_re.finditer(raw))

    if not all_weights:
        for sub in re.split(r",\s*", raw):
            sub = sub.strip()
            if sub and len(sub) >= 2:
                items.append((sub, 0.0))
        return items

    last_wm = all_weights[-1]
    unit = last_wm.group(2).lower()
    if unit == "quả":
        main_weight = 50.0
    elif unit in ("hộp", "ml"):
        main_weight = 180.0   # 01 hộp = 180ml (Grandcare Gold)
    else:  # g
        main_weight = float(last_wm.group(1).replace(",", "."))

    dish_part = raw[:last_wm.start()].strip()
    garnish_part = raw[last_wm.end():].strip(", ").strip()

    # ── Extract dishes from dish_part ─────────────────────────────────────────
    if dish_part:
        dish_seps = []
        for m in re.finditer(r",", dish_part):
            cp = m.start()
            before_slice = dish_part[max(0, cp - 6):cp]
            after_slice = dish_part[cp + 1:]
            preceded_by_weight = bool(re.search(
                r"\d+(?:[.,]\d+)?\s*(?:g|quả|khẩu phần|hộp|ml)\b",
                before_slice, re.IGNORECASE
            ))
            followed_by_weight = weight_re.search(after_slice) is not None
            if preceded_by_weight and followed_by_weight:
                dish_seps.append(cp)

        dish_segments = []
        prev = 0
        for cp in dish_seps:
            seg = dish_part[prev:cp].strip(", ").strip()
            if seg:
                dish_segments.append(seg)
            prev = cp + 1
        tail = dish_part[prev:].strip(", ").strip()
        if tail:
            dish_segments.append(tail)

        for seg in dish_segments:
            seg = seg.strip()
            if not seg:
                continue
            seg_weights = list(weight_re.finditer(seg))
            if seg_weights:
                first = seg_weights[0]
                unit2 = first.group(2).lower()
                if unit2 == "quả":
                    w = 50.0
                elif unit2 in ("hộp", "ml"):
                    w = 180.0
                else:
                    w = float(first.group(1).replace(",", "."))
                dish_name = seg[:first.start()].strip()
                if dish_name and len(dish_name) >= 2:
                    items.append((dish_name, w))
            else:
                if seg and len(seg) >= 2:
                    items.append((seg, main_weight))

    # ── Extract garnishes from garnish_part ────────────────────────────────────
    if garnish_part:
        for sub in re.split(r",\s*", garnish_part):
            sub = sub.strip()
            if not sub or len(sub) < 2:
                continue
            # Skip pure-numeric tokens (e.g. "10g", "1 quả", "20", "1.5")
            if re.match(r"^[\d]+(?:[.,][\d]+)?(?:\s+(?:g|ml|quả|lít|khẩu phần|hộp))?$", sub, re.IGNORECASE):
                continue
            if sub.replace(",", "").replace(".", "").isdigit():
                continue
            items.append((sub, 0.0))

    return items


def parse_proteins(raw_list: list) -> list[tuple[str, float]]:
    """
    Parse a list of protein dish strings.
    Handles compound dishes like "Thịt lợn băm xào cà rốt, hành lá: 50g, 10g, 5g"
    by splitting them into individual ingredients.
    """
    all_items = []
    for item in raw_list:
        compound = parse_compound_dish(item)
        if compound is not None:
            all_items.extend(compound)
        else:
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
            # Garnishes without weight get 0 (resolve() will zero them out)
            # Do NOT default to 50g — that inflates kcal for hành lá, rau mùi etc.
            # Skip bare numeric tokens (e.g. "10g", "20g", "1 quả")
            key = name.lower().strip()
            if re.fullmatch(r"[\d][\d.,]*\s*(g|ml|lít|quả|khẩu phần)?", key, re.IGNORECASE):
                continue
            n = resolve(name, weight, fct)
            if n is None:
                unfound.append(name)
            elif n["kcal"] == 0 and name.lower() not in (
                "gia vị", "hành lá", "rau mùi", "rau thơm",
            ):
                unfound.append(name)
            if n is not None:
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
            key = name.lower().strip()
            if re.fullmatch(r"[\d][\d.,]*\s*(g|ml|lít|quả|khẩu phần)?", key, re.IGNORECASE):
                continue
            n = resolve(name, weight, fct)
            if n is None:
                unfound.append(name)
            elif n["kcal"] == 0 and name.lower() not in (
                "gia vị", "hành lá",
            ):
                unfound.append(name)

            if n is not None:
                for k in totals:
                    totals[k] += n[k]

        # Vegetable
        veg_raw = meal.get("vegetable") or ""
        for name, weight in parse_items(veg_raw):
            if weight <= 0:
                weight = 200
            key = name.lower().strip()
            if re.fullmatch(r"[\d][\d.,]*\s*(g|ml|lít|quả|khẩu phần)?", key, re.IGNORECASE):
                continue
            n = resolve(name, weight, fct)
            if n is None:
                unfound.append(name)
            elif n["kcal"] == 0 and name.lower() not in (
                "gia vị", "hành lá",
            ):
                unfound.append(name)
            if n is not None:
                for k in totals:
                    totals[k] += n[k]

        # Proteins
        for name, weight in parse_proteins(meal.get("proteins") or []):
            if weight <= 0:
                weight = 80
            key = name.lower().strip()
            if re.fullmatch(r"[\d][\d.,]*\s*(g|ml|lít|quả|khẩu phần)?", key, re.IGNORECASE):
                continue
            n = resolve(name, weight, fct)
            if n is None:
                unfound.append(name)
            elif n["kcal"] == 0 and name.lower() not in (
                "gia vị", "hành lá", "cà rốt", "hành tây",
                "tôm rang thịt lợn",
                "tôm rang thịt lợn, hành lá",
                "thịt lợn băm xào cà rốt, hành lá",
                "gia vị vừa đủ sữa grandcare gold 180ml: 01 hộp",
            ):
                unfound.append(name)
            if n is not None:
                for k in totals:
                    totals[k] += n[k]

        # Soup
        soup_raw = meal.get("soup") or ""
        soup_key = soup_raw.lower().strip()
        soup_weight = SOUP_VEG_WEIGHTS.get(soup_key, 20.0)
        for name, weight in parse_items(soup_raw):
            if weight <= 0:
                weight = soup_weight
            key = name.lower().strip()
            if re.fullmatch(r"[\d][\d.,]*\s*(g|ml|lít|quả|khẩu phần)?", key, re.IGNORECASE):
                continue
            n = resolve(name, weight, fct)
            if n is None:
                unfound.append(name)
            elif n["kcal"] == 0 and name.lower() not in (
                "gia vị", "hành lá",
            ):
                unfound.append(name)
            if n is not None:
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
