"""ingest 第一步：raw/*.pdf → raw/*.txt（逐頁標記 === p.N ===）。

頁碼用 PDF 的實體頁序（第 1 頁 = p.1），Wiki 引用寫 [^KEY p.N]，lint_wiki.py 用這個頁碼回頭比對原文。
raw/ 不進 git（原文有著作權），重建方式：下載 data/sources.json 的 url 存成 raw/<KEY>.pdf，再跑本程式。

用法：python scripts/extract.py
"""
import sys
from pathlib import Path

import fitz  # PyMuPDF

RAW = Path(__file__).resolve().parent.parent / "raw"


def main():
    for pdf in sorted(RAW.glob("*.pdf")):
        out = pdf.with_suffix(".txt")
        if out.exists() and out.stat().st_mtime > pdf.stat().st_mtime:
            print(f"已有，跳過：{out.name}")
            continue
        doc = fitz.open(pdf)
        parts = [f"=== p.{i} ===\n{page.get_text()}" for i, page in enumerate(doc, 1)]
        out.write_text("\n".join(parts), encoding="utf-8")
        chars = sum(len(p) for p in parts)
        print(f"{pdf.stem}: {len(doc)} 頁, {chars} 字元")


if __name__ == "__main__":
    sys.exit(main())
