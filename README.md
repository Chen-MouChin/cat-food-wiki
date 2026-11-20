# 貓糧 LLM Wiki × 教學簡報

主題：**看懂貓糧：怎麼選、怎麼餵**。先把 9 份獸醫指引、產業指引和政府資料 ingest 成 LLM Wiki，再只用這個 Wiki 當知識來源，產生一份給「沒養過貓的人」看的 HTML 教學簡報。

- **簡報**：https://chen-mouchin.github.io/cat-food-wiki/
- **Wiki 首頁**：[wiki/index.md](wiki/index.md)；紀錄：[wiki/log.md](wiki/log.md)
- **規則**：[AGENTS.md](AGENTS.md)（[CLAUDE.md](CLAUDE.md) 匯入同一份）

## 核心設計：每一句都追得到原文

```
簡報的一點  ──引用──▶  Wiki 主張 [C-DM-02]  ──原句＋頁碼──▶  原文 PDF 第 N 頁
```

- Wiki 的每條知識都是一條「主張」：編號、中文、英文原句、頁碼（`wiki/sources/*.md`）。
- 主題頁（`wiki/concepts/*.md`）只能引用主張編號，不能新增事實。
- 簡報（`slides/deck.md`）的每一點都要標主張編號，數字必須出現在引用的主張裡。
- 檢查程式會回到原文逐條比對；簡報每頁底部列出依據的主張、來源和頁碼。

## Loop／Graph

這張圖可以實際執行：`scripts/run_graph.py` 照圖走，程式節點自動跑；遇到 AI 節點或人工關卡就停下來等；檢查不通過時，照圖上的線退回。下面的圖由同一支程式產生（`python scripts/run_graph.py --mermaid`），圖和程式不會對不上。

### 修改前（第一次執行前的設計）

```mermaid
flowchart LR
  A[Ingest] --> B{lint} --> C[生成簡報] --> D{簡報檢查} --> E{產出}
  B -- FAIL --> A
  D -- FAIL --> C
```

### 修改後（現在的 graph）

圖例：
- 綠色六角形：程式自動執行。
- 方框：AI agent 執行。
- 黃色平行四邊形：人工關卡。

```mermaid
flowchart TD
  S0[/"S0 討論範圍"/]
  S1["S1 取得原文"]
  S2{{"S2 抽逐頁文字"}}
  S3["S3 Ingest 寫主張"]
  S4{{"S4 Wiki 檢查 lint"}}
  S5["S5 AI 逐條對照意思"]
  H1[/"H1 人工抽查主張"/]
  S6["S6 整理主題頁"]
  S6L{{"S6L 主題頁檢查 lint"}}
  S7["S7 查 Wiki 排大綱"]
  S8["S8 生成簡報"]
  S9{{"S9 簡報檢查"}}
  S10["S10 獨立審查 agent"]
  H2[/"H2 人工裁決審查意見"/]
  S11{{"S11 產出 HTML"}}
  S12{{"S12 截圖 電腦/手機"}}
  H3[/"H3 人工確認發佈"/]
  S13["S13 發佈 GitHub Pages"]
  S0 --> S1
  S1 --> S2
  S2 --> S3
  S3 --> S4
  S4 -- 原句對不到／數字不一致 --> S3
  S4 --> S5
  S5 -- 中文超出原句 --> S3
  S5 --> H1
  H1 -- 抽查不通過 --> S3
  H1 --> S6
  S6 --> S6L
  S6L -- 句子沒有編號 --> S6
  S6L --> S7
  S7 --> S8
  S8 --> S9
  S9 -- 沒編號／數字不在主張／超出大綱 --> S8
  S9 --> S10
  S10 --> H2
  H2 -- 採納：簡報措辭 --> S8
  H2 -- 採納：Wiki 缺資料 --> S3
  H2 --> S11
  S11 --> S12
  S12 --> H3
  H3 -- 不通過：內容 --> S8
  H3 -- 不通過：版面 --> S11
  H3 --> S13
  classDef auto fill:#e7efe9,stroke:#3b6a50
  classDef human fill:#f6ecd2,stroke:#b8860b
  class S2,S4,S6L,S9,S11,S12 auto
  class S0,H1,H2,H3 human
```

### 三種節點

| 類型 | 節點 | 怎麼執行 |
|---|---|---|
| 程式（auto） | S2 抽逐頁文字、S4 Wiki 檢查、S6L 主題頁檢查、S9 簡報檢查、S11 產出、S12 截圖 | `run_graph.py` 直接呼叫，結果存進 `runs/graph/` |
| AI agent | S1 取得原文、S3 Ingest、S5 逐條對照意思、S6 主題頁、S7 排大綱、S8 生成簡報、S10 獨立審查、S13 發佈 | 程式停下來，把要修的項目寫進 `runs/tasks/<節點>.md`；agent 做完後用 `--done` 標記 |
| 人工（human） | S0 討論、**H1 抽查主張**、**H2 裁決審查意見**、**H3 確認發佈** | 程式產生 `runs/gates/<關卡>.md`；人逐項填「判定：」，程式讀檔後決定往哪走 |

### 人工關卡放在哪裡、為什麼

- **H1 抽查主張**（S5 之後）：中文主張多講一點，是這個專案最常見的錯，程式只查得到「原句存在、數字一致」。第一次抽查從每份來源抽 1 條，再加 1 條有數字的；之後只看改過或新增的主張（用雜湊值比對）。一條 NG，就把那條退回 S3。
- **H2 裁決審查意見**（S10 之後）：審查者也是 AI，意見不一定對，要不要改由人決定。採納的簡報措辭意見退回 S8；採納的「Wiki 缺資料」意見退回 S3；全部不採納才往下走。
- **H3 確認發佈**（S12 之後）：發佈到公開網址是對外的動作，要人看過截圖才發。NG 時，內容問題退回 S8，版面問題退回 S11。

### 會重複執行的迴圈與停止條件

| 迴圈 | 什麼時候退回 | 什麼時候結束 |
|---|---|---|
| S3 ↔ S4 | 原句不在原文那一頁、中文的數字不在原句裡 | lint 0 FAIL |
| S3 ↔ S5 ↔ H1 | 中文超出原句（AI 對照或人工抽查發現） | 抽查全部 OK |
| S6 ↔ S6L | 主題頁有句子沒有主張編號 | lint 0 FAIL |
| S8 ↔ S9 | 沒編號、數字不在主張裡、用了大綱沒列的主張、目錄對不到標題 | check_slides 0 FAIL |
| S8 → … → S10 → H2 | 人採納了審查意見 | 人裁決全部不採納（或審查沒有意見） |
| H2 → S3 | 人判定是 Wiki 缺資料 | 補主張後重走 S4 以下 |
| H3 → S8／S11 | 人看截圖不通過 | 人判定可以發佈 |

每條回頭的線最多走 **3 次**。超過就不再自動退回，停下來交給人決定下一步（`--goto`），避免 AI 一直改同一個地方。

### 為什麼這樣設計

- LLM 最容易犯的錯是「看起來有根據、其實沒有」：抄錯列、多寫一句推論、把「適當加工」寫成「煮熟」。所以每一層都要求可以追溯。程式查得到的寫成程式；程式查不到的「意思」，先交給 AI 對照和獨立審查，最後由人在關卡把關。
- 簡報只能用大綱列出的主張（S7 先查 Wiki），避免生成時憑印象補內容。
- 人不看每一條，只看三個地方：主張的抽樣、審查意見的取捨、發佈前的成品。這三個地方一出錯，就會一路錯到公開的簡報上。

### 怎麼執行這張圖

```bash
python scripts/run_graph.py --reset S4        # 從 S4 開始一次執行
python scripts/run_graph.py                   # 繼續；停在 agent 節點或人工關卡
python scripts/run_graph.py --done S10 "說明" runs/review_05.md   # agent 做完（S10 附審查檔）
python scripts/run_graph.py --status          # 目前停在哪裡、每條線走了幾次
```

每一步自動記在 [runs/graph_log.md](runs/graph_log.md)，人工關卡的判定留在 `runs/gates/`。

## 怎麼跑

```bash
python scripts/extract.py        # raw/*.pdf → raw/*.txt（raw/ 不進 git，照 data/sources.json 下載）
python scripts/lint_wiki.py      # Wiki 檢查
python scripts/query_wiki.py 乾物 罐頭
python scripts/check_slides.py   # 簡報檢查
python scripts/build_slides.py   # 兩支檢查都通過才產出 docs/index.html
python scripts/run_graph.py      # 照 graph 執行整條流程（見上一節）
```

需要 Python 3.10 以上；`extract.py` 另需 PyMuPDF，其他只用標準函式庫。

## 執行紀錄

- [runs/RUN_2026-11-19.md](runs/RUN_2026-11-19.md)：第一次完整執行的每一步、每次檢查的結果和修法。
- `runs/lint_*.txt`、`runs/check_*.txt`、`runs/review_*.md`：每次檢查的原始輸出。

## 來源與授權

9 份來源列在 [data/sources.json](data/sources.json)。原文有著作權，repo 只放出處與短句引用，不放 PDF 和全文。線條貓插畫為貓健康站自有素材。開發協作：Claude Code（Anthropic）。內容為衛教資訊，不取代獸醫師的建議。
