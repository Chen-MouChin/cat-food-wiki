# 獨立審查 第 8 輪（2026-11-20）

審查者沒有參與撰寫。這一輪只讀不改，本檔是唯一新建的檔案，也沒有執行 scripts/ 裡的任何程式。

做法：
- 讀 AGENTS.md、README.md 的「Loop／Graph」，以及 runs/review_05～07.md。
- 逐頁、逐點讀 slides/deck.md 全部 18 頁，包含標題、講者備註、第 17 頁的題目與答案，對照它引用的 wiki/sources/*.md 主張；再用 slides/outline.md 核對目錄、標題和小測驗範圍。
- 9 份來源頁的 71 條主張逐條比對中文和英文原句，來源頁的摘要也一起看。有疑問的回 raw/*.txt 看上下文，看過的段落有：
  - FDA p.1 全文
  - FEDIAF 2025 p.7、p.10、p.48、p.57 表 VII-9
  - FEDIAF 碳水 p.6、p.8–9
  - AAFP p.1–4
  - AAHA p.1、p.6
  - Delgado p.4
  - WSAVA 2011 p.1、p.3 表 1
  - WSAVA 熱量表、WSAVA 選食物全文
- 7 個主題頁逐句檢查有沒有主張以外的內容。
- 附錄兩頁依 scripts/build_slides.py 的 appendix()、scripts/run_graph.py 的 NODES、EDGES、run_auto()、review_route()，以及 scripts/render_graph.py、scripts/lint_wiki.py 的錯誤訊息判斷。docs/index.html 是舊版，沒有看。

結果：前三輪的實質問題都已經修正。這一輪沒有發現讀者會因此得到錯誤資訊、或拿到沒有出處資訊的地方。數字、單位、地區標示和但書都對得上原文；目錄對得上各頁標題；小測驗三題都只考第 6、7、10 頁教過的內容。下面列的都是輕微問題，有幾項是前幾輪的輕微問題還沒處理。

## 問題清單

- [R1]（簡報）（輕微）第 3 頁講者備註：「後面講『怎麼餵』時，都會回到這兩個天性」，但第 15 頁只回到「常吃、單獨吃」，「嚴格肉食」是在第 12 頁碳水才回到（第 7 輪 R8 還沒處理）。建議改成「後面講碳水和怎麼餵時，會回到這兩個天性」。
- [R2]（簡報）（輕微）第 6 頁第 1 點：「副食」「處方食品」第一次出現，沒照 AGENTS 寫成「中文（英文）」，沒養過貓的人不知道「副食」是什麼。C-ADQ-04 有原文 complementary。建議寫成「副食（complementary）」。
- [R3]（簡報）（輕微）第 9 頁第 1 點：全份簡報第一次出現「FEDIAF」是在這裡，中文全名到第 12 頁備註、第 13 頁才出現。建議這裡寫「歐洲寵物食品工業聯合會（FEDIAF）」，第 13 頁改用簡稱。
- [R4]（簡報）（輕微）第 13 頁第 4 點：「數字只是參考，每隻貓不同 {C-KCAL-05}」把 WSAVA 熱量表自己的但書套到三份指引的數字上。建議改引 FEDIAF 的 C-KCAL-02（每隻貓需要的熱量差很多，即使飼養條件相同也一樣），要先列進大綱第 13 頁；或寫明「WSAVA：這張表只是參考」。
- [R5]（簡報）（輕微）第 13 頁講者備註：公式裡的 100、75、130、0.67、0.4 都沒標主張編號，所以頁面底部的「依據 Wiki」也不會列出 C-KCAL-08、C-KCAL-09，聽眾追不到出處。建議照第 8 頁備註的寫法，在句尾加上（C-KCAL-08）、（C-KCAL-09）。
- [R6]（簡報）（輕微）第 14 頁第 1 點：沒交代 9 分制哪一端是胖、哪一端是瘦，讀者不知道第 3 點的「低於 4」「高於 5」各代表什麼（第 7 輪 R5 還沒處理）。建議用 C-BCS-08 原有的字，寫成「9 分制；極度肥胖的貓會超出 9 分，但沒有驗證過超過 9 分的系統」。
- [R7]（簡報）（輕微）第 15 頁第 2 點：「有些要推或用爪子」，但 C-FEED-09 的中文已經改成「撥弄餵食器」，原文是 manipulation of the feeder，簡報沒有跟著改。建議改成「有些要撥弄餵食器或用爪子才拿得到食物」。
- [R8]（簡報）（輕微）第 16 頁第 1 點：標題是「問廠商這幾件事」，第 2、3 點是問句，第 1 點只列資格，讀者不知道要問什麼（第 7 輪 R6）。WSAVA 原題「1. Do they employ a Nutritionist?」不在 C-BRD-01 的原句裡。建議 C-BRD-01 的原句往前抄到這個問題，簡報改成「有沒有聘用營養專家？合適的資格是…」。
- [R9]（簡報）（輕微）第 19 頁（appendix 的出處）：FDA 那一列顯示（2019），但原文網頁寫「Page Last Updated: 10/13/2017」，2019 是網頁存檔的日期。建議 data/sources.json 的年份改成 2017，或顯示成「2017，2019 存檔」。
- [R10]（簡報）（輕微）第 20 頁第 4 點（appendix）：「每一步記在 wiki/log.md 和 runs/」，但 run_graph.py 自動寫的只有 runs/graph_log.md（README 也這樣寫）。wiki/log.md 是 AGENTS 規定由人或 agent 記下失敗和修法。建議改成「每一步自動記在 runs/graph_log.md；失敗和修法另記在 wiki/log.md」。
- [R11]（簡報）（輕微）第 20 頁第 4 點（appendix）：「檢查沒過就照圖退回，每條線最多 3 次」和程式不完全一致，有兩個地方：
  1. run_graph.py 的 run_auto() 在 S6L 發現主張層級的 FAIL 時，會直接退回 S3，但沒有經過 go_back()，所以不計入 3 次上限；EDGES 和 README 的圖上也都沒有 S6L→S3 這條線。
  2. lint_wiki 的「wiki/index.md 沒有列出 concepts/…」這則訊息不含「wiki/concepts」字樣，會被歸成主張問題，退到 S3 而不是 S6。
  建議在 EDGES 補上 S6L→S3，並改用 go_back()；分類改成以「concepts/」判斷。
- [R12]（Wiki）（輕微）C-LBL-02：中文的「Formula」不在引用的原句裡，它出自 FDA 下一句「Many descriptors other than "dinner" are used, however, with … "Formula" being a few examples」；簡報第 7 頁第 2 點的「鮪魚配方」靠的就是這個字。建議原句延長到這一句。
- [R13]（Wiki）（輕微）C-LBL-04：中文的「成分表照重量排序」出自前一句「All ingredients are required to be listed in order of predominance by weight」，不在引用的原句裡（第 7 輪 R12 還沒處理）。建議原句往前抄。
- [R14]（Wiki）（輕微）C-ADQ-01：原句從「pet food must be substantiated…」開始，中文的「標『完整均衡』的飼料」不在原句裡。建議原句從「A "complete and balanced" pet food must be substantiated…」開始抄。
- [R15]（Wiki）（輕微）C-ADQ-02：原句沒有主詞，中文的「標『所有生命階段』的飼料」不在原句裡（第 7 輪 R14）。建議原句從「A product intended "for all life stages" meets…」開始抄。
- [R16]（Wiki）（輕微）C-ADQ-03：中文的「熟齡沒有專門的規範」出自前一句「no rules governing these types of statements have been established」，簡報第 5 頁第 3 點用的就是這半句（第 7 輪 R13）。建議原句往前抄到這一句。
- [R17]（Wiki）（輕微）C-CARB-02：原句只有公式，中文的「碳水可以用差值估算」「叫做無氮抽出物（NFE）」出自前兩句（第 7 輪 R15）。建議原句往前抄「it can be calculated by difference. This estimation is called 'nitrogen-free extract' (NFE)」。
- [R18]（Wiki）（輕微）C-CARB-09：同一份清單在水分那一項寫「not mandatory for dry foods; if not listed on standard pet food the moisture content is below 14%」，主張沒有收這個但書。簡報第 11 頁的估算公式要減水分，讀者拿乾糧標籤來算，可能找不到水分這一項。建議補一條主張，再視需要放進第 11 頁的講者備註。
- [R19]（Wiki）（輕微）C-DM-05：原文在定義後面註明「(Longstanding industry definition)」，中文沒寫，看起來像法規定義（第 7 輪 R3 的後半）。建議原句延長，中文補上「業界長期沿用的定義」。
- [R20]（Wiki）（輕微）C-BCS-04：原句是描述「把篩檢評估當成第五生命徵象，幾乎不需要額外時間或花費」，中文改寫成「應該當成…」，把描述變成了建議（第 7 輪 R16）。建議原句延長到「requires little to no additional time or cost」，中文照原文翻。
- [R21]（Wiki）（輕微）C-FEED-09：主題頁 wiki/concepts/how-to-feed.md 還寫「有些要貓推動餵食器」，和主張已經改好的「撥弄餵食器」不一致。建議主題頁改成「撥弄」。
- [R22]（Wiki）（輕微）C-CARB-06：來源頁 wiki/sources/FEDIAF-CARBOHYDRATES-FACTSHEET.md 的摘要寫「肥胖的風險因子主要是生活型態和高脂高熱量」，漏了原文的 it appears（看起來），還多了原文沒有的「主要是」。主張本身已經改對了。建議摘要改成「依目前證據，看起來肥胖的風險因子是生活型態和高脂高熱量，而不是碳水含量」。
- [R23]（Wiki）（輕微）wiki/index.md：寫「9 份來源、61 條主張」，實際是 71 條。各來源的主張數也是舊的：FEDIAF 碳水 9→11、FDA 15→19、WSAVA 2011 3→6、AAFP 10→11。附錄第 20 頁會依程式算出的數字顯示 71，兩邊對不上。建議更新首頁的數字。

總結：實質 0、輕微 23
