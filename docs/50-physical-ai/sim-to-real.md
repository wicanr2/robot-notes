# Sim-to-Real:把模擬訓練的策略搬上實車

在模擬裡訓練的導航策略,搬到真實機器人上常常「在模擬好好的、上車就壞」。這篇整理為什麼會這樣(reality gap,現實落差)、有哪些技術可以把落差縮小,以及對室內送餐機器人(AMR)來說,務實的上車步驟、常見地雷與驗收方式。

> 整理自 2025 年回顧論文《The Reality Gap in Robotics》、NVIDIA Isaac Lab/Sim 官方文件,與多篇 sim-to-real 研究(來源見文末)。
> 延伸閱讀:[Physical AI 總覽](physical-ai-overview.md)、[SLAM 建圖](../30-navigation/slam-mapping.md)、[定位](../30-navigation/localization.md)。

---

## 30 秒總覽

**Sim-to-real** = 在電腦模擬裡訓練一個會開車的「腦」(策略 / policy),再把這個腦原封不動或微調後,放到真實機器人上跑。

為什麼要這樣做:真實世界收資料**慢、貴、又危險**(撞到人、撞壞車)。模擬裡可以一秒跑幾千次、隨便撞、24 小時不停練。

問題出在哪:模擬永遠是真實的「近似」。模擬裡的摩擦力、馬達反應、感測器都太乾淨、太理想;真實世界有雜訊、延遲、滑動、磨損。這個差距就叫 **reality gap(現實落差)**。策略在乾淨的模擬裡學到的習慣,一碰到髒髒的真實世界就可能失靈。

整篇要回答的就是:這個落差從哪來、怎麼縮小、怎麼安全上車、怎麼知道成功了。

| 詞 | 一句話 |
|---|---|
| **policy(策略)** | 機器人的「腦」:吃感測器輸入、吐動作指令(如轉速、(v, ω))的函式,常用神經網路 |
| **reality gap(現實落差)** | 模擬與真實世界的差異總和;落差越大,模擬學到的策略越容易在實車失靈 |
| **domain randomization(領域隨機化)** | 訓練時把模擬參數隨機抖動,逼策略學到「對變化不敏感」的穩健行為 |
| **zero-shot transfer(零樣本遷移)** | 模擬訓練完直接上車、不用真實資料微調 |

---

## 1. Reality gap 從哪來

模擬之所以對不上真實,是因為它由「抽象與近似」組成,這些近似不可避免地引入差異(《The Reality Gap in Robotics》)。NVIDIA Isaac Lab 文件把根源歸成三類:**近似誤差**(物理/渲染只是自然律的近似,離散化會造成穿模等不真實行為)、**模型誤差**(連桿長度、質量、摩擦係數「在模擬裡永遠不可能 100% 準確」,加上製造公差與設備老化)、**未建模動態**(彈性致動器、彈簧等常被簡化)。

回顧論文把落差來源拆成四大類,對 AMR 來說最該在意的是前兩類:

- **動力學落差(Dynamics gap)**:摩擦、質量、慣量的參數誤差;接觸模型被簡化成點接觸、線性化摩擦錐;以及磨損、電池電壓隨負載下降等未建模效應。對送餐車而言,**輪子打滑、地板摩擦、載重變化**都落在這裡。
- **感知落差(Perception gap)**:真實感測器的雜訊「複雜、非高斯、隨狀態變化、且時間上相關」,但模擬常只用簡單高斯雜訊近似;相機缺鏡頭炫光、色差、捲簾快門(rolling shutter)等真實光學特性;LiDAR 有它特定的光束模式。模擬資產的低解析度貼圖、過度簡化的場景也讓**外觀(appearance)**對不上真實。
- **致動落差(Actuation gap)**:真實馬達是「高階系統」,有相位延遲、死區(dead-zone)、齒隙(backlash)、轉速變化率限制;PWM 解析度有限會把指令量化出死區。
- **系統設計落差(System design gap)**:通訊延遲與封包遺失、模擬裡沒有的安全機制、控制頻率不一致。對 AMR 來說,**上位機→下位機的指令延遲**就屬於這類。

把上面收斂成「軟體背景該記住的五個來源」:**物理參數**(質量/慣量/摩擦)、**感測噪聲**(非高斯、有時間相關)、**延遲**(感測、通訊、致動)、**摩擦/打滑**(接觸動態)、**外觀**(貼圖、光照、感測器光學特性)。

---

## 2. 縮小 gap 的主要技術

回顧論文把策略分兩大方向:**先把模擬做準一點(reduce the gap)**,再**訓練出對殘餘落差免疫的策略(overcome the gap)**。下面逐項說明。

### 2.1 Domain Randomization(領域隨機化)— 把模擬「弄亂」逼出穩健性

訓練時,不要只在「一個」固定模擬環境練,而是用「**一大堆**隨機變化的模擬環境」練——隨機抖動光照、材質、貼圖、背景、物件擺位(視覺類);以及質量、摩擦、感測雜訊、延遲(物理類)。OpenAI 對 DR 的經典說法是:只要模擬裡的變化夠多,**真實世界對策略來說就只是「又一種變化」而已**,因此能泛化過去。NVIDIA 在 Isaac Sim 用 Replicator 工具做 DR,隨機化物件 pose、scale、貼圖、光照來生成合成資料。DR 是目前最常用、最通用的手段,優點是不需要真實資料就能拉高穩健度;缺點是隨機範圍太寬會讓策略變保守、學不好(過度泛化),範圍太窄又蓋不到真實。

### 2.2 System Identification / 參數校準 — 量真實參數回填模擬

System identification(系統辨識)= 在真實機器上「量」出物理參數(質量、慣量、摩擦係數、馬達時間常數、延遲),再回填進模擬,讓模擬一開始就更接近真實。回顧論文指出,系統辨識「在導航、移動、操作各領域中,**一再被證明是 sim-to-real 成功的關鍵環節**」。延伸做法是 **learned residual model(學習殘差模型)**:訓練一個模型去「修正」不完美模擬器的輸出,補上沒建模的柔順性與摩擦。對 AMR 很實際的一步:把車**實測**的最大加速度、轉向延遲、實際輪距(可能因胎壓/磨損偏離標稱值)回填到模擬。DR 和 system ID 常搭配——先用 system ID 把模擬中心對準真實,再用 DR 在這個中心周圍撒範圍。

### 2.3 Domain Adaptation(領域適應)— 對齊兩邊的特徵分佈

跟 DR「把模擬撒得夠寬」不同,domain adaptation 是**主動把模擬與真實的特徵分佈對齊**,通常聚焦在「觀測 / 感知」這一側。常見做法是用影像轉譯把模擬影像變得像真實影像:CycleGAN 做不成對(unpaired)的影像翻譯;RL-CycleGAN、RetinaGAN 進一步在翻譯時保住任務相關物件(RetinaGAN 用物件偵測器約束翻譯前後預測一致,真實抓取成功率比先前方法高 12%,且在僅 5–10% 真實資料下仍有效)。純像素級 GAN 的風險是會任意改掉或刪掉任務需要的細節,因此也有「特徵級對齊」的做法:把模擬與翻譯後影像各自編碼,只對齊抽象、任務相關、domain-invariant 的特徵。Domain adaptation 通常需要一些真實資料,適合視覺導航(吃 RGB)的場景。

### 2.4 加真實感測噪聲 / 延遲模型 — 把「髒」也模擬進去

策略若只在乾淨資料上訓練,容易過度擬合,一遇到真實的感測雜訊或致動延遲就出現不穩路徑、甚至導航崩潰。所以一個直接而有效的做法:**在模擬裡主動注入真實感測器的雜訊與系統延遲**。關鍵在於雜訊模型要貼近真實——真實雜訊往往非高斯、隨狀態變化、且時間上相關,只加「簡單高斯雜訊」可能還是會在實車失靈。對 AMR 具體要注入:LiDAR 測距雜訊與掉點、odometry 的打滑誤差、IMU 漂移、相機曝光/動態模糊,以及**感測到動作之間的端到端延遲**。有研究團隊把這條路徑總結為「Noise is all you need」——足夠真實的雜訊本身就能跨過移動類的 sim-to-real 落差(待查證其適用範圍,此處只引述其主張)。

### 2.5 高擬真感測模擬 — 用 3D 重建把真實場景搬進模擬

與其讓模擬外觀「將就」,不如**把真實場景重建成高擬真的模擬**(real-to-sim),再在裡面訓練。近年主流是 **3D Gaussian Splatting(3DGS,高斯潑濺)**:用一堆帶顏色的 3D 高斯點重建真實場景,能在高畫格率下做出照片級渲染與新視角合成,渲染出來的影像與真實的外觀落差很小。代表性工作:**VR-Robo** 用平面化 3DGS 建出照片級、可物理互動的環境做 real-to-sim-to-real;**GaussGym** 把 3DGS 當渲染器塞進向量化物理模擬器,在消費級 GPU 上達到每秒超過 10 萬步;**NavGSim / ReaDy-Go** 則把 3DGS 用到大尺度導航與含移動障礙的視覺導航。這條路特別適合**吃相機的視覺導航**——外觀落差是它最大的痛點,3DGS 直接把外觀對準真實。NVIDIA 對應的元件是 Omniverse NuRec(神經重建,從真實感測資料重建 3D 場景)。

### 2.6 其他輔助手段

- **觀測模態選擇**:論文指出「用深度(depth)或點雲(point cloud)當觀測,落差比用 RGB 影像小」——因為深度/點雲對光照、貼圖不敏感。對成本敏感的 AMR,**用 2D LiDAR / depth 而非純 RGB 做導航,天生 sim-to-real 較友善**。
- **特權資訊 + 蒸餾(privileged + distillation)**:訓練時讓「老師策略」吃完整真實狀態(模擬裡才拿得到),再蒸餾成只吃感測器觀測的「學生策略」上車。
- **策略正則化(policy regularization)**:懲罰動作幅度、前後動作差、耗能,讓策略動作更平滑、對落差更穩健。
- **少量真實資料共訓(co-training)**:把有限的真實經驗和大量模擬經驗混在一起訓練。

---

## 3. 移動機器人 sim-to-real 的務實順序

對 AMR,業界主流不是「端到端 RL 取代一切」,而是**先在模擬把現成導航棧(如 ROS 2 的 Nav2)與參數調好,再小心上實車**。一個可落地的順序:

1. **先在模擬把 Nav2 / 策略調到能跑**:用 Gazebo 或 Isaac Sim 建出餐廳/倉儲場景,接上 Nav2(ROS 2 的導航棧:負責路徑規劃、避障、移動),把全域/區域規劃器、代價地圖(costmap)、控制器參數調到模擬裡穩定。模擬階段同時驗證多機協調與隊列管理。
2. **做 system identification,把模擬對準這台車**:實測本車的輪距、最大加減速、轉向延遲、感測器更新率,回填模擬,別只用標稱值。
3. **注入雜訊與延遲、開啟 domain randomization**:在對準後的模擬中心周圍,隨機化摩擦、載重、感測雜訊、延遲;視覺導航再加外觀隨機化或 3DGS 重建。
4. **盡量讓模擬與實車跑「同一套軟體棧」**:論文明列「複製模擬與真實之間的軟體棧」為降低落差的設計選擇——同一份 Nav2 設定、同樣的座標轉換、同樣的控制頻率,能少掉一整類落差。
5. **先 zero-shot 上車量基線,再決定要不要微調**:直接把模擬策略放上實車,在**受控、有人盯、低速、可急停**的環境量第一版成功率;表現不足再用真實資料做 domain adaptation 或共訓。
6. **量測 → 找失敗模式 → 針對性回頭加隨機化**,反覆迭代。一個被反覆強調的實務心法:**在真實硬體上跑、找出失敗模式,然後把隨機化精準對準「最可能造成這些失敗的模擬參數」**,而不是盲目把所有東西都隨機化。

> 安全是硬規則:首次上車一律低速、保留實體急停、有人在場、選空曠或封閉測試區,先確認不會傷人傷物再逐步放開。

---

## 4. 常見失敗模式與檢查清單

「模擬裡好、上車就壞」的典型原因:

- **只用簡單高斯雜訊訓練**:真實雜訊非高斯、隨狀態變化、時間相關,策略一遇真實感測器分佈就失靈。
- **忽略延遲**:模擬裡感測→動作是瞬時的,真實有端到端延遲且會抖動;沒建模延遲的策略容易振盪、過衝。
- **物理參數用標稱值沒校準**:標稱輪距/質量/加速度與實車有差,odometry 與運動學一起偏。
- **接觸/打滑沒模擬**:地板摩擦、輪子打滑、載重變化讓實車軌跡偏離模擬。
- **外觀落差(視覺導航)**:模擬貼圖、光照與真實差太多,感知模型直接認不得真實畫面。
- **隨機化範圍設錯**:太窄蓋不到真實、太寬讓策略過度保守學不好。
- **模擬與實車軟體棧不一致**:不同的座標轉換、控制頻率、濾波器,引入額外落差。
- **獎勵用了特權資訊**:訓練時用了實車拿不到的完整狀態,策略依賴它、上車就缺資訊。

**上車前檢查清單:**

- [ ] 是否做過 system identification,把實測物理參數回填模擬?
- [ ] 感測雜訊模型是否貼近真實(非僅高斯)、是否含掉點/漂移?
- [ ] 是否建模了感測→動作的端到端延遲(含抖動)?
- [ ] 摩擦、載重、打滑是否納入隨機化?
- [ ] 視覺導航:外觀是否用隨機化或 3DGS 對準真實?
- [ ] 模擬與實車是否跑同一套導航軟體棧與座標轉換?
- [ ] 觀測模態是否盡量用對落差友善的 depth/LiDAR?
- [ ] 首次上車的安全配置(低速、急停、有人、封閉區)是否就緒?
- [ ] 是否先用 open-loop replay 比對過模擬與真實軌跡的差?

---

## 5. 評估:怎麼量「遷移成不成功」

要分兩件事量:**落差有多大**、以及**策略遷移成不成功**。

**量落差大小(模擬有多準):**

- **Sim-to-Real Correlation Coefficient (SRCC,模擬-真實相關係數)**:模擬與真實兩邊效能指標的 Pearson 相關係數,越接近 +1 代表「模擬能準確預測真實表現」。這是判斷「能不能在模擬裡放心調參」的關鍵指標。
- **Offline replay error(離線重放誤差)**:把真實世界錄下的動作序列,在模擬裡 open-loop 重放,比對狀態軌跡的差距。這是上車前最便宜的對帳方式。
- **視覺擬真度**:用 FID、SSIM、PSNR 等量模擬影像與真實影像的差(視覺導航/3DGS 場景特別需要)。

**量遷移成不成功(策略表現):**

- **Success rate(成功率)**:成功完成任務的試驗佔比——對 AMR 就是「成功送達指定桌號 / 不撞不卡的比例」。最直接、最該優先報的指標。
- **Cumulative reward(累積獎勵)**:加總獎勵,反映 rollout 的進度與效率。
- **任務專屬指標**:導航類常用路徑效率(實際路徑/最短路徑)、到達時間(time-to-goal);AMR 還可加避障介入次數、人工接管次數。

**A/B 對比模擬 vs 真實**:核心方法是「同一套策略、同一批任務,分別在模擬與真實各跑一輪,比成功率與上述指標」。理想情況兩邊接近(SRCC 高);若模擬遠高於真實,差距就指向 reality gap 的某個來源,回頭對照第 4 節的失敗模式定位。論文也提醒:**重點不是把 reality gap 歸零,而是讓「效能落差」夠小**——策略只要對差異夠穩健,即使模擬與真實在參數上仍有差,遷移仍可成功。

---

## 來源

- 《The Reality Gap in Robotics: Challenges, Solutions, and Best Practices》(2025 回顧論文,Annual Reviews / arXiv 2510.20808):落差四大來源、技術分類、SRCC/replay error/success rate 等評估、best-practice recipe。<https://arxiv.org/html/2510.20808v1> / <https://arxiv.org/abs/2510.20808>
- 《Sim-to-Real Transfer in Deep Reinforcement Learning for Robotics: a Survey》(arXiv 2009.13303):DR、system ID、domain adaptation 等手段綜述。<https://arxiv.org/abs/2009.13303>
- NVIDIA Isaac Lab — What Is the Reality Gap?(近似誤差/模型誤差/未建模動態三分法、DR/real-to-sim/behavior regularization)。<https://docs.nvidia.com/learning/physical-ai/getting-started-with-isaac-lab/latest/transferring-robot-learning-policies-from-simulation-to-reality/02-the-reality-gap/index.html>
- NVIDIA Isaac Sim — Domain Randomization With Replicator(Replicator 隨機化 pose/scale/貼圖/光照)。<https://docs.nvidia.com/learning/physical-ai/getting-started-with-isaac-sim/latest/synthetic-data-generation-for-perception-model-training-in-isaac-sim/03-domain-randomization-with-replicator.html>
- NVIDIA Technical Blog — Training in NVIDIA Isaac Sim Closes the Sim2Real Gap。<https://developer.nvidia.com/blog/training-in-nvidia-isaac-sim-closes-the-sim2real-gap/>
- RL-CycleGAN(arXiv 2006.09001)與 RetinaGAN(retinagan.github.io):GAN 影像翻譯式 domain adaptation。<https://arxiv.org/pdf/2006.09001> / <https://retinagan.github.io/>
- Google Research — Toward Generalized Sim-to-Real Transfer for Robot Learning(RetinaGAN 物件一致性、少量真實資料)。<https://research.google/blog/toward-generalized-sim-to-real-transfer-for-robot-learning/>
- 3D Gaussian Splatting 用於 sim-to-real:VR-Robo(arXiv 2502.01536)、GaussGym(arXiv 2510.15352);NavGSim、ReaDy-Go 為大尺度/動態障礙視覺導航延伸。<https://arxiv.org/pdf/2502.01536> / <https://arxiv.org/html/2510.15352>
- Asimov / Noise is all you need to bridge the Sim-to-Real locomotion gap(雜訊注入主張,適用範圍待查證)。<https://news.asimov.inc/p/noise-is-all-you-need>
- Nav2 + Gazebo AMR 模擬/隊列測試實務參考(warehouse fleet、CycloneDDS 穩定性建議)。<https://www.atomicloops.com/technologies/industrial-automation-and-robotics/test-warehouse-robot-fleets-with-ros-2-nav2-and-gazebo-simulation-atomic-loops>
- MDPI Sensors — Deep RL of Mobile Robot Navigation in Dynamic Environment: A Review(導航類過度擬合/失敗模式)。<https://www.mdpi.com/1424-8220/25/11/3394>
