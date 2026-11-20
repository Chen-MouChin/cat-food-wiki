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
    for q in s.get("quiz", []):
        refs += [c for c in check_slides.REF.findall(q["why"]) if c not in refs]
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
    if s["layout"] == "quiz":
        return (f'<section class="slide" data-i="{i}"><header><span class="num">{i}</span>'
                f'<h2>{wrap(s["title"])}</h2>{cat}</header>'
                f'<div class="quiz">{"".join(quiz_card(k, q) for k, q in enumerate(s["quiz"], 1))}</div>'
                f'<footer class="refs"><span>依據 Wiki：</span>{foot}</footer>{note}</section>')
    foot_html = f'<footer class="refs"><span>依據 Wiki：</span>{foot}</footer>' if foot else ""
    return (f'<section class="slide" data-i="{i}"><header><span class="num">{i}</span>'
            f'<h2>{wrap(s["title"])}</h2>{cat}</header>'
            f'<ul class="points">{"".join(items)}</ul>'
            f'{foot_html}{note}</section>')


def quiz_card(k: int, q: dict) -> str:
    """小測驗的一題：正面是題目和選項，點了翻到背面，顯示答對或答錯、正確答案和解析。"""
    strip = lambda t: html.escape(check_slides.REF.sub("", t).strip())
    sup = lambda t: "".join(f'<sup class="ref">{c}</sup>' for c in check_slides.REF.findall(t))
    opts = "".join(f'<button type="button" class="opt" data-ok="{int(ok)}">{chr(64 + n)}. {html.escape(t)}</button>'
                   for n, (t, ok) in enumerate(q["options"], 1))
    right = next(f"{chr(64 + n)}. {html.escape(t)}" for n, (t, ok) in enumerate(q["options"], 1) if ok)
    return (f'<div class="qcard"><div class="qinner">'
            f'<div class="qface qfront"><p class="qtext"><b>第 {k} 題</b>　{strip(q["q"])}{sup(q["q"])}</p>'
            f'<div class="opts">{opts}</div></div>'
            f'<div class="qface qback" aria-live="polite"><p class="verdict"></p>'
            f'<p class="answer">正確答案：{right}</p><p class="why">{strip(q["why"])}{sup(q["why"])}</p>'
            f'<button type="button" class="again">再答一次</button></div></div></div>')


def appendix(start: int, sources: dict, n_claims: int, n_used: int) -> str:
    rows = "".join(
        f'<li><b>{html.escape(v["short"])}</b>　{html.escape(v["authors"])}（{v["year"]}）. '
        f'<a href="{html.escape(v["url"])}" target="_blank" rel="noopener">{html.escape(v["title"])}</a></li>'
        for v in sources.values())
    src = (f'<section class="slide" data-i="{start}"><header><span class="num">{start}</span>'
           f'<h2>出處：9 份來源</h2></header><ol class="sources">{rows}</ol></section>')
    import run_graph
    kinds = {"auto": "a", "human": "h", "agent": ""}
    flow = [(name, kinds[kind]) for name, kind in run_graph.NODES.values()]
    chips = "".join(f'<span class="node {k}">{html.escape(x)}</span>' for x, k in flow)
    meta = (f'<section class="slide" data-i="{start + 1}"><header><span class="num">{start + 1}</span>'
            f'<h2>這份簡報怎麼做出來的</h2></header><div class="flow">{chips}</div>'
            f'<ul class="points"><li>Wiki 有 {n_claims} 條主張，每條附英文原句與頁碼，程式回原文逐條比對</li>'
            f'<li>這份簡報引用其中 {n_used} 條；每一點都標了編號，數字必須出現在引用的主張裡</li>'
            f'<li>綠底由程式自動執行（抽文字、檢查、產出、截圖），白底由 AI 執行，黃底是人工關卡（開始前審核流程框架、發佈前審核成果）</li>'
            f'<li>檢查沒過就照圖退回，每條線最多 3 次；每一步記在 wiki/log.md 和 runs/</li></ul>'
            f'<footer class="refs"><a href="https://github.com/Chen-MouChin/cat-food-wiki" target="_blank" rel="noopener">'
            f'Wiki 與流程：github.com/Chen-MouChin/cat-food-wiki</a>'
            f'<a href="graph.html" target="_blank" rel="noopener">完整流程圖（含退回條件）</a></footer></section>')
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
.refs{margin-top:auto;padding-top:14px;display:flex;flex-wrap:wrap;gap:6px 12px;font-size:13px;color:var(--muted)}
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
.node.a{background:var(--pale)}.node.h{background:#f6ecd2;border-color:var(--gold)}
.nb{display:inline-block;max-width:100%}
.quiz{display:grid;gap:14px;max-width:1100px;margin-bottom:12px}
.qcard{perspective:1400px}
.qinner{display:grid;transition:transform .5s;transform-style:preserve-3d}
.qcard.flipped .qinner{transform:rotateY(180deg)}
.qface{grid-area:1/1;backface-visibility:hidden;-webkit-backface-visibility:hidden;background:var(--card);border:1px solid var(--border);border-left:5px solid var(--primary);border-radius:14px;padding:14px 18px}
.qback{transform:rotateY(180deg);display:flex;flex-direction:column;gap:6px}
.qtext{margin:0 0 10px;font-size:clamp(16px,2vw,22px);line-height:1.5}
.opts{display:flex;flex-wrap:wrap;gap:8px}
.opt,.again{font:inherit;font-size:clamp(15px,1.7vw,19px);min-height:44px;padding:6px 14px;border:1px solid var(--primary);border-radius:999px;background:var(--card);color:var(--deep);cursor:pointer}
.opt:hover,.opt:focus-visible,.again:hover,.again:focus-visible{background:var(--pale)}
.again{align-self:flex-start}
.verdict{margin:0;font-size:clamp(18px,2.2vw,24px);font-weight:700}
.qcard.right .verdict{color:var(--primary)} .qcard.right .qback{border-left-color:var(--primary);background:var(--pale)}
.qcard.wrong .verdict{color:#8a5a00} .qcard.wrong .qback{border-left-color:var(--gold);background:#fbf3df}
.answer,.why{margin:0;font-size:clamp(15px,1.8vw,20px);line-height:1.55}
@media (prefers-reduced-motion:reduce){.qinner{transition:none}}
.note{display:none;margin-top:18px;padding:12px 16px;border-radius:12px;background:#f6ecd2;color:var(--text2);font-size:15px;max-width:1100px}
.show-notes .note{display:block}
nav{position:fixed;left:0;right:0;bottom:0;height:40px;display:flex;align-items:center;justify-content:center;gap:16px;background:rgba(249,246,240,.92);border-top:1px solid var(--border);z-index:5}
nav button{border:1px solid var(--primary);background:var(--card);color:var(--deep);border-radius:999px;min-width:44px;height:30px;font-size:16px;cursor:pointer}
.bar{position:fixed;left:0;top:0;height:4px;background:var(--primary);transition:width .2s;z-index:6}
@media (max-width:640px){.points li{border-left-width:4px}.refs{margin-top:18px}.slide{padding-bottom:60px}}
@media print{.slide{display:flex!important;position:relative;page-break-after:always;height:100vh}nav,.bar{display:none}}
"""

JS = """
const S=[...document.querySelectorAll('.slide')],bar=document.querySelector('.bar'),cnt=document.querySelector('.cnt');
let i=Math.max(0,Math.min(S.length-1,(parseInt(location.hash.slice(1))||1)-1));
function go(n){i=Math.max(0,Math.min(S.length-1,n));S.forEach((s,k)=>s.classList.toggle('on',k===i));
bar.style.width=((i+1)/S.length*100)+'%';cnt.textContent=(i+1)+' / '+S.length;history.replaceState(null,'','#'+(i+1));}
document.querySelectorAll('.qcard').forEach(c=>{const v=c.querySelector('.verdict');
c.querySelectorAll('.opt').forEach(b=>b.onclick=()=>{const ok=b.dataset.ok==='1';c.classList.remove('right','wrong');
c.classList.add('flipped',ok?'right':'wrong');v.textContent=(ok?'答對了！':'答錯了')+'　你選的是 '+b.textContent;
c.querySelector('.qfront').setAttribute('aria-hidden','true');c.querySelector('.qback').removeAttribute('aria-hidden');c.querySelector('.again').focus()});
c.querySelector('.qback').setAttribute('aria-hidden','true');
c.querySelector('.again').onclick=()=>{c.classList.remove('flipped');c.querySelector('.qfront').removeAttribute('aria-hidden');
c.querySelector('.qback').setAttribute('aria-hidden','true');c.querySelector('.opt').focus()}});
document.addEventListener('keydown',e=>{if(e.target.closest&&e.target.closest('button')&&[' ','Enter'].includes(e.key))return;if(['ArrowRight','PageDown',' '].includes(e.key)){e.preventDefault();go(i+1)}
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
