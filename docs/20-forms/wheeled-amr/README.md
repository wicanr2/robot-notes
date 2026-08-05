# 輪式 AMR

輪子踩在平地上、支撐面固定、只在平面上動——這是四種形態裡約束最強的一種,也因此是唯一能把控制問題整條寫成封閉解的一種。送餐機器人、倉儲搬運車、無人叉車都在這條線上。

這一條線的內容大部分放在[共通核心](../../10-core/)裡,因為它就是本筆記最早展開的形態,很多「核心」的寫法其實是從輪式推出來的。真正只對輪式成立的東西在這裡:

- **[底盤與傳動](chassis-and-drivetrain.md)** — 兩輪差速、萬向輪、輪轂馬達、行星減速機、伺服馬達與底盤輪馬達的差別。

---

## 完整讀法(散在各章)

| 想知道 | 去哪 |
|---|---|
| 輪子怎麼轉起來 | [馬達與 FOC](../../10-core/10-hardware/motors-and-foc.md) → [編碼器](../../10-core/10-hardware/encoders.md) → [底盤與傳動](chassis-and-drivetrain.md) |
| 輪速指令怎麼下、怎麼保安全 | [下位機運動控制](../../10-core/20-firmware/low-level-control.md) → [上下位機協議](../../10-core/20-firmware/host-mcu-protocol.md) → [電源與安全](../../10-core/10-hardware/power-and-safety.md) |
| 車怎麼知道自己在哪、怎麼走 | [座標轉換與 TF](../../10-core/30-navigation/kinematics-and-coordinate-transforms.md) → [SLAM 建圖](../../10-core/30-navigation/slam-mapping.md) → [定位](../../10-core/30-navigation/localization.md) → [路徑規劃](../../10-core/30-navigation/path-planning.md) → [路徑平滑與軌跡](../../10-core/30-navigation/path-smoothing-and-trajectory.md) |
| 多台車怎麼不打架 | [路網與交管](../../40-fleet/roadnet-and-traffic-control.md) → [室內 AMR 路網選型](../../40-fleet/indoor-amr-roadnet-selection.md) → [OpenRMF](../../40-fleet/open-rmf.md) → [VDA5050](../../40-fleet/vda5050.md) |
| 上線要過哪些關 | [法規與認證總覽](../../60-compliance/README.md) |

---

## 為什麼輪式的問題最「乾淨」

三個約束疊起來的結果:

1. **支撐面固定**。四個接觸點一直在地上,重心只要落在輪距圍成的多邊形裡就不會翻。不必像足式那樣隨步態重算支撐多邊形。
2. **平面運動**。位姿只有 `(x, y, θ)` 三個量,而差速車只能控制其中兩個自由度(前進與轉向,不能橫移)——這叫**非完整約束(nonholonomic)**。約束雖然限制了動作,但也讓運動學收斂成兩條可以手推的公式。
3. **接觸不切換**。輪子與地面的接觸是連續的,不像腳有「著地/離地」的離散事件。沒有離散切換,系統就是連續可微的,古典控制理論整套都能用。

這三條一旦鬆掉——例如手臂伸出去改變重心(見[移動操作](../mobile-manipulator/))、或換成腳——問題的性質就變了,不是同一套方法調參數就能解決。
