# Physical AI:先在模擬裡把事情做完

真機做實驗很貴——撞壞要修、跑一次要人顧、環境變因控制不住。這一區處理的是「**把大部分工作搬進模擬,再把成果搬回真機**」這條路上會遇到的每一件事。

## 先講清楚:這一區走哪條線

模擬環境有兩大生態,這一區的**實作全部走 Gazebo**:

| | Gazebo(gz sim) | Isaac Sim / Isaac Lab |
|---|---|---|
| **定位** | 開源、輕量、與 ROS 2 整合最深 | NVIDIA 生態、GPU 加速、大規模平行訓練 |
| **本區內容** | 建模、資產、感測器、SLAM、叉車專案——**都能跟著做** | 只有[一篇概念對照](isaac-sim-isaac-lab-amr.md),**沒有實作走查** |

[總覽](physical-ai-overview.md) 裡那張 NVIDIA 官方堆疊圖(Omniverse → Replicator → Cosmos → Isaac Lab → Jetson Thor)是產業界的完整樣貌,不是這份筆記帶你走的路。**看到那張圖不必期待後面會一一實作。**

## 建議閱讀順序

| # | 篇 | 為什麼在這個位置 |
|---|---|---|
| 1 | [Physical AI 總覽](physical-ai-overview.md) | 這一區在解什麼問題、業界的工具版圖 |
| 2 | [Gazebo 與 ROS 2](simulation-gazebo-ros2.md) | 主線工具。**§7 第一次讀可以跳過**(那是搬移舊世界的實錄) |
| 3 | [SDF 與 3D 模型](sdf-3d-models.md) | 機器人在模擬裡「長什麼樣、怎麼動」:visual / collision / inertial 三層 |
| 4 | [模擬資產從哪來](simulation-asset-sources.md) | 查表用。**§9 是網址與 repo 的複驗紀錄,可以不讀** |
| 5 | [GPU 光達怎麼算](gpu-lidar-how-it-works.md) | 感測器在模擬裡是怎麼被「算」出來的。**§5(ray tracing 背景)標了可跳過,真的可以跳** |
| 6 | [Isaac Sim / Isaac Lab](isaac-sim-isaac-lab-amr.md) | 另一條生態的概念對照。涉及強化學習的詞彙,建議先看第 7 篇的名詞表 |
| 7 | [sim-to-real](sim-to-real.md) | **這一區的核心。** 模擬與真實差在哪五個地方、三種手段怎麼接力 |
| 8 | [Gazebo + SLAM 倉庫實例](gazebo-slam-warehouse.md) | 把前面幾篇串起來跑一次 |
| 9 | [叉車專案:RMF + Gazebo](project-forklift-rmf-gazebo.md) | 最完整的一篇。**它是專案計畫不是完成報告**,§14 是給 agent 抄的骨架,可以不讀 |
| 10 | [感測器資料與 3D 重建](sensor-data-and-3d-reconstruction.md) | 3DGS 那條線。第 7 篇會用到,想先看也可以 |
| 11 | [用 Claude 做 Physical AI](claude-physical-ai-workflow.md) | 方法論收尾:哪些環節適合交給 AI、哪些不適合 |

## 相關

- 導航演算法本身:[共通核心 / 導航](../10-core/30-navigation/)
- 模擬裡驗證多車調度:[多機調度](../40-fleet/)
- 跑模型的硬體:[VLM & LLM](../55-vlm-llm/)
