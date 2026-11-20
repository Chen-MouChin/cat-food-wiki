# AGENTS.md：貓糧 LLM Wiki 與教學簡報

給 AI（Claude Code、Codex 或其他 agent）和人看的規則。動手前先讀完。

## 1. 這個專案在做什麼

- **主題**：貓糧，看懂貓糧：怎麼選、怎麼餵。
- **LLM Wiki**：AI 讀原始資料（ingest），把知識整理成一頁一頁的 Markdown（`wiki/`）。之後回答問題、做簡報，都只從 Wiki 取材，不再回去憑印象寫。
- **教學簡報**：從 Wiki 查資料，產生一份給「沒養過貓、不懂貓糧」的人看的 HTML 簡報（`docs/index.html`）。
- **核心規則**：簡報上的每一句話都能追到 Wiki 的一條主張，每條主張都能追到原文的某一頁、某一句。

## 2. 目錄

```
AGENTS.md            本文件（規則）；CLAUDE.md 匯入本文件
data/sources.json    出處清單：key、標題、作者、年份、網址
raw/                 原文 PDF 與逐頁文字（有著作權，不進 git；照 sources.json 的網址可以重新下載）
wiki/
  index.md           Wiki 首頁：所有頁面的目錄
  log.md             紀錄：討論、ingest、lint、重新生成，照時間往下寫
  sources/<KEY>.md   每份來源一頁：摘要＋這份來源的所有主張
  concepts/*.md      主題頁：把多份來源的主張整理在一起，只引用主張編號，不新增事實
slides/
  outline.md         大綱：每一頁要回答的問題，以及查 Wiki 找到的主張編號
  deck.md            簡報原稿：每一點都要標主張編號
scripts/
  extract.py         raw/*.pdf → raw/*.txt（逐頁標 === p.N ===）
  lint_wiki.py       檢查 Wiki：主張格式、編號唯一、原句真的在原文那一頁、中文的數字都在原句裡、主題頁每一句都有編號
  query_wiki.py      查 Wiki：用關鍵字找主張，寫大綱用
  check_slides.py    檢查簡報：每點都有主張、數字對得上主張、用語、每頁長度
  build_slides.py    deck.md → docs/index.html（先跑 lint_wiki 和 check_slides，有 FAIL 就不產出）
  run_graph.py       照 graph 執行整條流程：程式節點自動跑，agent 節點與人工關卡停下來等，失敗依規則退回
runs/                每次實際執行的紀錄（哪一步出錯、怎麼修）；RUN_<日期>.md 是總表
assets/cats/         簡報用的線條貓插畫（貓健康站自有素材）
docs/                產出的簡報，GitHub Pages 從這裡發佈
```

## 3. 主張（claim）的格式

主張只寫在 `wiki/sources/<KEY>.md`，一行一條：

```
- [C-主題-兩位數] 中文主張 ｜ 「英文原句」 p.頁碼
```

- **編號**：主題代碼用大寫英文，例如 `ADQ` 完整均衡、`LBL` 標籤、`DM` 乾物、`CARB` 碳水、`KCAL` 熱量、`BCS` 體態、`FEED` 餵法、`TRT` 零食、`BRD` 品牌、`BEH` 貓的天性。全 Wiki 不可重複。
- **中文主張**：用飼主看得懂的話寫，只能寫原句裡有的意思；原句的但書要一起寫。
- **原句**：從 `raw/<KEY>.txt` 那一頁照抄，至少 6 個英文字。lint 會在忽略大小寫、空白、斷行連字號、連字（ﬁ→fi）的情況下比對，對不到就 FAIL。
- **頁碼**：PDF 的實體頁序（`=== p.N ===`），網頁來源一律是 p.1。

## 4. 操作

| 操作 | 做什麼 | 檢查 |
|---|---|---|
| **討論**（先討論、後生成） | 新主題、新來源、新簡報之前，先和負責人討論範圍、聽眾、要用的來源，決定寫進 `wiki/log.md` | 沒有討論紀錄不開始寫 |
| **Ingest** | 讀一份原文 → 寫 `wiki/sources/<KEY>.md`（摘要＋主張）→ 更新 `index.md`、`log.md` | `python scripts/lint_wiki.py`；再逐條對照中文有沒有超出原句（程式查不到） |
| **整理主題** | 把主張整理成 `wiki/concepts/*.md`，只引用 `[C-…]`，不新增事實 | `lint_wiki.py`（編號存在、主張至少被一個主題頁用到） |
| **Query** | 為簡報每一頁寫一個問題，查 Wiki，把可用的主張編號寫進 `slides/outline.md` | 每頁至少一個主張 |
| **生成簡報** | 照大綱寫 `slides/deck.md`，每一點結尾標 `{C-…}` | `python scripts/check_slides.py` |
| **獨立審查** | 請一個沒看過寫作過程的 agent，逐點比對簡報和引用的主張，找「意思超出主張」 | 審查結果存成 `runs/review_*.md`，修到沒有實質問題 |
| **人工關卡** | H1 抽查主張、H2 裁決審查意見、H3 確認發佈：`run_graph.py` 在 `runs/gates/` 產生檔案，負責人逐項填「判定：」 | agent 不可以替負責人填判定；判定 NG 照圖退回 |
| **產出** | `python scripts/build_slides.py` | 兩支檢查都要 0 FAIL；再看電腦版和手機版截圖，H3 通過才發佈 |

檢查沒過的處理：
- 原句對不到：回到原文重抄那一條，不可以改成意思相近的句子。
- 簡報的數字對不到主張：數字是 Wiki 沒有的，就刪掉那個數字，或回去 ingest 補一條有出處的主張。不可以在簡報裡自己算新數字。
- 審查發現 Wiki 缺資料：退回 Ingest 補主張，不在簡報裡寫沒有出處的解釋。
- 中文主張和簡報都不加「所以…」這類原文沒有的推論、因果或上下限配對。
- 每次失敗和修法都寫進 `wiki/log.md` 和 `runs/`。

## 5. 寫法

- 繁體中文，寫給沒養過貓的人看；專有名詞第一次出現寫成「中文（英文）」，例如美國飼料管理協會（AAFCO）。
- 不寫療效、不寫品牌名、不寫價格；不用「研究顯示」「專家建議」這種沒有出處的說法。
- 簡報每頁最多 4 點，每點最多 60 字；標題用問句或一句結論。
- 數字一律來自主張，單位照原文（kcal 寫成「大卡」）。

## 6. 發佈

- GitHub Pages 從 `main` 的 `/docs` 發佈；`raw/` 不進 git。
- Commit 格式：`類型(範圍): 摘要`，類型用 `wiki`、`簡報`、`檢查`、`建置`、`文件`、`紀錄`、`產出`；結尾加 `Co-Authored-By: Claude <noreply@anthropic.com>`，不加 session 連結。
