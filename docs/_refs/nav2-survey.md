# Nav2 導航全棧 survey(基礎參考論文)

robot-notes 的導航與多機調度章節,底層演算法大多來自 ROS2 的 Nav2 stack。這份由 Nav2 核心維護者(Steve Macenski 等)親自寫的 survey,把 Nav2 用到的整套演算法——全域規劃、區域控制、路徑平滑、感知 costmap、行為樹、狀態估計、定位建圖——一次講完,是入門 ROS2 導航最好的單篇起點。

本檔是它的導讀與對照地圖:論文每一節對應 robot-notes 哪一篇。

## 論文資訊(CC BY 4.0)

- **標題**:From the Desks of ROS Maintainers: A Survey of Modern & Capable Mobile Robotics Algorithms in the Robot Operating System 2
- **作者**:Steve Macenski, Tom Moore, David V. Lu, Alexey Merzlyakov, Michael Ferguson
- **出處**:_Robotics and Autonomous Systems_, Vol. 168, 2023
- **DOI**:[10.1016/j.robot.2023.104493](https://doi.org/10.1016/j.robot.2023.104493) ・ **arXiv**:[2307.15236](https://arxiv.org/abs/2307.15236) ・ 授權 **CC BY 4.0**
- **本地 PDF**:[nav2-survey-macenski-2023.pdf](nav2-survey-macenski-2023.pdf)(依 CC BY 4.0 收錄,著作權屬原作者)

## 為什麼當 starter

一台自走機器人要會三件事:知道自己在哪、算出怎麼走、把指令送給輪子。Nav2 把這些拆成清楚的模組,這篇 survey 正好沿著這條線,把每個模組的主流演算法、優缺點、何時選誰講一遍,而且作者就是寫這些程式的人。先讀它建立全貌,再回頭看 robot-notes 各篇細節,比較有地圖感。

論文還附兩個實用對照:Table I(全域規劃器比較)、Table II(區域控制器比較),以及 Appendix A 的「依機器人類型選演算法」速查。

## 章節對照地圖

| 論文章節 | 主題 | 對應 robot-notes |
|---|---|---|
| II 全域路徑規劃 | NavFn / Theta* / 2D-A*(holonomic)、Smac Hybrid-A* / State Lattice(運動學可行) | [路徑規劃與軌跡](../30-navigation/path-planning.md)、[私有系統大迴轉案例](../40-fleet/proprietary-vs-ros2-arbitrary-start.md) |
| III 區域軌跡規劃 | DWB(reactive)、TEB / MPPI(predictive)、RPP / Rotation Shim(geometric/control-law) | [路徑規劃與軌跡](../30-navigation/path-planning.md)、[CONTEXT 術語表](../../CONTEXT.md)(MPPI/DWB/RPP) |
| IV 路徑平滑 | 把規劃出的折線磨平、去抖動 | [路徑規劃與軌跡](../30-navigation/path-planning.md) |
| V 感知 / Costmap 層 | static / obstacle / inflation 等 costmap 層 | [路徑規劃與軌跡](../30-navigation/path-planning.md)、[CONTEXT](../../CONTEXT.md)(costmap/inflation) |
| VI 行為樹 | Nav2 用 BT 編排 規劃→跟隨→恢復 | [CONTEXT](../../CONTEXT.md)(行為樹) |
| VII 狀態估計 | `robot_localization` 的 EKF / UKF 融合 odom/IMU | [定位](../30-navigation/localization.md)、[座標轉換與 TF](../30-navigation/kinematics-and-coordinate-transforms.md) |
| VIII 定位與建圖 | AMCL 定位、SLAM 建圖 | [SLAM 建圖](../30-navigation/slam-mapping.md)、[定位](../30-navigation/localization.md) |
| Appendix A 依機器人型選演算法 | 差速/全向/Ackermann/legged 各該選哪個 planner/controller | 各篇 |
| Appendix B Smac Planner 框架 | Smac 的 2D-A* / Hybrid-A* / State Lattice 共用框架 | [私有系統大迴轉案例](../40-fleet/proprietary-vs-ros2-arbitrary-start.md) |

## 建議讀法

- **只想抓全貌**:I 緒論 → II、III 的開頭 → Appendix A 選型速查。
- **做導航調參**:II / III 各規劃器、控制器的優缺點 + Table I / II。
- **接大迴轉案例**:§II-B(Hybrid-A*、依「可否倒車」選 Dubins / Reeds-Shepp)+ Appendix B(Smac 框架),正是[那篇](../40-fleet/proprietary-vs-ros2-arbitrary-start.md)的上游出處。

## 小提醒

論文以 2022 年 11 月的 Nav2 為準;個別預設值與參數名可能隨版本變動,落地仍以當前 [Nav2 docs](https://docs.nav2.org/) 與原始碼為準(查證示範見[大迴轉案例](../40-fleet/proprietary-vs-ros2-arbitrary-start.md)的 §7 / §8)。
