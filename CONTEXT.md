# CONTEXT — 術語表(Ubiquitous Language)

本筆記共用的詞彙與一句話定義,寫文件、命名、討論時優先用這裡的詞。格式:`術語 — 定義`。

## 系統分層
- 上位機(High-level)— 跑 ROS2/Linux,負責 SLAM、定位、路徑規劃、避障的高運算層。
- 下位機(Low-level)— 跑 STM32 韌體,負責馬達閉迴路、odometry、急停等硬即時功能。
- AMR — Autonomous Mobile Robot,自主移動機器人;送餐機器人是室內 AMR。

## 機構與動力
- 差速驅動(Differential Drive)— 兩個獨立驅動輪 + 萬向輪,靠左右輪速差轉向。
- 輪轂馬達(Hub Motor)— 馬達整合在輪子裡的形式。
- BLDC — 無刷直流馬達。
- FOC — 磁場導向控制,現代無刷馬達的主流控制法。
- 行星減速機 — 用行星齒輪組放大扭矩、降低轉速的減速機構。

## 感測與定位
- Encoder(編碼器)— 量輪子轉動量的感測器,odometry 與速度環的回授來源。
- Odometry(里程定位)— 用輪子轉動量推算位移,相對定位、誤差只增不減。
- IMU — 慣性量測單元,量姿態/角速度,與 odometry 融合。
- 2D LiDAR — 平面雷射掃描,SLAM 建圖與定位主力。
- SLAM — 同時定位與建圖。
- AMCL — 已知地圖下用 LiDAR 即時匹配的粒子濾波定位。
- 地標定位 — 用相機看已知地標(如 AprilTag)反推自己的絕對位姿。
- AprilTag — 機器人視覺常用的基準標記(fiducial marker),非 QR code。

## 導航(Nav2 / TF)
- Nav2 — ROS2 的導航軟體堆疊(規劃 + 控制 + 行為樹)。
- costmap(代價地圖)— 把空間切格、每格帶代價;分 static/obstacle/inflation 層。
- inflation(膨脹層)— 在障礙周圍鋪漸層代價,讓有體積的車保持距離。
- Hybrid-A* — 考慮車輛運動學(最小轉彎半徑、可否倒車)的全域規劃器;以 Dubins/Reeds-Shepp 為展開的運動模型與啟發式。Nav2 實作為 `nav2_smac_planner`(Smac Hybrid-A*)。
- Dubins 曲線 — 只能前進、最小轉彎半徑下兩 pose 間的最短路徑,6 種「弧-直-弧」候選。_Avoid_: 講成含倒車。
- Reeds-Shepp 曲線 — 允許倒車的最短 pose-to-pose 路徑,46 種候選、含換向點(cusp);目標在後方時比 Dubins 短。
- MPPI / DWB / RPP — Nav2 的三種區域控制器(取樣最佳化 / 動態視窗 / 純追蹤)。
- tf2 — ROS2 維護座標系關係的樹狀變換系統。
- base_link — 剛性固定在車身上、跟著車一起走的參考座標系;差速車通常設在兩驅動輪的軸心中點。路徑點與位姿預設都是描述這個點,不是車頭。
- 行為樹(Behavior Tree)— Nav2 用來編排規劃→跟隨→恢復的可組合結構。

## 路徑平滑與軌跡
- 曲率(Curvature)`κ` — 單位弧長內方向轉了多少,`κ = dθ/ds`。折線轉角處 `κ → ∞`,所以走不了。
- 路徑(Path) vs 軌跡(Trajectory)— 路徑 `p(s)` 只有形狀(參數是弧長);軌跡 `q(t)` 多了時間。兩者由時間參數化 `s(t)` 連起來。
- G0 / G1 / G2 / G3 — 幾何連續性階梯:位置 / 切線方向 / 曲率 / 曲率變化率。對應到「車頭方向不跳 / 轉向角不跳 / 轉向角速度不跳」。
- Cⁿ vs Gⁿ — 參數連續(導數相等)vs 幾何連續(只要求方向一致)。`Cⁿ ⇒ Gⁿ`,工程上在意的是 G。
- Bézier 曲線 — 由 `n+1` 個控制點與 Bernstein 基底定義的多項式曲線;端點切線由相鄰控制點差分直接給出。
- Bernstein 基底 — `Bᵢⁿ(t) = C(n,i) tⁱ (1−t)ⁿ⁻ⁱ`;非負且和為 1,故曲線是控制點的凸組合。
- 凸包性質 — Bézier/B-spline 曲線必落在控制點凸包內;碰撞檢查便宜的根源(凸包不撞 ⇒ 曲線不撞)。
- de Casteljau — 用反覆線性內插求值,順帶把曲線切成兩段;細分後凸包更貼近曲線,用於遞迴碰撞檢查。
- B-spline — 由節點向量(knot vector)與 Cox–de Boor 遞推定義;`p` 次在單重節點自動 `C^{p−1}` 連續。
- 局部支撐(Local support)— `Nᵢ,ₚ(u)` 只在有限區間非零 → 移動一個控制點只影響 `p+1` 個區段。Bézier 沒有這個性質。
- NURBS — 有理 B-spline(控制點帶權重);能精確表示圓錐曲線,多項式做不到。
- Hermite 樣條 — 由兩端「位置 + 切向量」決定的多項式;三次 Hermite 與三次 Bézier 是同一條曲線,`P₁ = p₀ + m₀/3`。
- Clothoid(迴旋曲線 / Euler spiral)— 曲率沿弧長線性變化 `κ(s) = κ₀ + c·s`,等速行駛時轉向角速度為常數;位置需 Fresnel 積分,無初等封閉解。
- Jerk(加加速度)— 加速度的時間導數。梯形速度曲線的 jerk 無限大;S 曲線(jerk-limited)把加速度也做成連續。
- 側向加速度上限 — `a_lat = v²κ ≤ a_lat,max` ⟹ `v(s) ≤ √(a_lat,max / κ(s))`,「彎道要減速」的第一性原理。

## 通訊與電路
- CAN — 內建協議(訊框/CRC/仲裁)的差分匯流排,馬達/BMS 多節點即時控制主場。
- RS485 — 只定義電氣層的差分匯流排,協議自定(常用 Modbus RTU)。
- Open-drain(開漏)— 只能拉低、靠上拉電阻補高的數位輸出形式。
- STO — Safe Torque Off,驅動器內建的安全轉矩關斷輸入。

> 命名約定:散文一律寫 **Open-RMF**(官方品牌);套件名 / repo / apt 套件保留 `open-rmf` 原文。

## 路網與交管
- 拓樸路網(Topological graph)— 人為在地圖上畫的節點 + 有向邊,車只准沿邊走;多車場域的主流空間表示。
- 自由空間(Free space)— 以佔據柵格描述可走區域,車可走任何未被佔據的格子(Nav2 costmap 的模型)。
- 道路級路網 — 疊在節點路網之上的粗圖(交叉口 junction + 道路多邊形 road),專供快速估距用。
- 前導線(Leadline)— 車沿路徑往前預約的距離 = 制動距離 + 延遲位移 + 車身長度 + 餘裕;純空間交管的核心參數。
- 滾動視窗佔用 — 只預約前方一小段、隨車前進往前推的空間預約法;不預測時間,故對 ETA 誤差不敏感。
- 時空排程(Spacetime scheduling)— 以「帶時間戳的軌跡」定義佔用,衝突 = 兩條軌跡在時空中相交(rmf_traffic 的模型)。
- Token(佔用權)— 一塊空間的通行權憑證。**動態 token** 由兩車路徑交疊自動產生;**固定 token** 是人工劃定的會車區,帶入場名額。
- 掃掠面積(Swept area)— 車體輪廓沿整條路徑掃過的區域;交管的碰撞判斷對象。
- 車體 mask — 柵格化的車體輪廓圖;空車與載貨(叉車)需分別建立。
- 對頂死鎖(Pairwise deadlock)— 兩車面對面,雙方都必須進入對方要用的空間才能通過。
- 環形鎖(Chain lock)— A 等 B、B 等 C、C 等 A 的等待環;在**等待圖(wait-for graph)** 上做 DFS 找環偵測。
- 迴避點(Avoid spot)— 供讓路車暫停的預先佈設點位;容量不足時死鎖偵測會無出口。
- MAPF — Multi-Agent Path Finding,一次為全體車輛規劃互不衝突路徑的集中式方法。

## 調度
- Open-RMF — 開源多機隊調度框架(Open Robotics Middleware Framework)。
- VDA5050 — AGV/AMR 與上位調度系統之間的標準通訊協定。
- fleet adapter — 把某家車隊接進 RMF 的轉接層(翻譯 RMF 指令 ↔ 車隊 API)。
- released / horizon — VDA5050 order 中「已授權可走」vs「已規劃未授權」的分段。
- blockingType — VDA5050 action 是否擋行駛/並行(NONE/SOFT/HARD)。
- factsheet — VDA5050 車輛能力宣告(尺寸/載重/支援動作)。

## Physical AI
- Physical AI — 讓自主系統在真實物理世界感知、推理、行動的 AI。
- World Foundation Model (WFM) — 能模擬物理世界、生成訓練資料的大型基礎模型。
- Digital Twin(數位分身)— 真實場景的虛擬複本,用來產生訓練資料。
- Sim-to-real — 把模擬中訓練的模型遷移到真實機器。
- Reality gap(現實落差)— 模擬與真實世界的差異總和(物理參數、感測噪聲、延遲、摩擦、外觀);落差越大,模擬訓練的策略越容易在實車失靈。
- Policy(策略)— 機器人的「腦」:吃感測器輸入、吐動作指令的函式,常用神經網路。
- Domain Randomization(領域隨機化)— 訓練時隨機抖動模擬參數,逼策略對變化不敏感、提升真實世界泛化。
- System Identification(系統辨識)— 在真實機上量出物理參數回填模擬,讓模擬一開始就更接近真實。
- Domain Adaptation(領域適應)— 主動對齊模擬與真實的特徵分佈(常用影像翻譯,如 CycleGAN/RetinaGAN)。
- 3D Gaussian Splatting(3DGS,高斯潑濺)— 用帶色 3D 高斯點重建真實場景做照片級渲染,real-to-sim 縮外觀落差主流。
- Zero-shot transfer(零樣本遷移)— 模擬訓練完直接上車、不用真實資料微調。
- SRCC(Sim-to-Real Correlation Coefficient)— 模擬與真實效能指標的相關係數,衡量「模擬能否準確預測真實表現」。
- Isaac Sim / Isaac Lab — NVIDIA 的機器人模擬框架 / 學習框架。
- Cosmos — NVIDIA 的 WFM 實作(WFM 是概念、Cosmos 是產品)。
- NuRec — NVIDIA Omniverse 的神經重建(從真實感測資料重建 3D 場景)。
- DiffDrive / TricycleSteering — gz 的差速 / 三輪(單驅動轉向輪)驅動 plugin。
- DetachableJoint — gz 動態建立/分離兩 model 間固定關節(叉車取放用)。
- Gazebo Fuel — Gazebo 生態的公開模型與世界資料庫;`gz sim` 可用 Fuel URI 直接 `<include>`,不必先下載。
- SimReady 資產 — Omniverse 的資產品質標準:**內嵌物理屬性與語意標註**,不只是好看的 mesh。價值在於 collision / inertial / 語意都已補好。
- Asset root — Isaac 官方資產的雲端根路徑;可只抓單一 USD 檔核對 prim 路徑,不必下載整包 asset pack。
- prim — OpenUSD 場景樹上的節點。寫物理參數 override 前要先核對 prim 路徑,路徑錯了 override 會靜默失效而模擬照跑。
- Gymnasium — RL 環境的介面契約(reset/step/reward);**給的是任務不是幾何**,場景仍來自底下的模擬器。Isaac Lab 的 env 相容此 API。
- OmniGraph Action Graph — Isaac Sim 的視覺化節點式運算圖,ROS 2 的 publish/subscribe 與驅動鏈都在這裡串。`/cmd_vel` 的路徑是 Subscribe Twist → Differential Controller → Articulation Controller。
- Articulation(關節體)— 由多個剛體與關節組成、被當成一整組解算的機構;差速底盤的兩個輪子即以此表示。
- render 分水嶺 — 免費 CI runner 沒有 GPU,「需不需要 render」把驗證分成可靠與不可靠兩區。**視覺化 ≠ render**:把位姿軌跡畫成俯視路徑圖,能把視覺產出救回可靠區。

## 足式(四足 / 人形)
- 浮動基座(floating base)— 把軀幹當成在空間中自由漂浮的剛體,腿掛在它下面。廣義座標是 `q = (基座 6 DOF, 關節 n 個)`。
- 欠致動(underactuated)— 可控輸入(n 個關節)少於系統自由度(6 + n),**永遠差 6 個**,而且差的正好是想控的軀幹位姿。
- 接觸集合(contact set)— 當下哪幾隻腳踩在地上。四足有 2⁴ = 16 種,每一種對應一組不同的動力學方程式。16 是組合上限,實際步態只走訪一小部分,但踩空/打滑會把系統丟進沒預期的那幾種。
- 混合系統(hybrid system)— 連續動力學 + 離散切換。切換時刻由狀態自己觸發(腳高降到 0),不是外部給的。
- ZMP(Zero Moment Point,零力矩點)— 地面反作用力等效作用點。**保證腳掌不繞邊緣翻轉,不保證不跌倒**;飛行相無從定義。名詞本身是 1970–72 才創的,1969 原始論文沒用這個詞。
- Capture point — `ξ = x + ẋ√(z₀/g)`,踩上去能讓重心速度漸近收斂到零的落腳點。**機制是消掉定高倒單擺的發散模態,不是「動能被抬升重心的位能吃光」**——模型裡重心高度固定,沒有位能可吃。ZMP 的式子裡沒有速度,capture point 的式子裡速度是主角。
- Duty factor — 一隻腳在一個步態週期裡觸地的時間比例。**不出現飛行相的門檻是 `1/n`,n = 獨立錯開的支撐組數**:四腳各自錯開 → 0.25;對角配對(trot)與雙足 → 0.5。四腳平均錯開時 `d ≥ 3/4` 才恆三腳著地、可靜態穩定。
  - ⚠ **「0.5 是走與跑的分界」對四足是動物步態分類上的統計說法,不是幾何必然。** 反例:amble(靈長類、大象)duty factor < 0.5 卻無騰空相。我曾把這條寫成「幾何上的必然」,是把來源的「統計上…偏」過度強化,2026-08-05 修正。
- QDD(quasi-direct drive,準直驅)— 高扭矩密度馬達 + 低減速比(約 1:3~1:10)。可反向驅動,所以衝擊能被馬達轉動吸收、力控不必外加感測器。對比工業手臂的諧波減速機常見 1:50 以上。
- proprioceptive 力控 — 用馬達電流與位置推得關節扭矩,再用 `τ = JᵀF` 反推腳底受力,不裝力感測器。
- SEA(series elastic actuator,串聯彈性致動器)— 輸出端加實體彈簧量測力並吸收衝擊,代價是頻寬。與 QDD 是「衝擊被誰吸收」的兩種答案。
- teacher-student 特權學習 — 先用只有模擬知道的資訊訓練 teacher,再讓只吃本體感覺的 student 模仿。可查證的是 Lee 2020 → Miki 2022 這一支,別套用到其他論文。
- ISO/CD 25785-1 — 制定中的「動態穩定工業移動機器人」安全標準,範疇是「需主動控制才能維持平衡、斷電即可能失穩」。**目前沒有任何已發布的 ISO 標準涵蓋足式**,ISO 3691-4 明訂排除主動穩定機器人。

## 法規與認證
- UL 2271 — 輕型電動載具(LEV)電池安全標準(低壓、輕載)。
- UL 2580 — 電動車/工業車輛電池安全標準(較高壓、工業級;含熱擴散測試)。適用範圍**明文排除** LEV 並指向 UL 2271,所以兩者不可互換不是慣例而是標準寫死的。
- EESA(electrical energy storage assembly,電能儲存組件)— **UL 2580 的正式名詞**,指電池包、「電池包 + 電化學電容」的組合,以及構成它們的模組。UL 2271 不用這個詞,別寫成「兩張都是 EESA 層級」。
- 認證四角色 — 標準制定/推動者、顧問/輔導/評估者、檢測實驗室(能力依 ISO/IEC 17025)、驗證/發證機構(公正性依 ISO/IEC 17065)。**送測分界**把「自己準備」與「第三方判定」切開;顧問報告 ≠ 證書。
- ISO/IEC 17025 / 17065 — 不是機器人標準,是「認驗證制度如何可信」的底層規則:前者管實驗室能力,後者管驗證機構的公正性與證書管理。
- LFP (LiFePO4) — 磷酸鋰鐵電池;熱失控門檻高、不釋氧,本質安全優於三元鋰 NMC。
- UN 38.3 — 鋰電池運輸強制測試。
- SEMI — Semiconductor Equipment and Materials International,半導體設備標準組織。
- SEMI S2 — 半導體設備環安衛(EHS)安全準則。
- SEMI E84 — 自動搬運交接(handoff)平行 I/O 介面(AMR ↔ load port 交接 FOUP)。
- FOUP — Front Opening Unified Pod,晶圓盒。OHT — 天車(Overhead Hoist Transport)。

---

## Flagged ambiguities(待釐清)
- 「主板控制」目前指 STM32 下位機;若後續納入 Arduino 平台,需在 firmware 章節區分。
