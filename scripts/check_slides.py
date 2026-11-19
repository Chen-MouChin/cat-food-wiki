"""簡報檢查：deck.md 的每一點都要追得到 Wiki 的主張。

規則
  1. 每一點結尾要有 {C-…}；編號要存在於 Wiki。
  2. 每頁只能用 outline.md 那一頁列出的主張（先查 Wiki、再寫簡報）。
  3. 每一點的數字，都要出現在它引用的主張的中文裡（不可以自己算新數字）。
  4. 每頁最多 4 點、每點最多 60 字（不算編號）；標題要有。
  5. 用語：不用「研究顯示」「專家建議」「治療」「毛孩」這類字。
  6. 封面（layout: title）可以沒有主張。

用法：python scripts/check_slides.py   有 FAIL 回傳 1
"""
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from lint_wiki import load_claims, numbers  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
DECK = ROOT / "slides" / "deck.md"
OUTLINE = ROOT / "slides" / "outline.md"
REF = re.compile(r"\{(C-[A-Z]+-\d{2})\}")
BANNED = ["研究顯示", "專家建議", "治療", "毛孩", "主子", "醫療級"]
MAX_POINTS, MAX_CHARS = 4, 60


def parse_deck(text: str) -> list:
    slides = []
    for block in re.split(r"^---\s*$", text, flags=re.M):
        s = {"title": "", "layout": "", "points": [], "note": ""}
        for line in block.strip().splitlines():
            if line.startswith("## "):
                s["title"] = line[3:].strip()
            elif line.startswith("layout:"):
                s["layout"] = line.split(":", 1)[1].strip()
            elif line.startswith("- "):
                s["points"].append(line[2:].strip())
            elif line.startswith("note:"):
                s["note"] = line.split(":", 1)[1].strip()
        if s["title"]:
            slides.append(s)
    return slides


def parse_outline(text: str) -> dict:
    out = {}
    for m in re.finditer(r"^\|\s*(\d+)\s*\|[^|]*\|[^|]*\|([^|]*)\|", text, re.M):
        out[int(m.group(1))] = set(re.findall(r"C-[A-Z]+-\d{2}", m.group(2)))
    return out


def run():
    claims, _ = load_claims()
    slides = parse_deck(DECK.read_text(encoding="utf-8"))
    outline = parse_outline(OUTLINE.read_text(encoding="utf-8"))
    fails = []
    used = set()
    for i, s in enumerate(slides, 1):
        where = f"第 {i} 頁「{s['title'][:14]}」"
        if i not in outline:
            fails.append(f"{where} 不在 outline.md（先查 Wiki 寫大綱，再寫簡報）")
        if s["layout"] == "title":
            continue
        slide_refs = {r for p in s["points"] for r in REF.findall(p)}
        allowed_t = {float(n) for r in slide_refs if r in claims for n in numbers(claims[r]["zh"])}
        extra_t = [n for n in numbers(s["title"]) if float(n) not in allowed_t]
        if extra_t:
            fails.append(f"{where} 標題的數字 {extra_t} 不在這頁引用的主張裡")
        if len(s["points"]) > MAX_POINTS:
            fails.append(f"{where} 有 {len(s['points'])} 點，上限 {MAX_POINTS}")
        for j, p in enumerate(s["points"], 1):
            refs = REF.findall(p)
            text = REF.sub("", p).strip()
            if not refs:
                fails.append(f"{where} 第 {j} 點沒有主張編號：{text[:30]}")
                continue
            if len(text) > MAX_CHARS:
                fails.append(f"{where} 第 {j} 點 {len(text)} 字，上限 {MAX_CHARS}：{text[:30]}")
            for r in refs:
                used.add(r)
                if r not in claims:
                    fails.append(f"{where} 第 {j} 點引用了不存在的 {r}")
                elif r not in outline.get(i, set()):
                    fails.append(f"{where} 第 {j} 點用了 {r}，但大綱這一頁沒有列（要先查 Wiki、更新大綱）")
            allowed = {float(n) for r in refs if r in claims for n in numbers(claims[r]["zh"])}
            extra = [n for n in numbers(text) if float(n) not in allowed]
            if extra:
                fails.append(f"{where} 第 {j} 點的數字 {extra} 不在引用的主張裡（Wiki 沒有的數字不能寫）")
            for b in BANNED:
                if b in text:
                    fails.append(f"{where} 第 {j} 點用了「{b}」")
    for line in fails:
        print("FAIL", line)
    print(f"簡報 {len(slides)} 頁，引用 {len(used)} 條主張（Wiki 共 {len(claims)} 條）；FAIL {len(fails)}")
    return len(fails)


if __name__ == "__main__":
    sys.exit(1 if run() else 0)
