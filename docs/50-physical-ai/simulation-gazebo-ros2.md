# 用 Gazebo + ROS 2 模擬室內差速 AMR

一句話定位:在電腦裡用 **Gazebo**(開源機器人物理模擬器)蓋一個虛擬餐廳,放進一台差速送餐機器人,讓它產生跟真車一樣的感測器訊號(雷射、里程、姿態),再接上 **Nav2**(ROS 2 的導航軟體堆疊)跑 SLAM 與自主導航——整套不碰真硬體就能驗證導航邏輯。

> 延伸閱讀:[Physical AI 總覽](./physical-ai-overview.md)、[導航運動學與座標轉換](../30-navigation/kinematics-and-coordinate-transforms.md)、[SLAM 建圖](../30-navigation/slam-mapping.md)、[定位](../30-navigation/localization.md)

本檔聚焦 **Gazebo** 這條輕量、CPU 可跑、ROS 原生的路線;與 **Isaac Sim** 的分工放在最後一節。

---

## 1. 先把名字搞清楚:Gazebo Classic 已死,現在的「Gazebo」是 gz sim

這是新手最常踩的坑。同一個品牌「Gazebo」前後是**兩套完全不同的軟體**:

- **Gazebo Classic**(舊的,版本號到 Gazebo 11)— 已於 **2025-01-31 正式 end-of-life(EOL,停止維護)**。教學文章裡看到 `gazebo_ros`、`spawn_entity.py`、`<gazebo>` 標籤配 Gazebo 9/11 的,多半是這套舊的,新專案不要再用。
- **新 Gazebo**(現在官方就叫 **Gazebo**,執行檔 `gz sim`)— 前身叫 **Ignition / Ignition Gazebo**,2022 年改名回 Gazebo。版本用英文字母順序命名:**Fortress → Garden → Harmonic → Ionic → Jetty…**,套件名與指令都是 `gz-*`、`gz sim`。

命名為什麼亂:一個品牌名(Gazebo)被「舊架構(Classic)」和「新架構(原 Ignition)」共用過,中間還改名兩次(Gazebo→Ignition→Gazebo)。判斷手上是哪套,看**指令**最快:`gazebo` 是 Classic、`gz sim` 是新版。

> 名詞:**LTS**(Long-Term Support,長期支援版)指維護週期較長的版本。Gazebo Harmonic 是 LTS,支援到 2028-09。

來源:[Gazebo Classic EOL 公告(Open Robotics Discourse)](https://discourse.openrobotics.org/t/gazebo-classic-11-has-reached-end-of-life-x-post-gazebo-sim-community/41852)、[gazebo-classic GitHub(導向 gz-sim)](https://github.com/gazebosim/gazebo-classic)

### Gazebo 版本 ↔ ROS 2 版本對應(最容易踩雷)

每個 ROS 2 distro(發行版)官方「配對」一個 Gazebo 版本。用配對版本最省事;混搭可行但要自己裝非官方 binary 或從原始碼編 `ros_gz`。

| ROS 2 distro | 官方配對 Gazebo | 備註 |
|---|---|---|
| **Humble**(LTS, 22.04) | **Fortress** | 官方主支援是 Fortress;也可改裝 Harmonic(走 `ros-humble-ros-gzharmonic`),屬進階用法 |
| **Jazzy**(LTS, 24.04) | **Harmonic** | 從 Jazzy 起 Gazebo 走 ROS vendor package,整合最順 |
| **Kilted**(24.04) | **Ionic** | |
| **Rolling / 後續 LTS** | **Jetty** | Rolling 是滾動開發版 |

安裝就一行(裝配對版本的橋接 metapackage):

```bash
sudo apt-get install ros-${ROS_DISTRO}-ros-gz   # ROS_DISTRO 換成 humble / jazzy / kilted
```

實務建議:**新專案首選 Jazzy + Harmonic**(都是 24.04 上的 LTS、官方配對、整合最乾淨)。若被既有 Humble 環境綁住,維持 Humble + Fortress 最穩,要新功能再評估升 Harmonic。版本細節以官方最新為準。

> 名詞:**vendor package** 指 ROS 官方把 Gazebo 函式庫重新打包進 ROS apt 倉庫,讓相依關係跟 ROS 套件一致、不必另加第三方來源。

來源:[Installing Gazebo with ROS(官方)](https://gazebosim.org/docs/latest/ros_installation/)、[ros_gz README 相容矩陣](https://github.com/gazebosim/ros_gz/blob/ros2/README.md)

---

## 2. 一台差速 AMR 的模擬要哪些零件

把模擬拆成四塊:**機器人長相 → 怎麼動 → 怎麼感知 → 在哪裡跑**。

### (a) 機器人描述:URDF / SDF

- **URDF**(Unified Robot Description Format)— ROS 慣用的機器人描述格式(XML),描述連桿(link)、關節(joint)、外型、慣性。
- **SDF**(Simulation Description Format)— Gazebo 原生格式,除了機器人本身,還能描述世界、物理、感測器、外掛(plugin)。

實務上機器人本體寫 URDF(ROS 端的 robot_state_publisher 也要吃它),在 URDF 裡用 `<gazebo>` 區塊補上 Gazebo 專屬設定;Gazebo 載入時會把 URDF 轉成 SDF。差速車最少要有:底盤 link、左右驅動輪 joint(continuous)、一個萬向輪。

### (b) 怎麼動:ros2_control + diff_drive_controller

讓模擬輪子能被 ROS 指令驅動,標準作法是 **ros2_control**(ROS 2 的即時控制框架),在 Gazebo 端由 **gz_ros2_control** 這個外掛接起來:

- 在 URDF 加一個 `<ros2_control>` 區塊,宣告硬體外掛 `gz_ros2_control/GazeboSimSystem`,並列出左右輪 joint 的命令介面(velocity)與狀態介面(position/velocity)。
- 再加一個 Gazebo 系統外掛,指向一份 **controller YAML**(控制器設定檔)。
- YAML 裡設定 **diff_drive_controller**(差速驅動控制器):它訂閱 `/cmd_vel`(`geometry_msgs/Twist`,線速度+角速度指令),依輪距/輪徑換算成左右輪速,反過來用輪子轉動量算出 **odometry**,發布 `nav_msgs/Odometry` 到 `/odom` 並送出 `odom → base_link` 的 tf。

也就是說 `diff_drive_controller` 同時做兩件事:**收 `/cmd_vel` 驅動輪子** + **發 `/odom` 與 tf**。這正好是 Nav2 需要的介面。

> 名詞:**tf**(transform)指 ROS 的座標轉換樹,描述各座標系(map/odom/base_link/雷射…)之間的相對位姿。

來源:[gz_ros2_control 文件](https://control.ros.org/humble/doc/gz_ros2_control/doc/index.html)、[Setting Up Odometry - Gazebo(Nav2)](https://docs.nav2.org/setup_guides/odom/setup_odom_gz.html)

### (c) 怎麼感知:LiDAR / 相機 / IMU 感測器外掛

感測器在 SDF/URDF 裡以 `<sensor>` 宣告,由 Gazebo 的**系統外掛**負責模擬出資料:

| 感測器 | SDF type | 模擬它的系統外掛 | 產出(經橋接後的 ROS 訊息) |
|---|---|---|---|
| 2D/3D LiDAR | `gpu_lidar` | `gz-sim-sensors-system`(渲染類感測共用) | `sensor_msgs/LaserScan`(SLAM 主力) |
| 相機 | `camera` / `depth_camera` | 同上 | `sensor_msgs/Image` |
| IMU | `imu` | `gz-sim-imu-system` | `sensor_msgs/Imu` |

世界檔本身也要掛幾個基礎系統外掛才動得起來:`gz-sim-physics-system`(物理)、`gz-sim-scene-broadcaster-system`(場景廣播)、`gz-sim-sensors-system`(感測渲染)。

> 名詞:**plugin / system**(系統外掛)— Gazebo 把功能模組化成可掛載的外掛,物理、感測、控制各是一個 system,在 SDF 裡用 `<plugin filename=...>` 掛進去。

來源:[Gazebo Harmonic Sensors(官方)](https://gazebosim.org/docs/harmonic/sensors/)、[Setting Up Sensors - Gazebo(Nav2)](https://docs.nav2.org/setup_guides/sensors/setup_sensors_gz.html)

### (d) 在哪裡跑:世界檔(world)

**world** 是一份 SDF,描述場景:地面、牆壁、桌椅、光源、物理參數。送餐情境就是擺一個餐廳:走道、餐桌、出餐口。可以自己用 SDF 拼,或載入現成模型(Gazebo Fuel 線上模型庫)。世界檔決定了 LiDAR 會掃到什麼、SLAM 要建出什麼地圖。

---

## 3. 跟 Nav2 串接:sim → Nav2 閉迴路

核心觀念:**Gazebo 不知道 Nav2 存在,Nav2 也不知道 Gazebo 存在**。它們只透過幾個標準 ROS topic 與 tf 對話,中間靠 `ros_gz_bridge` 翻譯。把 Gazebo 換成真車(同樣發 `/scan /odom /tf`、收 `/cmd_vel`),Nav2 那側完全不用改——這正是模擬的價值。

資料流(閉迴路):

```
        ┌─────────────── Gazebo (gz sim) ───────────────┐
        │  物理 + 餐廳世界 + 差速 AMR + 感測器外掛        │
        └───┬───────────────────────────────────┬───────┘
            │ /scan /odom /tf (gz topics)        │ /cmd_vel (gz topic)
            ▼  ros_gz_bridge (雙向翻譯)           ▲  ros_gz_bridge
            │ /scan /odom /tf (ROS topics)        │ /cmd_vel (ROS topic)
        ┌───▼───────────────────────────────────┴───────┐
        │  slam_toolbox          Nav2                     │
        │  /scan + odom→base_link   訂 /scan /odom /tf    │
        │  → /map + map→odom tf     → 規劃 → 發 /cmd_vel  │
        └────────────────────────────────────────────────┘
```

tf 樹由三方各補一段,合起來才完整:

| 提供者 | 提供的 tf | 意義 |
|---|---|---|
| Gazebo / diff_drive_controller | `odom → base_link` | 機器人相對里程原點的位姿(相對定位,會漂移) |
| robot_state_publisher(讀 URDF) | `base_link → 各感測器/輪子` | 機器人本體固定幾何 |
| **slam_toolbox**(建圖時)/ AMCL(已知地圖時) | `map → odom` | 把里程漂移修正回全域地圖座標 |

- **建圖階段**:跑 **slam_toolbox**(ROS 2 主流 2D SLAM 套件,也是 Nav2 官方支援之一)。它吃 `/scan` + `odom→base_link`,即時產生 `/map` 與 `map→odom` 修正,可以邊走邊建圖(Navigating while Mapping)。
- **導航階段**:有了地圖後,改用 **AMCL**(粒子濾波定位)提供 `map→odom`;Nav2 依目標點規劃路徑、避開 costmap 上的障礙,持續發 `/cmd_vel`,Gazebo 把車開過去,新 `/scan` 又回饋進來——閉迴路成立。

來源:[Setting Up Odometry - Gazebo(Nav2)](https://docs.nav2.org/setup_guides/odom/setup_odom_gz.html)、[Navigating while Mapping (SLAM)(Nav2)](https://docs.nav2.org/tutorials/docs/navigation2_with_slam.html)、[Mapping and Localization(Nav2)](https://docs.nav2.org/setup_guides/sensors/mapping_localization.html)

---

## 4. 典型啟動方式(結構,不貼完整程式)

一個完整模擬通常由一個 ROS 2 **launch file**(啟動描述檔,Python 或 XML)把下列節點一次拉起來:

1. **啟 Gazebo + 載世界**:用 `ros_gz_sim` 提供的 launch 包起 `gz sim <restaurant.world>`。
2. **生成機器人**:把 URDF 餵給 `ros_gz_sim` 的 `create`,在世界裡 spawn 出 AMR。
3. **robot_state_publisher**:讀 URDF 發布機器人本體 tf。
4. **ros_gz_bridge**:逐一宣告要橋接的 topic 對應,把 gz 訊息翻成 ROS 訊息(雙向)。語法形如:
   ```
   /scan@sensor_msgs/msg/LaserScan@gz.msgs.LaserScan        # gz → ROS
   /cmd_vel@geometry_msgs/msg/Twist@gz.msgs.Twist           # ROS → gz
   /odom@nav_msgs/msg/Odometry@gz.msgs.Odometry
   ```
   (`@ROS型別@gz型別`,中間的方向由箭頭符號決定)
5. **controller_manager + spawner**:載入 `diff_drive_controller` 與 `joint_state_broadcaster`。
6. **slam_toolbox 或 Nav2**:依「建圖」或「導航」階段擇一啟動,通常各自一份 launch,再用一個上層 launch 組合。

> 名詞:**ros_gz_bridge / parameter_bridge** — `ros_gz` 套件群裡負責 Gazebo Transport 與 ROS 2 之間雙向轉訊息的橋。`ros_gz` 還含 `ros_gz_sim`(啟動/生成工具)、`ros_gz_image`(影像單向高效傳輸)等。

來源:[ros_gz README(套件職責)](https://github.com/gazebosim/ros_gz/blob/ros2/README.md)、[Setting Up Sensors - Gazebo(Nav2,橋接語法)](https://docs.nav2.org/setup_guides/sensors/setup_sensors_gz.html)

---

## 5. Gazebo 的定位 vs Isaac Sim:各適合什麼

兩者不是取代關係,是**不同階段、不同目的**的工具。

| 面向 | **Gazebo (gz sim)** | **NVIDIA Isaac Sim** |
|---|---|---|
| 授權/生態 | 開源,Open Robotics,**ROS 原生** | 免費但閉源,跑在 NVIDIA Omniverse 平台上 |
| 物理/算力 | CPU 即可跑,輕量 | GPU 加速物理;Isaac Lab 可在 GPU 上**並行上千個環境** |
| 畫面擬真 | 夠用,非照片級 | RTX 光線追蹤,**照片級渲染** |
| 強項定位 | 導航/控制/感測整合驗證、ROS2 堆疊聯調、教學、CI | 強化學習(RL)大規模訓練、合成資料生成(Replicator + 域隨機化)、電腦視覺/感知擬真 |
| ROS2 整合 | best-in-class(`ros_gz` 橋接) | 可接但學習曲線較陡 |
| 硬體門檻 | 低,無獨顯也能(可 headless) | 高,需較強 NVIDIA GPU |

選用建議:

- **驗證導航/控制邏輯、跑 Nav2/SLAM 閉迴路、團隊聯調、CI 自動測試** → **Gazebo**。輕、開源、ROS 原生,送餐機器人這類室內 2D 導航的甜蜜點。
- **訓練視覺感知模型、要照片級合成資料 + 標註、大規模 RL 平行訓練、sim-to-real 視覺** → **Isaac Sim / Isaac Lab**。用 GPU 算力換擬真度與吞吐。
- 常見組合:**Isaac 練感知/策略模型,Gazebo(或真車)驗導航整合**,各取所長。

> 名詞:**RL**(Reinforcement Learning,強化學習)讓機器人在模擬中反覆試錯學策略;**合成資料**指模擬器自動產生帶標註的訓練影像,省去真實標註成本;**域隨機化(Domain Randomization)** 隨機化光照/材質/物件以提升真實世界泛化(見 [Physical AI 總覽](./physical-ai-overview.md))。

來源:[Gazebo vs Isaac Sim 比較(SVRC)](https://www.roboticscenter.ai/learn/robot-simulation-software-comparison)、[Robot Simulation Software: 2026 Perspective(Black Coffee Robotics)](https://www.blackcoffeerobotics.com/blog/which-robot-simulation-software-to-use)

---

## 6. 安裝與硬體需求概況

- **作業系統**:Gazebo Harmonic 官方 binary 提供 **Ubuntu 22.04(Jammy)** 與 **24.04(Noble)**。Windows 走 WSL2 + Ubuntu;原生 Windows/macOS 支援有限,以官方最新為準。
- **安裝**:加 OSRF apt 來源後 `sudo apt install gz-harmonic`(只裝模擬器),或 `sudo apt install ros-${ROS_DISTRO}-ros-gz`(連 ROS 橋接一起裝,**做 ROS 專案用這個**)。
- **GPU**:跑模擬**不強制要獨顯**——感測器渲染走 OpenGL,內顯也能動;有獨顯則畫面/感測渲染更順。要完全無 GPU 環境(如 CI、伺服器)可開 **headless 模式**(不開 GUI),省資源也不需強 OpenGL 支援。
- **記憶體**:用 binary 安裝吃得不多;**從原始碼編譯**才重,官方提到編譯可能用到 ~16GB RAM,可用 `CMAKE_BUILD_PARALLEL_LEVEL=1` 降低佔用。一般人裝 binary 即可,不必自編。

> 對照:這份「內顯可跑、headless 可上 CI」正是 Gazebo 相對 Isaac Sim(需較強 NVIDIA GPU)的入門優勢。

來源:[Binary Installation on Ubuntu - Harmonic(官方)](https://gazebosim.org/docs/harmonic/install_ubuntu/)、[Installing Gazebo with ROS(官方)](https://gazebosim.org/docs/latest/ros_installation/)

---

## 參考來源(實際查證)

- Gazebo Classic EOL 公告:https://discourse.openrobotics.org/t/gazebo-classic-11-has-reached-end-of-life-x-post-gazebo-sim-community/41852
- gazebo-classic GitHub(導向 gz-sim):https://github.com/gazebosim/gazebo-classic
- Installing Gazebo with ROS(版本配對、安裝):https://gazebosim.org/docs/latest/ros_installation/
- ros_gz README(相容矩陣、套件職責、bridge):https://github.com/gazebosim/ros_gz/blob/ros2/README.md
- gz_ros2_control 文件:https://control.ros.org/humble/doc/gz_ros2_control/doc/index.html
- Nav2 — Setting Up Odometry (Gazebo):https://docs.nav2.org/setup_guides/odom/setup_odom_gz.html
- Nav2 — Setting Up Sensors (Gazebo,橋接語法):https://docs.nav2.org/setup_guides/sensors/setup_sensors_gz.html
- Nav2 — Mapping and Localization:https://docs.nav2.org/setup_guides/sensors/mapping_localization.html
- Nav2 — Navigating while Mapping (SLAM):https://docs.nav2.org/tutorials/docs/navigation2_with_slam.html
- Gazebo Harmonic Sensors(官方):https://gazebosim.org/docs/harmonic/sensors/
- Gazebo Harmonic Binary Install(官方):https://gazebosim.org/docs/harmonic/install_ubuntu/
- 模擬器比較(SVRC):https://www.roboticscenter.ai/learn/robot-simulation-software-comparison
- 模擬器比較(Black Coffee Robotics, 2026):https://www.blackcoffeerobotics.com/blog/which-robot-simulation-software-to-use
</content>
</invoke>
