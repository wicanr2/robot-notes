# 共通核心:換了形態也不會變的那些

一台輪式 AMR、一隻四足機器狗、一台人形、一台背著機械手臂的搬運車,外觀差很遠,但拆開來有很大一塊是同一批東西:都要有馬達把電變成力矩、都要有編碼器知道自己轉了多少、都要有一條匯流排把指令送下去、都要知道自己在地圖上哪裡、都要算一條不會撞到東西的路。

這一章放的就是**這一塊**。判準很簡單:**把機器人的形態換掉,這篇文件還成不成立?** 成立的放這裡,不成立的放 [形態分支](../20-forms/)。

---

## 三個層次

| 層 | 解什麼問題 | 為什麼形態無關 |
|---|---|---|
| **[10-hardware](10-hardware/)** | 電怎麼變成力矩、感測器怎麼把物理量變成數字、訊號怎麼在板子之間跑 | BLDC 的換相原理、編碼器的正交解碼、CAN 的仲裁機制,不管驅動的是輪子還是膝關節都一樣 |
| **[20-firmware](20-firmware/)** | 上位機的意圖怎麼變成馬達實際在轉、當機了怎麼辦 | PID 追目標、控制環要固定週期、通訊逾時要安全減速——這些是控制迴路本身的性質,跟被控對象是什麼無關 |
| **[30-navigation](30-navigation/)** | 我在哪、地圖長什麼樣、怎麼從 A 到 B | SLAM 的掃描匹配、AMCL 的粒子濾波、costmap 的膨脹、路徑平滑的曲率連續性,都在「平面上的剛體」這個抽象上成立 |

---

## 分岔點在哪

核心不是完全沒有形態的痕跡。有四個地方會分岔,每一處都在對應文件裡標了往哪走:

| 分岔點 | 核心給到哪 | 換形態之後 |
|---|---|---|
| **底盤運動學**(輪速 ↔ 車體速度) | [座標轉換與 TF](30-navigation/kinematics-and-coordinate-transforms.md) 的 TF 樹與 REP-105 慣例對所有形態成立 | 差速正逆解只對輪式成立;足式要處理浮動基座與接觸排程,見 [形態分支](../20-forms/) |
| **致動器選型** | [馬達與 FOC](10-hardware/motors-and-foc.md) 的 FOC 原理、[編碼器](10-hardware/encoders.md) 的回授 | 輪式用輪轂馬達 + 行星減速;足式要低減速比、高扭矩密度的 QDD;手臂用諧波或擺線減速機 |
| **狀態估計** | [定位](30-navigation/localization.md) 的 odometry 與 AMCL | 輪式 odometry 來自輪子;足式要靠腿部運動學 + 接觸偵測反推,而且基座會浮動 |
| **控制層** | [下位機運動控制](20-firmware/low-level-control.md) 的 PID、加減速 ramp、逾時保護 | 平衡、全身控制、力/阻抗控制是另一個量級的問題,不在 PID 這一層 |

---

## 從哪開始讀

沒有硬體背景 → [馬達與 FOC](10-hardware/motors-and-foc.md) → [編碼器](10-hardware/encoders.md) → [下位機運動控制](20-firmware/low-level-control.md)。

已經會寫軟體、想直接看導航 → [座標轉換與 TF](30-navigation/kinematics-and-coordinate-transforms.md) → [SLAM 建圖](30-navigation/slam-mapping.md) → [定位](30-navigation/localization.md) → [路徑規劃](30-navigation/path-planning.md)。

看到 `§N` 這種舊編號不知道在哪一篇 → 查 [章節對照表](../section-map.md)。
