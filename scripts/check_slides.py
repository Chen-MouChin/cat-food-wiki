"""簡報檢查：deck.md 的每一點都要追得到 Wiki 的主張。

規則
  1. 每一點結尾要有 {C-…}；編號要存在於 Wiki。
  2. 每頁只能用 outline.md 那一頁列出的主張（先查 Wiki、再寫簡報）。
  3. 每一點的數字，都要出現在它引用的主張的中文裡（不可以自己算新數字）。
  4. 每頁最多 4 點、每點最多 60 字（不算編號）；標題要有。
  5. 用語：不用「研究顯示」「專家建議」「治療」「毛孩」這類字。
  6. 封面（layout: title）、目錄（layout: agenda）可以沒有主張，但目錄只能列後面各頁的主題。
  7. 小測驗（layout: quiz）：每題 2～4 個選項、恰好 1 個正確、要有解析；正確選項和解析的數字要在解析引用的主張裡。

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
        s = {"title": "", "layout": "", "points": [], "note": "", "quiz": []}
        for line in block.strip().splitlines():
            m = re.match(r"^\s+- (?:\[(x| )\] )?(.*)$", line)
            if m and s["quiz"]:          # 小測驗：題目底下縮排的選項與解析
                if m.group(2).startswith("解析："):
                    s["quiz"][-1]["why"] = m.group(2)[3:].strip()
                elif m.group(1) is not None:
                    s["quiz"][-1]["options"].append((m.group(2).strip(), m.group(1) == "x"))
                continue
            if line.startswith("## "):
                s["title"] = line[3:].strip()
            elif line.startswith("layout:"):
                s["layout"] = line.split(":", 1)[1].strip()
            elif line.startswith("- "):
                s["points"].append(line[2:].strip())
                if s["layout"] == "quiz":
                    s["quiz"].append({"q": line[2:].strip(), "options": [], "why": ""})
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
        if s["layout"] in ("title", "agenda"):   # 封面、目錄沒有新事實
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
        # 小測驗：每題 2～4 個選項、恰好 1 個正確、要有解析；正確選項與解析的數字要在解析引用的主張裡
        # （錯誤選項是誘答，可以有主張以外的數字，但解析要說明正確答案）
        for j, q in enumerate(s.get("quiz", []), 1):
            if not 2 <= len(q["options"]) <= 4:
                fails.append(f"{where} 第 {j} 題有 {len(q['options'])} 個選項，要 2～4 個")
            if sum(1 for _, ok in q["options"] if ok) != 1:
                fails.append(f"{where} 第 {j} 題要恰好 1 個正確選項")
            wrefs = REF.findall(q["why"])
            if not wrefs:
                fails.append(f"{where} 第 {j} 題的解析沒有主張編號")
                continue
            for r in wrefs:
                used.add(r)
                if r not in claims:
                    fails.append(f"{where} 第 {j} 題解析引用了不存在的 {r}")
                elif r not in outline.get(i, set()):
                    fails.append(f"{where} 第 {j} 題解析用了 {r}，但大綱這一頁沒有列")
            allowed = {float(n) for r in wrefs if r in claims for n in numbers(claims[r]["zh"])}
            right = " ".join(t for t, ok in q["options"] if ok)
            extra = [n for n in numbers(REF.sub("", q["why"]) + " " + right) if float(n) not in allowed]
            if extra:
                fails.append(f"{where} 第 {j} 題正確選項或解析的數字 {extra} 不在解析引用的主張裡")
            if len(REF.sub("", q["why"])) > 90:
                fails.append(f"{where} 第 {j} 題解析太長（上限 90 字）")
    # 目錄的每一項，都要對得到後面某一頁的標題關鍵字（避免目錄偷偷加內容）
    titles = " ".join(x["title"] for x in slides)
    for s in slides:
        if s["layout"] == "agenda":
            for p in s["points"]:
                topics = [t for t in re.split(r"[：、，]", p)[1:] if t.strip()]
                for t in topics:
                    key = t.strip()[:2]
                    if key and key not in titles.replace(s["title"], ""):
                        fails.append(f"目錄「{p[:20]}」的「{t.strip()}」對不到任何一頁的標題")
    for line in fails:
        print("FAIL", line)
    print(f"簡報 {len(slides)} 頁，引用 {len(used)} 條主張（Wiki 共 {len(claims)} 條）；FAIL {len(fails)}")
    return len(fails)


if __name__ == "__main__":
    sys.exit(1 if run() else 0)
