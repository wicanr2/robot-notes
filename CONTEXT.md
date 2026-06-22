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

## 通訊與電路
- CAN — 內建協議(訊框/CRC/仲裁)的差分匯流排,馬達/BMS 多節點即時控制主場。
- RS485 — 只定義電氣層的差分匯流排,協議自定(常用 Modbus RTU)。
- Open-drain(開漏)— 只能拉低、靠上拉電阻補高的數位輸出形式。
- STO — Safe Torque Off,驅動器內建的安全轉矩關斷輸入。

## 調度(待 R2 展開)
- OpenRMF — 開源多機隊調度框架(Open Robotics Middleware Framework)。
- VDA5050 — AGV/AMR 與上位調度系統之間的標準通訊協定。

## Physical AI(R5)
- Physical AI — 讓自主系統在真實物理世界感知、推理、行動的 AI。
- World Foundation Model (WFM) — 能模擬物理世界、生成訓練資料的大型基礎模型。
- Digital Twin(數位分身)— 真實場景的虛擬複本,用來產生訓練資料。
- Sim-to-real — 把模擬中訓練的模型遷移到真實機器。
- Domain Randomization — 隨機化模擬環境以提升真實世界泛化。
- Isaac Sim / Isaac Lab — NVIDIA 的機器人模擬框架 / 學習框架。

---

## Flagged ambiguities(待釐清)
- 「主板控制」目前指 STM32 下位機;若後續納入 Arduino 平台,需在 firmware 章節區分。
