# 用 Isaac Sim + Isaac Lab 模擬室內自主移動機器人(AMR)

整理 NVIDIA 官方資料,聚焦「室內自主移動機器人 / 差速 AMR」場景下,如何用 Isaac Sim 與 Isaac Lab 做機器人模擬、ROS2 串接與強化學習訓練。

> **名詞速記**
> - **AMR(Autonomous Mobile Robot)** — 自主移動機器人,能自行規劃路徑、避障的輪式機器人(送餐機、倉儲搬運車屬於此類)。
> - **差速驅動(differential drive)** — 兩個獨立驅動輪靠左右輪速差來轉向的底盤,本筆記的目標機型。
> - 版本資訊以本文標示日期(SIGGRAPH 2025 GA)為準,實際開發請以官方最新版為準。

---

## 1. Isaac Sim 與 Isaac Lab 是什麼、怎麼分工

| 名稱 | 一句話定義 | 角色 |
|---|---|---|
| **OpenUSD(Universal Scene Description)** | 一套描述 3D 場景與資產的開放檔案格式與資料模型,原由 Pixar 開發 | 場景、機器人、資產怎麼定義與互通的底層格式 |
| **NVIDIA Omniverse** | 以 OpenUSD 為核心的 3D 模擬與協作平台 | 提供 RTX 算繪、物理、模擬基礎工具(Kit) |
| **Isaac Sim** | 建構在 Omniverse 上的**機器人模擬器** | 機器人專屬工具:感測器模擬、URDF 匯入、ROS2 橋接、合成資料生成 |
| **Isaac Lab** | 建構在 Isaac Sim 上的**開源機器人學習框架** | 強化學習(RL)/ 模仿學習(imitation learning)的訓練工作流 |

層次關係(由下而上):**OpenUSD(資料格式)→ Omniverse(模擬平台)→ Isaac Sim(機器人模擬器)→ Isaac Lab(機器人學習框架)**。

- **Isaac Sim** = 模擬器。負責把世界「跑起來」:算繪畫面、跑 PhysX 物理、模擬相機 / LiDAR / IMU、跟 ROS2 對接。
- **Isaac Lab** = 學習框架。在 Isaac Sim 之上,提供定義 RL 環境(reward / observation / action)、大規模平行訓練、輸出 policy 的工具。它繼承 Isaac Sim 的能力,並加上 RL 研究專屬功能,如致動器動態(actuator dynamics)、程序化地形生成、人類示範資料收集。

**官方建議工作流**:在 **Isaac Sim 裡組好機器人 → 在 Isaac Lab 裡訓練 → 回到 Isaac Sim 評估與測試**。

### 版本概況(2025–2026)

- **Isaac Sim 5.0** 與 **Isaac Lab 2.2** 於 **2025-08-11 SIGGRAPH 2025** 釋出正式版(GA),程式碼放上 GitHub。
- Isaac Sim 5.0 重點:神經重建與算繪(NuRec / 3DGUT)、OmniSensor USD schema(把 RTX 感測器定義進 USD)、標準化 robot schema(OpenUSD)、改良的合成資料管線、**完整支援 ROS 2 Jazzy Jalisco**、新增 ZeroMQ bridge。
- Isaac Lab 2.2 重點:合成動作生成(GR00T-Mimic)、Omniverse Fabric 整合(加快載入與物理)、tensorized 吸盤夾爪、與 Lightwheel 合作的 policy 評估框架。
- 開源狀態:Isaac Sim 與 Isaac Lab 的 extension 程式碼在 GitHub(`github.com/isaac-sim/IsaacSim`、`github.com/isaac-sim/IsaacLab`);但底層 Omniverse Kit 元件仍為閉源。
- 文件中亦出現 Isaac Sim 5.1 / 6.0 的頁面,版本仍在演進,**以官方最新版為準**。

---

## 2. 組一個 AMR 模擬要哪些要素

### 2.1 把機器人模型放進場景(URDF → USD)

室內 AMR 通常已有 **URDF(Unified Robot Description Format,描述機器人連桿與關節的 XML 格式)**。Isaac Sim 用 **URDF Importer** 擴充功能把它轉成 USD:

- 匯入時自動把 URDF 的 joint 資料轉成 **PhysX schema**(NVIDIA 的物理引擎介面),並對關節套上 Articulation API 與 Drive API、對剛體套上 Mass API。
- **Articulation(關節體)** = 由多個剛體與關節組成、被當成一整組來解算的機構;差速底盤的兩個輪子即以 articulation 表示。
- Joints & Drives 介面可逐關節設定:可用 **Stiffness(剛度)** 或 **Natural Frequency(自然頻率)** 兩種方式設定驅動;扭矩控制(torque-controlled)的 drive 其 stiffness/damping 設為 0。
- 匯入產物遵循 Isaac Sim 資產結構慣例,mesh 已做 instancing 以利效能。
- 除 URDF 外,也支援 MJCF(MuJoCo 格式)等其他匯入器。

### 2.2 加感測器(相機 / LiDAR / IMU)

Isaac Sim 提供機器人常用感測器的模擬:

- **相機(RGB / 深度)** — 可輸出 RGB、深度圖,供導航與感知用。
- **LiDAR(光達)** — Isaac Sim 5.0 起以 **RTX 感測器**模擬,並有 **OmniSensor USD schema** 把感測器定義進 USD;可輸出點雲,室內 AMR 常用 2D LaserScan。
- **IMU(慣性測量單元)** — 輸出加速度與角速度,供里程計 / 定位融合。

### 2.3 加物理(差速驅動)

物理由 Omniverse 內建的 **PhysX** 解算。差速底盤的驅動鏈,在 Isaac Sim 裡用 **OmniGraph Action Graph**(視覺化的節點式運算圖)串起來,核心兩個節點:

- **Differential Controller** — 把「車體速度(前進速度 + Z 軸旋轉速度)」換算成左右兩輪的輪速。
- **Articulation Controller** — 把輪速命令送進關節驅動(joint drives),真正驅動輪子轉。

---

## 3. ROS2 Bridge:跟 Nav2 串接

Isaac Sim 透過 **ROS 2 Bridge** 擴充功能跟 ROS2 對接。支援 **Humble**(較舊文件)與 **Jazzy Jalisco**(Isaac Sim 5.0 完整支援);實務上 Nova Carter 等樣板仍以 Humble 為主。

ROS2 環境須在啟動 Isaac Sim 前先 source,讓 bridge 載入系統的 ROS2 函式庫。

### 一台 AMR 跑 Nav2 時的 topic 流向

**Isaac Sim 對外 publish(模擬器當作真實機器人在發資料):**

| Topic | 訊息型別 | 內容 |
|---|---|---|
| `/scan` | `sensor_msgs/LaserScan` | 2D 雷射掃描(由點雲經 `pointcloud_to_laserscan` 轉出) |
| `/point_cloud` | `sensor_msgs/PointCloud2` | LiDAR 點雲(實務用 PointCloud2,非舊版 PointCloud) |
| `/odom` | `nav_msgs/Odometry` | 里程計 |
| `/tf` | `tf2_msgs/TFMessage` | 座標轉換樹 |
| `/map` | `nav_msgs/OccupancyGrid` | 佔據柵格地圖 |
| `/clock` | — | 模擬時間(讓 ROS2 用模擬時鐘) |

**Isaac Sim 對外 subscribe(接收外部命令):**

- `/cmd_vel`(`geometry_msgs/Twist`) — 速度命令。Nav2 算出來的 `cmd_vel` 進到 Isaac Sim,經 **ROS2 Subscribe Twist 節點 → Differential Controller → Articulation Controller**,驅動模擬車輪。

這些 publish/subscribe 都在 OmniGraph Action Graph 裡用對應節點(transform tree publisher、odometry publisher、joint state publisher 等)搭出來。

### 樣板機器人與套件

Isaac Sim 內附可直接跑 Nav2 的樣板:

- **Nova Carter** — 含 RTX LiDAR、Hawk 相機、差速驅動的行動機器人。
- **iw.hub** — 倉儲導航平台。
- ROS2 套件:`carter_navigation`(launch、導航參數、機器人模型)、`isaac_ros_navigation_goal`(程式化送導航目標)。

---

## 4. 強化學習訓練迴圈(Isaac Lab)

Isaac Lab 把 RL 任務建模成 **MDP(Markov Decision Process,馬可夫決策過程)**:環境提供當前 observation,agent 給出 action,環境回傳下一個 state、reward、done 旗標與 episode 資訊。

### 定義環境的兩種寫法

| 寫法 | 說明 |
|---|---|
| **Manager-Based(管理器式)** | 模組化:分別定義 Observations / Actions / Rewards / Terminations 的 config 類別,另可加 Event(隨機化)與 Curriculum(課程學習)。 |
| **Direct(直接式)** | 單一類別包辦所有環境邏輯,對 observation 計算、action 套用、reward 計算有更直接的控制。 |

核心管理器:

- **Observation Manager** — 算出 agent 的觀測,輸出 PyTorch tensor(可含隨機化)。
- **Action Manager** — 把 policy 輸出對應到機器人控制輸入(關節位置 / 速度等)。對差速 AMR,action 通常映射到左右輪速或車體 v/ω。
- **Reward Manager** — 用 `RewardTermCfg` 設定各 reward term(計算函式 + 權重),加總成 reward。對 AMR 常見 reward:朝目標前進、避免碰撞、行進平順等。
- **Event Manager** — 處理隨機化 / domain randomization。

### 大規模平行化

Isaac Lab 支援**向量化環境(vectorized environments)**:用 `num_envs` 指定子環境數量,可達**數千個**同時跑。每次 `step()` 收到一批 action、回傳一批 observation,GPU 上平行模擬讓資料收集量級提升,大幅縮短訓練時間。

### 演算法、RL 函式庫與 policy 產出

- 支援四大 RL 函式庫:**RSL-RL、RL-Games、SKRL、Stable-Baselines3**,常用演算法為 **PPO(Proximal Policy Optimization)**(部分支援 TRPO 等)。實務大規模 GPU 平行訓練以 RSL-RL / RL-Games 為主;Stable-Baselines3 因非向量化 pipeline,多供相容/小規模對照。
- 訓練好的 policy 以 PyTorch 模型(`.pt`)儲存,可轉成 **JIT / ONNX** 等最佳化格式,部署到 NVIDIA Jetson 等邊緣裝置。
- 落地時,sim 裡訓練好的 policy 回到 Isaac Sim 評估,再考慮 sim-to-real 遷移。

---

## 5. 合成資料生成(Replicator)

**Omniverse Replicator** = Isaac Sim 內的合成資料生成(SDG, Synthetic Data Generation)框架,用 `omni.replicator` 擴充。室內 AMR 常用它生成感知模型的訓練資料。

- **Domain Randomization(領域隨機化)** — Replicator 最重要能力之一:隨機化資產、材質、光照、相機位置等,讓訓出來的模型對真實世界變異更穩健。
- **標註(annotation)** — 算繪與資料生成時自動標註:對 3D 資產做語意標籤(Semantic Schema Editor 提供 UI 套標籤),Visualizer 可視化語意標籤與 2D/3D bounding box、normal、depth 等多種 annotation。
- 涵蓋 2D/3D 多種感測器模態,搭配 annotator + writer 輸出資料集。
- Isaac Sim 5.0 另加 MobilityGen、針對 NVIDIA Cosmos Transfer 最佳化的 Replicator writer、大規模環境的 Action/Event 資料生成。

---

## 6. 硬體 / 安裝需求

### GPU 與系統需求(Isaac Sim)

| 項目 | 最低 | 建議 | 理想 |
|---|---|---|---|
| GPU | GeForce RTX 4080(16GB) | GeForce RTX 5080(16GB) | RTX PRO 6000 Blackwell(48GB) |
| CPU | Intel i7(7代)/ Ryzen 5 | Intel i7(9代)/ Ryzen 7 | i9 X-series / Threadripper |
| 核心數 | 4 | 8 | 16 |
| RAM | 32GB | 64GB | 64GB |
| 儲存 | 50GB SSD | 500GB SSD | 1TB NVMe SSD |

- **必須有 RT Core**:A100、H100 這類無 RT Core 的資料中心 GPU **不支援**(以官方最新支援清單為準)。
- VRAM < 16GB 在算繪複雜場景(>16MP/frame)時會吃力。
- 作業系統:Ubuntu 22.04 / 24.04、Windows 11(Windows 10 不支援)。需相對較新的 NVIDIA 驅動。

### Headless 與容器化

- Isaac Sim 可 **headless**(無 GUI)執行,適合伺服器 / 雲端大量平行訓練與資料生成。
- **容器**:Isaac Sim container **僅支援 Linux**;NGC(NVIDIA GPU Cloud)提供官方容器 image。
- 雲端:Isaac Sim 5.0 / Isaac Lab 2.2 可透過 **NVIDIA Brev** 取得雲端 RTX GPU 實例。

> 領域備註:本團隊規範一律用 docker 建立編譯/執行環境,不污染系統環境。Isaac Sim 走官方 NGC container + headless 跑法,符合此原則。

---

## 7. Isaac Sim vs Gazebo 定位

**Gazebo** 是 ROS 生態長年的開源機器人模擬器,輕量、社群成熟、跟 ROS/ROS2 整合直接,適合一般導航 / 控制演算法的功能驗證與 CI,對 GPU 沒有硬性 RT Core 要求。**Isaac Sim** 走 GPU 加速的高擬真路線:RTX 物理算繪、貼近真實的感測器(相機 / RTX LiDAR)、OpenUSD 場景、Replicator 合成資料,並透過 Isaac Lab 支援數千環境平行 RL 訓練;代價是硬體門檻高(需含 RT Core 的 RTX GPU)。室內 AMR 若只驗 Nav2 行為,Gazebo 足夠;若要做感知模型合成資料、sim-to-real RL、或高擬真感測器測試,Isaac Sim + Isaac Lab 較合適。兩者皆可透過 ROS2 bridge 與 Nav2 串接。

---

## 參考來源(均為 NVIDIA 官方)

- Isaac Sim 產品頁:https://developer.nvidia.com/isaac/sim
- Isaac Sim 5.0 / Isaac Lab 2.2 GA 公告(Technical Blog):https://developer.nvidia.com/blog/isaac-sim-and-isaac-lab-are-now-available-for-early-developer-preview/
- Isaac Lab — Mastering Omniverse(分工說明):https://isaac-sim.github.io/IsaacLab/main/source/how-to/master_omniverse.html
- Isaac Lab — Reference Architecture(環境 / 管理器 / RL 函式庫):https://isaac-sim.github.io/IsaacLab/main/source/refs/reference_architecture/index.html
- Isaac Lab — Creating a Manager-Based RL Environment:https://isaac-sim.github.io/IsaacLab/main/source/tutorials/03_envs/create_manager_rl_env.html
- Isaac Lab — Training with an RL Agent:https://isaac-sim.github.io/IsaacLab/main/source/tutorials/03_envs/run_rl_training.html
- Isaac Lab — isaaclab.envs API:https://isaac-sim.github.io/IsaacLab/main/source/api/lab/isaaclab.envs.html
- Isaac Sim — ROS 2 Navigation 教學:https://docs.isaacsim.omniverse.nvidia.com/5.1.0/ros2_tutorials/tutorial_ros2_navigation.html
- Isaac Sim — Driving TurtleBot using ROS 2:https://docs.isaacsim.omniverse.nvidia.com/5.1.0/ros2_tutorials/tutorial_ros2_drive_turtlebot.html
- Isaac Sim — ROS 2 Bridge:https://docs.isaacsim.omniverse.nvidia.com/5.0.0/py/source/extensions/isaacsim.ros2.bridge/docs/index.html
- Isaac Sim — URDF Importer Extension:https://docs.isaacsim.omniverse.nvidia.com/6.0.0/importer_exporter/ext_isaacsim_asset_importer_urdf.html
- Isaac Sim — Replicator(Perception Data Generation):https://docs.isaacsim.omniverse.nvidia.com/latest/replicator_tutorials/index.html
- Isaac Sim — 硬體 / OS 需求:https://docs.isaacsim.omniverse.nvidia.com/latest/installation/requirements.html

> 本文部分版本號與數字若與你手上的安裝版本不符,以官方對應版本文件為準。
