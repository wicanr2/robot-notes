# 數位影子:讓開發板上的韌體開 Isaac Sim 裡的 TurtleBot3

一塊 STM32 開發板跑著正式的 Rust 韌體,透過 ROS 2 指揮模擬器裡的一台 TurtleBot3 Burger(以下稱 TB3,一台差速兩輪小車),在 Isaac Sim 的空地上繞 1 m 正方形三圈。韌體的輸出決定 TB3 怎麼動,TB3 的輪子實際轉了多少再回到韌體,韌體看到的車速與里程都來自 Isaac 的物理。這種「真的控制器配上模擬的車」的做法,工程上叫硬體在環(HIL,Hardware-in-the-Loop)模擬。

這篇從「為什麼要這樣接」講起,接著推導兩邊的換算公式,說明誰負責安全,再一步步說明怎麼在一台 RTX 主機上把開發板、Isaac Sim、bridge 與控制串起來,最後是驗證方法與量到的數字。

> 來源:作者 2026 年 11 月的私人實驗紀錄(實驗計畫、逐輪收據、Isaac 腳本與 bridge 原始碼)。原始 repo 不公開,這裡只寫機制與量測結果,車型、廠商與通訊協定的實際數值都改成通稱。
> 延伸閱讀:[主板模擬:Renode](../10-core/20-firmware/board-simulation-renode.md)、[上下位機通訊](../10-core/20-firmware/host-mcu-protocol.md)、[底層控制](../10-core/20-firmware/low-level-control.md)、[運動學與座標轉換](../10-core/30-navigation/kinematics-and-coordinate-transforms.md)、[ROS 2 與 DDS](../40-fleet/ros2-dds-intro.md)、[Isaac Sim / Isaac Lab](isaac-sim-isaac-lab-amr.md)、[Sim-to-real](sim-to-real.md)。

---

## 1. 要解決的問題:韌體需要一台會「頂嘴」的車

韌體的工作是把上位命令變成馬達輸出,出錯時把車停下來。要驗證它,得有一台會回應的車。手上有四種選擇:

| 做法 | 能證明什麼 | 證明不了什麼 |
|---|---|---|
| 上實車 | 全部都是真的 | 貴、危險、難注入故障,位姿真值也要另架量測設備 |
| 主機上編譯或 Renode 模擬 | 邏輯、周邊行為,可重現 | MCU 的實際中斷與時序要上真板才算數 |
| 真板 + 板內模型 | 真的 MCU、真的中斷、真的接收路徑 | 模型參數是韌體作者自己給的,模型裡沒有的損失與打滑就永遠不會出現 |
| 真板 + 外部物理模擬 | 車實際怎麼動,由韌體以外的物理引擎決定 | 實體馬達、電氣與實車動態 |

第三列的盲點是關鍵。韌體帶著一個自己寫的車體模型,等於自問自答:模型說車速是多少,韌體就看到多少。要讓韌體被「頂嘴」,至少有一部分回授必須來自它控制不了的地方。這篇的做法是第四列:韌體照舊跑在真板上,車換成 Isaac Sim 裡的 TB3,由 PhysX 物理引擎決定輪子實際轉多少。

這裡要先說清楚哪些部分換成了物理、哪些還是模型(第 3 節會再走一次):

| 部分 | 由誰決定 |
|---|---|
| 牽引馬達控制器對命令的反應(一階滯後、逾時、故障) | 仍是板內模型 |
| 舵角 | 仍是板內模型。TB3 沒有轉向關節,沒有物理量可以回送 |
| 車實際走了多遠、走多快 | Isaac 的物理,經回送取代板內模型的行程積分 |

所以這個實驗驗的是「速度與里程這一環」:輪子打滑、損失、車比預期慢,這些板內模型給不出來的情況,現在由 PhysX 給。

選 TB3 有個實際的理由:它在 Isaac 裡已經有量過的基準。沒有韌體、直接下命令時,三圈回原點差 4.1 mm。接上韌體之後出問題,比較容易分辨是韌體還是車。

## 2. 數位模型、數位影子、數位分身

<p align="center"><img src="../../img/dshadow-three-levels.svg" width="900" alt="三欄:數位模型兩個方向都手動;數位影子實體到數位自動、反向手動;數位分身兩個方向都自動。下方各自對應這個實驗"></p>

這三個詞常被混用。Kritzinger 等人在 2018 年的回顧論文用一個標準區分:看「既有的實體物件」與數位物件之間,每個方向的資料是手動還是自動。

- **數位模型(Digital Model)**:兩個方向都手動。
- **數位影子(Digital Shadow)**:實體的狀態自動流進數位端,數位端要影響實體還是得靠人。
- **數位分身(Digital Twin)**:兩個方向都自動。

套到這個實驗要先問:哪一端是實體?整套系統裡唯一的實體是開發板與它跑的韌體;Isaac 裡的 TB3 是數位的。命令從韌體自動送進 Isaac,TB3 的運動也自動回到韌體,兩個方向都自動。照這個分類,資料流是分身的等級,但它的實體端只是一塊控制板,車本身是模擬的。這種配置的正式名稱就是前面說的硬體在環模擬。

那為什麼標題叫「數位影子」?這是借用回送方向的意象:TB3 的輪子實際轉多少,自動寫進韌體內的車輛狀態,韌體眼中的那台車一路追著 TB3 走,像影子一樣。這是本文取的說法,不是 Kritzinger 意義下的嚴格分類。只開板內模型時,韌體不和任何外部物件自動交換資料,可以對應到「數位模型」那一格。

## 3. 系統全貌

<p align="center"><img src="../../img/dshadow-architecture.svg" width="960" alt="RTX 主機上有 Isaac Sim、command_bridge、feedback_bridge、XRCE Agent 與 probe,經一條 USB 接到開發板。藍線是命令,橘線是韌體的回應,綠線是 TB3 的實際運動回到韌體"></p>

先認識圖上的角色:

| 角色 | 在哪 | 做什麼 |
|---|---|---|
| 任務節點 | Isaac 行程內 | 每 1/60 s 依 TB3 的真值位姿算出「現在」該走多快、轉多快 |
| `command_bridge` | 主機容器 | 任務的 (V, ω) 換成舵輪命令送給韌體;韌體模型輸出的舵輪速度換回 (V, ω) 給 TB3;也負責啟動 Agent、解鎖與注入異常 |
| `feedback_bridge` | 主機容器 | TB3 兩輪的關節位置,配上韌體回報的舵角 δ,換算成「虛擬舵輪」的實際速度,送回韌體 |
| XRCE Agent | 和 `command_bridge` 同一個容器 | XRCE(DDS for eXtremely Resource Constrained Environments)讓記憶體很小的 MCU 也能用序列埠加入 ROS 2。主機上的 Agent 把 DDS 資料轉成序列框,韌體裡的 XRCE client 負責另一端。這裡用官方的 Micro XRCE-DDS Agent v2.4.3,由 `command_bridge` 以序列埠模式啟動 |
| 韌體 | 開發板 | 正式的控制邏輯與 1 kHz 安全迴路,另外編入板內模擬對端 |
| 板內模擬對端(sim-peers) | 韌體內,建置時明確選用 | 扮演牽引馬達控制器、編碼器與舵角。CAN 幀經硬體回送(silent loopback)在它與韌體之間往返,所以韌體走的是正式的 CAN 接收中斷;DAC 的值則在驅動層寫出成功後交給它 |
| probe 容器 | 主機容器 | 用 probe-rs 經板上的 ST-LINK 燒錄、側錄 log、收尾讀計數 |

韌體這一側叫「舵輪車」:前方一個可轉向的驅動輪(舵輪),後方兩個固定輪,第 4 節會用到。`plant_out`、`plant_in` 裡的 plant 是控制理論的用語,指「被控制的對象」,也就是車。

每個元件只懂自己這一層。任務節點不知道有韌體,韌體不知道 TB3 的輪距,所有換算都在兩座 bridge 裡。

### 3.1 一筆命令的完整旅程

依圖上的編號走一圈:

1. 任務節點算出此刻的 (V, ω),送給 `command_bridge`(①)。
2. `command_bridge` 反算成舵輪命令 (v, δ),經 Agent 與序列埠送進韌體(②)。
3. 韌體的控制邏輯算出牽引命令與舵角,經 CAN 回送與 DAC 交給板內模型(③)。
4. 板內模型的牽引控制器依一階滯後算出舵輪速度,連同舵角每 20 ms 經 XRCE 發出(④,`plant_out`)。
5. `command_bridge` 把它換成 (V, ω) 送給 TB3(⑤)。TB3 收到的是模型的輸出,不是韌體收到的原始命令。
6. Isaac 推進物理,發出兩輪的關節位置(⑥)。
7. `feedback_bridge` 把關節位置換成虛擬舵輪方向的實際速度,送回韌體(⑦,`plant_in`)。
8. 板內模型改用這個速度積分行程,再像真的編碼器一樣經 CAN 回送回覆韌體的讀取請求(⑧)。韌體從編碼器讀值差分出車速與里程。

下表是三圈第 1 輪各段的筆數:

| 編號 | 從哪到哪 | 送的東西 | 頻率 | 第 1 輪的筆數 |
|---|---|---|---|---|
| ① | 任務節點 → `command_bridge` | 當下要的 V、ω | 60 Hz | 收到 10638 |
| ② | `command_bridge` → Agent → 序列埠 → 韌體 | 舵輪速度 v、舵角 δ、序號 | 20 Hz | 送 4098,韌體收到 4079 |
| ③ | 韌體 → 板內模擬對端 | 牽引命令(CAN)、兩路舵角 DAC | 50 Hz | 10599 幀;DAC 兩路共寫入 21724 次、失敗 0 |
| ④ | 板內模擬對端 → 韌體 → Agent → `command_bridge`(`plant_out`) | 模型算出的舵輪速度與舵角 | 50 Hz | 送 10349,收到 10241 |
| ⑤ | `command_bridge` → Isaac | 換算後的 V、ω | 50 Hz | 送 10241 |
| ⑥ | Isaac → `feedback_bridge` | 兩輪關節位置,帶模擬時間 | 60 Hz | 收到 10638 |
| ⑦ | `feedback_bridge` → Agent → 韌體(`plant_in`) | 虛擬舵輪方向的實際速度 | 50 Hz | 送 8864,韌體收到 8864 |
| ⑧ | 板內模擬對端 → 韌體 | 編碼器讀值,經 CAN 回送 | 200 Hz | 請求 42400,回覆 42399 |

- 各段開始計數的時間不同:韌體與 `command_bridge` 從 XRCE 連上就開始計,Isaac 那幾段從 Isaac 開始步進才計,所以「筆數 ÷ 頻率」不會相同。
- ④ 與 ⑤ 筆數相同,因為 TB3 收到的速度全部來自 ④。
- ② 少掉的 19 筆,絕大多數是 XRCE 連線還沒建好時送出的。④ 少掉的 108 筆,是 `command_bridge` 結束之後韌體才送出的。

筆數相符只代表有送到。內容也要核對:模擬對端的輸出換算成車體速度後,和 TB3 的真值比,線速度相關係數 0.9999、均方根誤差 1.9 mm/s。原地轉時,TB3 的真值角速度約是 ⑤ 送給它的 ω 的 0.92 倍。不接韌體、直接下命令時也是這個比例,所以這個差來自 Isaac 那一端,與韌體無關;是輪地接觸、關節驅動還是求解器造成的,沒有再查。

## 4. 換算:把差速車偽裝成舵輪車

韌體是為舵輪車寫的。TB3 是差速車,沒有舵輪。要讓韌體以為自己在開舵輪車,兩座 bridge 得在兩種運動描述之間換算。

<p align="center"><img src="../../img/dshadow-virtual-tricycle.svg" width="900" alt="TB3 俯視圖,在兩輪輪軸中點 O 前方 L 處畫一個不存在的虛擬舵輪。舵輪點的速度分成往前的 V 與往左的 Lω,合成方向就是舵角 δ"></p>

### 4.1 從舵輪點的速度推出來

把 TB3 的兩輪輪軸中點 O 當成舵輪車的後軸中點,在它前方 L 的地方想像一個舵輪。L 用目標車型的軸距。韌體的舵輪速度上限與偏航率上限是用這個 L 算出來的,bridge 用同一個值換算,上限才對得上。

車體以 ω 繞 O 轉、O 往前走 V。剛體上任一點的速度等於 O 的速度加上旋轉造成的速度,舵輪點在 O 前方 L,所以它的速度是 (V, Lω):往前 V,往左 Lω。

**命令方向(韌體 → TB3)。** 韌體的模型說舵輪沿 δ 方向滾 v。這裡的 v 是舵輪本身沿滾動方向的速度。輪子不側滑,表示舵輪點的速度整個落在滾動方向上:

```text
(V, Lω) = v (cos δ, sin δ)
⇒ V = v cos δ
   ω = v sin δ / L
```

δ = 0 時 ω = 0,直走。δ = 90° 時 V = 0、v = Lω,車在原地轉。

> 另一種常見寫法是 ω = V tan δ / L,用的是後軸速度 V。把 V = v cos δ 代進去就得到上面的式子。用後軸速度寫時,δ = 90° 會讓 V = 0、式子失去意義;用舵輪速度 v 寫,原地轉也能表示。[術語表](../../CONTEXT.md)裡的舵輪式子用的是後軸速度。

**回送方向(TB3 → 韌體)。** TB3 實際的 V_a、ω_a 不一定剛好符合「不側滑」。韌體的編碼器量的是舵輪沿滾動方向轉了多少,所以把舵輪點的實際速度投影到滾動方向:

```text
v_fb = V_a cos δ + L ω_a sin δ
```

垂直滾動方向的分量是側滑,真實的編碼器量不到,這裡也丟掉。沒有任何損失時,把命令方向的式子代進去,v_fb 剛好等於 v。δ 由韌體每 20 ms 在 `plant_out` 裡回報,`feedback_bridge` 因此也訂閱 `plant_out`。

**反算(任務 → 韌體)。** 上位任務送來的是 (V, ω),`command_bridge` 要先反算成舵輪命令。倒車時舵輪不翻 180°,改成輪速取負號,所以分兩支:

```text
V ≥ 0:δ = atan2(Lω, V),     v = +√(V² + L²ω²)
V < 0:δ = atan2(−Lω, −V),   v = −√(V² + L²ω²)
V、ω 都在停止門檻內:送 0
```

### 4.2 TB3 的實際速度從哪來

`feedback_bridge` 用兩輪**關節位置的差分**算 V_a、ω_a,不用 PhysX 給的關節速度讀值。真車的編碼器量的是位置,這樣比較接近真車的資訊來源。

```text
V_a = r (Δθ_r + Δθ_l) / (2Δt)
ω_a = r (Δθ_r − Δθ_l) / (b Δt)
```

TB3 的輪半徑 r = 0.033 m、輪距 b = 0.160 m,執行時由 USD(Isaac 用的 3D 場景格式)模型的包圍盒讀回核對。實作有兩個細節:

- 轉動關節的位置在 (−π, π] 之間繞回,差分前要先把差值折回這個範圍,否則每轉一圈會跳一次 2π。前提是兩個樣本之間輪子轉不到半圈:60 Hz 取樣下輪速要低於約 188 rad/s,這裡的輪速約 6 rad/s。
- Isaac 每 1/60 s 發一筆關節位置,回送是 50 Hz。每次回送要把這段時間內的所有差分累加起來求平均,只取最後一步會漏掉中間的運動。

### 4.3 bridge 不幫忙

對韌體這一側,兩座 bridge 只做換算,不夾限、不逾時,也不幫忙停車。速度上限、命令逾時與故障停車都要由韌體自己證明。bridge 多做一點保護,就分不清車停下來是誰的功勞。

有兩個刻意的例外,都在「上位」或「環境」那一側:

- 任務的 (V, ω) 超過 0.5 s 沒更新,`command_bridge` 持續送 0。它不停送,因為停送會讓韌體逾時切輸出並重新鎖定。
- `plant_out` 超過 0.3 s 沒來,`command_bridge` 把 TB3 歸零,記一次環境停車。判讀器把這種輪次判成環境失敗,不算進韌體的量測。

另外,`command_bridge` 有一個測試用的縮放參數,可以把送給 TB3 的速度乘上固定倍率,第 5.2 節的「打 8 折」就是從這裡注入的。

## 5. 控制:安全由韌體負責

### 5.1 命令一筆一筆送

韌體從頭到尾只知道「此刻」的命令,下一段路長什麼樣它不知道。所以只要命令停止進來,車自然會停。

- 任務節點以 60 Hz 計算此刻的 (V, ω)。
- `command_bridge` 以 20 Hz 拿手上最新的 (V, ω),換成一筆舵輪命令送出。
- Agent 只轉送當下這一筆,不保存整段路徑。
- 韌體用一個只放得下一筆的命令信箱,新的來就蓋掉舊的。信箱裡的命令放了 200 ms 還沒被更新,韌體就切掉輸出。
- 想馬上停,上位直接送停止命令,省掉那 200 ms。

<p align="center"><img src="../../img/dshadow-mailbox-timeline.svg" width="900" alt="時間軸:命令每 50 ms 一筆,信箱每來一筆就蓋掉舊的;命令流斷掉 200 ms 後韌體切輸出,車速依一階滯後衰減,約 1.1 s 回報已停"></p>

信箱只留一筆的理由:佇列裡排著的舊命令,在命令流中斷後還會繼續把車往前推。只留最新一筆,停止的條件就只剩「有沒有新命令」。

車以 0.2 m/s 直走時,逐一製造下列狀況。每種跑 3 輪,表中是 3 輪的最小到最大,時間從狀況發生起算:

| 狀況 | 多久察覺 | 多久回報已停 | 多走的距離 |
|---|---|---|---|
| 上位送停止命令 | 0.03 到 0.06 s | 0.88 到 0.90 s | 5.4 到 5.5 cm |
| 命令流中斷 | 0.21 到 0.30 s | 1.10 到 1.14 s | 9.2 到 9.9 cm |
| 牽引控制器回報錯誤 | 0.23 到 0.30 s | 1.10 到 1.17 s | 10.0 到 11.2 cm |
| DAC 寫入失敗 | 0.20 到 0.25 s | 1.10 s | 9.1 到 9.6 cm |
| 編碼器沒有回應(⑧ 斷) | 0.23 到 0.25 s | 照設計不停車,改用前饋 | 車速維持 0.20 m/s |

「回報已停」的門檻是韌體回報的車速低於 0.01 m/s。命令流中斷那一列的距離可以拆成兩段:察覺前照原速走 0.2 到 0.3 s,約 4 到 6 cm;切輸出後車速依板內模型的一階滯後(時間常數 0.25 s)衰減,再走約 0.2 m/s × 0.25 s = 5 cm。兩段加起來和實測的 9 到 10 cm 相符。

幾個名詞:

- **鎖存**:故障發生後一直保持「故障」狀態,條件消失也不自動解除。DAC 寫入連續失敗 200 ms 就鎖存,要重開機或明確清除才能再走。
- **斜坡**:速度命令不直接跳到目標值,而是以固定的加減速率爬上去。停止命令全部解除後,車照斜坡恢復,不必重新解鎖。停止命令依來源分別記住,任一來源要求就切輸出,解除只解除該來源。
- **前饋**:不看量測,直接依命令與已知的對應表給輸出。編碼器斷線時,韌體失去速度量測,照設計退回前饋繼續走;這個選擇的理由,原始紀錄沒有寫。

### 5.2 回授讓韌體修正

`command_bridge` 把送給 TB3 的速度打 8 折,模擬「車比碼表慢」。韌體從回送看到車速偏低,把輸出補上去。3 輪最後 2 s 的真值車速落在 0.2003 與 0.2005 m/s 之間。這是閉迴路的主要證據,第 7 節用負對照證明補償確實來自 Isaac 的物理。

### 5.3 回送斷掉時

這裡有兩條不同的回授,斷掉時的反應也不同:

| 斷掉的是 | 韌體的反應 | 怎麼被發現 |
|---|---|---|
| ⑦ Isaac 的回送超過 200 ms 沒更新 | 板內模型改回自己積分行程,累計一次過期計數 | 判讀器檢查計數 |
| ⑧ 編碼器的 CAN 回覆停了 | 失去速度量測,改用前饋,不停車 | 韌體回報感測器狀態異常 |

⑦ 斷掉時選擇退回內部模型,理由是 Agent 中斷時韌體會停車。這時若沿用最後一筆回送速度,模擬的編碼器讀值會一直增加,車明明停了里程卻繼續累積,重新連線後的解鎖與量測都失去意義。

退回本身是靜默的,判讀器因此同時要求兩件事:

- 韌體收到的回送筆數大於 0。從沒收到回送時過期計數不會累計,只看計數會漏掉「完全沒回送」的情況。
- 解鎖之後過期計數沒有增加。

## 6. 在 RTX 主機上組起來

### 6.1 硬體

| 項目 | 這個實驗用的 | 說明 |
|---|---|---|
| 主機 | 28 核、61 GiB 記憶體、RTX 2000 Ada 16 GB | 和別人共用,實驗最多佔 14 核。要裝 NVIDIA 驅動與 NVIDIA Container Toolkit,Docker 才能用 `--gpus` |
| 開發板 | NUCLEO-F767ZI(Cortex-M7) | 和正式韌體同一份原始碼,建置時多開開發板與模擬對端的 feature(`nucleo-f767zi,sim-isaac`)。正式板是另一顆 Cortex-M4 |
| 線材 | 一條 USB | 板上的 ST-LINK 同時提供除錯通道與虛擬序列埠 |

開發板和主機之間只有一條 USB,上面有兩條通道:

- **SWD(Serial Wire Debug)**:ARM 的兩線除錯介面。用來燒錄、重置,也能在 CPU 執行中直接讀記憶體。收尾讀韌體計數靠它。
- **RTT(Real-Time Transfer)**:走在 SWD 上。韌體把 log 寫進記憶體裡的環形緩衝,除錯器讀走,不佔序列埠。把它持續記錄下來叫側錄。
- **虛擬序列埠(VCP)**:ST-LINK 把板上的 UART 轉成主機上的 `/dev/ttyACM*`。XRCE 走這條,115200 bps。

板上沒有實體的 CAN 收發器、DAC 晶片與馬達:

- CAN 控制器設成 silent loopback,幀經過真的 CAN 周邊,但不上線。
- DAC 的 SPI 照常送出,板上沒接晶片。SPI 主端不需要接收端也送得完,所以「寫入失敗」要靠異常注入才走得到。
- 馬達控制器、編碼器與舵角都在板內模擬對端裡。

### 6.2 主控腳本與容器配置

整輪由一支**主控腳本**指揮。它是一個在主機上直接執行的命令列程式,不在容器內,負責開跑前盤點、依序啟動容器、等旗標檔、收尾讀計數、最後呼叫**判讀器**。判讀器是另一支程式,讀這一輪的**收據**(log、計數、軌跡、韌體與映像的雜湊),依開跑前寫好的條件判 PASS 或 FAIL。

其餘每個元件各自一個 Docker 容器,用完即刪(`--rm`),以目前使用者的 UID/GID 執行,並限制記憶體、CPU、行程數與 log 大小。

| 容器 | 映像 | CPU | 記憶體 | 裝置 |
|---|---|---|---|---|
| Isaac Sim | `nvcr.io/nvidia/isaac-sim:6.0.1` | 綁 0 到 11 號核 | 16 GiB | `--gpus all` |
| `command_bridge` + Agent | 自建的 ROS 2 Jazzy + Rust 映像 | 綁 12、13 號核 | 3 GiB | 序列埠 |
| `feedback_bridge` | 同上 | 共用 12、13 | 1 GiB | 無 |
| probe | 自建,內含 probe-rs | 共用 12、13 | 512 MiB | USB 除錯器 |

網路的做法:

- `command_bridge` 的容器用 `--network none --ipc shareable` 起來,持有網路與 IPC(共享記憶體)的命名空間。`--network none` 底下仍有容器自己的 loopback 介面,只是沒有對外網卡。
- 其他容器用 `--network container:<command_bridge> --ipc container:<command_bridge>` 加入同一組命名空間,所以整組都對外無網路。
- 全部設同一個 `ROS_DOMAIN_ID`、同一個 RMW 實作(Fast DDS),並限制只在本機探索(`ROS_LOCALHOST_ONLY=1`)。

為什麼兩個命名空間都要共用:DDS 的探索(找到彼此)走 loopback 上的 UDP,所以要共用網路命名空間;同一台機器上的資料,Fast DDS 會改走共享記憶體,所以 `/dev/shm` 也要共用,也就是 IPC 命名空間。整組關在 `--network none` 裡,和共用主機上其他人的 DDS 完全隔開。

> `ROS_LOCALHOST_ONLY` 從 ROS 2 Iron 起列為棄用,新寫法是 `ROS_AUTOMATIC_DISCOVERY_RANGE=LOCALHOST`。Jazzy 仍接受舊變數。

CPU 以 `--cpuset-cpus` 綁定固定核心為主,`--cpus` 只當上限。Isaac 依看得到的核數開 worker 執行緒。早期試過只用 `--cpus 6` 的時間配額、不綁核,28 個 worker 搶 6 核的時間,不限速時的即時率只有 0.64 到 0.87,每輪還差很多;綁 12 核後,不限速的即時率是 4.17,兩輪一致。不限速的數字代表餘裕:有 4 倍的餘裕,正式輪次限速到 1 時才穩得住。

### 6.3 一輪的順序

<p align="center"><img src="../../img/dshadow-run-sequence.svg" width="940" alt="時序圖:盤點、燒錄、起 command_bridge、起 feedback_bridge、feedback_ready、啟動 Agent、起 Isaac、回送開始流、清異常與解鎖、armed 檔、任務跑完、讀計數、判讀"></p>

容器之間用收據目錄裡的旗標檔排順序,這個目錄同時掛進每個容器。幾個順序有它的理由:

- **`feedback_bridge` 要在 Agent 啟動前就緒。** 它為了取舵角 δ,也訂閱 `plant_out`。早期它在 Agent 已經收發資料之後才加入,約半數輪次在解鎖前出現約 360 ms 的 `plant_out` 中斷。改成先讓它建好訂閱、再啟動 Agent 之後,這個中斷就落在資料開始流之前,不再影響量測。中斷的時間點和它加入 DDS 的時間吻合,但 DDS 內部為什麼會卡住,沒有查證。
- **清掉殘留異常、有狀態、有回送才解鎖。** 解鎖(arm)是韌體允許輸出的狀態,沒解鎖時不論收到什麼命令都不輸出。`command_bridge` 先清掉板內殘留的異常,等收到韌體的狀態回報、而且韌體已收到回送,才呼叫解鎖服務。解鎖前車不動,回送的空檔不影響里程;解鎖時回送已經在流,韌體從第一步就用 Isaac 的物理。
- **Isaac 看到 armed 檔才開始任務。** 之前它照常步進、發關節位置,讓回送先流起來。
- **收尾經 SWD 讀計數。** 序列埠溢位、送出等待、DAC 寫入次數、回送收到數與過期次數都存在韌體的記憶體裡。經 SWD 直接讀出來,不經韌體的通訊路徑回報,通訊出問題時也讀得到。

### 6.4 Isaac 端:RTX 要注意的事

Isaac 這一端是一支 Python 腳本(以下稱 Isaac 腳本),用 `SimulationApp({"headless": True})` 無畫面啟動,透過 rclpy 收發 ROS 2,不經 OmniGraph。

**物理與迴圈。** `World` 設 `physics_dt = 1/240`、`rendering_dt = 1/60`,控制迴圈 60 Hz,每圈走 4 個物理子步。輪子的關節驅動設成速度控制:stiffness 0 表示不追位置,damping 就成了速度增益(腳本預設 damping 1000、最大力矩 5 N·m)。Isaac 的 `DifferentialController` 把 (V, ω) 換成兩輪角速度。物理 60 Hz 時原地轉的實際速度只有命令的 0.23 倍,240 Hz 是 0.92 倍,所以接韌體的輪次都用 240 Hz。

**一個不會報錯的坑。** 呼叫 `world.step(render=False)` 時,物理只前進一個 `physics_dt`(1/240 s)。每圈若只呼叫一次,物理時間只有迴圈時間的 1/4。這時兩個常看的指標都騙得過人:即時率是用迴圈累計的時間算的,照樣接近 1;任務節點靠真值位姿閉環,車慢一點也會走回原點。這個 bug 是在輪速與實際車速對不上時抓到的。修法是每圈呼叫 4 次,並在結束時核對「迴圈累計的時間」等於「PhysX 讀回的物理時間」。

**兩邊的時鐘要一致。** 韌體用 MCU 的毫秒計時器積分里程,Isaac 的時間則由模擬步數決定。模擬跑得比真實快或慢,同一段運動在兩邊就換算出不同的車速,而且沒有任何一層會報錯。處理方式:

- Isaac 腳本依牆鐘(真實世界的時間)限速,每步算完就睡到該到的時間。
- 每 10 s 記一次即時率。只要有一段落在 0.95 到 1.05 之外,那一輪就算環境失敗,數字不拿來評估韌體。

**渲染與錄影。** 在 RTX 2000 上一邊模擬一邊出畫面,算圖拖慢了模擬,韌體里程與 Isaac 行程的比值變成 1.84,那一輪只能作廢。所以跑的當下不渲染,只把每個 60 Hz 迴圈步的 PhysX 真值位姿寫進 `trajectory.csv`。事後另起一個 Isaac,照軌跡把 TB3 擺回當時的位姿,用 RTX 相機出影格,再和韌體的 RTT log 依時間並排合成影片,畫面上標明是軌跡重播。物理與渲染分開跑,渲染多慢都不影響實驗。

**理想化項。** 輪子的碰撞體換成同半徑的球,腳輪摩擦設 0。這兩項讓基準乾淨,但也是和真車的差異,報告裡要列出來。

**生效要自己證明。** 幾個回傳值不可信的地方:

- 啟用 ROS 2 bridge 擴充時,`enable_extension` 回傳成功不代表真的載入。要在已註冊的節點型別裡找得到 bridge 的節點,才算它活著。
- 腳本裡拋出的 Python 例外,不會讓 Isaac 行程以非零結束碼退出。Isaac 腳本另外把成敗寫進 `env.json` 的 `ok` 欄位,主控腳本依這個欄位判斷。
- `app.close()` 偶爾會卡住。結果寫完後直接 `os._exit`,不讓它拖住外層的逾時。
- 輪子的半徑與輪距執行時從模型讀回,和常數比對,寫進收據。

### 6.5 指令骨架

下面依時序圖的編號整理,名稱、路徑與 topic 命名空間 `<ns>` 都是示意。主控腳本做的事以註解標出。

先找裝置:

```bash
lsusb -d 0483:                          # ST-LINK 的 bus 與 device 編號 → /dev/bus/usb/<bus>/<dev>
ls -l /dev/serial/by-id/ | grep STLink  # 虛擬序列埠;/dev/ttyACM* 的編號會變,從 by-id 找
TTY=$(readlink -f /dev/serial/by-id/<stlink>-if02)   # 解出實際的 /dev/ttyACM*
stat -c %g "$TTY"                       # 序列埠的群組 ID,給 --group-add
```

再依序啟動:

```bash
COMMON="--rm --user $(id -u):$(id -g) -e HOME=/tmp --log-opt max-size=10m --log-opt max-file=3"
PROBE="docker run $COMMON --network none --memory 512m --cpuset-cpus 12-13 --pids-limit 64 \
  --device /dev/bus/usb/<bus>/<dev> --group-add <usb-gid> -v $PWD/fw:/fw:ro <probe-image>"

# ② 燒錄、重置,不重置地 attach(保留開機訊息),背景側錄 RTT
$PROBE probe-rs download --chip STM32F767ZITx --connect-under-reset --verify /fw/firmware.elf
$PROBE probe-rs reset --chip STM32F767ZITx --connect-under-reset
docker run $COMMON --name exp-rtt --network none --memory 512m --pids-limit 64 \
  --device /dev/bus/usb/<bus>/<dev> --group-add <usb-gid> -v $PWD/fw:/fw:ro <probe-image> \
  probe-rs attach --chip STM32F767ZITx /fw/firmware.elf > run/rtt.log &

# ③ command_bridge + Agent:持有網路與 IPC,掛序列埠。
#    它等 feedback_ready 出現才啟動 MicroXRCEAgent serial --dev /dev/ttyFW0 -b 115200(⑥),
#    之後清異常、等狀態與回送、呼叫 <ns>/set_armed 解鎖(⑩),成功後建 armed 檔(⑪)
docker run $COMMON --name exp-cmd --network none --ipc shareable --shm-size 1g \
  --cpuset-cpus 12-13 --cpus 2 --memory 3g --pids-limit 512 \
  --device "$TTY":/dev/ttyFW0 --group-add <tty-gid> \
  -e ROS_DOMAIN_ID=0 -e ROS_LOCALHOST_ONLY=1 -e RMW_IMPLEMENTATION=rmw_fastrtps_cpp \
  -v $PWD/run:/w/run <ros2-rust-image> command_bridge --agent-after /w/run/feedback_ready ... &

# ④ feedback_bridge:加入同一組命名空間,建好訂閱後寫 feedback_ready(⑤)
docker run $COMMON --name exp-fb --network container:exp-cmd --ipc container:exp-cmd \
  --cpuset-cpus 12-13 --cpus 1 --memory 1g --pids-limit 256 \
  -e ROS_DOMAIN_ID=0 -e ROS_LOCALHOST_ONLY=1 -e RMW_IMPLEMENTATION=rmw_fastrtps_cpp \
  -v $PWD/run:/w/run <ros2-rust-image> feedback_bridge --ready-file /w/run/feedback_ready ... &

# ⑦ Isaac Sim:GPU、綁 12 核、無畫面;看到 armed 檔才開始任務,跑完寫 mission_done(⑫)
docker run $COMMON --name exp-isaac --gpus all --network container:exp-cmd --ipc container:exp-cmd \
  --cpuset-cpus 0-11 --cpus 12 --memory 16g --pids-limit 1024 \
  -e ACCEPT_EULA=Y -e PRIVACY_CONSENT=Y \
  -e ROS_DOMAIN_ID=0 -e ROS_LOCALHOST_ONLY=1 -e ROS_DISTRO=jazzy \
  -e RMW_IMPLEMENTATION=rmw_fastrtps_cpp \
  -e LD_LIBRARY_PATH=/isaac-sim/exts/isaacsim.ros2.core/jazzy/lib \
  -v $PWD/isaac:/w/isaac:ro -v $PWD/assets:/w/assets:ro -v $PWD/run:/w/run \
  --entrypoint /isaac-sim/python.sh nvcr.io/nvidia/isaac-sim:6.0.1 \
  /w/isaac/tb3_run.py --hz 240 --sample-hz 60 --start-file /w/run/armed --done-file /w/run/mission_done ...

# ⑬ 收尾:先停 RTT(它佔著 ST-LINK),再逐一讀計數。位址事先用 nm 從 ELF 查出
docker stop exp-rtt
$PROBE probe-rs read --chip STM32F767ZITx b32 <addr> 1

# ⑭ 判讀
judge <case> run/
```

- Isaac 映像裡內建 ROS 2 Jazzy 的函式庫,用 `LD_LIBRARY_PATH` 指過去,容器裡不必另裝 ROS 2。
- TB3 的 USD 模型事先在有網路的機器上抓好,唯讀掛進去。Isaac 容器加入的是 `exp-cmd` 的命名空間,而那個命名空間本身是 `--network none`,所以 Isaac 一樣看不到外網,也不需要。

## 7. 怎麼證明它真的閉環

「車走完了」不足以證明任何事。車可能根本沒經過韌體,韌體可能偷偷用自己的模型,停車可能是注入本身造成的。這個實驗用三個手段把這些可能逐一排除。

**判準先寫死。** 每個階段開跑前,先把通過條件寫成文件提交到版控,看到結果後不再調鬆。每個案例跑 3 輪,3 輪同向才算數。

**鏈路對帳。** 相鄰兩段的筆數要對得上(第 3 節的表)。韌體只開機一次、故障位元為 0、序列埠沒有溢位、DAC 寫入失敗為 0,這些都寫進每輪的收據,連同韌體與映像的雜湊。

**負對照。** 每一個「靠韌體才通過」的說法,都配一個拿掉那個機制的版本,結果必須 FAIL,而且判讀器給的原因要和預期一字不差。

| 負對照 | 拿掉或改掉什麼 | 結果 | 證明什麼 |
|---|---|---|---|
| N1 | 讓板內模型的牽引卡死 | TB3 完全沒動 | TB3 的動作來自模型輸出 |
| N2 | 不經韌體,任務的命令直送 TB3 | 車照樣走完,但筆數對帳不過 | 判讀器看得出命令有沒有經過韌體 |
| N3 | 送出超過行走上限的命令 | 韌體拒收,車不動 | 上限確實生效 |
| N4 | 送給 TB3 的速度打 8 折,回送卻填命令值 | 真值只剩 0.158 m/s | 第 5.2 節的補償要靠真的回送 |
| N5 | 一筆回送都不發 | 「回送有在用」這一項不過 | 韌體改用自己的模型時會被發現 |
| N6 | 解鎖後暫停回送 1 s | 「回送沒有過期」這一項不過 | 跑到一半的回送中斷也會被發現 |
| N7 | 另建一顆拿掉 DAC 故障機制的韌體 | 車繼續走 | DAC 故障停車靠的是韌體 |
| N8 | 另建一顆拿掉停止命令的韌體 | 要求停止後的 4 s 內車走了 0.80 m(有機制時約 5.5 cm) | 停止命令靠的是韌體 |

<p align="center"><img src="../../img/dshadow-feedback-proof.svg" width="800" alt="長條圖:C1 回送實際運動時,韌體回報 0.2000、真值 0.2004 m/s;N4 回送填命令值時,韌體回報 0.2000、真值只有 0.1580 m/s"></p>

C1 和 N4 的韌體都回報 0.2000 m/s,差別只在回送的是什麼。只看韌體的回報分不出兩者,要看 Isaac 的真值才分得出來。

一個踩過的坑:板內異常存在跨重置保留的記憶體區,重燒與重置都不會清。試跑時注入的「牽引卡住」沒被清掉,之後幾個負對照的 FAIL 其實是車被卡住造成的,只是剛好符合預期。所以判讀器除了 FAIL,還要核對原因與車有沒有動;`command_bridge` 解鎖前清掉全部異常,判讀器要求開機時的異常遮罩為 0。

## 8. 結果

正式批次共 14 個案例、各 3 輪,合計 42 輪;加上 N7、N8 各 3 輪,結果與原因都和開跑前寫下的預期一致。沒有任何一輪因即時率偏離而作廢。

| 項目(正方形三圈) | 第 1 輪 | 第 2 輪 | 第 3 輪 | 通過條件 |
|---|---|---|---|---|
| 回原點差 | 10.7 mm | 11.9 mm | 10.6 mm | ≤ 5 cm |
| 偏航差 | 0.535° | 0.607° | 0.617° | ≤ 1° |
| 韌體里程 ÷ Isaac 行程 | 0.9920 | 0.9939 | 0.9914 | 1 ± 2% |
| 回送往返延遲 p99 | 48.5 ms | 44.8 ms | 48.6 ms | 只記錄 |

- **里程比**的分母是直行段 TB3 兩輪關節的平均行程。它確認韌體的里程與 Isaac 的輪子轉動一致,但單靠它排除不了「韌體偷用自己的模型」:不回送的 N5,依韌體回報與真值估算,比值約 1.01 到 1.02,同樣落在 ±2% 內。排除這種情況靠的是第 5.3 節的兩個條件,以及 C1 與 N4 的對照。
- **回送往返延遲**從 `feedback_bridge` 送出一筆 `plant_in` 算起,到收到韌體帶回這個序號的 `plant_out` 為止。它包含兩次序列埠傳輸與最多 20 ms 的 `plant_out` 週期,不含 Isaac 算一步的時間。

回原點差有散布。三圈的實驗前後共跑了 24 輪(含換韌體版本重跑與交替比較),回原點差最小 2.1 mm、最大 29.8 mm,都在通過條件內。散布來自 `command_bridge` 每 50 ms 才送一次命令:

- 直線段的長度固定,走完它的時間也固定,於是「該停了」那一刻容易落在兩次送命令的交界。
- 趕上這一次送出,停車滑行一種長度。晚一個控制迴圈步(1/60 s ≈ 16.7 ms)沒趕上,停止命令要等下一次,也就是晚 50 ms 送出;相對「該停」的時刻多晚了 50 − 16.7 ≈ 33 ms,滑行多約 8 mm。
- 一輪裡所有轉角都落在同一種時,誤差互相抵消;混了兩種就抵消不掉。
- 命令提高到 50 Hz 的探索輪裡,錯過一次只多等 20 ms,和「晚一個迴圈步」幾乎抵銷,兩種滑行長度併成一種,觀察結果也是如此。

這個量化大約是「車速 × 命令週期」,車越快越明顯。

## 9. 限制

- 沒有實車,也沒有實體馬達、DAC 晶片與 CAN 收發器。板內模型的參數都是估值,TB3 的結果不能推論到目標車型的動態。
- 牽引控制器的反應與舵角仍是板內模型,只有速度與里程換成了物理。
- 開發板是 Cortex-M7,正式板是 Cortex-M4,執行週期數不能直接搬過去。
- 從 PhysX 到韌體的實際延遲比實車長:Isaac 算一步、50 Hz 的平均窗、ROS 2、Agent、115200 bps 的序列埠都在路上。這段總延遲沒有直接量;量到的回送往返 p99 約 45 到 49 ms,只涵蓋主機到韌體來回那一段。上板前在主機的原生測試量過,速度迴路在 200 ms 以內的回授延遲都穩定。
- DAC 故障只看得到 SPI 傳輸有沒有完成。DAC 晶片本身壞掉或接線斷了,SPI 依舊能送完,韌體察覺不到。
- 解鎖前偶爾有約 350 ms 的韌體狀態回報空檔,和第 6.3 節已避開的 `plant_out` 中斷是兩件事。Agent 開到最細的 log 顯示,空檔期間序列埠接收照常,寫進 DDS 停了約 338 ms,可以排除韌體與序列埠;卡在 Fast DDS 的哪個環節還沒查。這個空檔只出現在解鎖前。
- 影片是事後的軌跡重播,車的位置與韌體 log 都是當輪紀錄,但畫面不是即時渲染。

## 10. 名詞

| 詞 | 一句話 |
|---|---|
| 硬體在環(HIL) | 真的控制器配上模擬的受控對象,一起跑閉迴路 |
| 數位影子(Digital Shadow) | 實體狀態自動流進數位端,反向仍靠人工。本文標題借用回送方向的意象 |
| 板內模擬對端(sim-peers) | 編進韌體、扮演馬達控制器與感測器的模型,CAN 經硬體回送接上韌體的正式接收路徑 |
| 虛擬舵輪 | TB3 沒有的舵輪。韌體眼中的 (v, δ) 經換算對應到 TB3 的 (V, ω) |
| plant、`plant_out`、`plant_in` | plant 指被控制的對象(車)。`plant_out` 是板內模型的輸出,`plant_in` 是送回模型的 Isaac 回送 |
| 解鎖(arm) | 韌體允許輸出的狀態。沒解鎖時不論收到什麼命令都不輸出 |
| XRCE | 小型 MCU 用序列埠加入 ROS 2 的協定;MCU 上跑 client,主機上的 Agent 轉進 DDS |
| SWD / RTT | ARM 的兩線除錯介面 / 走在 SWD 上、讀走記憶體裡 log 的機制 |
| 側錄 | 把 RTT log 持續記錄成檔案 |
| 前饋 | 不看量測,直接依命令與已知對應表給輸出 |
| 鎖存 | 故障發生後保持故障狀態,要明確清除才解除 |
| 斜坡 | 速度以固定的加減速率爬向目標值,不直接跳過去 |
| 即時率(real-time factor) | 模擬時間 ÷ 牆鐘時間,1 表示和真實時間一樣快 |
| 牆鐘 | 真實世界的時間,相對於模擬時間 |
| USD | Isaac 用的 3D 場景與模型格式 |
| 收據 | 每輪留下的 log、計數、軌跡與版本雜湊,判讀器只看它 |
| 判讀器 | 讀收據、依開跑前寫死的條件判 PASS 或 FAIL 的程式 |
| 負對照 | 刻意拿掉某個機制,結果必須 FAIL,用來證明通過是靠那個機制 |
| 軌跡重播 | 跑完後照紀錄把車擺回當時的位姿,再渲染成影格 |

## 來源

- W. Kritzinger, M. Karner, G. Traar, J. Henjes, W. Sihn, "Digital Twin in manufacturing: A categorical literature review and classification," *IFAC-PapersOnLine* 51(11), 2018, pp. 1016–1022. DOI [10.1016/j.ifacol.2018.08.474](https://doi.org/10.1016/j.ifacol.2018.08.474)。
- ROS 2 Iron Irwini 版本說明,`ROS_LOCALHOST_ONLY` 的棄用與 `ROS_AUTOMATIC_DISCOVERY_RANGE`:<https://docs.ros.org/en/rolling/Releases/Release-Iron-Irwini.html>。
- NVIDIA Isaac Sim 容器映像 `nvcr.io/nvidia/isaac-sim:6.0.1`。
- 實驗計畫、逐輪結果、Isaac 腳本與 bridge 原始碼:作者的私人 repo(2026-11),不公開。
