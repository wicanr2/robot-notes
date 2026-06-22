# robot-notes — 機器人知識筆記

從**軟體到硬體**,完整整理機器人相關知識。以**送餐機器人(室內 AMR)** 為主軸,逐步擴展到多機調度、主板模擬與 Physical AI。寫給想把機器人從頭搞懂的人,特別照顧「軟體背景、硬體不熟」的讀者。

> 進行中的整理計畫與分輪進度見 [PLAN.md](PLAN.md);術語表見 [CONTEXT.md](CONTEXT.md)。

<p align="center">
  <img src="img/bellabot.png" height="200" alt="BellaBot">
  <img src="img/keenon_t10.png" height="200" alt="Keenon T10">
  <img src="img/servi.png" height="200" alt="Servi">
</p>

---

## 從哪裡開始讀

| 你的情況 | 建議路線 |
|---|---|
| 想先看全貌 | [系統架構](docs/00-overview/system-architecture.md) |
| 軟體背景、想補硬體 | [底盤](docs/10-hardware/chassis-and-drivetrain.md) → [馬達/FOC](docs/10-hardware/motors-and-foc.md) → [感測器](docs/10-hardware/sensors.md) |
| 做下位機韌體 | [下位機運動控制](docs/20-firmware/low-level-control.md) → [編碼器](docs/10-hardware/encoders.md) → [通訊匯流排](docs/10-hardware/communication-buses.md) |
| 做導航 | [SLAM](docs/30-navigation/slam-mapping.md) → [定位](docs/30-navigation/localization.md) |
| 想做 AI 模擬 | [Physical AI 總覽](docs/50-physical-ai/physical-ai-overview.md) |

---

## 文件索引

### 00 系統全貌
- [系統架構](docs/00-overview/system-architecture.md) — 上位機/下位機分層、資料流、硬體選型、軟體架構、研發路線

### 10 硬體
- [底盤與驅動系統](docs/10-hardware/chassis-and-drivetrain.md) — 差速、萬向輪、輪轂馬達、BLDC、行星減速機
- [馬達與 FOC 控制](docs/10-hardware/motors-and-foc.md) — FOC、定子/轉子、有刷/無刷、功率橋、閘極驅動
- [編碼器](docs/10-hardware/encoders.md) — 霍爾、增量式 A/B 相、STM32 讀取
- [感測器](docs/10-hardware/sensors.md) — 2D LiDAR、深度相機、IMU
- [通訊匯流排](docs/10-hardware/communication-buses.md) — CAN 與 RS485,STM32F4 串接
- [數位電路](docs/10-hardware/digital-circuits.md) — open-drain、GPIO 輸出形式
- [電源與安全](docs/10-hardware/power-and-safety.md) — 電壓法規、急停、ramp/過流/堵轉保護

### 20 韌體
- [下位機運動控制](docs/20-firmware/low-level-control.md) — M1 知識清單、運動學解算 vs PID
- stm32-simulation-renode.md — STM32 在電腦上跑 Renode 模擬 *(待寫,R3)*

### 30 導航
- [SLAM 建圖](docs/30-navigation/slam-mapping.md) — 2D SLAM 流程、loop closure
- [定位](docs/30-navigation/localization.md) — AMCL、odometry、地標/AprilTag 定位
- kinematics-and-coordinate-transforms.md — 運動學與座標轉換公式 *(待寫,R4)*
- path-planning.md — 路徑規劃與軌跡計算 *(待寫,R4)*

### 40 多機調度
- open-rmf.md — OpenRMF 如何透過 VDA5050 調度不同廠家機器人 *(待寫,R2)*
- vda5050.md — VDA5050 協定整理 *(待寫,R2)*

### 50 Physical AI
- [Physical AI 總覽](docs/50-physical-ai/physical-ai-overview.md) — Physical AI、World Model、NVIDIA 堆疊、sim-to-real
- simulation-isaac-gazebo.md — 模擬環境 *(待寫,R5)*
- sim-to-real.md — 模擬到真實 *(待寫,R5)*
- claude-physical-ai-workflow.md — 用 Claude 完成機器人 Physical AI 模擬 *(待寫,R5)*

---

歷史原始整理文件保留在 [`docs/_legacy/`](docs/_legacy/)(已拆分到上述主題檔)。
