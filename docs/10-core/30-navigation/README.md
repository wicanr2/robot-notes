# 導航:我在哪、地圖長什麼樣、怎麼從 A 到 B

三個問題其實是同一個迴圈的三段:**先有共同的座標語言,才談得上地圖與定位;有了定位,才談得上規劃路徑;規劃出來的折線還要磨平,車才走得順。**

| # | 篇 | 一句話 |
|---|---|---|
| 1 | [運動學與座標轉換](kinematics-and-coordinate-transforms.md) | 全篇的共同語言:REP-103 軸向、roll/pitch/yaw、map / odom / base_link 為什麼要分層 |
| 2 | [SLAM 建圖](slam-mapping.md) | 「要定位需地圖、要建圖需定位」這個雞生蛋怎麼解;迴圈閉合為什麼是真正的難點 |
| 3 | [定位](localization.md) | AMCL 為什麼用一堆粒子而不是一個高斯;地標與 AprilTag 怎麼補 |
| 4 | [路徑規劃](path-planning.md) | Nav2 為什麼分三層;costmap 的 inflation 在解什麼 |
| 5 | [路徑平滑與軌跡生成](path-smoothing-and-trajectory.md) | 折線的轉角曲率是無限大,車開不過去;G0–G3、Bézier、B-spline、速度規劃 |
| 6 | [3D LiDAR SLAM](slam-3d-lidar.md) | 換成多線光達之後多了什麼、難在哪;**§4 與 §8 是選型時再回來查的表** |

> 第 2、3、6 篇反覆用到「最大化似然 ⟺ 最小化加權殘差平方和」——那一步的推導在[高斯第一性原理](../../90-foundations/gaussian-from-first-principles.md#補一條為什麼配得好不好總是變成平方和)。
>
> 這一層講「該往哪走」,[硬體](../10-hardware/)講「東西是什麼」,[韌體](../20-firmware/)講「怎麼指揮它」。多台車之間怎麼協調在[多機調度](../../40-fleet/)。
