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
- **VDA5050 的定位**:MVP 階段可先讓 RMF fleet adapter 直接驅動叉車(省一層);要展示「標準介面」時再把 pick/drop 對映成 VDA5050 action 接上(見 §7)。

## 2. 整體架構:每層各司其職

<p align="center"><img src="../../img/forklift-sim-architecture.svg" width="680" alt="叉車 demo 技術堆疊:Gazebo→ros_gz_bridge→ros2_control+Nav2→OpenRMF(+VDA5050)"></p>

由下而上:**Gazebo(物理 + 模型)→ ros_gz_bridge(gz↔ROS2)→ ros2_control(升降)+ Nav2(導航/對位)→ OpenRMF(派工/協商)→(選用)VDA5050 connector**。每層的「為什麼」在後面各節展開。

## 3. 三個關鍵設計決策(第一性原理的分岔點)

做這個 demo,最該先想清楚的是三個「走哪條路」的決策——選錯會在實作中卡很久:

| 決策 | 選項 A(簡單,先選) | 選項 B(真實,後換) | 第一性原理 |
|---|---|---|---|
| **底盤驅動** | 差速 DiffDrive | 後輪轉向 Ackermann/Tricycle | Nav2 對差速支援最成熟、odom/cmd_vel 最單純;先求導航跑通,再換真叉車運動學 |
| **取放怎麼做** | Teleport Dispenser/Ingestor(瞬移) | DetachableJoint(真實叉起) | 要展示「調度流程」用瞬移最省力(RMF demo 就這樣);要展示「真實貨叉物理」才上 DetachableJoint |
| **VDA5050** | 先不接,RMF 直接驅動 | 接 connector,pick/drop=action | 標準介面是價值但不是 MVP 必需;先把流程跑通,再加標準層 |

> 這張表本身就是專案的「風險前置」:三個都先選 A,最快看到端到端跑通;每個再獨立升級成 B,風險被切開、不會一次全擔。

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

## 6. Worklist:第一性原理排序的里程碑

排序原則:**每一步都建立在前一步「已驗證可動」之上,且每步都有可驗收的 pass/fail**(呼應 [Renode 篇](../20-firmware/board-simulation-renode.md) 的回饋迴路精神)。先讓「車會動」,再讓「車會搬」,最後才「RMF 來指揮」。

| 里程碑 | 要做的事 | 驗收(pass/fail) |
|---|---|---|
| **M0 場景與模型** | 倉儲 world + 叉車 URDF(底盤+prismatic+感測器)+ 棧板/貨架,物理參數設好(§5) | gz 裡叉車靜置不抖、不下沉、不爆炸 |
| **M1 底盤遙控** | DiffDrive plugin + ros_gz_bridge 出 `/odom /scan /tf`;鍵盤 `/cmd_vel` 遙控 | 遙控前進/轉彎,odom 不狂漂、scan 正常 |
| **M2 升降可控** | ros2_control + JointTrajectoryController 控 prismatic | 下指令叉子升到指定高度、停得住 |
| **M3 自主導航** | slam_toolbox 建圖 + Nav2(footprint 設長方形)點對點導航 + docking 精對位 | 指定點往返成功、能對位到貨架前 |
| **M4 取放** | DetachableJoint(或 Teleport Dispenser/Ingestor)接到「對位+升叉」時機 | 能叉起棧板、載運、放下,不掉不穿模 |
| **M5 RMF 派工** | fleet adapter(宣告 `actions: pick/drop`)+ nav graph 標取放點;下 Delivery 任務 | RMF 下「A→B」任務 → 叉車自動完成整趟(§8 流程) |
| **M6(選)VDA5050** | pick/drop 對映成 VDA5050 action(HARD);接 connector | 經 VDA5050 order/state 走完同一趟 |
| **M7(選)多車協商** | 加第二台叉車,RMF rmf_traffic 協商窄道/路口 | 兩車不死鎖、會互讓 |

> 為什麼是這個順序?**M0–M2 在驗證「物理與致動」,M3 驗證「感知與導航」,M4 驗證「操作」,M5+ 才疊「調度」**。把「物理穩不穩」「導航準不準」「取放對不對」「調度通不通」拆成獨立可驗收的層,任何一層壞了都能單獨定位——這比「全部接起來再一起 debug」省十倍時間。

## 7. RMF 整合與 VDA5050 對映

- **取放怎麼讓 RMF 表達**:兩條路——(A) RMF 內建 **Delivery Task + Teleport Dispenser/Ingestor**(在 A 放 Dispenser、B 放 Ingestor,瞬移取放,最省力,RMF demo 就這樣);(B) 自訂 **PerformAction**(fleet adapter 用 `add_performable_action("pick"/"drop", ...)` 宣告、`config.yaml` 的 `actions: [pick, drop]`、`execute_action` callback 內實際驅動升叉 + DetachableJoint,完成呼叫 `execution.finished()`)。
- **nav graph**:用 traffic-editor 畫 waypoint/lane,貨架前的 waypoint 標上 dispenser/ingestor 名稱或 dock 名。
- **VDA5050 對映**:叉車的「叉起/放下」= VDA5050 order 某 node 上的 **action**,`actionType: pick/drop`、`blockingType: HARD`(停車作業)、`actionParameters` 帶 `loadType: EPAL`。RMF 端要接需經 VDA5050 connector(`tum-fml/vda5050_connector`、`inorbit-ai/ros_amr_interop` 等),官方 RMF-as-VDA5050-master adapter 仍非現成(見 [open-rmf §4](../40-fleet/open-rmf.md))。

## 8. 一趟搬運的端到端流程

<p align="center"><img src="../../img/pallet-pickup-flow.svg" width="700" alt="搬運流程:RMF 派工→導到A→對位升叉→取貨→載運到B→放貨,Nav2/docking/DetachableJoint/VDA5050 對映"></p>

## 9. 風險與待查證

- **取放的時機控制**是最容易卡的:DetachableJoint 要求 attach 前父子不碰撞、接觸中不能 reattach——「對位→升叉→attach」的觸發條件要自己用位置/contact 判斷。MVP 想避開可先用 Teleport 瞬移。
- **物理不穩**多源於 inertia 亂填、μ 太低、步長太大(見 §5);先排除這三個。
- **待查證**:① Harmonic `DetachableJoint` 的 attach topic 是否支援 runtime 動態指定任意 child(官方偏向「reattach 同一 child」);② Fuel 上現成 forklift/EPAL/rack 模型清單;③ RMF↔VDA5050 維護中的橋接 repo;④ RMF PerformAction 任務 JSON schema;⑤ Jazzy 的 cmd_vel 是 `Twist` 還是 `TwistStamped`。動手前逐一確認。

## 10. 來源與現成素材

- Gazebo:[DetachableJoint(api/sim/9)](https://gazebosim.org/api/sim/9/detachablejoints.html)、[detachable_joint.sdf 範例](https://github.com/gazebosim/gz-sim/blob/ign-gazebo5/examples/worlds/detachable_joint.sdf)、[Fuel 模型插入](https://gazebosim.org/docs/latest/fuel_insert/)
- 控制/導航:[gz_ros2_control(Jazzy)](https://control.ros.org/jazzy/doc/gz_ros2_control/doc/index.html)、[Nav2 gz 感測器](https://docs.nav2.org/setup_guides/sensors/setup_sensors_gz.html)
- RMF:[PerformAction tutorial](https://osrf.github.io/ros2multirobotbook/integration_fleets_action_tutorial.html)、[rmf_simulation(Teleport plugins)](https://github.com/open-rmf/rmf_simulation)、[rmf_demos](https://github.com/open-rmf/rmf_demos)
- VDA5050:[官方規格](https://github.com/VDA5050/VDA5050/blob/main/VDA5050_EN.md)
- 現成倉儲:[aws-robomaker-small-warehouse-world](https://github.com/aws-robotics/aws-robomaker-small-warehouse-world)
