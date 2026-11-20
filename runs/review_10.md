# 審查第 10 輪（只審 commit d63f923 的修改）

範圍：slides/deck.md 第 1、6、14 頁；wiki/concepts/*.md（7 頁）、wiki/index.md、wiki/sources/FDA-PET-FOOD-LABELS-GENERAL.md 的 C-LBL-02；README.md；runs/RUN_2026-11-20.md。方法：用 git show 看差異，逐句對照 wiki/sources 的主張與 raw/*.txt 原文（只讀，沒有執行 scripts/）。結果：簡報三頁拿掉「獸醫」後意思沒有超出主張，也沒有漏掉必要的但書。C-LBL-02 延長後的原句和 raw/FDA-PET-FOOD-LABELS-GENERAL.txt p.1 一字不差，補上了「Formula」的出處（解決 review_08 R12）。主題頁加上的「美國／歐洲／FEDIAF／FDA／WSAVA」標示，都和各主張所屬的來源一致。wiki/index.md 的 71 條、各來源主張數（8/11/19/7/3/6/11/4/2）和 sources/*.md 實際條數相符。RUN_2026-11-20.md 的數字對照 graph_log.md 與 review_05～09，都對得上：各輪實質／輕微 8/24、4/23、1/18、0/23、0/10，主張 61→66→70→71，S10→S3 走滿 3 次，實質錯誤 20 項（審查 13＝簡報 5＋附錄 1＋Wiki 7，另有 lint 3、S5 3、H3 1）。沒有實質問題。輕微問題是流程沒走完整、一處中文超出引用句，以及紀錄沒有更新到最新。

- [R1]（Wiki）（輕微）concepts/calories-and-body-condition.md：刪掉「營養篩檢當第五生命徵象／每次看診做營養評估」那一點後，C-BCS-03、C-BCS-04 不再被任何主題頁引用，lint_wiki.py 第 134 行會列成「孤兒主張」WARN。建議看負責人的意思：要嘛把這點放回去（可以不寫「獸醫」），要嘛在 log 註明這兩條主張是刻意不用。
- [R2]（Wiki）（輕微）流程：這次改了 7 個主題頁和 C-LBL-02 的原句，但 graph_log.md 只記到 S8、S9，S4、S5、S6L 都沒有重跑。H3 判的是「NG 內容」，照圖會退回 S8；動到 Wiki 的部分應該是「NG Wiki」，退回 S3。建議補跑 S4～S6L，至少 lint 要確認 FAIL 0，並看 R1 的 WARN；或者在紀錄寫明為什麼跳過。
- [R3]（Wiki）（輕微）concepts/how-to-feed.md C-FEED-08：「不管是讓貓自由取食還是分餐」不在引用的原句裡，原句從「owners should track」才開始。raw/DELGADO p.4 的前一句是「allow cats to graze or offer multiple feeding choices (food puzzles, as well as meals)」，所以「分餐」也漏了益智餵食器。建議把原句往前延長到「Owners can allow cats to graze…」並同步修改主張的中文；不然就改回「不管怎麼餵」。
- [R4]（簡報）（輕微）第 6 頁第 1 點，以及 concepts/complete-and-balanced.md 的 C-ADQ-04：「照醫囑使用時例外」對應原文「under veterinarian supervision」。原文說的是持續監督，「照醫囑」比較接近開一次處方就好，意思弱了一點；而且主張本身的中文還是「在獸醫監督下」，三處說法不一致。建議改成「處方食品在醫療監督下使用時例外」，主張的中文也一起改（走 S3→S5）。
- [R5]（簡報）（輕微）runs/RUN_2026-11-20.md「走過的節點」：表格最後一列是「H3 負責人審核中」，但 graph_log.md 在 13:15 已經記了第 2 次 H3 NG（「獸醫」用語，以及 README、首頁、主題頁的修改），接著是 S8、S9，現在停在 S10。表格和「每個節點抓到的錯誤」都沒有算到這次 H3。開頭寫「實際跑完的一次執行」，也和現況不符。建議補上 13:15 這一輪、這輪審查的結果，並更新 H3 的狀態。
- [R6]（簡報）（輕微）runs/RUN_2026-11-20.md：寫「另外還有三件不算在上表的事」，下面只列了兩點（流程程式 2 項、審查 agent 誤操作 1 次）。建議改成「兩類」，或改成「三項（流程程式 2、誤操作 1）」。
- [R7]（簡報）（輕微）README.md：刪掉了「執行紀錄」一節和 runs/graph_log.md 的連結，現在 README 沒有任何連結通到 RUN_2026-11-19.md、RUN_2026-11-20.md，「每一步都會自動寫進執行紀錄」也沒寫在哪裡。建議至少留一行連結到 runs/RUN_2026-11-20.md 和 runs/graph_log.md。

總結：實質 0、輕微 7
