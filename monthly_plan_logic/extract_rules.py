# -*- coding: utf-8 -*-
"""Extract text from rules.pdf and save to rules.txt for analysis."""
import sys
from pathlib import Path

import pdfplumber

sys.stdout.reconfigure(encoding="utf-8")

HERE = Path(__file__).parent.resolve()
RULES_PDF = HERE / "data" / "rules.pdf"
OUT_TXT = HERE / "data" / "rules.txt"

with pdfplumber.open(RULES_PDF) as pdf:
    total_pages = len(pdf.pages)
    print(f"Total pages: {total_pages}")

    lines = []
    for i, page in enumerate(pdf.pages):
        txt = page.extract_text() or ""
        if txt.strip():
            lines.append(f"\n{'='*60}")
            lines.append(f"PAGE {i + 1}")
            lines.append(f"{'='*60}")
            lines.append(txt)

    full_text = "\n".join(lines)

with open(OUT_TXT, "w", encoding="utf-8") as f:
    f.write(full_text)

print(f"Wrote {len(full_text)} chars to {OUT_TXT}")
print(f"Pages with text: {sum(1 for p in pdf.pages if p.extract_text())}")
