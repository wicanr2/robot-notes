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
├── img/                      # 圖片與概念圖
└── docs/
    ├── 00-overview/          # 系統全貌
    │   └── system-architecture.md
    ├── 10-hardware/          # 硬體:機構、馬達、感測、電源、電路、通訊
    │   ├── chassis-and-drivetrain.md
    │   ├── motors-and-foc.md
    │   ├── encoders.md
    │   ├── sensors.md
    │   ├── communication-buses.md
    │   ├── digital-circuits.md
    │   └── power-and-safety.md
    ├── 20-firmware/          # 下位機韌體與模擬
    │   ├── low-level-control.md
    │   └── stm32-simulation-renode.md     (待寫)
    ├── 30-navigation/        # 導航:運動學、SLAM、定位、路徑
    │   ├── slam-mapping.md
    │   ├── localization.md
    │   ├── kinematics-and-coordinate-transforms.md   (待寫)
    │   └── path-planning.md                          (待寫)
    ├── 40-fleet/             # 多機調度
    │   ├── open-rmf.md                     (待寫)
    │   └── vda5050.md                       (待寫)
    └── 50-physical-ai/       # Physical AI 模擬與學習
        ├── physical-ai-overview.md
        ├── simulation-isaac-gazebo.md       (待寫)
        ├── sim-to-real.md                    (待寫)
        └── claude-physical-ai-workflow.md    (待寫)
```

> 命名用數字前綴(00/10/…)維持閱讀順序;每個 doc 開頭一段「一句話定位 + 延伸閱讀連結」。

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

## 判斷結論

- **`section-map.md` 不需要配圖**:它是純查表用的對照索引(§N → 檔案),不是概念。圖只會把一張可以 Ctrl-F 的表變難查。真正該做的是把跨檔 `§N` 改成帶連結的引用,讓這張表逐步不必被查。

## 內容原則

- **第一性原理優先(貫穿全專案)**:每篇都要從「這東西要解決什麼根本問題」「為什麼是這個設計/公式」推導,不只堆事實。既有文件後續輪次回頭補「為什麼」視角(見下方 backlog)。
- 繁體中文、中性技術風格;程式碼/識別符保留原文。
- 每個專有名詞首次出現當場一句話翻譯(對照 `CONTEXT.md`)。
- 圖解優先:ASCII 圖先行,概念圖在 R6 由 designer 補。
- 硬體不熟的讀者是主要受眾之一 → 從「它解決什麼問題」講起,再進細節。
- 正確性 > 可讀性 > 美觀;不確定的標「待查證」,不臆造。
