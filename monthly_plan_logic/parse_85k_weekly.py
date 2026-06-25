# -*- coding: utf-8 -*-
"""Extract the EXACT weekly meal plan from the 85k hospital monthly menu PDF.

The PDF (19 pages) holds two kinds of content:
  * pages 0..10  -> 11 weekly "cơm" (rice) menus, one per diet group, each a
                    fixed 13-row x 8-col grid (this script's target).
  * pages 11..18 -> supplementary cháo / OT (liquid / tube-feed) menus.

Each weekly grid is laid out as:
  row 0  header (Giờ | Thứ 2 .. Chủ nhật)
  row 1  breakfast name        (6h)
  row 2  breakfast detail / ingredients
  row 3  lunch  - rice         (11h)
  row 4  lunch  - vegetable
  row 5  lunch  - protein 1
  row 6  lunch  - protein 2 (cell may stack several dishes)
  row 7  lunch  - soup
  row 8  dinner - rice         (17h)
  row 9  dinner - vegetable
  row 10 dinner - protein 1
  row 11 dinner - protein 2
  row 12 dinner - soup
Columns 1..7 = Mon..Sun.

Outputs (written to the data/ subdirectory next to this script):
  data/weekly_meal_plan_85k.json  - full nested structure, weights preserved
  data/weekly_meal_plan_85k.csv   - one row per dish component (flat)
"""
import json
import os
import re
from pathlib import Path

import pdfplumber
import pypdf
from dotenv import load_dotenv

# Load .env from this script's directory
HERE = Path(__file__).parent.resolve()
DATA_DIR = HERE / "data"
DATA_DIR.mkdir(exist_ok=True)
load_dotenv(HERE / ".env")

# Auto-discover the meal-plan PDF in data/ (ignore rules.pdf / auxiliary files).
_pdf_candidates = [
    f for f in DATA_DIR.glob("*.pdf")
    if f.stem.lower() != "rules" and f.suffix.lower() == ".pdf"
]
if not _pdf_candidates:
    raise RuntimeError(
        f"No PDF found in {DATA_DIR}. "
        "Place the 85k meal plan PDF there."
    )
if len(_pdf_candidates) > 1:
    # Pick the one whose name contains "85k" or is largest
    _by_85k = [f for f in _pdf_candidates if "85k" in f.stem.lower()]
    PDF = _by_85k[0] if _by_85k else max(_pdf_candidates, key=lambda f: f.stat().st_size)
    print(f"Multiple PDFs found in {DATA_DIR}, using: {PDF.name}")
else:
    PDF = _pdf_candidates[0]

N_GRID_PAGES = 11

DAY_KEYS = ['mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun']
DAY_LABELS = ['Thứ 2', 'Thứ 3', 'Thứ 4', 'Thứ 5', 'Thứ 6', 'Thứ 7', 'Chủ nhật']

# Vietnamese hospital-dietetics diet-group abbreviations -> human label.
GROUP_LABELS = {
    'BT': 'Cơm thông thường (chuẩn)',
    'PT': 'Phẫu thuật / bệnh lý chung',
    'SẢN': 'Sản khoa',
    'TN': 'Bệnh thận',
    'TM': 'Tim mạch',
    'TH': 'Tăng huyết áp',
    'ĐĐ': 'Đái tháo đường',
    'GM': 'Gan mật',
    'UT': 'Ung thư',
    'GU': 'Gút',
    'IOD': 'Kiêng i-ốt (tuyến giáp)',
    'NGƯỜI': 'Người nhà người bệnh',
}


def cell_lines(cell):
    """Return cleaned, non-empty lines of a table cell."""
    if not cell:
        return []
    return [re.sub(r'\s+', ' ', ln).strip()
            for ln in cell.split('\n') if ln.strip()]


def is_continuation(line):
    """A wrapped line continues the previous dish if it starts lowercase/digit."""
    if not line:
        return True
    c = line[0]
    return c.isdigit() or c.islower()


def split_dishes(lines):
    """Merge wrapped continuation lines; split distinct dishes (uppercase start)."""
    dishes = []
    for ln in lines:
        if not dishes or not is_continuation(ln):
            dishes.append(ln)
        else:
            dishes[-1] += ' ' + ln
    return [re.sub(r'\s+', ' ', d).strip() for d in dishes if d.strip()]


def one_dish(lines):
    return ' '.join(split_dishes(lines)) or None


def split_name_portion(dish):
    """Split 'Cá trắm rán xốt cà chua: 140g, 20g' -> (name, portion)."""
    if not dish:
        return None, None
    parts = dish.split(':', 1)
    name = parts[0].strip()
    portion = parts[1].strip() if len(parts) > 1 else None
    return name, portion


def parse_meal(rows, ci, rice_i):
    """Parse a lunch/dinner block (5 stacked rows) for column ci."""
    rice = one_dish(cell_lines(rows[rice_i][ci]))
    veg = one_dish(cell_lines(rows[rice_i + 1][ci]))
    prot_lines = cell_lines(rows[rice_i + 2][ci]) + cell_lines(rows[rice_i + 3][ci])
    proteins = split_dishes(prot_lines)
    soup = one_dish(cell_lines(rows[rice_i + 4][ci]))
    return {'rice': rice, 'vegetable': veg, 'proteins': proteins, 'soup': soup}


def page_meta(reader, i):
    """Pull diet code / kcal / P:L:G from the raw page text."""
    txt = reader.pages[i].extract_text() or ''
    code = kcal = plg_g = plg_pct = note = meal_cost = None

    m = re.search(r'MÃ:\s*(.+?)\s*Mức ăn', txt)
    if m:
        code = re.sub(r'\s+', ' ', m.group(1)).strip()
        nm = re.search(r'\((.*?)\)', code)
        if nm:
            note = nm.group(1)
        dm = re.search(r'-\s*(không ăn[^\n]*)', code)
        if dm:
            note = dm.group(1).strip()

    m = re.search(r'Mức ăn:\s*([\d\.]+đ)', txt)
    if m:
        meal_cost = m.group(1)
    m = re.search(r'NL:\s*(\d+)\s*kcal', txt)
    if m:
        kcal = int(m.group(1))
    m = re.search(r'P:L:G \(g\):\s*([^\n]+)', txt)
    if m:
        plg_g = re.sub(r'\s+', ' ', m.group(1)).strip()
    m = re.search(r'P:L:G \(%\):\s*([^\n]+)', txt)
    if m:
        plg_pct = re.sub(r'\s+', ' ', m.group(1)).strip()
    return code, meal_cost, kcal, plg_g, plg_pct, note


def label_for(code):
    if not code:
        return None
    key = code.split('-')[0].split(',')[0].strip().split()[0].upper()
    for k, v in GROUP_LABELS.items():
        if key.startswith(k):
            return v
    for k, v in GROUP_LABELS.items():
        if k in code.upper():
            return v
    return code


def clean_codes(code):
    """Split a 'MÃ:' string into individual clean diet codes.

    Strip the trailing dietary note (e.g. '- không ăn rau cải, trứng, đậu phụ')
    BEFORE splitting on commas, so note fragments aren't mistaken for codes.
    """
    code = re.sub(r'\(.*?\)', '', code or '')
    code = re.sub(r'-\s*không ăn.*$', '', code)
    out = []
    for c in code.split(','):
        c = c.strip()
        if c:
            out.append(c)
    return out


def build():
    reader = pypdf.PdfReader(PDF)
    pdf = pdfplumber.open(PDF)

    groups = []
    for i in range(N_GRID_PAGES):
        rows = pdf.pages[i].extract_tables()[0]
        code, meal_cost, kcal, plg_g, plg_pct, note = page_meta(reader, i)
        days = []
        for di in range(7):
            ci = di + 1
            bname = one_dish(cell_lines(rows[1][ci]))
            bdetail = ' '.join(cell_lines(rows[2][ci])).strip() or None
            days.append({
                'key': DAY_KEYS[di],
                'label': DAY_LABELS[di],
                'breakfast': ({'name': bname, 'detail': bdetail}
                              if bname else None),
                'lunch': parse_meal(rows, ci, 3),
                'dinner': parse_meal(rows, ci, 8),
            })
        groups.append({
            'page': i + 1,
            'code': code,
            'codes': clean_codes(code),
            'label': label_for(code),
            'note': note,
            'mealCost': meal_cost,
            'kcal': kcal,
            'plgG': plg_g,
            'plgPct': plg_pct,
            'isBase': i == 0,
            'days': days,
        })

    return {
        'source': PDF.name,
        'title': 'Thực đơn cơm thông thường và bệnh lý tháng 5 năm 2026',
        'month': 'Tháng 05/2026',
        'mealLevel': '85.680đ',
        'gridPages': N_GRID_PAGES,
        'note': ('Pages 12-19 of the PDF contain supplementary cháo/OT '
                 '(liquid/tube-feed) menus, not part of this weekly grid extract.'),
        'groups': groups,
    }


def write_json(data, path):
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def write_csv(data, path):
    import csv
    cols = ['page', 'diet_code', 'diet_codes', 'diet_label', 'note',
            'meal_cost', 'group_kcal', 'group_plg_g', 'group_plg_pct',
            'day_key', 'day_label', 'meal', 'meal_time', 'slot',
            'item_index', 'dish_full', 'dish_name', 'portion']
    meal_time = {'breakfast': '6h', 'lunch': '11h', 'dinner': '17h'}
    with open(path, 'w', encoding='utf-8-sig', newline='') as f:
        w = csv.writer(f)
        w.writerow(cols)
        for g in data['groups']:
            base = [g['page'], g['code'], '; '.join(g['codes']), g['label'],
                    g['note'], g['mealCost'], g['kcal'], g['plgG'], g['plgPct']]
            for d in g['days']:
                def emit(meal, slot, idx, dish):
                    name, portion = split_name_portion(dish)
                    w.writerow(base + [d['key'], d['label'], meal,
                                       meal_time[meal], slot, idx,
                                       dish, name, portion])

                bf = d['breakfast']
                if bf:
                    name = bf['name']
                    detail = bf['detail']
                    full = f"{name}: {detail}" if detail else name
                    w.writerow(base + [d['key'], d['label'], 'breakfast',
                                       '6h', 'main', 1, full, name, detail])
                for meal in ('lunch', 'dinner'):
                    m = d[meal]
                    if not m:
                        continue
                    if m['rice']:
                        emit(meal, 'rice', 1, m['rice'])
                    if m['vegetable']:
                        emit(meal, 'vegetable', 1, m['vegetable'])
                    for k, p in enumerate(m['proteins'], 1):
                        emit(meal, 'protein', k, p)
                    if m['soup']:
                        emit(meal, 'soup', 1, m['soup'])


def main():
    if not PDF.exists():
        raise FileNotFoundError(
            f"PDF not found at: {PDF}\n"
            "Check PDF_PATH in .env and make sure the file exists."
        )

    data = build()
    jpath = DATA_DIR / "weekly_meal_plan_85k.json"
    cpath = DATA_DIR / "weekly_meal_plan_85k.csv"
    write_json(data, jpath)
    write_csv(data, cpath)

    n_groups = len(data['groups'])
    n_dishes = 0
    for g in data['groups']:
        for d in g['days']:
            if d['breakfast']:
                n_dishes += 1
            for meal in ('lunch', 'dinner'):
                m = d[meal]
                if not m:
                    continue
                n_dishes += sum(bool(m[s]) for s in ('rice', 'vegetable', 'soup'))
                n_dishes += len(m['proteins'])
    print(f'groups: {n_groups}  dish-rows: {n_dishes}')
    print('wrote', jpath)
    print('wrote', cpath)


if __name__ == '__main__':
    main()
