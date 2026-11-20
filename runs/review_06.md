# 獨立審查 第 6 輪（2026-11-20）

審查者沒有參與撰寫，只讀不改（本檔是唯一新建的檔案；沒有執行 lint_wiki.py／check_slides.py／build_slides.py，因為它們會寫入 runs/ 或 docs/）。做法：讀 AGENTS.md、README.md 的 Loop／Graph、runs/review_05.md；逐頁、逐點讀 slides/deck.md 全部 18 頁（標題、每一點、講者備註、第 17 頁題目與答案），對照它引用的 wiki/sources/*.md 主張；9 份來源頁的 66 條主張全部讀過，逐條比對中文和英文原句，這次新增或修改的 C-LBL-03、C-LBL-06～08、C-FEED-01、C-BRD-01～03、C-ADQ-04、C-CARB-06、C-KCAL-02、C-BCS-01、C-BCS-07～09 都回 raw/*.txt 看上下文（FDA p.1 第 53–69、78–85 行、FEDIAF 2025 p.48/p.57、FEDIAF 碳水 p.8–9、WSAVA 2011 p.3、WSAVA 選食物 p.1、WSAVA 熱量 p.1、AAFP p.3–4、Delgado p.4）；7 個主題頁逐句檢查有沒有主張以外的內容；用 slides/outline.md 核對目錄、標題、小測驗範圍；附錄依 scripts/build_slides.py 的 appendix() 和 scripts/run_graph.py 的 NODES／EDGES、README、docs/graph.html（render_graph.py 產生，已是新版）判斷。上一輪的實質問題（肉粉定義、24 小時、BRD 序數、三份都是平均）都已修正，下面是這一輪仍存在或新發現的問題。

## 問題清單

- [R1]（簡報）（實質）第 13 頁第 1 點：「結紮或室內成貓，每公斤每天 35–45 大卡」漏了 C-KCAL-03 的條件「以 4 公斤的貓計算」；FEDIAF 的原始值是每公斤代謝體重（BW^0.67）52–75 大卡，換成每公斤體重的 35–45 只對 4 公斤的貓成立，讀者會拿去乘任何體重。條件只寫在講者備註，畫面上沒有。建議改成「FEDIAF：結紮或室內成貓，以 4 公斤的貓算，每公斤每天 35–45 大卡」。
- [R2]（簡報）（實質）第 14 頁第 1 點：「有些極度肥胖的會超過 9 分制的 9 分」會讓人以為有 10 分、11 分；WSAVA 2011 p.3 原句接著說 there is presently no validated scoring system that extends beyond that point，意思是「胖到超出量表能描述的範圍」，不是分數能超過 9。建議改成「9 分是最胖的一端；有些極度肥胖的貓已經超出 9 分能描述的範圍」，並等 C-BCS-08 補但書後再引用。
- [R3]（Wiki）（實質）C-BCS-08：中文「體態評分會超過 9 分制的 9 分」漏了同一句的但書「目前沒有經過驗證、超過 9 分的評分系統」，意思變成分數可以超過 9。建議原句延長到「…there is presently no validated scoring system that extends beyond that point」，中文改成「有些極度肥胖的病例胖過 9 分制的 9 分，但目前沒有經過驗證、能超過 9 分的評分系統」。
- [R4]（Wiki）（實質）wiki/concepts/calories-and-body-condition.md：表格寫「美國貓科獸醫師協會（AAFP，現名 FelineVMA）」，「現名 FelineVMA」不在任何主張、也不在 data/sources.json，違反主題頁「不新增事實」。建議刪掉「，現名 FelineVMA」；如果要保留，先從有出處的資料 ingest 一條主張。
- [R5]（簡報）（輕微）第 5 頁第 1、3 點：第 2 點標了「在歐洲」，第 1 點（所有生命階段）和第 3 點（熟齡）都是 FDA 講的美國規則卻沒標，讀者會以為是通則。建議兩點前面加「美國：」。
- [R6]（簡報）（輕微）第 6 頁第 1 點：漏了 C-ADQ-04 的但書「處方食品在獸醫監督下例外」，也漏了「短期」，「只能佔 10% 以下」變成沒有例外。建議改成「標短期、間歇或副食的產品，只能佔飲食的 10% 以下（獸醫監督下的處方食品例外）」。
- [R7]（簡報）（輕微）第 6 頁第 4 點：WSAVA 在全份簡報第一次出現在這裡，沒照 AGENTS 寫成「中文（英文）」，全名要到第 13 頁才出現。建議這裡寫「世界小動物獸醫協會（WSAVA）」，第 13 頁改用簡稱。
- [R8]（簡報）（輕微）第 8 頁第 3 點：FDA 第一次出現沒寫中文全名；而且這點要靠 FDA 的例子才看得懂（一款成分表第一項是肉、另一款第一項是玉米、第二項才是肉粉），簡報沒交代，「排在後面的肉粉」是跟誰比讀者看不出來；這頁也比第 9 頁更早用到「乾物」。建議寫「美國食品藥物管理局（FDA）」，在講者備註補上例子的兩款成分表，或把這一頁移到第 9、10 頁之後。
- [R9]（簡報）（輕微）第 8 頁第 4 點：C-LBL-08 的重點是「這不代表肉粉那一款的『肉』比較多」，簡報只寫「肉粉本身不算是肉」，和第 3 點的關係沒講清楚。建議改成「但這不代表它的『肉』比較多：肉粉本身不算是肉」。
- [R10]（Wiki）（輕微）C-LBL-08：原句的「or in fact, any meat at all」（甚至可能完全沒有肉）在中文裡不見了。建議中文改成「這不代表第二個產品的『肉』比較多，甚至不代表它有肉；肉粉本身不算是肉…」。
- [R11]（簡報）（輕微）第 9 頁第 1 點：「乾糧是水分 14% 以下」是 FEDIAF（歐洲）的定義，和同頁 FDA（美國）的 88–90% 放在一起沒標地區。建議改成「歐洲的定義：乾糧是水分 14% 以下的寵物食品」。
- [R12]（Wiki）（輕微）C-DM-02：第 9 頁標題「不能直接比」和第 18 頁第 2 點「比較營養前，先換成乾物」是指引性的結論，C-DM-01／02 只是公式，沒有一條主張說「比較時要先換成乾物」。建議從 FDA p.1 補一條「The most accurate means of doing this is to convert the guarantees for both products to a moisture-free or dry matter basis」，兩處改引這條。
- [R13]（Wiki）（輕微）C-CARB-02：「灰分」在簡報第 11 頁第一次出現沒有解釋（上一輪 R15 未處理）。FEDIAF 碳水 p.8 同頁有「Crude ash (or Incinerated residue, or Inorganic matter)」可以抄。建議補一條主張說明灰分是燒完剩下的無機物，第 11 頁第 2 點加括號說明。
- [R14]（Wiki）（輕微）C-CARB-01：原句出自「According to the EU law … must be declared」那一段，講的是歐盟標籤；中文沒寫範圍，簡報第 11 頁接在美國標籤之後，讀者會當成各地通則。建議中文改成「依歐盟規定的標籤項目，沒有可消化碳水（糖和澱粉）這一項」，簡報第 11 頁第 1 點同步加「歐盟」。
- [R15]（簡報）（輕微）第 11 頁第 3 點：「因為粗纖維被低估」意思不準；原文是「粗纖維的分析方法大幅低估了實際的膳食纖維」，所以扣掉的纖維太少、碳水算多了。建議改成「粗纖維的測法會低估實際的纖維，扣得太少，算出的碳水通常偏高」。
- [R16]（簡報）（輕微）第 12 頁第 3 點：保留語氣已補上，但沒交代這是歐洲寵物食品業者團體 FEDIAF 的整理（上一輪 R16 後半未處理），碳水和業者利益有關，沒養過貓的人需要知道是誰說的。建議改成「FEDIAF 整理目前證據，看起來…」。
- [R17]（Wiki）（輕微）C-KCAL-06：中文前半「大多數家貓結紮又不太活動」出自前一句，不在引用的原句裡。建議把原句往前抄到「Most house cats are neutered and minimally active. Therefore, use 40–66 kcal/kg…」。
- [R18]（Wiki）（輕微）C-BCS-06：中文以「所以」開頭，但這條主張本身沒有前提，而且漏了主詞「獸醫和飼主」（簡報第 14 頁反而有寫）。建議中文改成「因為真正的熱量需求以體態為準，獸醫和飼主要經常看體態，再調整餵的量」或直接刪「所以」補主詞。
- [R19]（Wiki）（輕微）C-FEED-02：第 15 頁第 2 點的「益智餵食器」對沒養過貓的人是陌生詞，Wiki 沒有說明是什麼。AAFP p.3 有「Some types require more effort … either by manipulation of the feeder or by the use of paws or tongue to reach the food」可以抄。建議補一條主張，簡報這點加一句說明。
- [R20]（Wiki）（輕微）C-FEED-06：原句 control food access and amount，中文寫成「控制吃的時間和份量」，access 不只是時間。建議改成「控制貓能不能吃到、吃多少」。
- [R21]（Wiki）（輕微）C-BRD-01：問題本身「Do they employ a Nutritionist?」不在引用的原句裡，中文「挑品牌要問：有沒有聘用營養學專家」沒有出處。建議原句從「1. Do they employ a Nutritionist?」開始抄（或另立一條）。
- [R22]（簡報）（輕微）第 16 頁第 1 點：「獸醫營養專科認證」把原文限定的 ACVN、ECVCN 兩個學院放寬成任何獸醫營養專科。建議改成「美國或歐洲獸醫營養學院的專科認證」。
- [R23]（Wiki）（輕微）wiki/concepts/calories-and-body-condition.md：「兩份表用的公式不同」不對，FEDIAF 一般活動成貓（100 × 體重^0.67）和 WSAVA 精瘦成貓的公式相同（簡報第 13 頁備註已改對，主題頁沒跟著改）；「三份指引給的起始值」也只有 AAFP 說是起算點。建議改成「FEDIAF 一般活動成貓的公式和 WSAVA 精瘦成貓相同，不同在室內或結紮成貓另估 75」，「起始值」改成「建議值」。
- [R24]（Wiki）（輕微）wiki/concepts/reading-labels.md：「名稱差一個字，點名的食材比例差很多」不在任何主張裡（C-LBL-03 已刪掉這半句）；C-LBL-07 那句的「排在後面的肉粉」「排在前面的鮮肉」也不在主張裡。建議刪掉這兩處，或補一條含「even a minor change in the wording of the name has a dramatic impact」與 FDA 例子設定的主張。
- [R25]（Wiki）（輕微）wiki/concepts/how-to-feed.md：「餵食點不要靠近砂盆 [C-FEED-04]」放在「多貓家庭」小節下，和簡報第 15 頁已修正的寫法相反，又把一般建議限縮成多貓家庭。建議移到「餵法」小節。
- [R26]（Wiki）（輕微）wiki/concepts/carbohydrates.md：最後一點「要和罐頭比，記得先換成乾物」沒有主張編號，是主題頁新增的建議。建議刪掉，或改成只放連結「乾物換算見…」。
- [R27]（簡報）（輕微）第 20 頁（build_slides.py 的 appendix）：說明寫「綠底是程式自動檢查」，但 run_graph.NODES 的 auto 節點還有「抽逐頁文字」「產出 HTML」「截圖」，不是檢查；白底的 AI agent 節點（含 S5 逐條對照、S10 獨立審查）沒有任何說明，讀者看不出哪些是 AI 做的；節點以單線箭頭排列，看不到 README 圖上的退回線。建議說明改成「綠底＝程式自動執行、白底＝AI agent、黃底＝人工關卡；這裡只列順序，退回線見完整流程圖」。

總結：實質 4、輕微 23
