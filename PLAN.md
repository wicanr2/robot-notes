# robot-notes 整理計畫(PLAN)

把機器人知識「從軟體到硬體」完整整理成一套可在 GitHub 上隨時閱讀的筆記。以送餐機器人(室內 AMR)為主軸,逐步擴展到調度軟體、主板模擬與 Physical AI。

每個主題一個 markdown,`README.md` 當索引入口。每完成一輪就更新 GitHub,並請「專家」與「學生」兩個角色的 agent 讀過新文件,確認清楚到能讓人快速理解。

---

## 目錄結構

```
robot-notes/
├── README.md                 # 索引入口(GitHub 首頁)
├── PLAN.md                   # 本檔:整理計畫與進度
├── CONTEXT.md                # 術語表(ubiquitous language)
├── img/                      # 概念圖與示意圖(SVG 為主)
└── docs/
    ├── 00-overview/       # 系統全貌
    │   └── system-architecture.md
    ├── 10-core/           # 共通核心 —— 換了形態也還在
    │   ├── README.md
    │   ├── 10-hardware/   # 硬體:電怎麼變成力矩、感測器怎麼把物理量變成數字
    │   │   ├── README.md
    │   │   ├── communication-buses.md
    │   │   ├── digital-circuits.md
    │   │   ├── encoders.md
    │   │   ├── lidar-landscape.md
    │   │   ├── motors-and-foc.md
    │   │   ├── power-and-safety.md
    │   │   └── sensors.md
    │   ├── 20-firmware/   # 韌體:意圖怎麼變成馬達實際在轉
    │   │   ├── README.md
    │   │   ├── board-simulation-renode.md
    │   │   ├── host-mcu-protocol.md
    │   │   ├── low-level-control.md
    │   │   └── stm32-rest-tls.md
    │   └── 30-navigation/ # 導航:我在哪、地圖長什麼樣、怎麼從 A 到 B
    │       ├── README.md
    │       ├── kinematics-and-coordinate-transforms.md
    │       ├── localization.md
    │       ├── path-planning.md
    │       ├── path-smoothing-and-trajectory.md
    │       ├── slam-3d-lidar.md
    │       └── slam-mapping.md
    ├── 20-forms/          # 形態分支 —— 換了形態就得換
    │   ├── README.md
    │   ├── legged/        # 四足
    │   │   ├── README.md
    │   │   ├── gait-and-actuation.md
    │   │   └── legged-fundamentals.md
    │   ├── mobile-manipulator/ # 搬運車 + 機械手臂
    │   │   ├── README.md
    │   │   ├── arm-kinematics.md
    │   │   └── mobile-manipulation.md
    │   └── wheeled-amr/   # 輪式 AMR
    │       ├── README.md
    │       └── chassis-and-drivetrain.md
    ├── 40-fleet/          # 多機調度
    │   ├── README.md
    │   ├── indoor-amr-roadnet-selection.md
    │   ├── mqtt-tls-emqx.md
    │   ├── open-rmf.md
    │   ├── proprietary-vs-ros2-arbitrary-start.md
    │   ├── rmf-adapter-cookbook.md
    │   ├── rmf-maps-and-traffic.md
    │   ├── rmf-multi-container-deploy.md
    │   ├── roadnet-and-traffic-control.md
    │   ├── robot-wan-5g-satellite.md
    │   ├── ros2-dds-intro.md
    │   ├── slot-reservation-dispatch-strategies.md
    │   └── vda5050.md
    ├── 50-physical-ai/    # Physical AI:模擬與 sim-to-real
    │   ├── README.md
    │   ├── claude-physical-ai-workflow.md
    │   ├── gazebo-slam-warehouse.md
    │   ├── gpu-lidar-how-it-works.md
    │   ├── isaac-sim-isaac-lab-amr.md
    │   ├── physical-ai-overview.md
    │   ├── project-forklift-rmf-gazebo.md
    │   ├── sdf-3d-models.md
    │   ├── sensor-data-and-3d-reconstruction.md
    │   ├── sim-to-real.md
    │   ├── simulation-asset-sources.md
    │   └── simulation-gazebo-ros2.md
    ├── 55-vlm-llm/        # VLM 與 LLM
    │   ├── README.md
    │   ├── llm-vlm-for-robots.md
    │   └── local-llm-on-nvidia-gb10.md
    ├── 60-compliance/     # 法規與認證
    │   ├── README.md
    │   ├── battery-certification.md
    │   ├── pwc-semi-iso3691-certification.md
    │   └── semiconductor-amr-standards.md
    ├── 70-security/       # 資安
    │   ├── README.md
    │   ├── ota-firmware-signing.md
    │   ├── secure-boot.md
    │   └── sros2-dds-security.md
    ├── 90-foundations/    # 數學與力學基礎
    │   ├── feedback-control-pid-lqr.md
    │   ├── gaussian-from-first-principles.md
    │   └── robot-dynamics.md
    ├── _meta/             # 工作方法與教訓
    │   ├── github-actions-gz-sim-playbook.md
    │   └── lessons-learned.md
    ├── _refs/             # 參考論文導讀
    │   └── nav2-survey.md
    └── _legacy/           # 舊版單檔整理(已被取代,保留對照)
        ├── README.md
        ├── delivery-robot-architecture.md
        └── delivery-robot-fundamentals.md
```

> **兩層骨幹**:`10-core/` 是換了形態也還在的部分(硬體 / 韌體 / 導航),`20-forms/` 是換了形態就得換的部分。判準是「把形態換掉,這篇還成不成立?」
>
> 數字前綴是為了讓 GitHub 的字母排序剛好等於閱讀順序(沒有前綴的話 `core/` 會排到 `90-foundations` 後面)。每個 doc 開頭一段「一句話定位 + 延伸閱讀連結」;每一區都有 `README.md` 當入口。

---

## 分輪計畫與進度

| 輪次 | 主題 | 產出 | 狀態 |
|---|---|---|---|
| **R1** | 基礎建設 + 送餐機器人拆分 | PLAN/README/CONTEXT;把既有架構與 28 節基礎原理拆成 hardware/firmware/navigation 主題檔;Physical AI 總覽 | ✅ 完成 |
| **R1.5** | 審查修補 | 章節對照表 `section-map.md`、README 加 30 秒總覽+核心詞、進階小節標示、文字修正;Physical AI 新增「感測器資料與 3D Gaussian 重建」(含高斯為何無所不在) | ✅ 完成 |
| **R3** | 主板控制與模擬 | `board-simulation-renode.md`(STM32/Arduino 在電腦上跑 Renode 模擬)+ 2 張第一性原理 SVG | ✅ 完成 |
| **R4** | 導航數學 | `kinematics-and-coordinate-transforms.md`(座標轉換/TF)、`path-planning.md`(Nav2 規劃)+ 4 張第一性原理 SVG | ✅ 完成 |
| **R5** | Physical AI 模擬 | `isaac-sim-isaac-lab-amr.md`、`simulation-gazebo-ros2.md`、`sim-to-real.md`、`claude-physical-ai-workflow.md`;高斯第一性原理 + 一批數學/流程 SVG 示意圖 | ✅ 完成 |
| **R2** | 多機調度軟體 | `open-rmf.md`、`vda5050.md`(OpenRMF 如何透過 VDA5050 調度不同廠家機器人)+ 4 張第一性原理 SVG | ✅ 完成 |
| **R6** | 圖文並茂 | 把既有 ASCII 圖逐步升級成 SVG;數學概念一律配圖(已起步) | 🔄 進行中 |
| **R7** | 第一性原理補強 | 核心公式(差速/odometry/FOC/AMCL…)從根本推導 + 7 張數學 SVG | ✅ 完成 |
| **R8** | 法規與認證 | 電池認證(UL 2271/2580、LFP)、半導體 fab AMR(SEMI S2/E84) | ✅ 完成 |
| **R11** | 路網規劃與交管 + 全 repo ASCII→SVG | `40-fleet/roadnet-and-traffic-control.md`(三條技術路線第一性原理比較:空間表示、衝突偵測、仲裁脫困;前導線公式推導、柵格化理由、環形鎖 DFS)、`40-fleet/indoor-amr-roadnet-selection.md`(叉車/搬運車/送貨機器人分場景選型)+ 6 張 SVG;既有硬體/導航文件的 ASCII 概念圖批次升級 SVG;README 重編(加全書地圖、補回漏索引的資安三篇);經專家(技術正確性)+ 學生(可讀性)審查並修補(R11.5:AprilTag 斜看方向鏡像、Clarke α 軸對齊 a 軸、前導線圖文編號統一、地標算例自洽化、I²t 疊純 I²t 參考線、補 base_link/Nav2/MAPF/潛伏頂升的首次出現解釋) | ✅ 完成 |
| **R10** | VLM & LLM + 本地 AI 硬體 | `55-vlm-llm/llm-vlm-for-robots.md`(LLM/VLM/VLA 第一性原理)、`local-llm-on-nvidia-gb10.md`(FLOP 量級+記憶體頻寬 bound+量化+GB10/DGX Spark 官方規格查證+本地部署)+ 7 張第一性原理 SVG;經專家(技術正確性)+ 學生(可讀性)審查並修補(FP4→FP16 換算修正、prefill/batching/KV cache 限定、補 self-attention QKV 圖等) | ✅ 完成 |

> 輪次可調整;新需求隨時插入。已寫好的檔不重做,只增修。

---

## 每輪收尾固定流程

1. 更新受影響的 `README.md` 索引與本檔進度表。
2. `git add` → commit(繁中 message)→ push 到 `origin/main`。
3. 啟動兩個 review agent 讀新增/修改的文件:
   - **專家角色**:檢查技術正確性、有無過度簡化或錯誤、領域用詞是否精準。
   - **學生角色**(硬體不熟的讀者):檢查是否讀得懂、哪裡卡住、需要補什麼前置知識或圖。
4. 把兩方意見整理成下一輪的修訂清單。

---

## 審查待辦 backlog(R1 專家/學生審查產出)

來自 R1 收尾的兩個 review agent,尚未處理的高優先項,排進後續輪次:

- ~~**上下位機通訊協議專篇**(`20-firmware/host-mcu-protocol.md`)~~ ✅ 完成:三痛點→framing/CRC16/心跳逾時/序號,第一性原理 + 4 張 SVG(幀格式/接收狀態機/逾時看門狗/編碼範例)。
- **Nav2 規劃/控制層**(`30-navigation/path-planning.md`,R4):costmap、global planner、controller(MPPI/DWB)、behavior tree/recovery。對應 CLAUDE.md「路徑計算/軌跡計算」。
- **座標系與 TF 專篇**(`30-navigation/coordinate-frames-tf.md`,R4):map→odom→base_link→sensor、各 frame 語意、外參標定。對應「座標轉換公式」。
- ~~**Physical AI** 收緊 Cosmos=WFM 措辭、區分 Jetson Thor(robot)/ DRIVE AGX(automotive)~~ ✅(R9 總體檢);Isaac ROS 一列可選補。
- **電池續航/功耗預算**一節(中優先)。
- 較深的跨檔 `§N` 引用,長期改為帶連結的引用(目前先用 `section-map.md` 兜底)。
- **第一性原理回顧(全專案)**:既有硬體/韌體/導航文件逐篇補「為什麼是這個設計/公式」的第一性原理視角(高斯那篇是範本)。專家審查結論:硬體層(FOC/數位電路/電源)已近範本水準;缺口集中在「會動到數學公式」的地方——先給公式再解釋符號,而非把式子逼出來。

  **第一性原理補強 Top 8 — ✅ 全數完成(R7),各配 SVG:**
  1. **ICC 推導差速運動學** + ICC 幾何 SVG — `chassis-and-drivetrain.md §1.1`(目前標「必背」=反第一性原理訊號)
  2. **odometry 積分推導**(車體位移經 θ 旋轉到世界系、中點朝向 Δθ/2 少一階誤差)+ 一步積分 SVG — `low-level-control.md §4.1`
  3. **FOC「τ ∝ sin(夾角)」一條式子** + 夾角/扭矩曲線 SVG — `motors-and-foc.md §2.2`
  4. **AMCL 權重=似然 P(z|x)、z_hit/z_rand/z_short=量測模型分解、為何用粒子不用高斯(多峰)** + 多峰 SVG — `localization.md §22`
  5. **IMU bias 二次積分發散**(t² 爆炸 → 距離信 encoder、角度信 IMU)+ 發散 SVG — `sensors.md §3.3`
  6. **scan matching=最小化點到牆殘差平方和、pose graph=加權最小二乘** + 代價函數 SVG — `slam-mapping.md §21.2/§21.3`
  7. **PID 的 I 項第一性原理**(純 P 對常值負載必留穩態誤差 → 需 I 保住輸出;windup 由此推) — `low-level-control.md §7.3`
  8. **wired-AND 跨章節 SVG 錨點**(供 CAN 仲裁、I²C、共享中斷線共同回指) — `digital-circuits.md §13.4` → `communication-buses.md §6.2`

  > SVG 補強優先給 ASCII 畫不好的數學概念(ICC 幾何、sinθ 曲線、bias 發散、多峰分布、scan 殘差),結構剖面圖維持 ASCII。

| **R13** | 路徑平滑與軌跡生成 | `30-navigation/path-smoothing-and-trajectory.md`:從「折線轉角 κ→∞」推起,涵蓋幾何/時間的拆分、G0–G3 連續性階梯、Bézier 完整推導(Bernstein 基底→凸包性質→de Casteljau 碰撞檢查→曲率式)、B-spline(Cox–de Boor、局部支撐、內建 C²)、NURBS、clothoid、離散平滑器最佳化、速度規劃(梯形 vs S 曲線七段、彎道速度上限),以及 Open-RMF 兩 waypoint 間三次 Hermite 與 Bézier 互轉 + 6 張 SVG;順帶修掉 nav2-survey「IV 路徑平滑」指向沒有該節的檔案這個斷鏈 | ✅ 完成 |

| **R14** | 模擬資產來源盤點 | `50-physical-ai/simulation-asset-sources.md`:先拆清「找 3D 模型」其實指五類東西(機器人本體/場景/物件/材質/訓練環境),再依生態盤點來源並**實查數字**(Fuel 3360 models/270 worlds、forklift 只有 1;AWS RoboMaker 服務 2025-09-10 終止、五個 world repo 全數封存;rmf_demos 七個場景;Isaac 雲端 asset root 可只抓單檔核對 prim 路徑),最後用 visual/collision/inertial/語意標註 四欄說明「拿到資產不等於能用」與 SimReady 的價值 + 1 張來源地圖 SVG;順帶修掉 `sdf-3d-models.md` 引用的 `app.gazebosim.org/fuel` 死連結(實測 404) | ✅ 完成 |

| **R14.1** | 資產來源的網址與 repo 實測 | 補上 §5/§6 原本缺的入口連結,並新增 §9.1 網址狀態表(18 條全數 200)與 §9.2 GitHub repo 表(14 個,含 ★/最後 push/封存/授權)。實測三件會誤導人的事:Isaac 雲端 asset root **4.5/5.0/5.1/6.0 都在**(Nova_Carter_ROS.usd 各 85,526 / 135,278 / 151,435 / 153,649 bytes,可不裝 Isaac Sim 就核對 USD 結構);Asset Browser 文件的 `latest` 與 `6.0.0` 路徑**實測 404**(6.0 搬過位置,改認版本號);`allenai/procthor` 最後 push 停在 2023-04-07、`StanfordVL/OmniGibson` 無授權標示。另記下自己踩到的 jq 陷阱(`--jq '.archived and "已封存" or "活躍"'` 恆為 true,因 jq 的 and/or 回傳布林而非運算元)並寫進 §9.3 | ✅ 完成 |

| **R15** | 補完 R12 中斷的圖 + R11 backlog | R12 那五張沒把關的 SVG 逐一渲染核對:法規編號全部對得上原文(S2/S8/S14/S22、E84/E87/E88/E90/E10、ISO 3691-4/13849/14644、UL 2271/2580、UN 38.3、CISPR/CNS 13438、IEC 62368-1),沒有臆造;修掉 `pai-reality-gap` 與 `pai-gap-techniques` 底部各數十 px 的空白 viewBox 與兩處標籤壓線後插進對應各篇。新畫五張:`cmp-certification-roles`(取代 pwc 篇那張 38 行的 ASCII 流程圖)、`pai-isaac-stack`、`pai-isaac-ros2-nav2`、`meta-ci-verification-ladder`、`roadnet-two-layer`。順帶修掉兩個內容問題:`pwc-semi-iso3691-certification.md` 標題寫「三種認證角色」但表格是四種(已改四種);同檔 §5 出現兩個內部專案代號(已改成中性描述) | ✅ 完成 |

| **R15.1** | 視覺與體例一致性掃全 repo | 派便宜 agent 盤點 63 個 md + 174 張 SVG,主迴圈逐條核實後修:**八張圖底部空白 41–80 px** 裁到一致的 18 px 餘裕;**三張圖右側內容被 viewBox 裁掉**(`max-entropy` 圖例少 63 px、`indoor-amr-decision` 那段字超出自己的框 69 px、`amcl-multimodal` 少 21 px);字體字串統一(`rviz-slam-mapping` 多插了 DejaVu Sans);三張縮到 0.71–0.74 倍的圖放大回 0.9 倍附近;`sensors.md` 三張 1280×1600 截圖與 `localization.md` 的 AprilTag 圖從裸 `![]()` 改成置中 + 尺寸控制;`pwc-semi-iso3691` 整篇全形標點(153 個)轉半形。另把跨檔 `§N` 改成可點連結(51 處 / 10 個檔),同檔內部維持裸寫 | ✅ 完成 |

| **R15.2** | 套用專家 + 學生審查 | 專家沒抓到必須修的技術錯(標準編號與 Isaac/Nav2 事實逐一比對官方來源都對得上),但學生抓到一個更嚴重的:`img/keenon_t10.png` 標成「DINERBOT T10 官網頁面」,**實際是 Keenon 官網首頁、主視覺是 KLEENBOT C40 掃地機**——而且這個假宣稱是 R15 把裸 `![]()` 改成置中寫法時我自己「補完」出來的(原本 alt 誠實寫「Keenon 官網首頁」)。三張截圖在 `height="240"` 下只有 192 px 寬、根本讀不到規格,整段拿掉。另修:`pai-gap-techniques` 的三個等大方框被讀成「三選一」(加 ①②③ 與接力順序帶)、`pai-isaac-stack` 回頭箭頭只有一條卻標「改設計 / 換 reward」(拆兩條)、`cmp-semi-standards-map` 的向下箭頭被讀成檢查順序(補方向提示);精確度:CNS 13438 對應 CISPR 22 而非 32、ISO 13482 是個人照護機器人不是服務機器人、清掉一處可辨識的客戶指涉;補 PL/SIL/SELV/GAN/FID/SSIM/PSNR 的當場翻譯;標明 sim-to-real「五個來源」是本篇二次加工非論文原始分類 | ✅ 完成 |

## 教訓:改寫既有內容時,不要「順手補完」自己沒查證的細節

R15.2 那個假宣稱值得記住。原本的圖說是誠實的「Keenon 官網首頁」,我在做「裸 `![]()` → 置中寫法」這個**純格式**的改動時,覺得 alt 文字寫得太籠統,就順手改成「Keenon DINERBOT T10 官網頁面」——內容我沒開圖看過。格式改動裡夾帶未查證的內容改動,而且因為 commit 訊息寫的是「改排版」,審查時也不會有人特別去看它。

**規則:格式改動就只改格式。** 覺得原本的描述不夠好,那是另一件事,要另外查證再改。

## 量測方法備忘(下次要再掃時直接用)

SVG 的「內容到底畫到哪」不能用抓 `y=`/`x=` 屬性的座標估法——量不到 `<path>` 與**文字實際渲染出來的墨水範圍**,估出來的數字是錯的。正確作法是用 chrome 跑 `getBoundingClientRect()` 再換算回 viewBox 座標(腳本邏輯見 R15.1 的 commit 訊息)。

`getBBox()` 也不行:它回傳**套用 transform 之前**的框,有 `rotate` 的標籤會被誤報成溢出(`pai-isaac-stack`、`meta-ci-verification-ladder` 都被這樣誤標過)。

| **R16** | 擴大範圍到多形態 + 移動操作第一輪 | 使用者指出機器人不限服務型,人形 / 四足 / 搬運車加手臂都算。先重構成「共通核心 + 形態分支」(判準:把形態換掉這篇還成不成立),`10-hardware`/`20-firmware`/`30-navigation` 整批進 `docs/10-core/`,只有 `chassis-and-drivetrain.md` 真的搬去 `docs/20-forms/wheeled-amr/`;177 個圖引用與所有 md 連結逐一改寫並驗過零斷鏈。再寫第一種形態:**移動操作**——`arm-kinematics.md`(FK 求值 vs IK 求根、DH 的 4 個參數是兩個約束消出來的、六軸八組解、球型手腕是機構遷就 Pieper 準則、Jacobian 三重身分含虛功原理推 `τ = JᵀF`)+ `mobile-manipulation.md`(冗餘與零空間投影、三種協調策略、公分級定位對公釐級抓取的誤差預算、合力作用線與傾覆)+ 9 張新 SVG。README 改成多形態定位 | ✅ 完成 |

## 這一輪查證抓到的兩件事

- **安全標準之間有一道空隙,而且移動操作正好掉進去。** ISO 10218:2025(第 3 版)的定義擴大到「fixed to a mobile platform」的手臂,但**明確不處理移動性本身的危害**;ISO 3691-4:2023 歷來**不處理**車上加裝手臂。中間那塊「因為組合才產生的危害」在 ISO 這條線上懸空,已有 ISO/NP 26058-1 在補。**美規 ANSI/RIA R15.08-1 走得比較前面**——Part 1 直接定義 IMR Type C = AMR/AGV + 機械手臂 attachment。
- **MoveIt 2 官方沒有標準的移動底盤支援**,官方 Future Projects 頁自己寫著只有「a non-standard way… requires modifying your robot model」。這反過來佐證了「分階段(停穩再動手臂)」不只是保守——那條路在工具層面本來就沒鋪好。

> ISO/TS 15066 是否已正式撤銷:公開來源說法不一致,**只能確定技術內容已進 ISO 10218:2025 正式條文**。文件裡已標明不要對客戶說「TS 15066 已廢止」。

| **R17** | 形態第二輪:四足 | `20-forms/legged/` 兩篇 + 8 張 SVG。`legged-fundamentals.md` 從一個觀察推起:**翻遍一隻四足找不到任何一顆馬達連到軀幹**——於是軀幹 6 DOF 沒有直接控制輸入(欠致動,永遠差 6 個);接觸集合 16 種讓系統變成混合系統(**沒有一組固定增益能同時對 16 種動力學都好**);支撐多邊形從三角形退化到線段再到不存在,**靜態判準不是難滿足是失去意義**;ZMP 管腳與地的介面、capture point 管能量餘裕;狀態估計的水平位置與 yaw **在數學上不可觀測**。`gait-and-actuation.md`:duty factor 的門檻、腳每步撞地讓工業減速機不能用、QDD 與 SEA 是「衝擊被誰吸收」的兩種答案、RL 為什麼主導、**安全標準目前是空的** | ✅ 完成 |
| **R17.1** | 套用 R17 審查:兩個錯誤斷言 | 學生與專家**各自獨立**抓到同一個錯:「duty factor < 0.5 必有飛行相」被我寫成「幾何上的必然」。實際門檻是 `1/n`(n = 獨立錯開的支撐組數):四腳各自錯開 0.25、對角配對(trot)與雙足才 0.5;四腳平均錯開要 `d ≥ 3/4` 才恆三腳著地。專家補上真實反例 amble(靈長類、大象,duty factor < 0.5 卻無騰空相,Schmitt 2006 JEB 209:2042)。專家另外抓到我沒發現的第二個錯:capture point 被解釋成「動能被抬升重心的位能吃光」,但 Pratt 2006 / Caron 用的是**定高**倒單擺,高度不變、沒有位能可吃——改成完整推導(`ξ = x + ẋ/ω` → `ξ̇ = ω(ξ−p)` → 踩在 ξ 上發散項歸零、指數收斂)。另補:ZMP「合法但仍會跌倒」的機制(瞬時條件,合法的是每一格不是整段軌跡)、`img/nav-roll-pitch-yaw.svg` + 定義表(全庫二十幾個檔在用卻從沒定義過)、諧波減速機一句話說明、反射慣量為何是平方的能量推導、接觸集合 16 是組合上限 | ✅ 完成 |
| **R17.2** | 覆審修正輪(學生 + 專家) | **修正本身也被抓到錯。** 專家指出 duty factor 0.5 對四足**不是**「統計性描述」——Hildebrand 的對稱步態定義就是同一對左右腳差半週期,所以每一對是 n=2、k=1 的系統,`d ≥ 0.5 ⟹ 無騰空相` 是成立的幾何定理。真正的病是**把充分條件當成充要**(反向的 `d < 0.5 ⟹ 有騰空相` 才錯)。上一輪把病因診斷成「把統計說法升級成幾何必然」並已寫進 lessons-learned,等於把錯誤診斷制度化,一併改掉。另修:amble 引用漏掉來源限定詞「**至少一肢** duty factor < 50%」+ diagonality 區間;`nav-roll-pitch-yaw.svg` 的 roll 畫反(正 roll 是左側抬起,後視圖上是螢幕順時針);「不可反向驅動是高反射慣量造成的」錯——反射慣量是純運動學量,自鎖來自摩擦與反向效率 `η_rev ≈ 2 − 1/η_fwd`,改成兩個彼此獨立的性質;反射慣量「兩個 N」改用力矩路徑;諧波減速機補波發生器;ZMP「式子裡沒有速度」限縮到點質量形式;補與 Pratt 原文 orbital energy 的對帳;3/4 門檻補 McGhee & Frank 1968。學生端:撤回的舊斷言還活在四處(兩處在 README 索引);capture point 補上三根缺的接線(方程式來源、ξ 的動機、`p` 就是壓力中心)+ 新圖 `leg-capture-point-modes.svg`;duty factor 兩張表收斂成 `d ≥ k/n` 一條規則 + 兩個但書(「等間隔」不能省、「至少 k 組」不是「恆為 k 組」);GitHub lazy continuation 把整段併進條列項 | ✅ 完成 |

## R17 查證抓到的四件事

1. **足式的安全標準是空白,而且是被明確排除的。** ISO 3691-4 **明訂不適用於具主動控制穩定性的機器人**;ISO 10218 不管移動;ISO 13482 限非工業場域。制定中的 **ISO/CD 25785-1**(動態穩定工業移動機器人)範疇寫著「需主動控制才能維持平衡、斷電即可能失穩」,正是為此而開,但仍在草案(時程只查到「2026–2027」區間)。
2. **teacher-student 特權學習只能歸給 Lee 2020 → Miki 2022 這一支。** Hwangbo 2019 的核心是致動器網路、Rudin 2021 是訓練基礎設施,查不到它們也用同一框架的依據——不要把四篇說成同一套路線。
3. **「zero-moment point」這個詞是 1970–72 才創的**,Vukobratović & Juričić 1969 那篇原始論文並沒有用這個名字。
4. **Kenneally 那篇直驅足式論文是賓州大學的 Minitaur,不是 MIT Cheetah 系列**——我在派工 prompt 裡把它歸錯了,研究 agent 抓出來並更正。

> 另記:「機身高度會漂」這個現象**沒有公認的專有名詞**,文獻都是描述性寫法。研究 agent 明確提醒不要杜撰一個聽起來像術語的稱呼——已照辦。

## R17 這條線上抓到的三件事(每一件都是下一輪才浮出來的)

1. **把充分條件當成充要。** `d ≥ 0.5 ⟹ 無騰空相` 成立(對稱步態每一對是 n=2 系統),反過來不成立(amble)。原文寫成雙向。**判斷法:寫下「⟺」「必然」「才可能」之前,把箭頭兩個方向分開各證一次**——正向證得出來會給人「整條都懂了」的錯覺。
2. **解釋機制比寫對公式更容易錯,也更難被抓到。** capture point 的公式沒寫錯,但配上的物理解釋(動能換位能)跟模型假設(定高)直接矛盾,也跟自己引的兩份來源矛盾。「能量守恆」這類解釋最危險,因為讀起來太順。
3. **修正本身也要被審,而且錯誤的診斷比沒有診斷更糟。** R17.1 把第 1 條的病因診斷成「把統計說法升級成幾何必然」,那是錯的,而它已經被寫進 `lessons-learned.md` 當成規則。派覆審的專家去讀「修正後的版本」而不是只讀原版,是這一次抓到的關鍵。

> 三件事全是審查抓的,沒有一件是自己複查抓的。順序也有訊息:**學生問「憑什麼」先到**(「照 walk 那張圖的排法算,門檻是 0.25」),專家答「對照哪一篇」在後,而第三件要等到**下一輪覆審**才浮出來。角色分開派 + 修正後再審一次,兩件都有效。
>
> 另記一個自己的推導失誤:roll 的旋轉方向我親手推過一次還推錯——逆時針是把 9 點鐘帶到 6 點鐘(壓下去),不是抬起來。**推導過不等於推對了**,幾何方向這種一步就能翻的東西要用代數驗,不要靠腦內轉圖。

| **R18** | 機器人動力學 | `90-foundations/robot-dynamics.md`:整合 [HITSZ-OpenAuto AUTO3005](https://github.com/HITSZ-OpenAuto/AUTO3005)(港科大李澤湘 2012 講義 + MLS 教材)的動力學章。從「速度環為什麼把動力學藏得住」推起:Newton vs Lagrange 兩條路(單擺對照,約束力不做虛功)、廣義座標、慣性張量與剛體動能、M(θ)θ̈+C θ̇+N=τ 三項各自的來源(C = 慣量隨構型變的倒影,Christoffel)、平面二連桿的 m₁₁=α+2βcosθ₂、三條結構性質(M 正定 / Ṁ−2C 反對稱=能量記帳 / 對慣性參數線性)、Newton-Euler O(n) 遞迴(重力=基座向上加速的技巧)、完整 vs 非完整約束(差速側滑約束積不回去→接回 Hybrid-A* 與曲率約束)、computed torque 與 PD+重力補償的 Lyapunov 能量論證、「什麼時候可以不管動力學」的兜底機制表 + 7 張 SVG(全部 chrome 渲染核對過)。體系註記:原課程用旋量/PoE,本篇用廣義座標寫法銜接全書 | ✅ 完成 |

| **R18.1** | 套用 R18 專家 + 學生審查 | 專家抓到五處「詮釋句比數學多說半步」:**「C 不做功」是過強斷言**(θ̇ᵀCθ̇ 一般非零,為零的是它與 ½Ṁθ̇ 的組合→改成「能量帳上淨貢獻為零」,CONTEXT 同步改);**P3 的線性參數化指錯對象**(對 (m, c, ℐ_c) 不線性,線性的是 (m, m·c, 對連桿原點的 ℐ) 這組;補 base parameters 但書);質心「唯一選擇」加「對任意運動」限定(固定點特例也行);「非完整=不限制能到哪」限縮到差速車單約束例(一般要可控性論證);QDD「沒有平方放大」改成「只剩幾十倍」。Coriolis 圖右半 `2m·θ̇ᵢθ̇ⱼ` 量綱不是力→改 `2m·ṙ·θ̇ᵢ`。學生端 18 條:∂L/∂θ̇ 把 θ 與 θ̇ 當獨立引數 + τ 是廣義力放右邊(兩個最大裂縫)、P2 補「Mθ̈ 已用運動方程代換」與反對稱定義、帶約束完整方程 + λ 命名 + Aᵀλ 形狀從虛功原理接回、ω 是 3 維向量、q vs θ 符號交代、構型定義、Coriolis 圖與 2R 的對應註記、陀螺項 ω×ℐω 一句解釋、π 與圓周率消歧、hat 記號、正定⇒可逆白話、極點改白話、科氏/達朗貝爾/克里斯多福/自適應/李亞普諾夫/全身控制/摩擦錐/前饋當場翻譯、§8→§9 接橋;剛體動能圖改成「同一根棒兩種擺法」與正文對齊、單擺結論式字級加大 | ✅ 完成 |

| **R19** | GitHub Pages 上線 | https://wicanr2.github.io/robot-notes/ 。`_config.yml` 用 GH Pages 白名單 plugin(optional-front-matter / readme-index / relative-links / default-layout / titles-from-headings)讓純 markdown repo 直接成站,`docs/_legacy`、`_meta`、`_refs` 底線目錄明確 `include` 否則被 Jekyll 吃掉;`_layouts/default.html` 單檔版面(層級靠細線與留白、關鍵色只有墨綠一個、表格細線無彩色表頭、中文行高 1.95、深色模式同一組語意變數換值)。數學式:kramdown 在 GH Pages 實際輸出裸 `\[...\]`,MathJax 3 的 displayMath delimiter 直接吃(另留 math/tex script 轉換 shim 當備援)。踩到一個:CSS `img{height:auto}` 會蓋掉 HTML 的 `height` 屬性,README 兩張 `height="180"` 產品照被撐成全寬——改成只對帶 `width` 屬性的圖做 `height:auto`。首頁與動力學頁(含 §2–§5 公式段)已實際 chrome 渲染核對 | ✅ 完成 |

| **R20** | 回授控制:PID 與 LQR(叉車 / 搬運車) | `90-foundations/feedback-control-pid-lqr.md`,兩半各半。**Part A 數學**:從「開環要求映射完全已知且不變」推出回授的價值是「不需要準」;PID 三項逐項問「不加它缺什麼」,I 項給到**內模原理**這一層(常值擾動的生成模型是 1/s → 迴路必須有積分器;斜坡需要兩個,所以貨叉等速上升用 PID 會留固定落差)、反算式 anti-windup、微分踢與濾波微分、離散化三個會出事的細節;`xᵀQx + uᵀRu` **用 Taylor 展開逼出來**(前兩項被「目標點為零」與「原點是最小」強制歸零 → 最低階非零項就是二次項),R 為何必須嚴格正定、Q/R 只有比值有意義、Bryson 法則;`u = −Kx` 走**動態規劃 → HJB → 猜 V=xᵀPx → 對 u 求導**完整推出(不是假設的結構,是推導的結果),CARE 與 DARE 兩版都推;可控性(只算到 A^{n-1}B 是 Cayley–Hamilton)、Lyapunov 證閉迴路穩定(`V̇ = −(xᵀQx+uᵀRu)`,下降速率等於當下正在付的代價)、裕度保證與它的四個失效條件。**Part B 叉車**:舵輪 ICR 推 `ω = v·tanδ/L`、非完整約束;四層迴路(路徑追蹤 LQR / 轉向速度 PID / FOC PI / 貨叉位置環)與「什麼時候該從 PID 換成 LQR」的三條判準;標準 LQR **沒有積分器**在坡道會留穩態偏差 → LQI;橫向與航向誤差為何不能拆成兩個 PID(`B = [0, v/L]ᵀ` 的那個零);載重增益排程;LQR 的三個假設叉車違反三個 → MPC(並指出 LQR 是 MPC 的特例、MPC 終端代價的 P 就用 LQR 的 Riccati 解);可執行的 Python 算 K 與 C 的 MCU 實作。11 張 SVG,全部 chrome 量測邊界 + 抽三張渲染核對 | ✅ 完成 |

## R20 這一輪抓到的四件事

1. **推出了一個文獻沒有的結論,而它必須標明是自己推的。** 三輪平衡重式叉車是後輪轉向、前軸驅動,順著無側滑約束算下去,後軸中心對轉向輸入的傳遞函數是 `v(Ls−v)/(Ls²)`——**零點在 `s = v/L`,前進時落在右半平面**,所以車尾會先往錯的方向走,而且閉迴路頻寬被硬性限制在 `v/L` 的量級。倒車時 `v < 0`,零點移到左半平面,限制消失。這同時給了「叉車載重常倒著開」一個控制論上的解釋——但**文獻與原廠訓練資料講的理由是視野與載重分配**,查不到有人把最小相位當成理由。正文已標明這是本篇的推導、不是既有論述。
2. **圖的分類標籤要對得上實體,不是對得上數學模型。** 第一版的舵輪 ICR 圖把「轉向輪在前」那半標成前移式 / 電動拖板車——但 reach truck 的舵輪在**遠離貨叉那端**,貨叉朝前行駛時它是後輪轉向,落在圖的另一半。數學模型沒錯(tricycle 就是 tricycle),錯的是把它掛到哪台車上。改成以「行進方向」為準的標題後才自洽,而且正好把倒車那一節的伏筆埋進圖裡。**渲染核對抓到的,量測抓不到這種。**
3. **研究 agent 對叉車構型的描述自相矛盾,而既有文件是對的。** agent 回報「三輪平衡重式:後方單一舵輪(驅動+轉向同一輪),前方兩個驅動輪不轉向」——後輪既驅動又轉向、前輪也驅動,自己打自己。`project-forklift-rmf-gazebo.md` §3.1 早就查證過(標明來源 Toyota/Raymond/Hyster):**前兩輪驅動、後單輪主動轉向**。採信既有文件,並在本篇連回去,沒有重新裁定。
4. **邊界量測與重疊檢查抓的是不同的病,兩個都要做。** `getBoundingClientRect` 換算回 viewBox 抓到一處真溢出(標籤超出右緣 8 px)與六處邊界過緊 / 留白過寬,但**完全抓不到標籤壓在曲線上**——那三處是渲染成 PNG 後看出來的(I 與 P 兩個標籤疊字、D 的切線與曲線重合到分不出來、P+I 的說明壓在藍色曲線上)。

> 待查證(正文 §15 已列):各機型舵輪的轉向角範圍、ISO 2328 / 2331 各級叉齒尺寸(所以正文只寫「扣掉厚度後剩幾十毫米」不給精確餘裕)、ISO 3691-4 的具體速度與停止距離(標準原文付費未購買)、Balyo / Seegrid / Fox Robotics 的官方定位精度、叉車領域明確以 gain scheduling 命名的公開文獻(查不到,正文標明是把通用理論套上去的推導)、Apollo `lat_controller.cc` 現行原始碼(取用路徑回 404,狀態向量定義來自二手來源)。

| **R20.1** | 套用 R20 專家 + 學生審查 | **專家**抓到一個必修:單輸入 LQR 的增益裕度 `(1/2,∞)` 與相位裕度 60° 應引 **Kalman 1964**(*When Is a Linear Control System Optimal?*, ASME J. Basic Eng. 86(1) 51–60,已實查 DOI 10.1115/1.3653115;該文核心結論「回歸差絕對值在所有頻率上 ≥ 1」正是裕度的來源),原本引的 Safonov & Athans 1977 標題明寫 multiloop,拿它支持單輸入結果是錯位。另補三處限定:§2.2 貨叉斜坡的積分器數量、§12.2 MPC 穩定性還需要終端不變集(只講終端代價是漏一半)、§4.1 二次型論證要 C² 而非只要可微。**學生**抓到全文最大的裂縫:**拉氏轉換從頭到尾沒解釋**,而 §10.2 整段 RHP 零點的推導建立在它上面——學生的原話是那段「讀了等於沒讀」,補了一張三列對照表(微分↔乘 s、積分↔除 s)與轉移函數/零點極點的一句話定位。另補三處無聲跳步:矩陣對向量求導的兩條規則、「純量等於自己的轉置」這個技巧(§5.3 與 §6.2 各用一次卻從沒交代)、§6.2 的 Lyapunov 代入原本五步一次跳到底(現在逐項展開 ①②③)。以及 `Q^{1/2}`、正定、嚴格凸、頻寬、相位裕度、QP、`T_t`、`N` 的當場翻譯,`ω` 角頻率與角速度雙重用法的標註,舵輪圖移到 ICR 被定義之後。新增第 12 張圖 `ctl-forklift-stability-triangle`,並把 §11.1 從一句話擴成傾覆力矩推導:`m·a·h > m·g·d ⟹ a_max = g·d/h`,配 `a = v²/R` 得 `v_max = √(g·d·R/h)`——**質量兩邊約掉,決定翻不翻的是幾何不是載重** | ✅ 完成 |

## R20.1 抓到的三件事

1. **審查 agent 的診斷要自己驗算,它可能只對一半。** 專家對引用的指控成立,但它附帶的推論「Safonov & Athans 1977 已被 Doyle 1978 反駁」是錯的——1977 講的是**狀態回授** regulator 的多迴路裕度,1978 講的是**含 Kalman 濾波器**的 LQG,兩者對象不同、並不衝突。照抄那個推論會在文件裡種下一個新的假斷言。最後只採納「引用錯位」這一半,把 Safonov 保留為多變量推廣並註明它處理的是狀態回授。
2. **它確認對的那一行旁邊,才是真正錯的那一行。** 專家指出 §13.1 的 `Ad = I + A*T` 對這個 `A`(`A² = 0`)是**精確值**不是近似——正確,而且是個好教學點。但**同一段裡 `Bd = B*T` 才是錯的**:精確的零階保持是 `Bd = (T·I + T²A/2)·B`,漏掉 `T²/2·AB` 讓 `K` 的第二個元素偏掉 2.2%(10.395 → 10.168)。專家沒抓到。是自己按著它的提示往下驗算才發現的——**驗證一個斷言時,順手把它的鄰居也算一遍**。
3. **選視角本身就是物理判斷。** 穩定三角形圖的第一版畫成**側視圖**,渲染出來才發現 `d`(重心到傾覆軸的水平距離)幾乎變成 0——因為側視圖表達的是前後傾覆,而 §11.1 講的轉彎傾覆是**側向**的,要用後視圖才畫得出來。公式沒寫錯,錯的是用一個看不到該現象的視角去畫它。這和 R20 那條「圖的分類標籤要對得上實體」是同一類病的兩種形狀。

> 另記一個學生的判準值得留著:它讀完之後被要求用自己的話回答三個問題,「為什麼是二次型」答得完整、「K 從哪來」答得出來源但答不出每一步、「倒車為什麼好控制」只能複述而無法解釋機制。**答不出來的那兩題,精確對應到文中真正缺的兩塊**(矩陣微積分、頻域直覺)。比起請它列出「哪裡看不懂」,請它**複述**更能定位裂縫。

| **R21** | 取樣式 MPC:MPPI 的完整推導與 Nav2 實作 | 起因是「ROS 2 有沒有官方的 LQR / MPC」這個提問。查證結論:**官方零 LQR**(`ros2_controllers` 十幾個 controller、`control_toolbox`、Nav2 的五個 plugin 都沒有),唯一與 MPC 相關的是 `nav2_mppi_controller`,而它是**取樣式**不是解 QP 的。於是在 `feedback-control-pid-lqr.md` 補上 §13(原 §13–16 順推為 §14–17):**Gibbs 變分原理自己推**(最小化 `E_q[S] + λ·KL(q‖p)`,把泛函湊成 `λ·KL(q‖q*) − λ log Z`,靠 KL 非負直接逼出 `q* ∝ e^{−S/λ}p`——指數權重不是設計選擇是推導結果,地位等同 §5 的 `u = −Kx`);重要性取樣讓算不出來的 `Z` 在分子分母對消,得到 softmax 權重;更新律的兩種等價寫法(論文的 `u ← u + Σw_kε_k` 與 Nav2 原始碼的 `u = Σw_k v_k`,因 `Σw_k = 1` 而等價);λ 溫度的兩個極端;**核心那一節**——整條推導裡 `S` 只出現在 `e^{−S/λ}`,從頭到尾沒有求導,所以代價可以是 costmap 查表、碰撞布林、if-else,而 LQR 的閉式解正是用「代價必須是二次型」換來的;Nav2 實際參數(原始碼級核對)與 11 個 critic;PID / LQR / MPPI 三者對「代價需要多少結構」的光譜對照。新增 3 張 SVG(`ctl-quadratic-vs-costmap` 二次碗 vs 真實代價地形、`ctl-mppi-mechanism` 七步流程 + 軌跡束、以及順手修準的局部最小標記) | ✅ 完成 |

## R21 查證抓到的四件事

1. **先 grep 自己的庫,答案就在裡面。** 要回答「Nav2 為什麼不做 LQR」時,第一步不是上網搜,而是 grep `docs/_refs/` ——那裡躺著 Nav2 維護者親寫的 survey **全文 PDF**。`pdftotext` 抽出來一 grep:**全文零次提及 LQR**。這個負面證據兩秒就拿到,而且比任何二手討論權威。它的 Table II(各 controller 的 Max. Frequency:MPPI 125 Hz、Graceful 1800 Hz、RPP >4000 Hz)與五類分法(reactive / predictive / geometric / machine-learning / control-law)也直接給出了「LQR 會落在哪一格、那格已經被誰佔住」的答案。
2. **agent 的引文要回原文核對,因為格式標記會在轉述中丟失。** 研究 agent 正確找到了 navigation2#1710 裡 Macenski 對 LQR 的定性,但回報的純文字裡看不出**那一行帶刪除線**(`~LQR/iLQR/CiLQR …~ MPPI supersedes`)。刪除線正是「評估過、決定不做」與「還沒排到」的分野——用 `gh api` 讀原始 markdown 才看得到。
3. **文件與原始碼不一致時,以原始碼為準,而且要主動去核對。** agent 自己誠實標了「參數預設值只是文件層級,建議另做原始碼級核對」。照做之後:預設值全部吻合(`batch_size` 1000、`time_steps` 56、`model_dt` 0.05、`temperature` 0.3、`gamma` 0.015),但**Savitzky-Golay 濾波器在文件裡不明顯、原始碼確實有呼叫**(`optimizer.cpp` 的 `savitskyGolayFilter`)。這種只有讀碼才看得到的東西,正是筆記該寫進去的。
4. **拿不到原文時,能自己推的就自己推,不要引用沒核對過的式號。** 論文 PDF 抓不到(判定為掃描影像),agent 給的自由能式子是經 HTML 轉譯後的摘要,而且不同文獻的定義差一個 `−λ` 因子。處置是**自己重推一次 Gibbs 變分原理**——只用 KL 散度非負這一個性質,四行就推完,結論自洽且與文獻一致。正文標明這是本篇自推、未逐式核對原文,並註記那個因子差異不影響 `q*` 的形式。

| **R21.1** | 套用 R21 專家 + 學生審查 | **專家**把 §13 的數學逐條重推,**核心推導全數驗算通過**(Gibbs 變分、重要性取樣的 Z 對消、兩種更新律等價、λ 的兩個極限、Ackermann 的 `\|ω\|≤\|v\|/R_min` 與 §7.1 `κ=tanδ/L` 等價);抓到四處要補:§13.2 缺兩個技術前提(`q≪p`、`Z<∞`)、**QP 與 NLP 被揉成一列**(QP 是二次代價+線性約束因此恆凸,「只要可微、允許非凸」講的是 NLP,兩種求解器的假設不同 → 拆成兩列)、§13.7 的「56,000 個位姿就是 125 Hz vs >4000 Hz 的來源」因果過度簡化(RPP 根本不模擬未來,運算性質不同,不能反推單位姿成本)、§13.1 的 `p` **每輪都用上一輪的解重新定義**所以最優性是相對「這一輪的名目控制」、整條演算法是疊代近似而非一次求到全域最優。另補三條限制:有效樣本數塌陷、**加權平均在非凸可行集下可能自己製造不可行解**、維度與時域的覆蓋率詛咒。**學生**判定 §13.2 整段「讀了等於沒讀」,原因是三個斷點:`S/λ = log e^{S/λ}` 那步沒寫、「分母上下同乘 Z」的**措辭誤導**(實際是拿 `Zq* = e^{−S/λ}p` 做代換,不是通分)、以及**KL 散度全文從沒被寫成公式卻被拿去對消算式**。另補 `E_q[·]`、泛函、`K`、logit、歸一化常數的當場翻譯,並修掉 **`Σ` 同時當共變異數與求和**的符號衝突(改記 `Σ_ε`)。圖修兩處:MPPI 流程圖的 ⑥→⑦ 少一個箭頭讓流程看起來在⑥就結束、代價地形圖的「障礙物」只有文字沒有實體 | ✅ 完成 |

## R21.1 抓到的三件事

1. **文字定義不能拿來對消算式。** KL 散度在 §13.2 之前只有一句文字描述(「衡量兩個分布差多少,恆非負」),然後推導裡直接把 `E_q[log(q/q*)]` 記成 `D_KL(q‖q*)`。對已經知道定義的人這是同義反覆,對不知道的人這是憑空跳步——學生的原話是「一個從沒被寫成算式的東西,被拿去對消一個算式」。**規則:凡是會在推導中被當成算式操作的符號,就必須先以算式的形式出現過。**
2. **描述動作的措辭要對得上實際做的動作。** 「分母上下同乘 `Z`」在數學上是錯的描述——實際做的是用 `Zq* = e^{−S/λ}p` 這個已知等式做**代換**。學生說這句話「誤導我去找一個乘法步驟」。這種錯**專家抓不到**(知道答案的人會自動腦補成正確操作),只有真的在跟著推的讀者會卡住。
3. **專家與學生抓到的是不相交的兩組問題。** 這一輪特別明顯:專家的四條全在「斷言精不精確」(QP vs NLP、因果簡化、缺前提、最優性的範圍),學生的四條全在「跟不跟得上」(缺中間步驟、缺公式定義、符號衝突、圖少一個箭頭)。**兩組沒有任何重疊。** 只派一邊,另一邊的問題會完整地留在文件裡。

## 後續形態輪次(待做)

| 輪次 | 主題 | 內容 |
|---|---|---|
| 待排 | 移動操作 II | 抓取與力控(夾爪 vs 吸盤、力/力矩感測、阻抗 vs 導納)、視覺伺服(eye-in-hand 標定、影像式 vs 位置式) |
| 待排 | 人形 | 雙足平衡、全身控制(QP / 階層式 QP)、上肢操作、VLA 模型 |
| 待排 | 協作安全專篇 | ISO 10218:2025 + 四種協作模式 + PFL 的力/壓力限值結構;需購買標準原文才能寫定論 |

## 判斷結論

- **`section-map.md` 不需要配圖**:它是純查表用的對照索引(§N → 檔案),不是概念。圖只會把一張可以 Ctrl-F 的表變難查。真正該做的是把跨檔 `§N` 改成帶連結的引用,讓這張表逐步不必被查。

## 內容原則

- **第一性原理優先(貫穿全專案)**:每篇都要從「這東西要解決什麼根本問題」「為什麼是這個設計/公式」推導,不只堆事實。既有文件後續輪次回頭補「為什麼」視角(見下方 backlog)。
- 繁體中文、中性技術風格;程式碼/識別符保留原文。
- 每個專有名詞首次出現當場一句話翻譯(對照 `CONTEXT.md`)。
- 圖解優先:ASCII 圖先行,概念圖在 R6 由 designer 補。
- 硬體不熟的讀者是主要受眾之一 → 從「它解決什麼問題」講起,再進細節。
- 正確性 > 可讀性 > 美觀;不確定的標「待查證」,不臆造。
