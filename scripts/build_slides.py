"""產出簡報：slides/deck.md → docs/index.html（單一 HTML，GitHub Pages 發佈）。

先跑 lint_wiki 和 check_slides，有 FAIL 就不產出。每頁底部列出引用的主張（編號、來源、頁碼），
點了連到 GitHub 上的 Wiki 來源頁。最後自動加上「出處」和「這份簡報怎麼做出來的」兩頁。

用法：python scripts/build_slides.py
"""
import html
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import check_slides  # noqa: E402
import lint_wiki  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
DOCS = ROOT / "docs"
REPO = "https://github.com/Chen-MouChin/cat-food-wiki/blob/main"
CATS = ["sitting", "mochi-lying", "head-tilt", "eating", "kitten", "box", "playing", "sleeping", "carrier"]


def wrap(text: str) -> str:
    """標題只在標點後面換行：每一段包成 inline-block（沿用 HW9 的作法）。"""
    parts = re.findall(r"[^，、：；？]+[，、：；？]?", text)
    return "".join(f'<span class="nb">{html.escape(x)}</span>' for x in parts)


def cat_svg(name: str) -> str:
    svg = (ROOT / "assets" / "cats" / f"{name}.svg").read_text(encoding="utf-8")
    return svg.replace("<svg ", '<svg class="cat" aria-hidden="true" ', 1)


def slide_html(i: int, s: dict, claims: dict, sources: dict) -> str:
    refs = []
    items = []
    for p in s["points"]:
        ids = check_slides.REF.findall(p)
        text = html.escape(check_slides.REF.sub("", p).strip())
        chips = "".join(f'<sup class="ref">{c}</sup>' for c in ids)
        items.append(f"<li>{text}{chips}</li>")
        refs += [c for c in ids if c not in refs]
    foot = "".join(
        f'<a href="{REPO}/wiki/sources/{claims[c]["source"]}.md" target="_blank" rel="noopener">'
        f'{c}｜{html.escape(sources[claims[c]["source"]]["short"])} p.{claims[c]["page"]}</a>'
        for c in refs if c in claims)
    note = f'<aside class="note">{html.escape(s["note"])}</aside>' if s["note"] else ""
    if s["layout"] == "title":
        return (f'<section class="slide title-slide" data-i="{i}">{cat_svg("mochi-lying")}'
                f'<h1>{wrap(s["title"])}</h1>'
                f'<ul class="sub">{"".join(items)}</ul>{note}'
                f'<p class="hint">← → 換頁　N 講者備註</p></section>')
    cat = cat_svg(CATS[i % len(CATS)])
    return (f'<section class="slide" data-i="{i}"><header><span class="num">{i}</span>'
            f'<h2>{wrap(s["title"])}</h2>{cat}</header>'
            f'<ul class="points">{"".join(items)}</ul>'
            f'<footer class="refs"><span>依據 Wiki：</span>{foot}</footer>{note}</section>')


def appendix(start: int, sources: dict, n_claims: int, n_used: int) -> str:
    rows = "".join(
        f'<li><b>{html.escape(v["short"])}</b>　{html.escape(v["authors"])}（{v["year"]}）. '
        f'<a href="{html.escape(v["url"])}" target="_blank" rel="noopener">{html.escape(v["title"])}</a></li>'
        for v in sources.values())
    src = (f'<section class="slide" data-i="{start}"><header><span class="num">{start}</span>'
           f'<h2>出處：9 份來源</h2></header><ol class="sources">{rows}</ol></section>')
    flow = ["討論範圍", "取得原文", "抽成逐頁文字", "Ingest 寫主張", "Wiki 檢查", "整理主題頁",
            "查 Wiki 排大綱", "生成簡報", "簡報檢查", "獨立審查", "產出 HTML"]
    chips = "".join(f'<span class="node">{html.escape(x)}</span>' for x in flow)
    meta = (f'<section class="slide" data-i="{start + 1}"><header><span class="num">{start + 1}</span>'
            f'<h2>這份簡報怎麼做出來的</h2></header><div class="flow">{chips}</div>'
            f'<ul class="points"><li>Wiki 有 {n_claims} 條主張，每條附英文原句與頁碼，程式回原文逐條比對</li>'
            f'<li>這份簡報引用其中 {n_used} 條；每一點都標了編號，數字必須出現在引用的主張裡</li>'
            f'<li>檢查沒過就退回重寫那一條或那一頁，紀錄在 Wiki 的 log.md</li></ul>'
            f'<footer class="refs"><a href="https://github.com/Chen-MouChin/cat-food-wiki" target="_blank" rel="noopener">'
            f'Wiki 與流程：github.com/Chen-MouChin/cat-food-wiki</a></footer></section>')
    return src + meta


CSS = """
:root{--bg:#f9f6f0;--card:#fff;--text:#1d1d1f;--text2:#4a4a4c;--muted:#636368;--primary:#3b6a50;--deep:#2a4c39;
--pale:#e7efe9;--gold:#b8860b;--border:#e8e4db;--cat-white:#f9fbf9;--cat-blush:#f2d6d0;--cat-ink:#1d1d1f;color-scheme:light}
*{box-sizing:border-box}html,body{margin:0;height:100%;background:var(--bg);color:var(--text);
font-family:"Noto Sans TC","PingFang TC","Microsoft JhengHei",system-ui,sans-serif}
.deck{position:relative;height:100%;overflow:hidden}
.slide{position:absolute;inset:0;display:none;flex-direction:column;padding:clamp(20px,5vw,64px) clamp(20px,7vw,110px) 90px;overflow-y:auto}
.slide.on{display:flex}
header{display:flex;align-items:center;gap:16px;margin-bottom:clamp(16px,3vh,32px)}
.num{flex:none;width:44px;height:44px;border-radius:50%;background:var(--pale);color:var(--deep);display:grid;place-items:center;font-weight:700}
h1{font-size:clamp(28px,5.4vw,56px);margin:.2em 0;text-align:center;text-wrap:balance}
h2{font-size:clamp(22px,3.6vw,40px);margin:0;flex:1;line-height:1.3;text-wrap:balance}
.cat{width:clamp(56px,8vw,96px);height:auto;flex:none;color:var(--cat-ink)}
.points{list-style:none;padding:0;margin:0;display:grid;gap:clamp(10px,2vh,18px);max-width:1100px}
.points li{background:var(--card);border:1px solid var(--border);border-left:5px solid var(--primary);border-radius:14px;
padding:clamp(12px,2vh,20px) 20px;font-size:clamp(17px,2.2vw,26px);line-height:1.55}
.ref{font-size:.5em;color:var(--primary);margin-left:6px;vertical-align:super;font-weight:700;white-space:nowrap}
.refs{position:absolute;left:clamp(20px,7vw,110px);right:clamp(20px,7vw,110px);bottom:46px;display:flex;flex-wrap:wrap;gap:6px 12px;font-size:13px;color:var(--muted)}
.refs a{color:var(--deep);text-decoration:none;background:var(--pale);padding:2px 8px;border-radius:999px}
.title-slide{align-items:center;justify-content:center;text-align:center}
.title-slide .cat{width:clamp(120px,18vw,200px)}
.sub{list-style:none;padding:0;font-size:clamp(16px,2vw,22px);color:var(--text2);line-height:1.7}
.hint{color:var(--muted);font-size:14px;margin-top:24px}
.sources{font-size:clamp(14px,1.6vw,18px);line-height:1.6;max-width:1100px;padding-left:1.3em}
.sources a{color:var(--deep)}
.flow{display:flex;flex-wrap:wrap;gap:8px;margin-bottom:22px}
.node{background:var(--card);border:1px solid var(--primary);color:var(--deep);border-radius:999px;padding:6px 14px;font-size:clamp(13px,1.5vw,17px)}
.node:not(:last-child)::after{content:" →";color:var(--gold)}
.nb{display:inline-block;max-width:100%}
.note{display:none;margin-top:18px;padding:12px 16px;border-radius:12px;background:#f6ecd2;color:var(--text2);font-size:15px;max-width:1100px}
.show-notes .note{display:block}
nav{position:fixed;left:0;right:0;bottom:0;height:40px;display:flex;align-items:center;justify-content:center;gap:16px;background:rgba(249,246,240,.92);border-top:1px solid var(--border);z-index:5}
nav button{border:1px solid var(--primary);background:var(--card);color:var(--deep);border-radius:999px;min-width:44px;height:30px;font-size:16px;cursor:pointer}
.bar{position:fixed;left:0;top:0;height:4px;background:var(--primary);transition:width .2s;z-index:6}
@media (max-width:640px){.points li{border-left-width:4px}.refs{position:static;margin-top:18px}.slide{padding-bottom:60px}}
@media print{.slide{display:flex!important;position:relative;page-break-after:always;height:100vh}nav,.bar{display:none}}
"""

JS = """
const S=[...document.querySelectorAll('.slide')],bar=document.querySelector('.bar'),cnt=document.querySelector('.cnt');
let i=Math.max(0,Math.min(S.length-1,(parseInt(location.hash.slice(1))||1)-1));
function go(n){i=Math.max(0,Math.min(S.length-1,n));S.forEach((s,k)=>s.classList.toggle('on',k===i));
bar.style.width=((i+1)/S.length*100)+'%';cnt.textContent=(i+1)+' / '+S.length;history.replaceState(null,'','#'+(i+1));}
document.addEventListener('keydown',e=>{if(['ArrowRight','PageDown',' '].includes(e.key)){e.preventDefault();go(i+1)}
else if(['ArrowLeft','PageUp'].includes(e.key)){e.preventDefault();go(i-1)}else if(e.key==='n'||e.key==='N'){document.body.classList.toggle('show-notes')}});
document.querySelector('.prev').onclick=()=>go(i-1);document.querySelector('.next').onclick=()=>go(i+1);
let x0=null;document.addEventListener('touchstart',e=>{x0=e.touches[0].clientX},{passive:true});
document.addEventListener('touchend',e=>{if(x0===null)return;const dx=e.changedTouches[0].clientX-x0;if(Math.abs(dx)>50)go(i+(dx<0?1:-1));x0=null});
go(i);
"""


def main():
    print("== lint_wiki"); f1 = lint_wiki.run()
    print("== check_slides"); f2 = check_slides.run()
    if f1 or f2:
        print("產出中止：先修好上面的 FAIL")
        return 1
    claims, _ = lint_wiki.load_claims()
    sources = lint_wiki.SOURCES
    slides = check_slides.parse_deck((ROOT / "slides" / "deck.md").read_text(encoding="utf-8"))
    used = {r for s in slides for p in s["points"] for r in check_slides.REF.findall(p)}
    body = "".join(slide_html(i, s, claims, sources) for i, s in enumerate(slides, 1))
    body += appendix(len(slides) + 1, sources, len(claims), len(used))
    page = f"""<!doctype html>
<html lang="zh-Hant-TW"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>看懂貓糧：怎麼選、怎麼餵</title>
<meta name="description" content="用貓糧 LLM Wiki 做的教學簡報：完整均衡、看懂標籤、乾物換算、碳水、熱量與體態、怎麼餵。">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Noto+Sans+TC:wght@400;500;700&display=swap" rel="stylesheet">
<style>{CSS}</style></head>
<body><div class="bar"></div><main class="deck">{body}</main>
<nav><button class="prev" aria-label="上一頁">←</button><span class="cnt"></span><button class="next" aria-label="下一頁">→</button></nav>
<script>{JS}</script></body></html>"""
    DOCS.mkdir(exist_ok=True)
    (DOCS / "index.html").write_text(page, encoding="utf-8")
    (DOCS / ".nojekyll").write_text("", encoding="utf-8")
    print(f"完成：docs/index.html，{len(slides) + 2} 頁（含出處、流程兩頁附錄），引用 {len(used)} 條主張")
    return 0


if __name__ == "__main__":
    sys.exit(main())
