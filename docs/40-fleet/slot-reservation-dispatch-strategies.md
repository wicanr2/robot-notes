# 目的點/儲位重複預定:預排即拒絕,還是調度層序列化

一個多機現場常碰到的調度設計題:同一個目的點(以下叫 **B 點**,可以是某個儲位、放貨點、停靠點)被**不只一筆任務**指定。系統該怎麼處理?

把情境講具體。現場有兩台車,各被排了兩筆「取放任務」:

- **車1**:`A取B放`(從 A 取貨、放到 B)、`C取B放`(從 C 取貨、再放到 B)
- **車2**:`B取E放`(從 B 取貨、放到 E)、`B取F放`(從 B 取貨、放到 F)

注意 B 在這裡**同時是車1 的「放」目的、也是車2 的「取」來源**。問題就出在:當系統裡已經有一筆「放到 B」的任務(`A取B放`),使用者(或上位系統)還能不能再排第二筆「放到 B」的任務(`C取B放`)?

兩種設計策略,沒有對錯,只是取捨不同:

1. **策略一:預排即拒絕** —— 只要 B 已被某筆任務預定為放貨目的,就**拒絕**再排任何放到 B 的新任務。儲位在排程當下就被鎖住。
2. **策略二:允許預排、調度層序列化** —— **允許**一次把多筆放 B 的任務都排進來,但在調度層做序列化:前一筆跟 B 相關的任務沒結束前,下一筆放 B 的任務**不會被觸發**(卡在調度層等,UI 跳警告提示)。這種「條件成立才放行、否則卡著等」的閘門,下面叫它 **gating**(像水閘)。

> 用詞先講清楚:這裡的**序列化**指「把並行的任務排出一個先後順序」,**不是**程式把物件存成 bytes 的那個 serialization,別搞混。

> 前置脈絡:[OpenRMF](open-rmf.md)、[VDA5050 協定](vda5050.md)、[Fleet 深入:API/圖資/座標/避塞車](rmf-maps-and-traffic.md)。本篇是策略分析,不綁定任何特定產品或客戶。

---

## 1. 先看清本質:B 是一個「容量 1 的共用暫存格」

把雜訊去掉,這題的骨架是電腦科學裡很經典的東西:

- B 是一個**一次只能放一件**的格子(容量 1 的緩衝區,英文 bounded buffer)。
- 往 B **放貨**的角色叫**生產者(producer)**,前提是 **B 必須空**;從 B **取貨**的角色叫**消費者(consumer)**,前提是 **B 必須滿**。
- 在**本例的任務集**下,車1(`A取B放`、`C取B放`)整路都在放、剛好扮 producer;車2(`B取E放`、`B取F放`)整路都在取、扮 consumer。但要注意:**一般情況下這兩個角色是「看任務而定」的**,同一台車對同一個 B 也可能又放又取、輪替扮演——別把 producer/consumer 當成固定的車身屬性。

<p align="center"><img src="../img/slot-reservation-strategies.svg" width="860" alt="B 是容量 1 的共用暫存格:車1 放(producer,需 B 空)、車2 取(consumer,需 B 滿);策略二允許一次排入、靠 B 空/滿 gating 自動交錯成生產者-消費者流水,策略一則在 B 被預定時拒絕第二筆放 B,逼使用者手動分批補單"></p>

理想的流水是自動交錯的:**車1 放 B(B 滿)→ 車2 把 B 取走(B 空)→ 車1 再放 B(B 滿)→ 車2 再取走**。這正是作業系統教科書裡的 **producer–consumer 問題**(白話:一個人放、一個人拿、中間只有一格暫存,得排好先後別撞在一起),核心約束是 **mutual exclusion(互斥)**:任何時刻只能有一台車對 B 動作。

兩個策略的差別,其實就是**「這個互斥要在哪一層、用什麼方式達成」**:

- 策略一在**排程當下**就鎖死 B(誰先預定誰獨佔,別人連排都不准排)。
- 策略二讓大家都先排進來,在**執行當下**用「B 空/滿」這個條件一筆一筆放行。

---

## 2. 對應到經典理論:悲觀鎖 vs 樂觀並行 + 序列化

這兩條路在資料庫/作業系統裡有成熟的名字:

| 本題策略 | 對應理論 | 一句話 |
|---|---|---|
| 策略一(預排即拒絕) | **悲觀鎖(pessimistic locking)/ 兩階段鎖 2PL** | 2PL = 先只拿鎖、後只放鎖的兩階段;假設衝突常見,先取鎖再動、鎖到結束才放。一致性最強,並行度最低 |
| 策略二(允許排入 + 序列化) | **樂觀准入 + 執行期條件序列化** | 准入不上鎖(這是「樂觀」),靠「B 空/滿」當條件、卡住排隊放行,使結果等價於某個串行順序。並行度高,但要管好排隊 |
| 「一次只一台對 B 寫」 | **互斥 + serializability(可串行化)** | 多筆並行的最終效果,等價於把任務一個一個串行做 B |

幾個從理論借來的判斷:

- **先澄清「樂觀」**:這裡的樂觀指**准入階段不上鎖**(先讓任務排進來),**不是**資料庫 OCC 那種「執行到最後才驗證、撞到衝突就整筆 abort 重做」。策略二撞到衝突是**排隊等**、不是重做——所以它的失效模式是 deadlock / 飢餓(見 §4),而不是 retry 風暴。
- **策略一單純鎖一個 B 不會死結**:因為每筆任務只需要 B 這**單一資源**,拿不到就還沒持有任何鎖,湊不出「持有並等待 + 循環等待」(死結需要 Coffman 四條件:互斥、持有並等待、不可搶占、循環等待,四條同時成立;單一資源天生缺後兩條)。
- **策略二的風險來自跨資源**:`A→B`、`C→B`、`B→E`、`B→F` 交錯起來會牽涉 B、E、F、車輛位置等多個資源,釋放條件寫不好就可能湊出「車1 等車2 取走 B、車2 等車1 放進 B」的循環等待。
- 作業系統的 **banker's algorithm(銀行家演算法)** 給了中間路線:批准一筆任務前,先驗證「整批任務存在一個能安全做完的順序」再放行——**前提是每筆任務的資源需求能事先宣告/枚舉**。這是「策略二要把序列化做對」的理論版本。

> 一句話:策略一 = 悲觀、保守、簡單;策略二 = 樂觀、高吞吐,但正確性全押在「序列化與釋放條件」做不做得紮實。

---

## 3. 業界與開源系統怎麼做

查了 Open-RMF、VDA5050、倉儲 WCS/WES 的設計,業界**主流不是策略一,而是策略二的變形**——而且更進階:用「帶時間窗的動態預定」而非永久鎖死。

### 3.1 Open-RMF:協商為主,獨佔點用「租約」,另有預定節點

Open-RMF 沒有「排程當下把目的地鎖死」的單一全域設計,而是分三層機制:

- **Traffic Schedule + Negotiation(主幹,偏樂觀)**:各車隊把預期行程上報到共享的 Traffic Schedule;真撞上才發 conflict notice、進入協商,由第三方仲裁選較佳組合。是「報行程 + 協商」,不是事先鎖地點。([rmf_traffic](https://github.com/open-rmf/rmf_traffic)、[RMF core 章](https://osrf.github.io/ros2multirobotbook/rmf-core.html))
- **mutex_groups(真正獨佔,但用租約 + 心跳)**:需要獨佔的點要持有 mutex(mutual exclusion 的縮寫,一把同時只有一台車能拿到的鎖)才能進,且必須**週期性續租**(像租約要定期繳費),心跳沒到就 timeout 自動釋放。這裡有個**對本題很關鍵的已知坑**:「任務結束」不等於「車離開 B」——mutex 一放,別台車可能就進來,但前一台其實還停在 B 上。([mutex 釋放討論](https://github.com/open-rmf/rmf/discussions/466))
- **rmf_reservation(預定/排隊,實驗性)**:獨立的資源預定節點,車去目的地前先問「這裡可用嗎」,用 ticket + 候選等待點配最低成本目的地。這條最接近「先問可用、排隊等位」。([rmf_reservation_node 文件](https://docs.ros.org/en/rolling/p/rmf_reservation_node/)、[rmf_reservation](https://github.com/open-rmf/rmf_reservation))

### 3.2 VDA5050:協定不管預定,只給「逐段釋放」的機制

[VDA5050](vda5050.md) 是上位與車之間的介面標準,**它本身不處理儲位預定**:

- 一張運輸單是 node + edge + action 的圖;路徑分 **base(已釋放、可走)** 與 **horizon(已規劃、未釋放)**,節點/邊上有 `released` 旗標,上位可以**只釋放到某個路口為止**,逐段協調多車。
- action 有 `blockingType`(NONE / SOFT / HARD)管「這個動作要不要停車、能不能跟別的動作並行」——但那是動作層的互斥,不是儲位層的鎖。
- 規格白紙黑字:**交通管理、routing、優先序、死結解法不在標準範圍內**。儲位/目的地預定是上位(master control)的 business logic。

> 直接含意:VDA5050 不會幫你判「B 已被預定就拒絕」。**策略一或策略二,都是上位/車隊層要自己實作的政策**,協定只負責把決定好的節點逐段下發。([VDA5050 spec](https://github.com/VDA5050/VDA5050/blob/main/VDA5050_EN.md)、[路口管理屬上位職責的討論](https://github.com/VDA5050/VDA5050/discussions/110))

### 3.3 倉儲分層:儲位歸上位,車隊只負責消化

典型倉儲是 WMS → WES → WCS → 車隊 → 設備的分層:

- **「貨該放哪個 B」通常是 WMS / WES 的決策**(它握有庫存與儲位狀態),不是車隊層。
- **上位一次塞大量任務、由車隊/交通管理層消化,是常態**;排隊與序列化交給車隊層,上位不需要等前一筆做完才丟下一筆。

這帶出一個現場常見的張力:**若場域有強勢上位系統(WMS/WES),它本來就會一次塞一串任務下來**。這時車隊層若採策略一(直接拒收第二筆放 B),等於把上位的職責拉回車隊層、製造雙重事實來源,且會讓「習慣一次塞滿」的上位系統大量任務被擋下。策略二(車隊只負責序列化執行)更貼近這種主流分工。([WCS/WES/WMS 分工](https://kpisolutions.com/resources/wcs-vs-wes-vs-wms-the-software-behind-warehouse-operations/)、[AGV 車隊架構](https://www.smartloadinghub.com/insights/agv-amr/designing-agv-fleet-architecture-reliable-warehouse/))

### 3.4 學界:目的/資源衝突有成熟解法,且偏向「帶時間窗的動態預定」

多機路徑規劃(MAPF,multi-agent path finding)把「目的衝突 / 資源衝突」當核心問題:

- 兩台車都要用 B,可看成 MAPF 的 **vertex conflict**(兩 agent 同一時刻佔同一節點)的**時間區間版**——B 是在「一段時間」被重複預定,而非同一瞬間相撞,這也是後面推「帶時間窗的動態預定」更貼切的原因。標準最優解法 **CBS(Conflict-Based Search)** 用雙層搜尋對衝突加約束、重規劃。([CBS 原始論文](https://www.sciencedirect.com/science/article/pii/S0004370214001386))
- **CBS 加先後約束**正好對應「放 B 要在取 B 之後」這種 precedence。([CBS + temporal/precedence](https://arxiv.org/abs/2402.08772))
- 最貼近策略二的工程化做法是**動態資源預定**:用「在某個時間窗預定 B」而非永久鎖死,達成 time-efficient 且 deadlock-free 的移動。([IEEE: Dynamic Resource Reservation for Multi-AGV](https://ieeexplore.ieee.org/document/10419190/))

> 重點:「reserve destination(預定目的點)」在學界是成熟概念,而且更先進的是**帶時間維度的動態預定**——比策略一的「一占就拒」彈性高,又比沒約束的策略二安全。

---

## 4. 策略二的坑:死結與飢餓,怎麼防

策略二的成敗全在序列化條件。設計不良會踩到:

- **循環等待型死結**:序列化條件若寫成「車1 等 B 空、車2 等貨進 B」而沒有打破循環的規則,就可能互等。**防法**:固定通行/優先規則(right-hand rule、FCFS)、或 banker's 式的「批准前驗證存在安全完成序列」。
- **飢餓(starvation)**:用強優先序時,低優先任務可能永遠排不到 B。**防法**:**aging**——等待越久優先序自動升高。
- **持鎖者失聯**:佔住 B 的車掛了、資源永遠不還。**防法**:**租約 + 心跳 + timeout 自動釋放**(Open-RMF mutex 就是這套)。
- **釋放條件要看物理佔用,不能只看任務狀態**:這是最容易錯的一點。「B 何時算空出來」要定義成「貨真的被取走 / 車真的離開 B」,而不是「上一筆任務的狀態變成 done」——否則會出現「任務說完成了、車還停在 B 上,下一台就撞上去」(正是 Open-RMF mutex 那個已知坑)。

---

## 5. 綜合判斷:沒有單一正解

這題本質是**一致性/安全 ↔ 吞吐/彈性**的取捨,跟場景強相關,沒有放諸四海的最佳解。

| 維度 | 策略一(預排即拒絕 / 悲觀鎖) | 策略二(允許排入 + 序列化) |
|---|---|---|
| 一致性/安全 | 強。占用即拒,不可能兩單同時寫 B | 靠序列化條件保證,取決於釋放與防死結設計 |
| 吞吐/彈性 | 低。逼使用者手動分批、等前筆做完 | 高。一次排入、自動交錯流水 |
| 實作複雜度 | 低。一個預定旗標 + 拒絕邏輯 | 高。要管 queue、釋放條件、死結/飢餓防護 |
| 失效模式 | 體感卡、需人工介入;但不會死結 | 設計不良會 deadlock / 飢餓 |
| 與主流分工契合 | 把上位職責拉到車隊層 | 貼近「上位塞、車隊消化」 |

**選型該看三個場景變數**:

1. **有沒有強勢上位(WMS/WES)**:有的話,「B 能否重複指派」本該由上位的儲位狀態決定;車隊層做策略一等於跟上位搶鎖、製造雙重事實來源。這種場域,習慣一次塞滿的上位會被策略一大量擋下。
2. **儲位是不是物理單佔、放錯代價多高**:若 B 單佔且放錯會撞貨/壓壞/出安全事故,策略一的保守值得;若 B 只是邏輯目的、衝突代價只是「多等一下」,策略二的吞吐優勢明顯。
3. **任務交錯密度與是否要自動流水**:像本例這種高交錯、又期望「自動交錯流水」的場景,策略一的手動分批會直接變成吞吐瓶頸。

**比較務實的方向(非定論)**:業界與學界的成熟做法**既不是純策略一、也不是裸策略二**,而是混合體——**樂觀允許進入 + 帶時間窗的動態預定 + 明確的物理釋放條件 + 租約心跳 timeout + aging 防飢餓**。更實際的工程選擇是**讓策略可設定**:預設走策略二自動交錯,但對標記為「高衝突代價 / 物理單佔」的儲位,退化成策略一的悲觀鎖。

誠實的結論:**沒有單一正解**。安全代價高、儲位強單佔、本來就靠人工調度的場域,策略一簡單可靠;吞吐要求高、有強勢上位、任務高度交錯、要自動流水的場域,策略二(且必須補齊防死結/飢餓)才是主流方向。做不紮實的策略二,風險其實比策略一還高——這也是為什麼它「看起來彈性好」卻不能無腦選。

---

## 來源

- Open-RMF:[rmf_traffic](https://github.com/open-rmf/rmf_traffic)・[RMF core 章](https://osrf.github.io/ros2multirobotbook/rmf-core.html)・[mutex 釋放討論](https://github.com/open-rmf/rmf/discussions/466)・[rmf_reservation_node](https://docs.ros.org/en/rolling/p/rmf_reservation_node/)・[rmf_reservation](https://github.com/open-rmf/rmf_reservation)
- VDA5050:[spec(EN）](https://github.com/VDA5050/VDA5050/blob/main/VDA5050_EN.md)・[路口管理屬上位職責](https://github.com/VDA5050/VDA5050/discussions/110)
- 倉儲分層:[WCS/WES/WMS](https://kpisolutions.com/resources/wcs-vs-wes-vs-wms-the-software-behind-warehouse-operations/)・[AGV 車隊架構](https://www.smartloadinghub.com/insights/agv-amr/designing-agv-fleet-architecture-reliable-warehouse/)
- 經典 CS:[Optimistic concurrency control](https://en.wikipedia.org/wiki/Optimistic_concurrency_control)(列此供對照,策略二的「樂觀」指准入不上鎖,非此類 abort-retry)・[悲觀鎖/2PL](https://www.moderntreasury.com/learn/pessimistic-locking-vs-optimistic-locking)・[Banker's algorithm](https://en.wikipedia.org/wiki/Banker%27s_algorithm)・[Deadlock 四條件(UIC 課程)](https://www.cs.uic.edu/~jbell/CourseNotes/OperatingSystems/7_Deadlocks.html)
- MAPF/資源預定:[CBS 原始論文](https://www.sciencedirect.com/science/article/pii/S0004370214001386)・[CBS + precedence](https://arxiv.org/abs/2402.08772)・[動態資源預定(IEEE)](https://ieeexplore.ieee.org/document/10419190/)

> 註:部分來源(IEEE 全文、某些廠商頁)為付費或防爬,引用以標題/摘要層級論點為準(動態資源預定 → deadlock-free、儲位歸上位等),寫入正式評估前建議補讀全文。未發現「策略一 vs 策略二有公認量化基準」的單一權威來源——這本身也支持「沒有單一正解」。
