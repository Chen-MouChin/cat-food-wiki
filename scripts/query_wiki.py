"""查 Wiki：用關鍵字找主張（比對中文主張和英文原句），列出編號、中文、來源。

用法：
    python scripts/query_wiki.py 乾物 罐頭          # 任一關鍵字符合就列出
    python scripts/query_wiki.py --all 熱量 體重    # 全部關鍵字都要符合
大綱（slides/outline.md）的每一頁都要記下查了什麼、用了哪些編號。
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from lint_wiki import load_claims, SOURCES  # noqa: E402


def query(words, need_all=False):
    claims, _ = load_claims()
    hits = []
    for c in claims.values():
        text = (c["zh"] + " " + c["quote"]).lower()
        ok = [w.lower() in text for w in words]
        if (all(ok) if need_all else any(ok)):
            hits.append(c)
    return hits


def main():
    args = [a for a in sys.argv[1:] if a != "--all"]
    hits = query(args, "--all" in sys.argv)
    for c in hits:
        print(f"[{c['id']}] {c['zh']}（{SOURCES[c['source']]['short']} p.{c['page']}）")
    print(f"共 {len(hits)} 條")


if __name__ == "__main__":
    main()
