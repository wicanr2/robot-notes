# 章節編號對照表(§N → 檔案)

各主題檔的章節編號**沿用原始《送餐機器人基礎原理補充》與《系統架構》文件**,方便對照舊版。重組成多檔後,文件裡的跨檔交叉引用(如「見 §11.3」「§4.1 的公式」)可能指向另一個檔。看到 `§N` 不確定在哪,就查這張表。

> 適用範圍:**本表只涵蓋送餐機器人「基礎原理 §1–§28」這套舊編號**(分散在 hardware/firmware/navigation)。**後來新增的主題篇章**(40-fleet、50-physical-ai、60-compliance、90-foundations)用各篇自己的目錄(§1, §2…從頭數,不共用這套編號),直接看該篇開頭即可,不必查本表。
>
> 規則速記:
> - **§1 ～ §28**(基礎原理):分散在 hardware / firmware / navigation,查下表。
> - **§N 帶「安全功能 / 選型 / 軟體分層 / 研發路線 / 風險」語意**(如 §3.1 安全放下位機、§2.4 超音波、§2.5 回充、§3.3 分工):多半指 [系統架構](00-overview/system-architecture.md) 的內部章節,見文末第二張表。

---

## 基礎原理 §1 – §28

| § | 主題 | 檔案 |
|---|---|---|
| §1 | 底盤裝置(差速、萬向輪、輪轂馬達、BLDC、encoder 概觀) | [10-hardware/chassis-and-drivetrain.md](10-hardware/chassis-and-drivetrain.md) |
| §2 | FOC 磁場導向控制 | [10-hardware/motors-and-foc.md](10-hardware/motors-and-foc.md) |
| §3 | 感測器:2D LiDAR、深度相機、IMU | [10-hardware/sensors.md](10-hardware/sensors.md) |
| §4 | M1 底盤控制知識清單與驗收 | [20-firmware/low-level-control.md](20-firmware/low-level-control.md) |
| §5 | BLDC + 行星減速機 | [10-hardware/chassis-and-drivetrain.md](10-hardware/chassis-and-drivetrain.md) |
| §6 | CAN 與 RS485 串接 | [10-hardware/communication-buses.md](10-hardware/communication-buses.md) |
| §7 | 運動學解算 vs PID | [20-firmware/low-level-control.md](20-firmware/low-level-control.md) |
| §8 | x86 NUC 是什麼 | [00-overview/system-architecture.md](00-overview/system-architecture.md)(附錄) |
| §9 | 馬達驅動晶片行銷術語拆解 | [10-hardware/motors-and-foc.md](10-hardware/motors-and-foc.md) |
| §10 | 伺服馬達 vs 底盤輪馬達 | [10-hardware/chassis-and-drivetrain.md](10-hardware/chassis-and-drivetrain.md) |
| §11 | 霍爾編碼器原理與接線 | [10-hardware/encoders.md](10-hardware/encoders.md) |
| §12 | 功率橋與閘極驅動器 | [10-hardware/motors-and-foc.md](10-hardware/motors-and-foc.md) |
| §13 | Open-drain 是什麼 | [10-hardware/digital-circuits.md](10-hardware/digital-circuits.md) |
| §14 | STM32 的 open-drain 程式控制 | [10-hardware/digital-circuits.md](10-hardware/digital-circuits.md) |
| §15 | 為什麼開漏「留下管」 | [10-hardware/digital-circuits.md](10-hardware/digital-circuits.md) |
| §16 | 定子與轉子、Park 變換 | [10-hardware/motors-and-foc.md](10-hardware/motors-and-foc.md) |
| §17 | 有刷 vs 無刷直流馬達 | [10-hardware/motors-and-foc.md](10-hardware/motors-and-foc.md) |
| §18 | 電壓法規與日台標準 | [10-hardware/power-and-safety.md](10-hardware/power-and-safety.md) |
| §19 | 增量式 A/B 相 encoder 圖解 | [10-hardware/encoders.md](10-hardware/encoders.md) |
| §20 | Encoder 回授與 STM32 程式 | [10-hardware/encoders.md](10-hardware/encoders.md) |
| §21 | 2D SLAM 建圖流程 | [30-navigation/slam-mapping.md](30-navigation/slam-mapping.md) |
| §22 | AMCL 定位演算法 | [30-navigation/localization.md](30-navigation/localization.md) |
| §23 | 深度相機輸出(RGB + 深度圖) | [10-hardware/sensors.md](10-hardware/sensors.md) |
| §24 | 深度相機送餐機產品案例 | [10-hardware/sensors.md](10-hardware/sensors.md) |
| §25 | 急停控制 | [10-hardware/power-and-safety.md](10-hardware/power-and-safety.md) |
| §26 | 加減速 ramp 與過流/堵轉保護 | [10-hardware/power-and-safety.md](10-hardware/power-and-safety.md) |
| §27 | Odometry 定義與本質限制 | [30-navigation/localization.md](30-navigation/localization.md) |
| §28 | 地標定位(AprilTag / PnP) | [30-navigation/localization.md](30-navigation/localization.md) |

## 系統架構文件內部章節

跨檔引用若提到安全/選型/軟體分層/研發路線,通常指這裡(全部在 [00-overview/system-architecture.md](00-overview/system-architecture.md)):

| § | 主題 |
|---|---|
| §1 | 整體架構概觀(§1.1 分層、§1.2 送餐資料流) |
| §2 | 硬體選型(§2.4 感測器/超音波、§2.5 電源/回充) |
| §3 | 軟體架構(§3.1 下位機韌體與安全、§3.2 上下位機協議、§3.3 上位機軟體) |
| §4 | 建議研發路線(M1–M5) |
| §5 | 風險與注意事項 |

> 註:基礎原理與系統架構各有一套 §1–§5,語意衝突時依上面的「規則速記」判斷。長期計畫(見 [PLAN.md](../PLAN.md))會逐步把跨檔 `§N` 改成帶連結的引用。
