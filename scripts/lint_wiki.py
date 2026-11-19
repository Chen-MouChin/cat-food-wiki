"""Wiki 檢查（lint）：主張格式、編號唯一、原句真的在原文那一頁、主題頁引用的編號存在。

用法：
    python scripts/lint_wiki.py            # 檢查全部
    python scripts/lint_wiki.py --json     # 另外輸出 runs/last_lint.json（給執行紀錄用）
有 FAIL 回傳 1。
"""
import json
import re
import sys
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
WIKI = ROOT / "wiki"
RAW = ROOT / "raw"
SOURCES = json.loads((ROOT / "data" / "sources.json").read_text(encoding="utf-8"))
SOURCES = {k: v for k, v in SOURCES.items() if not k.startswith("_")}

CLAIM_RE = re.compile(r"^- \[(C-[A-Z]+-\d{2})\]\s*(.+?)\s*｜\s*「(.+?)」\s*p\.(\d+)\s*$")
REF_RE = re.compile(r"\[(C-[A-Z]+-\d{2})\]")
MIN_WORDS = 6


def norm(s: str) -> str:
    """比對用：NFKC（ﬁ→fi）、斷行連字號（physi- cal→physical）、引號統一、空白壓成一格、小寫。"""
    s = unicodedata.normalize("NFKC", s)
    s = s.replace("­", "")
    s = re.sub(r"[‘’´`]", "'", s)
    s = re.sub(r"[“”]", '"', s)
    s = re.sub(r"[–—]", "-", s)
    s = re.sub(r"(\w)-\s+(\w)", r"\1\2", s)
    s = re.sub(r"\s+", " ", s)
    return s.strip().lower()


def numbers(s: str) -> list:
    """抓出文字裡的數字（3.5、40–66 會拆成 40 和 66）。頁碼、編號不算。"""
    s = re.sub(r"\[C-[A-Z]+-\d{2}\]", "", s)
    return [n.rstrip(".") for n in re.findall(r"\d+(?:\.\d+)?", s)]


def raw_pages(key: str) -> dict:
    f = RAW / f"{key}.txt"
    if not f.exists():
        return {}
    t = f.read_text(encoding="utf-8")
    return {int(m.group(1)): norm(m.group(2))
            for m in re.finditer(r"=== p\.(\d+) ===\n(.*?)(?==== p\.|\Z)", t, re.S)}


def load_claims():
    """回傳 {claim_id: {...}} 和格式錯誤清單。"""
    claims, errors = {}, []
    for f in sorted((WIKI / "sources").glob("*.md")):
        key = f.stem
        for n, line in enumerate(f.read_text(encoding="utf-8").splitlines(), 1):
            if not line.startswith("- [C-"):
                continue
            m = CLAIM_RE.match(line)
            if not m:
                errors.append(f"wiki/sources/{f.name}:{n} 主張格式不對：{line[:60]}")
                continue
            cid, zh, quote, page = m.groups()
            if cid in claims:
                errors.append(f"{cid} 重複（{claims[cid]['file']} 和 {f.name}）")
            claims[cid] = {"id": cid, "source": key, "zh": zh, "quote": quote,
                           "page": int(page), "file": f.name, "line": n}
    return claims, errors


def run(write_json=False):
    fails, warns = [], []
    claims, errs = load_claims()
    fails += errs

    # 1. 來源頁和 sources.json 對得上
    for f in (WIKI / "sources").glob("*.md"):
        if f.stem not in SOURCES:
            fails.append(f"wiki/sources/{f.name} 不在 data/sources.json")
    for key in SOURCES:
        if not (WIKI / "sources" / f"{key}.md").exists():
            fails.append(f"{key} 在 sources.json，但還沒有 wiki/sources/{key}.md（還沒 ingest）")

    # 2. 原句比對原文
    cache = {}
    verified = 0
    for c in claims.values():
        if len(c["quote"].split()) < MIN_WORDS:
            fails.append(f"{c['id']} 原句太短（少於 {MIN_WORDS} 個字），容易誤配：{c['quote']}")
            continue
        pages = cache.setdefault(c["source"], raw_pages(c["source"]))
        if not pages:
            warns.append(f"{c['id']} 找不到 raw/{c['source']}.txt，無法比對（本機沒有原文）")
            continue
        q = norm(c["quote"])
        if q in pages.get(c["page"], ""):
            verified += 1
            continue
        other = [p for p, t in pages.items() if q in t]
        if other:
            fails.append(f"{c['id']} 原句在 p.{other[0]}，不是 p.{c['page']}")
        else:
            fails.append(f"{c['id']} 原句在 {c['source']} 找不到：「{c['quote'][:70]}」")

    # 2b. 數字一致：中文主張裡的每個數字都要出現在原句裡（2026-11-19 第一次執行後加的：
    #     C-KCAL-04 的原句存在，但抄成表格的別一列，只比對原句存在抓不到）
    for c in claims.values():
        q_nums = {float(n) for n in numbers(c["quote"])}
        missing = sorted({n for n in numbers(c["zh"]) if float(n) not in q_nums}, key=float)
        if missing:
            fails.append(f"{c['id']} 中文主張的數字 {missing} 不在原句裡（原句可能抄錯列，或中文多寫了原文沒有的數字）")

    # 3. 主題頁引用的編號存在；每條主張至少被一個主題頁用到
    used = set()
    for f in sorted((WIKI / "concepts").glob("*.md")):
        for cid in REF_RE.findall(f.read_text(encoding="utf-8")):
            used.add(cid)
            if cid not in claims:
                fails.append(f"wiki/concepts/{f.name} 引用了不存在的 {cid}")
        # 主題頁每一句都要有主張編號；只有導覽句（連到其他 .md）、標題、引言、表格分隔可以沒有
        for n, line in enumerate(f.read_text(encoding="utf-8").splitlines(), 1):
            body = line.strip()
            if not body or body.startswith(("#", ">", "|---", "| 來源", "| 名稱")) or ".md)" in body:
                continue
            for sent in re.split(r"(?<=[。：])", body):
                s = sent.strip(" -0123456789.")
                if len(s) > 8 and not REF_RE.search(sent) and not s.endswith("：") and not s.startswith("|"):
                    fails.append(f"wiki/concepts/{f.name}:{n} 這句沒有主張編號（主題頁不能新增事實）：{s[:40]}")
                if s.startswith("|") and len(s) > 8 and not REF_RE.search(s):
                    fails.append(f"wiki/concepts/{f.name}:{n} 表格這列沒有主張編號：{s[:40]}")
    for cid in claims:
        if cid not in used:
            warns.append(f"{cid} 沒有任何主題頁用到（孤兒主張）")

    # 4. index.md 列出所有頁面
    index = (WIKI / "index.md").read_text(encoding="utf-8") if (WIKI / "index.md").exists() else ""
    for f in list((WIKI / "sources").glob("*.md")) + list((WIKI / "concepts").glob("*.md")):
        if f.name not in index:
            fails.append(f"wiki/index.md 沒有列出 {f.parent.name}/{f.name}")

    for line in fails:
        print("FAIL", line)
    for line in warns:
        print("WARN", line)
    print(f"主張 {len(claims)} 條，原句比對成功 {verified} 條；FAIL {len(fails)}，WARN {len(warns)}")
    if write_json:
        out = ROOT / "runs" / "last_lint.json"
        out.write_text(json.dumps({"claims": len(claims), "verified": verified, "fails": fails, "warns": warns},
                                  ensure_ascii=False, indent=1), encoding="utf-8")
    return len(fails)


if __name__ == "__main__":
    sys.exit(1 if run("--json" in sys.argv) else 0)
