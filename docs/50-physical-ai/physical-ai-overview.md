# Physical AI 總覽

這套筆記的一個目標,是用 Claude 協助完成機器人的 **Physical AI 模擬**。本篇先建立全貌:Physical AI 是什麼、跟一般生成式 AI 差在哪、NVIDIA 的技術堆疊各自扮演什麼角色,以及這一切怎麼接回室內送餐機器人(AMR)的開發。

> 整理自 NVIDIA 官方 glossary 與 Isaac Sim / Cosmos 官方頁(來源見文末)。
> 延伸閱讀:[系統架構](../00-overview/system-architecture.md)、[SLAM 建圖](../30-navigation/slam-mapping.md)、[定位](../30-navigation/localization.md)。後續 `simulation-isaac-gazebo.md`、`sim-to-real.md`、`claude-physical-ai-workflow.md` 會展開模擬與訓練流程。

---

## 1. 一句話定義

**Physical AI** 讓自主系統(攝影機、機器人、自駕車等)能在真實物理世界中感知、理解、推理,並執行或編排複雜動作。**Generative Physical AI** 再進一步:把生成式 AI 延伸到具備「3D 世界的空間關係與物理行為理解」,並用生成模型大量產生訓練資料來開發這類系統。

對比一下:一般生成式 AI 是 input → text/image(吃文字圖片、吐文字圖片);Physical AI 是 **input → action**(吃感測器資料、吐機器人動作)。

## 2. 核心概念

- **比一般生成式 AI 多了「物理世界的理解」**:傳統生成式 AI 訓練在文字/影像上;Physical AI 額外加入空間關係與 3D 世界的物理行為理解。
- **多模態輸入 → 行動輸出**:吃進影像、影片、文字、語音或真實感測器資料,轉成自主機器可執行的洞察或動作。
- **World Foundation Model (WFM,世界基礎模型)**:用來大量生成、擴增、整理、標註 Physical AI 的訓練資料。
- **3D / 物理模擬作為訓練場**:physics-based simulation 提供「安全、可控」的環境訓練機器,避免真實世界中昂貴或危險的資料收集。
- **Digital Twin(數位分身)**:真實空間(如餐廳、工廠)的虛擬複本,用來產生訓練資料。
- **Embodiment(具身)分級**:不同機器人需求不同 —— AMR 用車載感測器回授導航、機械手臂依物件 pose 調抓取、人形機器人要粗/細動作 + 感知 + 推理。
- **Synthetic data + Domain randomization**:在模擬中生成合成資料、隨機化環境與物件(光線、材質、擺位),增加多樣性,提升真實世界的泛化能力。
- **OpenUSD + SimReady 資產**:OpenUSD 是跨產業互通的 3D 場景通用資料標準;SimReady 資產內嵌物理與語意屬性,讓模擬逼真到可直接拿來訓練。

## 3. NVIDIA 技術堆疊

只列官方頁面確實提到的元件:

| 產品 / 平台 | 角色與用途 |
|---|---|
| **DGX Platform** | 訓練算力 —— 提供訓練 foundation model 所需的大量運算 |
| **Omniverse** | 開發工業數位分身與模擬應用的函式庫/微服務集合;Isaac Sim 建構於其上 |
| **Omniverse NuRec** | 神經重建(neural reconstruction),從真實感測器資料重建 3D 場景 |
| **Omniverse Replicator** | 對環境與物件做 domain randomization,產生多樣化合成資料 |
| **Cosmos** | World foundation model 平台;擴增/整理/標註生成資料、擴展情境、模擬符合物理的世界 |
| **Isaac Lab** | 模組化機器人學習框架,用強化學習(RL)或模仿學習(IL)訓練機器人策略 |
| **Isaac Sim** | 開源機器人模擬框架(建於 Omniverse、用 OpenUSD),做模擬、測試、合成資料生成、驗證模型;支援 SIL/HIL 與 ROS/ROS2 橋接 |
| **Jetson Thor / DRIVE AGX** | 邊緣端 runtime 部署電腦,跑在嵌入式自主系統上 |
| **RTX PRO Servers** | 模擬與較大型推理工作負載的基礎設施 |

> 註:OSMO 未出現在所查的官方 glossary / Isaac Sim / Cosmos 頁,**待查證**,此處不臆造其角色。

## 4. 典型工作流(模擬 → 訓練 → sim-to-real)

```
① 建虛擬環境        ② 生成合成資料       ③ 擴增/標註資料
   Omniverse           Replicator           Cosmos (WFM)
   數位分身             domain               擴展情境
   OpenUSD/SimReady     randomization        標註整理
        │                   │                    │
        └───────────────────┴────────────────────┘
                            ▼
④ 訓練策略           ⑤ 模擬中驗證          ⑥ 邊緣部署
   Isaac Lab            Isaac Sim            Jetson Thor /
   RL / IL              SIL / HIL            DRIVE AGX
   (大量試誤)           驗證模型             → 真實世界
                                            (sim-to-real)
```

## 5. 與送餐機器人 / AMR 的關聯

- **AMR 就是官方點名的 embodiment 之一**:glossary 明述 AMR「以車載感測器回授導航」,正是室內送餐機器人的核心場景,可直接套用這套堆疊開發導航與避障策略。
- **室內場景的數位分身 + 合成資料**:餐廳/醫院/辦公樓內部可建成 Omniverse 數位分身,用 Replicator 隨機化動態障礙(人、桌椅、燈光)生成大量合成資料,降低真實場域反覆採集的成本與風險。
- **sim-to-real 部署路徑**:在 Isaac Lab 訓練、Isaac Sim 驗證後,部署到 Jetson 級邊緣運算,對應送餐機器人主機的算力與感測整合需求。

## 6. 關鍵術語表

| 術語 | 一句話翻譯 |
|---|---|
| Physical AI | 讓自主系統在真實物理世界中感知、理解、推理並行動的 AI |
| Generative Physical AI | 結合生成模型與 3D 物理理解,用生成資料規模化開發 Physical AI |
| World Foundation Model (WFM) | 能模擬符合物理的世界、生成合成影片、擴增訓練資料的大型基礎模型(NVIDIA 實作為 Cosmos) |
| Digital Twin(數位分身) | 真實空間/物件的虛擬複本,用來模擬與產生訓練資料 |
| Sim-to-real | 把模擬中訓練/驗證的模型,遷移部署到真實機器上運作 |
| Domain Randomization(領域隨機化) | 隨機化環境與物件外觀/配置,提升真實世界泛化 |
| Synthetic Data(合成資料) | 在模擬中生成的訓練資料,取代昂貴或危險的真實採集 |
| OpenUSD | 跨產業互通的 3D 場景通用資料標準 |
| SimReady Assets | 內嵌物理與語意屬性、可直接用於 AI 訓練模擬的 3D 資產 |
| Reinforcement / Imitation Learning | 透過大量試誤(RL)或示範模仿(IL)訓練機器人策略 |
| VLA Model(Vision-Language-Action) | 將感測輸入即時轉成決策動作的模型 |

## 7. 來源

- [NVIDIA — Generative Physical AI (glossary)](https://www.nvidia.com/en-us/glossary/generative-physical-ai/)(主軸)
- [NVIDIA Isaac Sim](https://developer.nvidia.com/isaac/sim)
- [NVIDIA Cosmos](https://www.nvidia.com/en-us/ai/cosmos/)
