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
| **R2** | 多機調度軟體 | `open-rmf.md`、`vda5050.md`(OpenRMF 如何透過 VDA5050 調度不同廠家機器人) | ⬜ |
| **R3** | 主板控制與模擬 | `board-simulation-renode.md`(STM32/Arduino 在電腦上跑 Renode 模擬)+ 2 張第一性原理 SVG | ✅ 完成 |
| **R4** | 導航數學 | `kinematics-and-coordinate-transforms.md`(座標轉換/TF)、`path-planning.md`(Nav2 規劃)+ 4 張第一性原理 SVG | ✅ 完成 |
| **R5** | Physical AI 模擬 | `isaac-sim-isaac-lab-amr.md`、`simulation-gazebo-ros2.md`、`sim-to-real.md`、`claude-physical-ai-workflow.md`;高斯第一性原理 + 一批數學/流程 SVG 示意圖 | ✅ 完成 |
| **R2** | 多機調度軟體 | `open-rmf.md`、`vda5050.md`(OpenRMF 如何透過 VDA5050 調度不同廠家機器人)+ 4 張第一性原理 SVG | ✅ 完成 |
| **R6** | 圖文並茂 | 把既有 ASCII 圖逐步升級成 SVG;數學概念一律配圖(已起步) | 🔄 進行中 |
| **R7** | 第一性原理補強 | 核心公式(差速/odometry/FOC/AMCL…)從根本推導 + 7 張數學 SVG | ✅ 完成 |
| **R8** | 法規與認證 | 電池認證(UL 2271/2580、LFP)、半導體 fab AMR(SEMI S2/E84) | 🔄 進行中 |

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
- **Physical AI 補 Isaac ROS** 一列、收緊 Cosmos=WFM 措辭、區分 Jetson Thor(robot)/ DRIVE AGX(automotive)。
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

## 內容原則

- **第一性原理優先(貫穿全專案)**:每篇都要從「這東西要解決什麼根本問題」「為什麼是這個設計/公式」推導,不只堆事實。既有文件後續輪次回頭補「為什麼」視角(見下方 backlog)。
- 繁體中文、中性技術風格;程式碼/識別符保留原文。
- 每個專有名詞首次出現當場一句話翻譯(對照 `CONTEXT.md`)。
- 圖解優先:ASCII 圖先行,概念圖在 R6 由 designer 補。
- 硬體不熟的讀者是主要受眾之一 → 從「它解決什麼問題」講起,再進細節。
- 正確性 > 可讀性 > 美觀;不確定的標「待查證」,不臆造。
