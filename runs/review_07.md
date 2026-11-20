# 獨立審查 第 7 輪（2026-11-20）

審查者沒有參與撰寫，只讀不改（本檔是唯一新建的檔案；沒有執行 scripts/ 裡的任何程式）。做法：讀 AGENTS.md、README.md 的 Loop／Graph、runs/review_05.md、runs/review_06.md；逐頁、逐點讀 slides/deck.md 全部 18 頁（標題、每一點、講者備註、第 17 頁題目與答案），對照它引用的 wiki/sources/*.md 主張，並用 slides/outline.md 核對目錄、標題與小測驗範圍；9 份來源頁的主張全部逐條比對中文和英文原句，有疑問的回 raw/*.txt 看上下文（FDA p.1 的名稱規則、成分表與肉粉例子、乾物換算、營養充足與生命階段段落；FEDIAF 2025 p.7、p.10、p.57 表 VII-9；FEDIAF 碳水 p.6、p.8–9；AAFP p.3–4 與附錄；AAHA p.6；Delgado p.4；WSAVA 2011 p.1、p.3；WSAVA 熱量表；WSAVA 選食物全文）；7 個主題頁逐句檢查有沒有主張以外的內容；附錄兩頁依 scripts/build_slides.py 的 appendix()、scripts/run_graph.py 的 NODES／EDGES／MAX_ROUNDS、scripts/render_graph.py 產生的 docs/graph.html 和 README 判斷（docs/index.html 仍是 11-19 的舊版，沒有拿來判斷附錄）。前兩輪的實質問題（肉粉定義、24 小時、BRD 序數、三份都是平均、35–45 的 4 公斤條件、BCS 超過 9 分、FelineVMA）都已修正；數字、單位、地區標示這輪沒有發現錯誤。下面是仍存在或新發現的問題。

## 問題清單

- [R1]（Wiki）（實質）C-LBL-07：第 8 頁講者備註「甲款第一項是肉、第二項是玉米；乙款第一項是玉米、第二項才是肉粉；只看排序會以為甲款的動物性蛋白質比較多」在 FDA p.1 確實有，但不在任何一條主張裡，違反「簡報每一句都追得到主張」；主題頁 reading-labels.md 和 C-LBL-07 的「第二個產品」「第一個產品」也因此沒有交代是哪兩款。建議從 FDA p.1 補一條主張，原句抄「For example, one pet food may list "meat" as its first ingredient, and "corn" as the second ingredient. The manufacturer doesn't hesitate to point out that its competitor lists "corn" first ("meat meal" is second), suggesting the competitor's product has less animal-source protein than its own」，列進大綱第 8 頁，再在第 8 頁第 3 點或備註引用它。
- [R2]（簡報）（輕微）第 8 頁第 3 點：「換成乾物比」在第 8 頁就出現，但「乾物」到第 9 頁才定義，沒養過貓的人在這裡看不懂。建議寫成「換成乾物（扣掉水分）比」，或在講者備註說明「乾物下一頁會講」。
- [R3]（簡報）（輕微）第 9 頁第 1 點：「歐洲的定義」讀起來像法規定義，但 FEDIAF 2025 p.7 原文註明這是「Longstanding industry definition」（業界長期沿用的定義）；C-DM-05 的中文也沒寫出這點。建議改成「歐洲寵物食品業界（FEDIAF）的定義：乾糧是水分 14% 以下」，C-DM-05 原句可延長到「(Longstanding industry definition)」。
- [R4]（簡報）（輕微）第 13 頁第 3 點：AAFP 的 40–66 大卡只說「當作起算點」，漏了 C-KCAL-06 的對象「大多數家貓結紮又不太活動」；同頁第 1、2 點都寫了對象，這點沒寫，讀者會以為對任何貓都適用。建議改成「AAFP：大多數家貓結紮又不太活動，每公斤每天 40–66 大卡當起算點」。
- [R5]（簡報）（輕微）第 14 頁第 1 點：只寫「9 分制，沒有驗證過超過 9 分的系統」，沒交代分數哪一端是胖、哪一端是瘦（C-BCS-08 的「極度肥胖」被刪掉了），沒養過貓的人看不懂第 3 點「低於 4 或高於 5」各代表什麼。建議改成「9 分制；極度肥胖的貓會超出 9 分，但沒有驗證過超過 9 分的系統」，用主張原有的字讓讀者知道 9 分是胖的一端。
- [R6]（簡報）（輕微）第 16 頁第 1 點：標題是「問廠商這幾個問題」，第 2、3 點是問句，第 1 點卻只列「營養專家的資格」，讀者不知道要問什麼（WSAVA 原題是「有沒有聘用營養專家？」）。建議等 R10 補好主張後改成「有沒有聘用營養專家？合適的資格是動物營養學博士，或美國、歐洲獸醫營養學院的專科認證」。
- [R7]（簡報）（輕微）第 18 頁第 2 點：「比較營養前，先換成乾物」只引 C-DM-02（換算公式），說「要換成同樣水分基礎才能比」的是 C-DM-07，而且 C-DM-07 的範圍是「罐頭和乾糧之間」，簡報寫成所有比較都要先換。建議改成「罐頭和乾糧比營養前，先換成乾物 {C-DM-07}{C-DM-02}」，並把 C-DM-07 列進大綱第 18 頁。
- [R8]（簡報）（輕微）第 3 頁講者備註：「後面講『怎麼餵』時，都會回到這兩個天性」，但「嚴格肉食」在第 15 頁怎麼餵沒有再出現，回到它的是第 12 頁碳水。建議改成「後面講碳水和怎麼餵時，會回到這兩個天性」。
- [R9]（簡報）（輕微）第 20 頁第 3 點（build_slides.py 的 appendix）：「綠底由程式自動執行（檢查、產出、截圖）」的括號漏了 S2「抽逐頁文字」；同頁連結的 docs/graph.html（render_graph.py 產生）圖例仍寫「程式自動檢查」，和 README「綠色六角形：程式自動執行」、這頁附錄的說法不一致。建議括號改成「（抽逐頁文字、檢查、產出、截圖）」，render_graph.py 的圖例改成「程式自動執行」。
- [R10]（Wiki）（輕微）C-BRD-01：主題頁 choosing-a-brand.md 寫「有沒有聘用營養學專家；合適的資格是…[C-BRD-01]」，但「有沒有聘用營養學專家」不在 C-BRD-01 的原句裡（上一輪 R21 只改了主張中文，主題頁沒跟著處理）。建議把原句往前抄成「Do they employ a Nutritionist? Appropriate qualifications are either a PhD in Animal Nutrition or Board Certification by…」，中文補上「挑品牌要問：有沒有聘用營養專家」。
- [R11]（Wiki）（輕微）C-FEED-09：「有些要貓推動餵食器」把「manipulation of the feeder」（撥弄、操作餵食器）縮成「推」；簡報第 15 頁第 2 點「有些要推或用爪子」跟著變窄。建議改成「撥弄餵食器」，簡報同步改。
- [R12]（Wiki）（輕微）C-LBL-04：中文「成分表照重量排序」出自前一句「All ingredients are required to be listed in order of predominance by weight」，不在引用的原句裡。建議原句往前抄到這一句。
- [R13]（Wiki）（輕微）C-ADQ-03：中文「熟齡沒有專門的規範」出自前一句「no rules governing these types of statements have been established」，不在引用的原句裡（簡報第 5 頁第 3 點用的就是這半句）。建議原句往前抄，從「there is little information as to the true dietary needs…」開始。
- [R14]（Wiki）（輕微）C-ADQ-02：原句「meets the more stringent nutritional needs for growth and reproduction」沒有主詞，中文的「標『所有生命階段』的飼料」不在原句裡。建議原句從「A product intended "for all life stages" meets…」開始抄。
- [R15]（Wiki）（輕微）C-CARB-02：原句只有公式，中文的「碳水可以用差值估算」「叫做無氮抽出物（NFE）」出自前兩句。建議原句往前抄「In order to obtain an estimation of digestible carbohydrates in pet food (mainly starch), it can be calculated by difference. This estimation is called 'nitrogen-free extract' (NFE)」。
- [R16]（Wiki）（輕微）C-BCS-04：原句在 fifth vital sign 截斷，原文整句是「把篩檢評估當成第五生命徵象，幾乎不需要額外時間或花費」，中文改寫成「應該當成…」，把描述變成建議。建議原句延長到「requires little to no additional time or cost」，中文照實翻。
- [R17]（Wiki）（輕微）wiki/concepts/calories-and-body-condition.md：「三份指引給的起始值」只有 AAFP 說是起算點（上一輪 R23 後半未處理）；「這些表都只是參考 [C-KCAL-05]」把 WSAVA 熱量表自己的但書擴大到 FEDIAF、AAFP。建議改成「三份指引給的數字」「WSAVA 這張表只是參考…」。
- [R18]（Wiki）（輕微）wiki/concepts/complete-and-balanced.md：「標短期、間歇或副食的食物，只能佔飲食的 10% 以下 [C-ADQ-04]」漏了主張裡已有的但書「處方食品在獸醫監督下例外」。建議補上。
- [R19]（Wiki）（輕微）wiki/concepts/choosing-a-brand.md：「holistic、premium 這類字…不能拿來判斷 [C-LBL-05]」比原文「of little practical value」（幾乎沒有實際用處）語氣強。建議照主張寫「對判斷營養幾乎沒有用」。

總結：實質 1、輕微 18
