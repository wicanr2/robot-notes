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
- Hybrid-A* — 考慮車輛運動學(最小轉彎半徑、可否倒車)的全域規劃器。
- MPPI / DWB / RPP — Nav2 的三種區域控制器(取樣最佳化 / 動態視窗 / 純追蹤)。
- tf2 — ROS2 維護座標系關係的樹狀變換系統。
- 行為樹(Behavior Tree)— Nav2 用來編排規劃→跟隨→恢復的可組合結構。

## 通訊與電路
- CAN — 內建協議(訊框/CRC/仲裁)的差分匯流排,馬達/BMS 多節點即時控制主場。
- RS485 — 只定義電氣層的差分匯流排,協議自定(常用 Modbus RTU)。
- Open-drain(開漏)— 只能拉低、靠上拉電阻補高的數位輸出形式。
- STO — Safe Torque Off,驅動器內建的安全轉矩關斷輸入。

> 命名約定:散文一律寫 **Open-RMF**(官方品牌);套件名 / repo / apt 套件保留 `open-rmf` 原文。

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

## 法規與認證
- UL 2271 — 輕型電動載具(LEV)電池安全標準(低壓、輕載)。
- UL 2580 — 電動車/工業車輛電池安全標準(較高壓、工業級;含熱擴散測試)。
- LFP (LiFePO4) — 磷酸鋰鐵電池;熱失控門檻高、不釋氧,本質安全優於三元鋰 NMC。
- UN 38.3 — 鋰電池運輸強制測試。
- SEMI — Semiconductor Equipment and Materials International,半導體設備標準組織。
- SEMI S2 — 半導體設備環安衛(EHS)安全準則。
- SEMI E84 — 自動搬運交接(handoff)平行 I/O 介面(AMR ↔ load port 交接 FOUP)。
- FOUP — Front Opening Unified Pod,晶圓盒。OHT — 天車(Overhead Hoist Transport)。

---

## Flagged ambiguities(待釐清)
- 「主板控制」目前指 STM32 下位機;若後續納入 Arduino 平台,需在 firmware 章節區分。
