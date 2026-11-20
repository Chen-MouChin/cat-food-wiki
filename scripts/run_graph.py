"""照 graph 執行整條流程：程式節點自動跑，agent 節點與人工關卡停下來等，失敗依規則退回。

節點有三種：
  auto   程式自動執行（lint、簡報檢查、產出、截圖）
  agent  交給 AI agent（ingest、寫主題頁、排大綱、生成簡報、獨立審查）；做完用 --done 標記
  human  人工關卡（抽查主張、裁決審查意見、確認發佈）；在 runs/gates/ 的檔案逐項填「判定：」

每條回頭的線最多走 MAX_ROUNDS 次，超過就停下來交給人決定（--goto 指定下一步）。
狀態存在 runs/graph_state.json，每一步記在 runs/graph_log.md。

用法：
  python scripts/run_graph.py                 從目前節點繼續跑，直到遇到 agent 或人工關卡
  python scripts/run_graph.py --reset S4      重新開始一次執行，從 S4 開始
  python scripts/run_graph.py --done S8 "說明"  標記 agent 節點完成，繼續往下跑
  python scripts/run_graph.py --goto S8       人工指定下一步（超過輪數上限時用）
  python scripts/run_graph.py --status        看目前停在哪裡
  python scripts/run_graph.py --mermaid       印出流程圖（README 用）
"""
import contextlib
import hashlib
import io
import json
import random
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
    "S0": ("討論範圍", "human"),
    "S1": ("取得原文", "agent"),
    "S2": ("抽逐頁文字", "auto"),
    "S3": ("Ingest 寫主張", "agent"),
    "S4": ("Wiki 檢查 lint", "auto"),
    "S5": ("AI 逐條對照意思", "agent"),
    "H1": ("人工抽查主張", "human"),
    "S6": ("整理主題頁", "agent"),
    "S6L": ("主題頁檢查 lint", "auto"),
    "S7": ("查 Wiki 排大綱", "agent"),
    "S8": ("生成簡報", "agent"),
    "S9": ("簡報檢查", "auto"),
    "S10": ("獨立審查 agent", "agent"),
    "H2": ("人工裁決審查意見", "human"),
    "S11": ("產出 HTML", "auto"),
    "S12": ("截圖 電腦/手機", "auto"),
    "H3": ("人工確認發佈", "human"),
    "S13": ("發佈 GitHub Pages", "agent"),
}
EDGES = [  # (from, to, 條件)；條件空白 = 通過
    ("S0", "S1", ""), ("S1", "S2", ""), ("S2", "S3", ""), ("S3", "S4", ""),
    ("S4", "S3", "原句對不到／數字不一致"), ("S4", "S5", ""),
    ("S5", "S3", "中文超出原句"), ("S5", "H1", ""),
    ("H1", "S3", "抽查不通過"), ("H1", "S6", ""),
    ("S6", "S6L", ""), ("S6L", "S6", "句子沒有編號"), ("S6L", "S7", ""),
    ("S7", "S8", ""), ("S8", "S9", ""), ("S9", "S8", "沒編號／數字不在主張／超出大綱"), ("S9", "S10", ""),
    ("S10", "H2", ""),
    ("H2", "S8", "採納：簡報措辭"), ("H2", "S3", "採納：Wiki 缺資料"), ("H2", "S11", ""),
    ("S11", "S12", ""), ("S12", "H3", ""),
    ("H3", "S8", "不通過：內容"), ("H3", "S11", "不通過：版面"), ("H3", "S13", ""),
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
        kind = NODES[node][1]
        f.write(f"| {t} | {node} {NODES[node][0]} | {kind} | {result} | {to} | {detail.replace('|', '／')[:300]} |\n")
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


# ---------------------------------------------------------------- 自動節點
def run_auto(st: dict, node: str) -> str:
    i = st["counter"] = st["counter"] + 1
    if node == "S2":
        missing = [k for k in lint_wiki.SOURCES if not (lint_wiki.RAW / f"{k}.txt").exists()]
        if missing:
            subprocess.run([sys.executable, str(ROOT / "scripts" / "extract.py")], check=True)
        log(st, node, "OK", nxt(node), f"逐頁文字 {len(lint_wiki.SOURCES)} 份")
        return nxt(node)
    if node in ("S4", "S6L"):
        n, out = capture(lint_wiki.run, True)
        (RUNS / "graph").mkdir(exist_ok=True)
        (RUNS / "graph" / f"{i:02d}_{node}.txt").write_text(out, encoding="utf-8")
        fails = json.loads((RUNS / "last_lint.json").read_text(encoding="utf-8"))["fails"]
        if node == "S4":
            claim_fails = [x for x in fails if "wiki/concepts" not in x]
            if claim_fails:
                task(node, "S3", claim_fails)
                return go_back(st, node, "原句對不到／數字不一致", "；".join(claim_fails))
            log(st, node, "OK", nxt(node), out.strip().splitlines()[-1] if out.strip() else "")
            return nxt(node)
        concept_fails = [x for x in fails if "wiki/concepts" in x]
        if concept_fails:
            task(node, "S6", concept_fails)
            return go_back(st, node, "句子沒有編號", "；".join(concept_fails))
        if fails:  # 主題頁通過但主張又壞了：退回 ingest
            task(node, "S3", fails)
            st["rounds"]["S6L->S3"] = st["rounds"].get("S6L->S3", 0) + 1
            log(st, node, "FAIL：主張", "S3", "；".join(fails))
            return "S3"
        log(st, node, "OK", nxt(node), out.strip().splitlines()[-1] if out.strip() else "")
        return nxt(node)
    if node == "S9":
        n, out = capture(check_slides.run)
        (RUNS / "graph").mkdir(exist_ok=True)
        (RUNS / "graph" / f"{i:02d}_S9.txt").write_text(out, encoding="utf-8")
        if n:
            fails = [l for l in out.splitlines() if "FAIL" in l]
            task(node, "S8", fails)
            return go_back(st, node, "沒編號／數字不在主張／超出大綱", "；".join(fails))
        log(st, node, "OK", nxt(node), out.strip().splitlines()[-1] if out.strip() else "")
        return nxt(node)
    if node == "S11":
        import build_slides
        n, out = capture(build_slides.main)
        if n:
            log(st, node, "FAIL", "人工決定", out[-200:])
            st["waiting"] = "產出失敗：看上面的訊息"
            return node
        log(st, node, "OK", nxt(node), out.strip().splitlines()[-1])
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
        subprocess.run([EDGE, "--headless=new", "--hide-scrollbars", "--window-size=375,740",
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


# ---------------------------------------------------------------- 人工關卡
def claim_hash(c: dict) -> str:
    return hashlib.sha1(f"{c['zh']}|{c['quote']}|{c['page']}".encode("utf-8")).hexdigest()[:10]


def gate_file(name: str) -> Path:
    GATES.mkdir(parents=True, exist_ok=True)
    return GATES / f"{name}.md"


def parse_gate(text: str) -> list:
    """每項以 ### [編號] 開頭，項內一行「判定：」；回傳 [(編號, 判定文字)]"""
    items = []
    for m in re.finditer(r"^### \[([^\]]+)\].*?^判定：(.*)$", text, re.S | re.M):
        items.append((m.group(1), m.group(2).strip()))
    return items


def make_h1(st: dict) -> Path:
    claims, _ = lint_wiki.load_claims()
    approved = st.get("approved_claims", {})
    changed = [c for c in claims.values() if approved.get(c["id"]) != claim_hash(c)]
    rng = random.Random(st["run"])
    pick = []
    if len(changed) < len(claims):        # 之前抽查過：改過或新增的主張全部要看
        pick = changed
    else:                                 # 第一次：每份來源抽 1 條，再加 1 條有數字的
        by_src = {}
        for c in claims.values():
            by_src.setdefault(c["source"], []).append(c)
        pick = [rng.choice(v) for _, v in sorted(by_src.items())]
        nums = [c for c in claims.values() if re.search(r"\d", c["zh"]) and c not in pick]
        pick.append(rng.choice(nums))
    lines = [f"# H1 人工抽查主張（執行 {st['run']}）", "",
             f"從 {len(claims)} 條主張抽 {len(pick)} 條（每份來源 1 條＋1 條有數字的；之後只看改過或新增的）。",
             "請打開 PDF 那一頁，對照英文原句，判斷中文有沒有超出原句、數字和但書有沒有抄對。",
             "每一條的「判定：」後面填 **OK**，或 **NG 原因**。填完存檔，再執行 `python scripts/run_graph.py`。", ""]
    for c in pick:
        src = lint_wiki.SOURCES[c["source"]]
        raw = lint_wiki.RAW / f"{c['source']}.pdf"
        where = f"本機 `raw/{raw.name}` 第 {c['page']} 頁" if raw.exists() else f"[網頁]({src['url']})"
        lines += [f"### [{c['id']}] {src['short']} p.{c['page']}", "",
                  f"- 中文：{c['zh']}", f"- 原句：「{c['quote']}」", f"- 原文：{where}（{src['url']}）", "",
                  "判定：", ""]
    f = gate_file(f"H1_{st['run']}")
    f.write_text("\n".join(lines), encoding="utf-8")
    st["h1_pick"] = {c["id"]: claim_hash(c) for c in pick}
    return f


def make_h2(st: dict) -> Path:
    rev = st.get("review_file")
    text = (ROOT / rev).read_text(encoding="utf-8") if rev else ""
    found = re.findall(r"^- \[(R\d+)\]\s*（(簡報|Wiki)）(.*)$", text, re.M)
    lines = [f"# H2 人工裁決審查意見（執行 {st['run']}，審查檔 {rev}）", "",
             "審查者是另一個 agent，意見不一定對。逐項決定：「判定：」後面填 **採納**、**不採納 理由**。",
             "採納的「簡報」意見退回 S8 改簡報；採納的「Wiki」意見退回 S3 補主張。都不採納就往下產出。", ""]
    if not found:
        lines += ["### [R0] 審查沒有提出問題", "", "判定：", ""]
    for rid, kind, body in found:
        lines += [f"### [{rid}] （{kind}）", "", body.strip(), "", "判定：", ""]
    f = gate_file(f"H2_{st['run']}")
    f.write_text("\n".join(lines), encoding="utf-8")
    st["h2_kinds"] = {rid: kind for rid, kind, _ in found}
    return f


def make_h3(st: dict) -> Path:
    d = SHOTS / st["run"]
    shots = sorted(p.name for p in d.glob("*.png"))
    lines = [f"# H3 人工確認發佈（執行 {st['run']}）", "",
             f"截圖在 `runs/shots/{st['run']}/`（{len(shots)} 張），也可以直接開 `docs/index.html`。",
             "「判定：」填 **OK**、**NG 內容 原因**（退回 S8）或 **NG 版面 原因**（退回 S11）。", "",
             "### [PUBLISH] 這一版可以發佈嗎？", "", "\n".join(f"- {s}" for s in shots), "", "判定：", ""]
    f = gate_file(f"H3_{st['run']}")
    f.write_text("\n".join(lines), encoding="utf-8")
    return f


def run_human(st: dict, node: str) -> str:
    f = gate_file(f"{node}_{st['run']}")
    if not f.exists():
        f = {"H1": make_h1, "H2": make_h2, "H3": make_h3}[node](st)
        st["waiting"] = f"人工關卡 {node}：請填 {f.relative_to(ROOT)}"
        return node
    items = parse_gate(f.read_text(encoding="utf-8"))
    if not items or any(not v for _, v in items):
        st["waiting"] = f"人工關卡 {node}：{f.relative_to(ROOT)} 還有項目沒填「判定：」"
        return node
    bad = [(k, v) for k, v in items if not (v.upper().startswith("OK") or v.startswith("不採納"))]
    rel = f.relative_to(ROOT).as_posix()
    if node == "H1":
        if bad:
            task(node, "S3", [f"{k}：{v}" for k, v in bad])
            f.rename(f.with_name(f.stem + f"_退回{st['counter']}.md"))
            return go_back(st, node, "抽查不通過", "；".join(f"{k} {v}" for k, v in bad))
        st.setdefault("approved_claims", {}).update(st.get("h1_pick", {}))
        log(st, node, f"OK（{len(items)} 條全部通過）", nxt(node), rel)
        return nxt(node)
    if node == "H2":
        took = [(k, v) for k, v in items if v.startswith("採納")]
        if took:
            wiki = [k for k, _ in took if st.get("h2_kinds", {}).get(k) == "Wiki"]
            f.rename(f.with_name(f.stem + f"_處理{st['counter']}.md"))
            if wiki:
                task(node, "S3", [f"{k}：見 {st['review_file']}" for k in wiki])
                return go_back(st, node, "採納：Wiki 缺資料", "採納 " + "、".join(k for k, _ in took))
            task(node, "S8", [f"{k}：見 {st['review_file']}" for k, _ in took])
            return go_back(st, node, "採納：簡報措辭", "採納 " + "、".join(k for k, _ in took))
        log(st, node, f"OK（{len(items)} 項都不採納或沒有問題）", nxt(node), rel)
        return nxt(node)
    if node == "H3":
        if bad:
            v = bad[0][1]
            f.rename(f.with_name(f.stem + f"_退回{st['counter']}.md"))
            cond = "不通過：版面" if "版面" in v else "不通過：內容"
            if cond.endswith("內容"):
                task(node, "S8", [v])
            return go_back(st, node, cond, v)
        log(st, node, "OK：可以發佈", nxt(node), rel)
        return nxt(node)
    raise KeyError(node)


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
        if node == "S13" and st["node"] == "S13" and not st.get("waiting"):
            return


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    a = sys.argv[1:]
    if a[:1] == ["--mermaid"]:
        print(mermaid()); return
    st = load()
    if a[:1] == ["--reset"]:
        start = a[1] if len(a) > 1 else "S0"
        n = sum(1 for _ in GATES.glob("H1_*")) if GATES.exists() else 0
        run = datetime.now().strftime("%Y-%m-%d") + f"-{len([1 for l in (LOG.read_text(encoding='utf-8').splitlines() if LOG.exists() else []) if l.startswith('## 執行')]) + 1}"
        st = {"run": run, "start": start, "node": start, "rounds": {}, "counter": 0, "_new_run": True,
              "approved_claims": st.get("approved_claims", {})}
    elif a[:1] == ["--done"]:
        node, note = a[1], (a[2] if len(a) > 2 else "")
        if st.get("node") != node:
            raise SystemExit(f"目前在 {st.get('node')}，不是 {node}")
        if node == "S10" and len(a) > 3:
            st["review_file"] = a[3]
        st["waiting"] = None
        (TASKS / f"{node}.md").unlink(missing_ok=True)
        log(st, node, "完成", nxt(node), note)
        st["node"] = nxt(node)
        if node == "S13":
            log(st, "S13", "結束", "—", "這次執行完成")
            save(st); return
    elif a[:1] == ["--goto"]:
        st["waiting"] = None
        log(st, st["node"], "人工指定下一步", a[1], a[2] if len(a) > 2 else "")
        st["node"] = a[1]
    elif a[:1] == ["--status"]:
        print(json.dumps({k: v for k, v in st.items() if k not in ("approved_claims", "h1_pick")}, ensure_ascii=False, indent=1)); return
    elif st.get("waiting") and st["node"] in ("H1", "H2", "H3"):
        st["waiting"] = None   # 人工關卡：重新讀檔看填好了沒
    if not st:
        raise SystemExit("還沒開始：python scripts/run_graph.py --reset S0")
    step(st)
    save(st)


if __name__ == "__main__":
    main()
