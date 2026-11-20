"""把 run_graph.py 的 graph 畫成圖：docs/graph.html（Mermaid）＋ docs/graph.png（Edge 無頭模式截圖）。

圖的內容只來自 run_graph.py 的 NODES、EDGES，圖和程式不會對不上。
用法：python scripts/render_graph.py
"""
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import run_graph  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
DOCS = ROOT / "docs"

PAGE = """<!doctype html>
<html lang="zh-Hant-TW"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>貓糧 LLM Wiki：Loop／Graph</title>
<style>
body{{margin:0;background:#f9f6f0;color:#1d1d1f;font-family:"Noto Sans TC","Microsoft JhengHei",system-ui,sans-serif}}
main{{max-width:1180px;margin:0 auto;padding:20px}}
h1{{font-size:24px;margin:0 0 6px}} p{{margin:0 0 10px;color:#4a4a4c}}
.legend span{{display:inline-block;border:1px solid;border-radius:6px;padding:2px 10px;margin-right:8px;font-size:14px}}
.a{{background:#e7efe9;border-color:#3b6a50}} .g{{background:#fff;border-color:#888}} .h{{background:#f6ecd2;border-color:#b8860b}}
.mermaid{{background:#fff;border:1px solid #e8e4db;border-radius:12px;padding:12px}}
</style></head><body><main>
<h1>貓糧 LLM Wiki 與教學簡報：Loop／Graph</h1>
<p>由 scripts/run_graph.py 的節點與邊產生；箭頭上的文字是退回的條件，沒有文字的箭頭代表通過。每條回頭的線最多 {max_rounds} 次，超過就交給人決定。</p>
<p class="legend"><span class="a">程式自動檢查</span><span class="g">AI agent</span><span class="h">人工關卡</span></p>
<pre class="mermaid">
{mermaid}
</pre>
</main>
<script src="https://cdn.jsdelivr.net/npm/mermaid@10.9.1/dist/mermaid.min.js" integrity="sha384-WmdflGW9aGfoBdHc4rRyWzYuAjEmDwMdGdiPNacbwfGKxBW/SO6guzuQ76qjnSlr" crossorigin="anonymous"></script>
<script>mermaid.initialize({{startOnLoad:true,theme:"base",flowchart:{{curve:"basis"}},
themeVariables:{{fontFamily:"Microsoft JhengHei, Noto Sans TC, sans-serif",fontSize:"15px",primaryColor:"#ffffff",primaryBorderColor:"#888",lineColor:"#2a4c39"}}}});</script>
</body></html>
"""


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    DOCS.mkdir(exist_ok=True)
    html = DOCS / "graph.html"
    html.write_text(PAGE.format(mermaid=run_graph.mermaid(), max_rounds=run_graph.MAX_ROUNDS), encoding="utf-8")
    png = DOCS / "graph.png"
    subprocess.run([run_graph.EDGE, "--headless=new", "--hide-scrollbars", "--virtual-time-budget=8000",
                    "--force-device-scale-factor=1.5", "--window-size=1200,1720", f"--screenshot={png}", html.as_uri()],
                   capture_output=True)
    print(f"完成：{html.relative_to(ROOT)}、{png.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
