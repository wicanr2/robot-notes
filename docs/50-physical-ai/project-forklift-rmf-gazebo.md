# 專案探討:在 Gazebo 做叉車搬運(OpenRMF + VDA5050)

把這份筆記學到的東西全部串起來,做一個能跑的小專案:**在 Gazebo 裡一台叉車,聽 OpenRMF 的調度,把棧板從 A 貨架搬到 B 貨架**,並讓「叉起/放下」對映到 VDA5050 的動作。這篇用第一性原理討論——要達成「叉車 Physical AI 模擬」這個目標,**worklist 有哪些、模型怎麼準備、物理參數怎麼設**——而不是直接貼一份 launch 檔。

> 本篇是整合性探討,前置散在各章:[Physical AI 總覽](physical-ai-overview.md)、[Gazebo+ROS2 模擬](simulation-gazebo-ros2.md)、[OpenRMF](../40-fleet/open-rmf.md)、[VDA5050](../40-fleet/vda5050.md)、[座標轉換/TF](../30-navigation/kinematics-and-coordinate-transforms.md)、[路徑規劃](../30-navigation/path-planning.md)。
> 版本基準:**gz sim Harmonic + ROS 2 Jazzy + gz_ros2_control(Jazzy)**;以官方當前為準。

---

## 1. 目標與範圍:先把「做到什麼算成功」釘死

第一性原理的第一步不是寫 code,是**定義可驗證的成功條件**。本專案的最小可驗收目標(MVP):

> 在 Gazebo 倉儲場景裡,一台叉車收到 RMF 下的「把 A 點棧板搬到 B 點」任務後,**自主導航到 A → 對位 → 升叉取貨 → 載運到 B → 放貨 → 回報完成**,全程不撞貨架、可重複執行。

範圍取捨(先做什麼、先不做什麼):
- **要**:單台叉車、單一棧板、固定 A/B 點、RMF 派工 + Nav2 導航 + 升降取放。
- **暫不做**:多台叉車交通協商(RMF 的強項,但留到 MVP 通了再加)、真實叉車後輪轉向運動學、載重對重心的精細物理、生產級 VDA5050 雙向。
- **VDA5050 的定位**:MVP 階段可先讓 RMF fleet adapter 直接驅動叉車(省一層);要展示「標準介面」時再把 pick/drop 對映成 VDA5050 action 接上(見 §10)。

## 2. 整體架構:每層各司其職

<p align="center"><img src="../../img/forklift-sim-architecture.svg" width="680" alt="叉車 demo 技術堆疊:Gazebo→ros_gz_bridge→ros2_control+Nav2→OpenRMF(+VDA5050)"></p>

由下而上:**Gazebo(物理 + 模型)→ ros_gz_bridge(gz↔ROS2)→ ros2_control(升降)+ Nav2(導航/對位)→ OpenRMF(派工/協商)→(選用)VDA5050 connector**。每層的「為什麼」在後面各節展開。

## 3. 三個關鍵設計決策(第一性原理的分岔點)

做這個 demo,最該先想清楚的是三個「走哪條路」的決策——選錯會在實作中卡很久:

| 決策 | 選項 A(簡單,先選) | 選項 B(真實,後換) | 第一性原理 |
|---|---|---|---|
| **底盤驅動** | 差速 DiffDrive(模擬簡化) | 依真實車型(見下) | Nav2 對差速支援最成熟;但 diff-drive **不等於真叉車運動學**,要清楚這是簡化 |
| **取放怎麼做** | Teleport Dispenser/Ingestor(瞬移) | DetachableJoint(真實叉起) | 要展示「調度流程」用瞬移最省力(RMF demo 就這樣);要展示「真實貨叉物理」才上 DetachableJoint |
| **VDA5050** | 先不接,RMF 直接驅動 | 接 connector,pick/drop=action | 標準介面是價值但不是 MVP 必需;先把流程跑通,再加標準層 |

> 這張表本身就是專案的「風險前置」:三個都先選 A,最快看到端到端跑通;每個再獨立升級成 B,風險被切開、不會一次全擔。

### 3.1 先搞清楚:真實叉車的驅動/轉向不是差速

「叉車」不是單一運動學,主流分兩種構型(查證自 Toyota/Raymond/Hyster 等原廠):

<p align="center"><img src="../../img/forklift-drive-configs.svg" width="680" alt="叉車兩構型:三輪平衡重式(前兩驅+後轉向)vs 前移式 reach truck(單一驅動轉向舵輪+從動載重輪)"></p>

- **三輪平衡重式 (counterbalance)**:**前兩輪驅動**(雙馬達,負載壓前軸→前輪牽引力大、雙前驅可小半徑轉),後單輪轉向。
- **前移式 / 倉儲堆高機 (reach truck / stacker)**:**單一「驅動轉向一體輪(舵輪)」在後**(遠離牙叉端),負責牽引 + 轉向;**牙叉端的兩輪是從動載重輪 (load wheels),只滾不驅動**。第一性原理:load wheels 在貨叉下、要小且能伸進貨架、承受變動重載,做成驅動+轉向太複雜;把驅動+轉向集中到遠離負載的單一後輪,一顆馬達牽引、一顆轉向,控制最單純。

**對模擬的意義(務必誠實)**:reach truck 那種「單一驅動轉向輪 + 從動輪」運動學是**三輪車 (tricycle)**,對應 gz 的 **`TricycleSteering`**,**不是** `DiffDrive`。本專案 MVP 用 `DiffDrive` 是「為了最快接通 Nav2」的**模擬簡化**,代價是底盤運動學不符真實 reach truck(原地旋轉能力、轉彎軌跡都不同);要做擬真就換 `TricycleSteering`/`AckermannSteering`,Nav2 端也要改用支援該運動學的 planner/controller(Hybrid-A* + 非完整約束 controller)。

## 4. 模型怎麼準備

### 4.1 叉車 URDF/SDF 結構

<p align="center"><img src="../../img/forklift-urdf-structure.svg" width="660" alt="叉車 URDF:base_link 差速底盤 → mast_link → prismatic 升降 → fork_carriage_link"></p>

關鍵是「升降 = `prismatic`(滑動)關節」:`base_link --fixed--> mast_link --prismatic(Z 軸)--> fork_carriage_link --fixed--> 貨叉`。底盤掛 DiffDrive plugin（出 `/odom`、tf）、gpu_lidar（`/scan`）、imu；升降關節用 ros2_control 的 `JointTrajectoryController` 控位置。**`fork_carriage_link` 是取放的關鍵 link**——當 DetachableJoint 的 `parent_link`。

### 4.2 棧板、貨架、倉儲場景

- **棧板 pallet**:一個 box model,尺寸取 EPAL 標準 1.2 × 0.8 m;要有 `visual + collision + inertial` 三件(少了 inertial 物理會出錯)。
- **貨架 rack**:設 `<static>true</static>` 的固定多層 box(取放點設在某層高度);static 物件不參與動力學、省算力也不會被撞飛。
- **倉儲 world**:可直接拿 `aws-robotics/aws-robomaker-small-warehouse-world` 改,省去手刻;取放點放 Teleport Dispenser/Ingestor 或標成 nav graph 的 waypoint。
- **現成素材**:gz Fuel 模型庫可搜 pallet/forklift/warehouse 直接 `<include>`;gz-sim repo 的 `detachable_joint.sdf` 範例正是「車載物件再分離」的範本。

## 5. 物理參數怎麼設(模擬穩不穩,八成看這裡)

這是新手最容易忽略、卻最常讓模擬「爆炸 / 抖動 / 打滑」的地方。第一性原理:**模擬器是在解牛頓方程,參數不合理,數值積分就發散**。逐項:

### 5.1 質量與慣性張量(最關鍵)

- **每個會動的 link 都要有合理的 `mass` 與 `inertia`(慣性張量)**。最常見的爆炸原因就是 inertia 亂填(留 0 或 1e-9)。
- box(長寬高 a×b×c、質量 m)的慣性張量有公式,務必用它算,別亂填:

```
Ixx = m(b² + c²)/12     Iyy = m(a² + c²)/12     Izz = m(a² + b²)/12
（Ixy = Iyz = Ixz = 0,對齊主軸時)
```

- **慣性要和質量、尺寸一致**:一個 20kg、1.2m 的棧板,inertia 數量級應在 ~1（kg·m²),不是 0.001 也不是 1000。不一致 → 接觸時抖動或彈飛。
- **質量比不要太懸殊**:叉車幾百 kg、棧板幾十 kg 還行;但棧板設 0.01kg 配叉車 500kg,接觸求解器會不穩。MVP 階段**棧板設輕一點(5–20kg)** 較穩。

### 5.2 摩擦係數(決定會不會打滑)

- **輪子與地面的摩擦 μ 要夠高**(乾地 0.8–1.0)。太低 → 差速車原地打滑、odom 狂漂、Nav2 定位跟著爛(呼應 [感測器 §3.3](../10-hardware/sensors.md) 的打滑問題)。
- 棧板與貨叉之間:用 DetachableJoint 剛性連接時不靠摩擦;若想靠摩擦夾持(較難穩)才需要調高接觸摩擦。
- 貨叉/地面接觸的 `<surface>` 可設 `mu`、`mu2`(兩個方向的摩擦)。

### 5.3 關節限制與致動力

- **prismatic 升降關節**:`<limit>` 要設 `lower/upper`(行程,如 0~1.5m)、`effort`(最大力,**要 ≥ (叉車前段+載重)×g + 餘裕**,否則升不動)、`velocity`(升降速度上限)。
- effort 設太小 → 升不起棧板;設無限大 → 升降瞬間衝擊、物理不穩。給一個物理合理值。

### 5.4 物理引擎步長與求解器

- **`max_step_size`(模擬步長)**:常見 1ms(0.001s)。步長越大越快但越不穩;接觸/取放這種需要穩定的場景,步長別開太大。
- **`real_time_factor` / 求解器迭代數**:headless 訓練可拉高 RTF 加速;接觸不穩時增加 solver iterations。
- 這幾個是「速度 vs 穩定」的取捨旋鈕,接觸抖動先從「縮小步長、增加迭代」下手。

### 5.5 DetachableJoint 的物理前提(取放專屬)

- 運動拓樸必須**樹狀(不可成環)**。
- **初始狀態父/子 model 不可有碰撞**,否則 joint 建不起來——所以「對位後才升叉、升到位才 attach」的時機要控好。
- 分離後父子若會互撞,父 model 要設 `<self_collide>true</self_collide>`。
- **接觸中不支援 reattach**——attach/detach 的時機要避開正在碰撞的瞬間。

## 6. 地面異常:給模擬加「壓力測試」

平地上一切正常的系統,不代表它穩。**地面異常的本質,是專門用來逼出感測缺陷的測試夾具**——沒有異常,你永遠不知道 odom 會不會漂、IMU 接不接得到、定位扛不扛得住。在 gz 裡擺幾種異常:

| 異常 | 怎麼建 | 逼出什麼缺陷(第一性原理) |
|---|---|---|
| **低摩擦「濕滑」區** | 一塊地磚 box,`<surface><friction><ode>` 設低 `mu`/`mu2`(如 0.05)、調高 `slip1`/`slip2` | 切向需求 > μ×法向力 → **輪子打滑空轉** → 輪式 odom 多積分 → **位置漂** |
| **凸塊 / 門檻** | 很扁的小 box(如 0.05×1×0.02)貼地擺 | 過坎瞬間 → **IMU 的 a_z、ω_y 出現尖峰** |
| **坡道 ramp** | 傾斜 box(pose 帶 pitch,如 0.15 rad) | 上坡需更多扭矩、輪易空轉(odom 高估);過度傾斜 → **重心超出支撐多邊形 → 翻車** |
| **縫隙 / 起伏地形** | 有限尺寸地板拼接留空(gap);大面積起伏用 **heightmap**(灰階圖→地形,放進 `<collision>` 才影響物理) | 顛簸、卡住、定位抖動 |

實作要點:
- 摩擦/彈跳調在接觸面的 `<surface>`:`<friction><ode><mu>/<mu2>/<slip1>/<slip2>`、`<bounce><restitution_coefficient>`、`<contact><ode><kp>/<kd>`(接觸剛度/阻尼,影響過坎手感)。
- **heightmap 要設 collision 才有物理**(只放 visual 輪子會穿透);gz 官方建議 heightmap world 把碰撞偵測器設成 `bullet`(DART 預設對 heightmap 較差)。
- 現成素材:gz-sim 的 `examples/worlds/heightmap.sdf`、`dem_*.sdf`(DEM 地形)可改。

## 7. 感測器與物理整合:讓異常「反映得出來」

地面異常擺好了,但**如果感測器讀的是「理想真值」,異常就完全看不到**。第一性原理:**感測器必須讀模擬的物理量**,異常才會反映成 odom 漂移、IMU 尖峰、雷射量測變化——這才有訓練/測試的意義。

<p align="center"><img src="../../img/sensor-physics-integration.svg" width="700" alt="感測器讀模擬物理:低摩擦→輪式odom漂、過坎→IMU尖峰、LiDAR打collision;EKF融合odom+IMU、AMCL用LiDAR修漂"></p>

三個關鍵接法:

- **odom 一定要用「輪式」不能用真值**:gz 有兩個 plugin——`DiffDrive`(讀**輪關節轉動量**積分,**會反映打滑/坡度** → 會漂)vs `OdometryPublisher`(直接讀車的**真實世界位姿** → 不漂)。**要看到異常造成 odom 漂移,就必須用 `DiffDrive` 的輪式 odom**;`OdometryPublisher` 的真值只拿來當**驗收基準**(算漂移量 = 輪式 odom − 真值)。
- **IMU / LiDAR 讀物理**:`gz-sim-imu-system` 讀模擬的角速度/加速度(過坎、傾斜出尖峰);`gpu_lidar` 的光線打在 world 的碰撞/視覺幾何上(斜坡會量到不同高度)。兩者都該掛 **noise model**(`<noise type="gaussian">` 設 `stddev`、`bias_*`)讓它更像真感測器,而不是完美量測。
- **融合 = robot_localization EKF + AMCL**:EKF 融合「會漂的輪式 odom(信任其 `vx`)+ IMU(信任其 `ω_yaw`、去重力後的 `a`)」→ 發布平滑的 `odom→base_link`,抑制短期漂移;AMCL 用 LiDAR 對 static map 重定位 → 發布 `map→odom` 修長期漂(離散跳變)。**EKF 不碰 LiDAR、AMCL 不碰高頻 odom**,正好對應 [座標篇](../30-navigation/kinematics-and-coordinate-transforms.md) 的 TF 兩層、[感測器 §3.3](../10-hardware/sensors.md)「距離信 encoder、角度信陀螺儀」、[定位 §27](../30-navigation/localization.md)。
- **時間要對齊**:所有 ROS 2 節點 `use_sim_time:=true` 吃 gz 的 `/clock`(單向橋 `rosgraph_msgs/Clock`),否則 tf/感測時間源混用會報錯。

## 8. Worklist:第一性原理排序的里程碑

排序原則:**每一步都建立在前一步「已驗證可動」之上,且每步都有可量化、可自動判定的 pass/fail**(呼應 [Renode 篇](../20-firmware/board-simulation-renode.md) 的回饋迴路精神)。先讓「車會動」,再「會感知」,再「會搬」,最後「RMF 指揮」。**這份表就是給其他 agent 的執行規格**:一列一個可獨立交付、可驗收的里程碑。

| 里程碑 | 產出 artifact | 可量化驗收(pass/fail) |
|---|---|---|
| **M0 場景與模型** | 叉車 URDF/xacro + 棧板/貨架 SDF + 平地 world;物理參數設好(§5) | gz 裡靜置 10s 不抖、不下沉、位置不漂 > 1cm |
| **M1 底盤遙控** | DiffDrive plugin + `bridge.yaml` + `use_sim_time`;鍵盤 `/cmd_vel` | 遙控直線 5m,**輪式 odom 對真值(OdometryPublisher)漂移 < 5cm** |
| **M2 升降可控** | ros2_control + JTC + `controllers.yaml` | 下指令叉子升到指定高度 ±2cm、停得住 |
| **M3 感測 + 地面異常** | 加 LiDAR/IMU(含 noise)+ 異常 world(§6) | 過低摩擦區後 **odom 漂移明顯 > 平地**;過坎時 **IMU `a_z` 出現尖峰 > 閾值** |
| **M4 感測融合** | robot_localization EKF(§7)`ekf.yaml` | **EKF 輸出對真值的誤差 < 純輪式 odom**(異常區尤其) |
| **M5 自主導航** | slam_toolbox 建圖 + Nav2(footprint 長方形)+ docking | 指定點往返成功;到點誤差 < 0.25m / 0.25rad;能對位到貨架前 |
| **M6 取放** | DetachableJoint(或 Teleport Dispenser/Ingestor)接「對位+升叉」時機 | 叉起棧板、載運、放下,不掉不穿模 |
| **M7 RMF 派工** | fleet adapter(`actions: pick/drop`)+ nav graph(traffic-editor) | 下「A→B」Delivery 任務 → 自動完成整趟(§11 流程) |
| **M8(選)VDA5050** | pick/drop 對映 VDA5050 action(HARD)+ connector | 經 VDA5050 order/state 走完同一趟 |
| **M9(選)多車協商** | 加第二台叉車,rmf_traffic 協商 | 兩車不死鎖、會互讓 |

> 為什麼是這個順序?**M0–M2 驗證「物理與致動」,M3–M4 驗證「感知會反映異常、融合能抑制」,M5 驗證「導航」,M6 驗證「操作」,M7+ 才疊「調度」**。每層獨立可驗收,壞了能單獨定位——比「全接起來一起 debug」省十倍時間。M3/M4 刻意排在導航之前:**先確認 odom 會漂、IMU 接得到、EKF 壓得下,再讓 Nav2 站在這之上**,否則導航爛了分不清是規劃問題還是感測問題。

## 9. 給其他 agent 執行的規劃骨架

這份探討要能直接派給其他 agent 執行,需要三樣東西落地(以下為可照抄的慣例):

**package / 檔案結構**:

```
forklift_gz_sim/
├── description/  forklift.urdf.xacro(含 gz plugin、sensor)、forklift.gazebo.xacro
├── worlds/       flat.sdf(基準平地)、terrain_anomaly.sdf(ramp/bump/gap/低摩擦/heightmap)
├── config/       ekf.yaml、bridge.yaml(topic 對應)、nav2_params.yaml、controllers.yaml
├── launch/       sim.launch.py、localization.launch.py、nav2.launch.py
└── maps/         AMCL static map
```

**派工給 agent 的紀律**(對齊本專案工作守則):每個 agent 認領一個里程碑(§8 一列),產出該列的 artifact,並**自己用該列的 pass/fail 訊號驗收**;驗收用 `ros2 topic echo` / `ros2 bag record` + 離線比對腳本(例:錄 `/odom` 與真值 pose,算漂移量;抓 `/imu` 的 `a_z` 尖峰;Nav2 到點誤差)。**有界執行**:做不到就誠實標受阻,不要硬湊綠燈。

**headless 跑法(CI / agent 環境)**:`gz sim -s -r --headless-rendering <world>.sdf`(`-s` server-only、`-r` 載入即跑、`--headless-rendering` 走 EGL 供 gpu_lidar);無 GPU 時用 CPU `type="lidar"` 或接受軟體渲染變慢。記得設 `GZ_SIM_RESOURCE_PATH` / `GZ_SIM_PLUGIN_PATH`,否則 `<include>` 的模型找不到。

## 10. RMF 整合與 VDA5050 對映

- **取放怎麼讓 RMF 表達**:兩條路——(A) RMF 內建 **Delivery Task + Teleport Dispenser/Ingestor**(在 A 放 Dispenser、B 放 Ingestor,瞬移取放,最省力,RMF demo 就這樣);(B) 自訂 **PerformAction**(fleet adapter 用 `add_performable_action("pick"/"drop", ...)` 宣告、`config.yaml` 的 `actions: [pick, drop]`、`execute_action` callback 內實際驅動升叉 + DetachableJoint,完成呼叫 `execution.finished()`)。
- **nav graph**:用 traffic-editor 畫 waypoint/lane,貨架前的 waypoint 標上 dispenser/ingestor 名稱或 dock 名。
- **VDA5050 對映**:叉車的「叉起/放下」= VDA5050 order 某 node 上的 **action**,`actionType: pick/drop`、`blockingType: HARD`(停車作業)、`actionParameters` 帶 `loadType: EPAL`。RMF 端要接需經 VDA5050 connector(`tum-fml/vda5050_connector`、`inorbit-ai/ros_amr_interop` 等),官方 RMF-as-VDA5050-master adapter 仍非現成(見 [open-rmf §4](../40-fleet/open-rmf.md))。

## 11. 一趟搬運的端到端流程

<p align="center"><img src="../../img/pallet-pickup-flow.svg" width="700" alt="搬運流程:RMF 派工→導到A→對位升叉→取貨→載運到B→放貨,Nav2/docking/DetachableJoint/VDA5050 對映"></p>

## 12. 風險與待查證

- **取放的時機控制**是最容易卡的:DetachableJoint 要求 attach 前父子不碰撞、接觸中不能 reattach——「對位→升叉→attach」的觸發條件要自己用位置/contact 判斷。MVP 想避開可先用 Teleport 瞬移。
- **物理不穩**多源於 inertia 亂填、μ 太低、步長太大(見 §5);先排除這三個。
- **待查證**:① Harmonic `DetachableJoint` 的 attach topic 是否支援 runtime 動態指定任意 child(官方偏向「reattach 同一 child」);② Fuel 上現成 forklift/EPAL/rack 模型清單;③ RMF↔VDA5050 維護中的橋接 repo;④ RMF PerformAction 任務 JSON schema;⑤ Jazzy 的 cmd_vel 是 `Twist` 還是 `TwistStamped`。動手前逐一確認。

## 13. 來源與現成素材

- Gazebo:[DetachableJoint(api/sim/9)](https://gazebosim.org/api/sim/9/detachablejoints.html)、[detachable_joint.sdf 範例](https://github.com/gazebosim/gz-sim/blob/ign-gazebo5/examples/worlds/detachable_joint.sdf)、[Fuel 模型插入](https://gazebosim.org/docs/latest/fuel_insert/)
- 控制/導航:[gz_ros2_control(Jazzy)](https://control.ros.org/jazzy/doc/gz_ros2_control/doc/index.html)、[Nav2 gz 感測器](https://docs.nav2.org/setup_guides/sensors/setup_sensors_gz.html)
- RMF:[PerformAction tutorial](https://osrf.github.io/ros2multirobotbook/integration_fleets_action_tutorial.html)、[rmf_simulation(Teleport plugins)](https://github.com/open-rmf/rmf_simulation)、[rmf_demos](https://github.com/open-rmf/rmf_demos)
- VDA5050:[官方規格](https://github.com/VDA5050/VDA5050/blob/main/VDA5050_EN.md)
- 現成倉儲:[aws-robomaker-small-warehouse-world](https://github.com/aws-robotics/aws-robomaker-small-warehouse-world)
