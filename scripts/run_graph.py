"""照 graph 執行整條流程：程式節點自動跑，agent 節點與人工關卡停下來等，失敗依規則退回。

節點有三種：
  auto   程式自動執行（lint、簡報檢查、產出、截圖）
  agent  交給 AI agent（ingest、對照、主題頁、大綱、生成簡報、獨立審查、發佈）；做完用 --done 標記
  human  人工關卡：H0 審核流程框架（開始前）、H3 審核最終成果（發佈前）；在 runs/gates/ 的檔案填「判定：」

中間的檢查交給程式與 AI：獨立審查的意見由程式分流，有「實質」問題就退回，只剩「輕微」才往下走。
每條回頭的線最多 MAX_ROUNDS 次，超過就停下來交給人決定（--goto 指定下一步）。
狀態存在 runs/graph_state.json，每一步記在 runs/graph_log.md。

用法：
  python scripts/run_graph.py --reset H0           重新開始一次執行（預設從 H0）
  python scripts/run_graph.py                      從目前節點繼續跑，直到遇到 agent 或人工關卡
  python scripts/run_graph.py --done S8 "說明"       標記 agent 節點完成，繼續往下跑
  python scripts/run_graph.py --done S10 "說明" runs/review_05.md   S10 要附審查檔，程式依實質／輕微分流
  python scripts/run_graph.py --goto S8 "理由"       人工指定下一步（超過輪數上限時用）
  python scripts/run_graph.py --status             看目前停在哪裡
  python scripts/run_graph.py --mermaid            印出流程圖（README 用）
"""
import contextlib
import io
import json
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import check_slides  # noqa: E402
import lint_wiki  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
RUNS = ROOT / "runs"
GATES = RUNS / "gates"
TASKS = RUNS / "tasks"
SHOTS = RUNS / "shots"
STATE = RUNS / "graph_state.json"
LOG = RUNS / "graph_log.md"
MAX_ROUNDS = 3
EDGE = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"

# ---------------------------------------------------------------- graph 定義（README 的圖由這裡產生）
NODES = {
    "H0": ("人工審核流程框架", "human"),
    "S0": ("討論範圍與來源", "agent"),
    "S1": ("取得原文", "agent"),
    "S2": ("抽逐頁文字", "auto"),
    "S3": ("Ingest 寫主張", "agent"),
    "S4": ("Wiki 檢查 lint", "auto"),
    "S5": ("AI 逐條對照意思", "agent"),
    "S6": ("整理主題頁", "agent"),
    "S6L": ("主題頁檢查 lint", "auto"),
    "S7": ("查 Wiki 排大綱", "agent"),
    "S8": ("生成簡報", "agent"),
    "S9": ("簡報檢查", "auto"),
    "S10": ("獨立審查 agent", "agent"),
    "S11": ("產出 HTML", "auto"),
    "S12": ("截圖 電腦/手機", "auto"),
    "H3": ("人工審核最終成果", "human"),
    "S13": ("發佈 GitHub Pages", "agent"),
}
EDGES = [  # (from, to, 條件)；條件空白 = 通過
    ("H0", "S0", ""),
    ("S0", "S1", ""), ("S1", "S2", ""), ("S2", "S3", ""), ("S3", "S4", ""),
    ("S4", "S3", "原句對不到／數字不一致"), ("S4", "S5", ""),
    ("S5", "S3", "中文超出原句"), ("S5", "S6", ""),
    ("S6", "S6L", ""), ("S6L", "S6", "句子沒有編號"), ("S6L", "S7", ""),
    ("S7", "S8", ""), ("S8", "S9", ""), ("S9", "S8", "沒編號／數字不在主張／超出大綱"), ("S9", "S10", ""),
    ("S10", "S8", "實質問題：簡報措辭"), ("S10", "S3", "實質問題：Wiki 缺資料"), ("S10", "S11", ""),
    ("S11", "S12", ""), ("S12", "H3", ""),
    ("H3", "S8", "不通過：內容"), ("H3", "S3", "不通過：Wiki"), ("H3", "S11", "不通過：版面"), ("H3", "S13", ""),
]


def mermaid() -> str:
    shape = {"auto": ("{{", "}}"), "agent": ("[", "]"), "human": ("[/", "/]")}
    out = ["flowchart TD"]
    for k, (name, kind) in NODES.items():
        a, b = shape[kind]
        out.append(f'  {k}{a}"{k} {name}"{b}')
    for f, t, cond in EDGES:
        out.append(f"  {f} -- {cond} --> {t}" if cond else f"  {f} --> {t}")
    out += ["  classDef auto fill:#e7efe9,stroke:#3b6a50", "  classDef human fill:#f6ecd2,stroke:#b8860b",
            "  class " + ",".join(k for k, v in NODES.items() if v[1] == "auto") + " auto",
            "  class " + ",".join(k for k, v in NODES.items() if v[1] == "human") + " human"]
    return "\n".join(out)


def nxt(node: str, cond: str = "") -> str:
    for f, t, c in EDGES:
        if f == node and c == cond:
            return t
    raise KeyError(f"{node} 沒有條件「{cond}」的邊")


# ---------------------------------------------------------------- 狀態與紀錄
def load() -> dict:
    return json.loads(STATE.read_text(encoding="utf-8")) if STATE.exists() else {}


def save(st: dict):
    STATE.write_text(json.dumps(st, ensure_ascii=False, indent=1), encoding="utf-8")


def log(st: dict, node: str, result: str, to: str, detail: str = ""):
    if not LOG.exists():
        LOG.write_text("# Graph 執行紀錄\n\n由 `scripts/run_graph.py` 自動寫入。\n", encoding="utf-8")
    t = datetime.now().strftime("%Y-%m-%d %H:%M")
    with LOG.open("a", encoding="utf-8") as f:
        if st.get("_new_run"):
            f.write(f"\n## 執行 {st['run']}（從 {st['start']} 開始）\n\n| 時間 | 節點 | 類型 | 結果 | 下一步 | 說明 |\n|---|---|---|---|---|---|\n")
            st["_new_run"] = False
        f.write(f"| {t} | {node} {NODES[node][0]} | {NODES[node][1]} | {result} | {to} | {detail.replace('|', '／')[:300]} |\n")
    print(f"[{node}] {result} → {to}  {detail[:160]}")


def go_back(st: dict, frm: str, cond: str, detail: str) -> str:
    to = nxt(frm, cond)
    key = f"{frm}->{to}"
    st["rounds"][key] = st["rounds"].get(key, 0) + 1
    if st["rounds"][key] > MAX_ROUNDS:
        log(st, frm, f"FAIL（{key} 第 {st['rounds'][key]} 次，超過 {MAX_ROUNDS} 次）", "人工決定", detail)
        st["waiting"] = f"超過輪數上限：請人工決定，用 --goto 指定下一步（{detail[:100]}）"
        return frm
    log(st, frm, f"FAIL：{cond}", to, detail)
    return to


def capture(fn, *a):
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        n = fn(*a)
    return n, buf.getvalue()


def last_line(out: str) -> str:
    lines = [l for l in out.strip().splitlines() if l.strip()]
    return lines[-1] if lines else ""


# ---------------------------------------------------------------- 自動節點
def run_auto(st: dict, node: str) -> str:
    st["counter"] += 1
    i = st["counter"]
    (RUNS / "graph").mkdir(exist_ok=True)
    if node == "S2":
        missing = [k for k in lint_wiki.SOURCES if not (lint_wiki.RAW / f"{k}.txt").exists()]
        if missing:
            subprocess.run([sys.executable, str(ROOT / "scripts" / "extract.py")], check=True)
        log(st, node, "OK", nxt(node), f"逐頁文字 {len(lint_wiki.SOURCES)} 份")
        return nxt(node)
    if node in ("S4", "S6L"):
        n, out = capture(lint_wiki.run, True)
        (RUNS / "graph" / f"{i:02d}_{node}.txt").write_text(out, encoding="utf-8")
        fails = json.loads((RUNS / "last_lint.json").read_text(encoding="utf-8"))["fails"]
        concept = [x for x in fails if "wiki/concepts" in x]
        claim = [x for x in fails if x not in concept]
        if claim:
            task(node, "S3", claim)
            if node == "S4":
                return go_back(st, node, "原句對不到／數字不一致", "；".join(claim))
            log(st, node, "FAIL：主張", "S3", "；".join(claim))
            return "S3"
        if node == "S6L" and concept:
            task(node, "S6", concept)
            return go_back(st, node, "句子沒有編號", "；".join(concept))
        log(st, node, "OK", nxt(node), last_line(out))
        return nxt(node)
    if node == "S9":
        n, out = capture(check_slides.run)
        (RUNS / "graph" / f"{i:02d}_S9.txt").write_text(out, encoding="utf-8")
        if n:
            fails = [l for l in out.splitlines() if "FAIL" in l]
            task(node, "S8", fails)
            return go_back(st, node, "沒編號／數字不在主張／超出大綱", "；".join(fails))
        log(st, node, "OK", nxt(node), last_line(out))
        return nxt(node)
    if node == "S11":
        import build_slides
        n, out = capture(build_slides.main)
        (RUNS / "graph" / f"{i:02d}_S11.txt").write_text(out, encoding="utf-8")
        if n:
            log(st, node, "FAIL", "人工決定", out[-200:])
            st["waiting"] = "產出失敗：看 runs/graph 裡的輸出"
            return node
        log(st, node, "OK", nxt(node), last_line(out))
        return nxt(node)
    if node == "S12":
        shots = screenshot(st["run"])
        log(st, node, "OK", nxt(node), f"{len(shots)} 張截圖存在 runs/shots/{st['run']}/")
        return nxt(node)
    raise KeyError(node)


def screenshot(run: str) -> list:
    d = SHOTS / run
    d.mkdir(parents=True, exist_ok=True)
    page = (ROOT / "docs" / "index.html").as_uri()
    n = len(check_slides.parse_deck((ROOT / "slides" / "deck.md").read_text(encoding="utf-8"))) + 2
    out = []
    for i in range(1, n + 1):
        f = d / f"desktop_{i:02d}.png"
        subprocess.run([EDGE, "--headless=new", "--hide-scrollbars", "--window-size=1280,720",
                        f"--screenshot={f}", f"{page}#{i}"], capture_output=True)
        out.append(f)
    for i in (1, 2, n - 3):
        wrap = d / f"m{i}.html"
        wrap.write_text(f'<!doctype html><body style="margin:0"><iframe src="{page}#{i}" '
                        f'style="width:375px;height:740px;border:0"></iframe></body>', encoding="utf-8")
        f = d / f"mobile_{i:02d}.png"
        subprocess.run([EDGE, "--headless=new", "--hide-scrollbars", "--virtual-time-budget=2000", "--window-size=375,740",
                        f"--screenshot={f}", wrap.as_uri()], capture_output=True)
        wrap.unlink()
        out.append(f)
    return out


# ---------------------------------------------------------------- agent 節點：寫任務檔，停下來等
def task(frm: str, to: str, items: list):
    TASKS.mkdir(parents=True, exist_ok=True)
    body = "\n".join(f"- {x}" for x in items)
    (TASKS / f"{to}.md").write_text(f"# 給 {to} {NODES[to][0]} 的任務（由 {frm} 退回）\n\n{body}\n\n"
                                     f"做完後：`python scripts/run_graph.py --done {to} \"改了什麼\"`\n", encoding="utf-8")


def review_route(st: dict, review_file: str) -> str:
    """S10 做完：讀審查檔，每項寫成「- [R1]（簡報|Wiki）（實質|輕微）內容」；有實質問題就退回。"""
    text = (ROOT / review_file).read_text(encoding="utf-8")
    items = re.findall(r"^- \[(R\d+)\]\s*（(簡報|Wiki)）（(實質|輕微)）(.*)$", text, re.M)
    major = [(r, k, b) for r, k, sev, b in items if sev == "實質"]
    minor = len(items) - len(major)
    if major:
        cond = "實質問題：Wiki 缺資料" if any(k == "Wiki" for _, k, _ in major) else "實質問題：簡報措辭"
        task("S10", nxt("S10", cond), [f"{r}（{k}）{b.strip()}" for r, k, b in major] + [f"另有輕微 {minor} 項，見 {review_file}"])
        return go_back(st, "S10", cond, f"{review_file}：實質 {len(major)}、輕微 {minor}")
    log(st, "S10", f"OK（實質 0、輕微 {minor}）", nxt("S10"), review_file)
    return nxt("S10")


# ---------------------------------------------------------------- 人工關卡
def gate_file(name: str) -> Path:
    GATES.mkdir(parents=True, exist_ok=True)
    return GATES / f"{name}.md"


def parse_gate(text: str) -> list:
    """每項以 ### [編號] 開頭，項內一行「判定：」；回傳 [(編號, 判定文字)]"""
    return [(m.group(1), m.group(2).strip())
            for m in re.finditer(r"^### \[([^\]]+)\].*?^判定：(.*)$", text, re.S | re.M)]


def make_h0(st: dict) -> Path:
    lines = [f"# H0 人工審核流程框架（執行 {st['run']}）", "",
             "開始之前，由負責人審核整條流程的設計。圖、節點、迴圈和停止條件在 README 的「Loop／Graph」，規則在 AGENTS.md。",
             "「判定：」填 **OK**，或 **要修改 意見**（照意見改完框架，再審一次）。", "",
             "### [FRAMEWORK] 流程框架", "",
             "- 節點三種：程式自動（lint、簡報檢查、產出、截圖）／AI agent（ingest、逐條對照、主題頁、大綱、生成、獨立審查、發佈）／人工（H0 框架、H3 成果）",
             "- 中間的檢查交給程式與 AI：獨立審查的意見由程式分流，有「實質」問題就退回（簡報措辭 → S8；Wiki 缺資料 → S3），只剩「輕微」才往下產出",
             f"- 每條回頭的線最多 {MAX_ROUNDS} 次，超過就停下來交給人決定",
             "- 發佈前一定經過 H3：負責人看簡報、截圖和這次執行的摘要，決定能不能發佈", "",
             "判定：", ""]
    f = gate_file(f"H0_{st['run']}")
    f.write_text("\n".join(lines), encoding="utf-8")
    return f


def make_h3(st: dict) -> Path:
    shots = sorted(p.name for p in (SHOTS / st["run"]).glob("*.png"))
    rows = [l for l in LOG.read_text(encoding="utf-8").split(f"## 執行 {st['run']}")[-1].splitlines() if l.startswith("| 20")]
    lines = [f"# H3 人工審核最終成果（執行 {st['run']}）", "",
             "請看成果本身：簡報（直接開 `docs/index.html`，按 N 看講者備註）、截圖，以及下面這次執行的摘要。",
             f"截圖在 `runs/shots/{st['run']}/`（{len(shots)} 張）。",
             "「判定：」填 **OK**，或 **NG 內容 原因**（退回 S8）、**NG Wiki 原因**（退回 S3）、**NG 版面 原因**（退回 S11）。", "",
             "這次執行經過的節點：", "", "| 時間 | 節點 | 類型 | 結果 | 下一步 | 說明 |", "|---|---|---|---|---|---|", *rows, "",
             "### [PUBLISH] 這一版可以發佈嗎？", "", *[f"- {s}" for s in shots], "", "判定：", ""]
    f = gate_file(f"H3_{st['run']}")
    f.write_text("\n".join(lines), encoding="utf-8")
    return f


def run_human(st: dict, node: str) -> str:
    f = gate_file(f"{node}_{st['run']}")
    if not f.exists():
        f = {"H0": make_h0, "H3": make_h3}[node](st)
        st["waiting"] = f"人工關卡 {node}：請填 {f.relative_to(ROOT)}"
        return node
    items = parse_gate(f.read_text(encoding="utf-8"))
    if not items or any(not v for _, v in items):
        st["waiting"] = f"人工關卡 {node}：{f.relative_to(ROOT)} 還沒填「判定：」"
        return node
    bad = [(k, v) for k, v in items if not v.upper().startswith("OK")]
    rel = f.relative_to(ROOT).as_posix()
    if not bad:
        log(st, node, "OK", nxt(node), rel)
        return nxt(node)
    v = bad[0][1]
    f.rename(f.with_name(f.stem + f"_退回{st['counter']}.md"))
    if node == "H0":
        log(st, node, "要修改", "H0", v)
        st["waiting"] = f"負責人要修改框架：{v}（改完再跑一次，會產生新的審核單）"
        return node
    cond = "不通過：版面" if "版面" in v else "不通過：Wiki" if "Wiki" in v else "不通過：內容"
    task(node, nxt(node, cond), [v])
    return go_back(st, node, cond, v)


# ---------------------------------------------------------------- 主迴圈
def step(st: dict):
    while True:
        node = st["node"]
        if st.get("waiting"):
            print(f"\n停在 {node} {NODES[node][0]}：{st['waiting']}")
            return
        kind = NODES[node][1]
        if kind == "auto":
            st["node"] = run_auto(st, node)
        elif kind == "human":
            st["node"] = run_human(st, node)
        else:
            t = TASKS / f"{node}.md"
            hint = f"任務在 {t.relative_to(ROOT)}" if t.exists() else "照 AGENTS.md 的操作做"
            st["waiting"] = f"等 agent 做 {node} {NODES[node][0]}（{hint}），做完用 --done {node} \"說明\""
        save(st)


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    a = sys.argv[1:]
    if a[:1] == ["--mermaid"]:
        print(mermaid())
        return
    st = load()
    if a[:1] == ["--reset"]:
        start = a[1] if len(a) > 1 else "H0"
        runs = [l for l in (LOG.read_text(encoding="utf-8").splitlines() if LOG.exists() else []) if l.startswith("## 執行")]
        st = {"run": datetime.now().strftime("%Y-%m-%d") + f"-{len(runs) + 1}", "start": start, "node": start,
              "rounds": {}, "counter": 0, "_new_run": True}
    elif a[:1] == ["--done"]:
        node, note = a[1], (a[2] if len(a) > 2 else "")
        if st.get("node") != node:
            raise SystemExit(f"目前在 {st.get('node')}，不是 {node}")
        st["waiting"] = None
        (TASKS / f"{node}.md").unlink(missing_ok=True)
        if node == "S10":
            if len(a) < 4:
                raise SystemExit('S10 要附審查檔：--done S10 "說明" runs/review_05.md')
            st["review_file"] = a[3]
            st["node"] = review_route(st, a[3])
        elif node == "S13":
            log(st, node, "完成", "結束", note)
            st["node"], st["waiting"] = "S13", "這次執行已完成"
            save(st)
            return
        else:
            log(st, node, "完成", nxt(node), note)
            st["node"] = nxt(node)
    elif a[:1] == ["--goto"]:
        st["waiting"] = None
        log(st, st["node"], "人工指定下一步", a[1], a[2] if len(a) > 2 else "")
        st["node"] = a[1]
    elif a[:1] == ["--status"]:
        print(json.dumps(st, ensure_ascii=False, indent=1))
        return
    elif st.get("waiting") and NODES.get(st.get("node"), ("", ""))[1] == "human":
        st["waiting"] = None   # 人工關卡：重新讀檔看填好了沒
    if not st:
        raise SystemExit("還沒開始：python scripts/run_graph.py --reset H0")
    step(st)
    save(st)


if __name__ == "__main__":
    main()
