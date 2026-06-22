# 半導體晶圓廠 AMR 的 SEMI 標準與合規地圖

把一台自主移動機器人(AMR)放進一般倉庫,跟放進台積電的晶圓廠(fab),合規門檻不在同一個量級。倉庫只要過得了通用工業安全標準;晶圓廠多了一整套半導體業專屬的 **SEMI 標準**,還疊上潔淨室、靜電、逸氣這些「肉眼看不到、但會毀掉整批晶圓」的要求。

本篇是給「要在晶圓廠導入 AMR/AGV 的工程團隊」看的合規地圖:**哪些 SEMI 標準會被客戶要求、哪些通用國際安全標準仍然適用、兩者是互補還是重疊、最後要過哪幾關**。

> 名詞會在首次出現時當場用一句話解釋(括號或破折號)。
> **標準編號容易記錯**,本篇逐一查證;仍有把握不足之處明確標「待查證」,不臆造標準內容。版本與強制範圍會更新,**實際導入以客戶(fab)規範、SEMI 官方文件、檢測機構當下要求為準**。
> 延伸閱讀:[電池認證法規](battery-certification.md)、[電源與安全](../10-hardware/power-and-safety.md)、[VDA5050 與多機調度](../40-fleet/vda5050.md)(待 R2)。

---

## 0. 先把名詞釘住(一句話版)

晶圓廠搬運的不是箱子,是晶圓。先記住幾個會反覆出現的詞:

| 詞 | 一句話 |
|---|---|
| **fab** | Fabrication facility,晶圓製造廠(就是「晶圓廠」)。 |
| **晶圓(wafer)** | 一片圓形的矽基板,晶片就刻在上面;300mm fab 一片直徑 30 公分。 |
| **FOUP** | Front Opening Unified Pod,**晶圓盒**——密封塑膠盒,裝最多 25 片 300mm 晶圓,前開門讓機器手臂取放,內部維持低污染環境。 |
| **OHT** | Overhead Hoist Transport,**天車**——掛在天花板軌道上、把 FOUP 在機台之間吊運的搬運車。fab 主力搬運就是它。 |
| **load port** | 機台的**裝載口**——FOUP 跟製程機台交接的接口,搬運系統把 FOUP 放上去/取下來。 |
| **AMHS** | Automated Material Handling System,**自動物料搬運系統**——fab 裡所有自動搬運的總稱(OHT、AGV、AMR、軌道車…)。 |
| **AMR** | Autonomous Mobile Robot,自主移動機器人;在 fab 裡常做地面(非天車)的 FOUP/物料搬運。 |
| **SEMI** | Semiconductor Equipment and Materials International,半導體設備暨材料國際協會——制定下面這整套標準的組織。 |

一句話定位三者的關係:**OHT 在天上跑、AMR 在地上跑、兩者都是 AMHS 的一員,搬的都是 FOUP,交接點都是 load port。**

---

## 1. SEMI 是什麼

**SEMI(Semiconductor Equipment and Materials International)** 是半導體與相關產業(平面顯示器、太陽能、MEMS)的全球產業協會,1970 年成立。對導入 AMR 的團隊來說,SEMI 最重要的身分是**標準制定組織**:它底下的 International Standards Program 制定了一大套字母編號的標準,涵蓋設備安全、自動化通訊、物料搬運、潔淨度等。

兩條跟 AMR 直接相關的標準線:

- **S 系列(Safety / EHS)**:設備的環境、健康、安全準則。核心是 **SEMI S2**,其他 S 標準都是支撐它的。
- **E 系列(Equipment Automation / AMHS)**:設備自動化與物料搬運的通訊與介面標準,如 E84、E87、E90。

關鍵認知:**很多 SEMI 標準的正式定位是「Guideline(準則)」而非強制法規,但驅動力來自客戶(end user)而非政府**。台積電、Intel 這類大廠會在採購前要求設備/車輛提交 **SEMI S2 報告**,等於把「準則」變成「進得了廠的門票」。沒有政府強制,但沒過就賣不進去。

---

## 2. S 系列:設備環安衛安全準則

### 2.1 SEMI S2 — 環安衛總綱(核心)

正式名稱:**Environmental, Health, and Safety Guideline for Semiconductor Manufacturing Equipment**(半導體製造設備環境、健康與安全準則)。

- **定位**:整個 S 系列的**核心**,其他所有 S 標準都視為對 S2 的支撐。1991 年首版,持續改版(查證到較新版本為 SEMI S2-0821,2021 年 8 月)。
- **性質**:**績效導向(performance-based)** 的準則——訂出環安衛的最低門檻,但不寫死實作方式,允許設備商用尚未被標準涵蓋的新技術,只要能達到同等或更好的安全表現。
- **涵蓋面**:查證到的版本約 28 個章節 + 5 個附錄,涵蓋電氣安全、機械安全、防火、化學/氣體危害、人因、緊急停止、警示標示、文件等。
- **對 AMR 的意義**:fab 客戶把 AMR 當「進廠的移動設備」看待,常要求**對應 S2 的安全評估報告(S2 report)**。AMR 要證明:急停、機械夾點防護、電氣安全、警示、文件等符合 S2 的精神。**S2 是「進得了 fab 的門票」**,不是選配。

> S2 本身是傘狀總綱,實際評估時會引用下面幾個更專門的 S 標準。

### 2.2 SEMI S8 — 人因工程(Ergonomics)

正式名稱:**Safety Guideline for Ergonomics Engineering of Semiconductor Manufacturing Equipment**。

- 規範設備在「人要操作/維護」時的人因設計:施力、姿勢、可及範圍、搬運重量、維護點高度等,降低操作員肌肉骨骼傷害。
- **對 AMR 的意義**:維護面板高度、需人工介入(換電池、清障、手動推車)時的施力與姿勢、HMI(人機介面)位置都會被以 S8 角度檢視。

### 2.3 SEMI S14 — 火災風險評估與緩解(Fire Risk)

正式名稱:**Safety Guideline for Fire Risk Assessment and Mitigation for Semiconductor Manufacturing Equipment**。

- 提供設備**火災風險評估與緩解**的方法論:材料可燃性、起火源、火災蔓延、抑制手段。
- **對 AMR 的意義**:AMR 帶**鋰電池**(熱失控起火風險,見[電池認證](battery-certification.md)),又在潔淨室這種高價值、人車混流空間跑,火災風險評估幾乎必做。電池選型(LFP vs NMC)、外殼阻燃、充電站防護都會牽動 S14 評估。

### 2.4 SEMI S22 — 電氣設計安全(Electrical Design)

正式名稱:**Safety Guideline for the Electrical Design of Semiconductor Manufacturing Equipment**。

- 提供**設計階段**的電氣安全準則:配線、接地、保護、隔離、過流/過載防護、可觸及帶電部位等。
- **對 AMR 的意義**:AMR 的電源分配、充電介面、馬達驅動、急停迴路的電氣設計會被以 S22 角度審。它跟通用電氣安全(如 IEC/UL)互補——S22 是半導體業在電氣設計上的共通語言。

> **小結**:S2 是總綱,S8(人因)/S14(火災)/S22(電氣)是常被一起引用的三個專門支柱。AMR 進廠通常要面對「S2 報告 + 引用 S8/S14/S22 的對應評估」。其他 S 標準(如 S10 風險評估流程、S23 能源使用…)視客戶要求補。

---

## 3. SEMI E84 — 自動搬運交接的平行 I/O 介面

正式名稱:**Specification for Enhanced Carrier Handoff Parallel I/O Interface**(增強型載具交接平行 I/O 介面規範)。

這是 AMR 在 fab 裡**最會直接碰到的一條 E 標準**,因為它就是「AMR/OHT 把 FOUP 放上機台 load port、或從 load port 取走」那一瞬間的握手協議。

### 它解決什麼

FOUP 交接(load/unload)如果沒有可靠的握手,後果是「放歪了、夾爪沒對準、機台還沒準備好就放下去」——在 fab 裡這等於可能砸壞一盒 25 片晶圓。E84 用一組**平行 I/O 訊號線**(實體 I/O 點,不是封包協議),讓搬運端(AMR/OHT)跟機台 load port 在交接前後互打信號:

- **選 port**:`CS_0` / `CS_1` 訊號選定要交接的是哪個 load port(一台機台可能有多個)。
- **交接序列**:雙方按定義好的時序握手(我要來了 → 你準備好了嗎 → 可以放 → 放完了 → 確認),含連續交接(continuous)、同時交接(simultaneous)。
- **錯誤偵測與復原**:逾時、訊號不一致時能偵測、指示並進入復原流程。
- 規範還定義連接器型式、接腳配置、300mm 載具用的感測器尺寸。

E84 是在更舊的 **SEMI E23**(平行 I/O 基礎)之上**增強**而來,目的是讓交接更可靠、更有效率。

> **對 AMR 的意義**:AMR 要跟 fab 機台自動交接 FOUP,**E84 的實體 I/O 與時序幾乎是必備**。這是硬體 + 韌體層級的對接(光耦合 I/O、時序狀態機),不是軟體 API。

---

## 4. E 系列 AMHS 標準概覽:哪幾個跟 AMR 直接相關

E 系列很龐大(常合稱 **GEM300**,300mm fab 的自動化標準群)。對 AMR 來說,真正會碰到的是「交接、載具管理、晶圓追蹤、儲存」這幾條,其餘多半是機台端的事。

| 標準 | 正式定位 | 跟 AMR 的關係 |
|---|---|---|
| **SEMI E84** | 增強型載具交接平行 I/O 介面 | **直接、必備**。AMR↔load port 的實體交接握手(見上節)。 |
| **SEMI E87** | 載具管理(Carrier Management System, CMS) | **相關**。定義 FOUP 在 load port 上/廠內被載入、卸載、追蹤的場景與狀態。AMR 把 FOUP 送來/取走,要對得上 E87 的載具狀態流(誰擁有這個 FOUP、放在哪、是否已存取)。可由人工或經 AMHS(即 E84)送達。 |
| **SEMI E90** | 基板(晶圓)追蹤(Substrate Tracking) | **間接**。FOUP 被開盒、晶圓進機台後,E90 追蹤每片晶圓在機台內的位置。AMR 通常只到 FOUP 層級,不直接管 E90,但整個物料可追溯鏈要接得起來。 |
| **SEMI E88** | AMHS 儲存(Stocker)規範 | **相關**。定義 stocker(晶圓盒倉儲)的控制命令與協議。AMR 若把 FOUP 送進/取出 stocker,要對上 E88。 |
| **SEMI E10** | 設備可靠度/可用度/可維護度(RAM)與稼動率的定義與量測 | **間接但常被要求**。E10 定義設備的六大狀態(生產、待機、維護、停機…)與 MTBF、稼動率等指標。客戶常用 E10 框架評估 AMR 車隊的稼動表現。**E10 不是搬運交接標準,是績效量測標準**,別跟 E84/E87 混。 |

> 還有 **E82(Interbay/Intrabay AMHS SEM)**、**E5/SECS-II**、**E30/GEM**(設備通訊)等更上層的自動化/通訊標準。AMR 若要跟 fab 的 **MCS(Material Control System,物料控制系統)/ MES** 對接,會接觸到這層,但那是調度軟體層的事(對應本筆記 [40-fleet](../40-fleet/) 與 VDA5050 主題),跟 E84 的「實體交接握手」是不同層次。**待查證**:特定 fab 對 AMR 要求哪幾條 E 標準,依該廠 MCS 架構而定。

**一句話收斂**:AMR 工程團隊優先吃透 **E84(交接)+ E87(載具狀態)**;E88(若進 stocker)、E10(稼動評估)按需補;E90、E82、E30 多半是機台/上層系統的責任邊界。

---

## 5. 潔淨室相關:看不見但會毀掉晶圓的三件事

fab 是潔淨室(cleanroom)。一台車進來,除了「會不會撞人」,還要管「**會不會吐微粒、會不會放電、會不會散發氣體**」。這三件事在一般倉庫完全不存在,卻是 fab AMR 的硬門檻。

### 5.1 潔淨度:ISO 14644 等級與微粒釋出

**ISO 14644** 是潔淨室空氣潔淨度的國際標準,用每立方公尺的微粒數定義 Class(等級,數字越小越乾淨):

- **ISO Class 1**:≥0.1μm 微粒 ≤10 顆/m³(最嚴,核心製程區)。
- **ISO Class 3**:≤1,000 顆/m³,**前段 fab(front-end)常見**。
- **ISO Class 5**:對應舊制 Class 100,常見於支援區、更衣區。

> 不同來源對 fab 各區的等級對應略有出入(製程區比 gowning/sub-fab 嚴),**實際以該廠各區指定的 ISO Class 為準(待查證)**。

對 AMR 的要求不是「車本身多乾淨」,而是**車運轉時釋出的微粒不能超過所在區的等級上限**:輪子摩擦、馬達/風扇氣流、皮帶、潤滑、外殼材質都可能產生微粒。應對手段——**低逸塵設計**:潔淨室等級的材料與表面處理、避免裸露摩擦面、氣流方向控制、必要時負壓/局部抽風。**車要做潔淨室適用性驗證(particle generation test),證明在目標 ISO Class 下達標。**

### 5.2 ESD(靜電放電)防護

**ESD(Electrostatic Discharge,靜電放電)** 能瞬間擊穿晶片上的微米/奈米結構。AMR 在乾燥潔淨室裡跑、輪子摩擦地面會累積靜電,放電可能毀晶圓、也可能干擾電子。

- 應對:**靜電消散(static dissipative)** 設計——導電/抗靜電輪、接地路徑、表面電阻控制在約 **10⁶–10⁹ Ω**(既不絕緣到累積電荷、也不導電到變成放電路徑),外殼用抗靜電材質。
- fab 通常要求 AMR 通過 ESD 相關規範(對應 ANSI/ESD 或客戶內規);**車的接地與表面電阻要可量測、可驗證**。

### 5.3 Out-gassing(逸氣)

**Out-gassing(逸氣)** 指材料緩慢釋放的揮發性氣體分子。在 fab 這會變成 **AMC(Airborne Molecular Contamination,空氣分子污染)**——氣態污染物會跟敏感製程反應,在 10nm 以下製程越來越致命(ISO 14644-8 專門管分子污染)。

- 應對:AMR 用料要**低逸氣(low-outgassing)**——塑膠、潤滑油、線材、塗層都要選低揮發配方,避免釋出會污染晶圓的分子。
- **車的材料清單(BOM)要做 outgassing 評估**,高揮發材料要替換或封裝。

> **潔淨室三件事一句話**:微粒(別吐塵)、ESD(別放電)、逸氣(別放毒氣)——三項都要**可量測、可驗證**,且各自有目標數值,不是「感覺很乾淨」就過。

---

## 6. 跟通用 AMR 安全標準的關係:互補,不是重疊

fab 客戶要 SEMI 那套,**不代表通用工業 AMR 安全標準就不用了**。兩套管的是不同東西,**互補**:

| 標準 | 管什麼 | 跟 SEMI S2 的關係 |
|---|---|---|
| **ISO 3691-4** | **無人駕駛工業車輛(driverless industrial trucks)的安全**——涵蓋 AGV、AMR、自動推車等。規範防撞、速度、保護性停止、人員偵測、區域掃描等。2020/2023 版。 | **互補**。S2 管「設備在 fab 的環安衛」,ISO 3691-4 管「這台會動的車在有人環境怎麼不撞人」。fab AMR 兩個都要。 |
| **ANSI/RIA R15.08** | **美國的工業移動機器人(IMR)安全標準**(RIA/A3 制定)。聚焦工廠/倉庫/實驗室裡,車與周邊「受安全訓練人員」的安全。Part 1(車本體)/Part 2(系統整合)/Part 3(使用者)。 | **互補**。是 ISO 3691-4 的**北美對應**,但**兩者來源不同、不等價**(平行發展,非誰衍生誰),涵蓋假設有差異。賣到美系客戶常被要求 R15.08。 |
| **ISO 13849** | **控制系統安全相關部件的功能安全**——用 PL(Performance Level)量化安全功能(如急停、安全掃描器到停車)的可靠度。 | **底層基石**。ISO 3691-4 的安全控制功能其實是建在 ISO 13849 的方法上(13849 是更通用的功能安全框架)。S2 的電氣/急停安全評估也會引用功能安全要求。 |

**怎麼理解這三層 + SEMI**:

- **ISO 13849** = 最底層的「功能安全方法論」(安全功能要多可靠)。
- **ISO 3691-4 / ANSI R15.08** = 在其上的「移動車輛專屬安全」(怎麼不撞人),依目標市場(歐系/美系)選對應那套或兩套都過。
- **SEMI S2(+ S8/S14/S22)** = 再疊上「半導體 fab 環安衛」這層(電氣、火災、人因、潔淨…)。

四者不是擇一,而是**疊加**:一台進 fab 的 AMR,底下踩 ISO 13849 的功能安全、套 ISO 3691-4(或/與 R15.08)的移動安全、再過 SEMI S2 系列的 fab 環安衛、外加第 5 節的潔淨室三件事。

---

## 7. 名詞速查(本篇用到的關鍵詞)

| 詞 | 一句話 |
|---|---|
| **FOUP** | 晶圓盒,裝 25 片 300mm 晶圓的密封前開門容器。 |
| **OHT** | 天車,天花板軌道吊運 FOUP 的搬運車。 |
| **load port** | 機台裝載口,FOUP 與機台交接的接口。 |
| **AMHS** | 自動物料搬運系統,fab 內所有自動搬運的總稱。 |
| **MCS** | Material Control System,物料控制系統,調度 AMHS 的上層軟體。 |
| **GEM300** | 300mm fab 設備自動化的 SEMI 標準群總稱。 |
| **EHS** | Environment, Health, Safety,環境/健康/安全(= S 系列管的領域)。 |
| **AMC** | 空氣分子污染,逸氣造成的氣態污染。 |
| **PL** | Performance Level,ISO 13849 量化安全功能可靠度的等級。 |

---

## 8. 半導體 fab AMR 合規清單(總結)

要把一台 AMR 開進晶圓廠,大致要過這幾關。**逐項都應有可提交的報告/測試證據**,不是口頭聲稱:

**A. SEMI 安全(進廠門票)**
- [ ] **SEMI S2** 環安衛評估報告(核心,客戶採購前常強制要求)。
- [ ] 引用 **S8**(人因)/ **S14**(火災,含鋰電池熱風險)/ **S22**(電氣設計)的對應評估。
- [ ] 其他 S 標準(S10 風險評估流程等)按客戶要求補。

**B. SEMI 自動化/搬運(對得上 fab 物流)**
- [ ] **SEMI E84** FOUP 交接平行 I/O 介面(AMR↔load port,實體握手,直接必備)。
- [ ] **SEMI E87** 載具管理狀態流對接(FOUP 狀態追蹤)。
- [ ] **SEMI E88**(若進 stocker)/ **E10**(稼動評估,客戶常用)/ 與 **MCS/MES** 的上層介面(按該廠架構,待查證)。

**C. 潔淨室適用性(看不見的硬門檻)**
- [ ] 達標 **ISO 14644** 目標 Class 的**微粒釋出**驗證(particle generation test)。
- [ ] **ESD** 防護:導電/抗靜電輪、接地、表面電阻 10⁶–10⁹ Ω 可量測。
- [ ] **Out-gassing**:材料 BOM 低逸氣評估,避免 AMC。

**D. 通用功能/移動安全(底層基石,疊加非擇一)**
- [ ] **ISO 13849** 功能安全:安全功能(急停、安全掃描器→停車)達到所需 PL。
- [ ] **ISO 3691-4**(歐系)/ **ANSI/RIA R15.08**(美系):移動車輛防撞/人員偵測安全,依目標市場選對應或兩者。

**E. 其他廠務整合**
- [ ] **電池認證**(UL 2271 / UL 2580,見[電池認證](battery-certification.md))。
- [ ] 充電站、無線網路、定位基礎建設、與 fab 既有 OHT/AGV 的避讓協調(待查證,依現場)。

> **一句話總結**:fab AMR 的合規 = **SEMI S2 系列(環安衛)+ SEMI E84/E87(搬運交接)+ ISO 14644/ESD/逸氣(潔淨室)+ ISO 13849/3691-4/R15.08(功能與移動安全)+ 電池認證**。SEMI 那套是「半導體業專屬、客戶驅動的進廠門票」,通用安全標準是「底層基石」,兩者疊加,缺一進不了廠。

---

## 查證來源(URL)

SEMI 標準:
- SEMI S2(EHS 總綱):https://store-us.semi.org/products/s00200-semi-s2-environmental-health-and-safety-guideline-for-semiconductor-manufacturing-equipment 、 https://www.semi.org/en/node/114001 、 https://www.techintl.com/semi-safety-guidelines/s2/
- SEMI S22(電氣設計):https://store-us.semi.org/products/s02200-semi-s22-safety-guideline-for-the-electrical-design-of-semiconductor-manufacturing-equipment
- SEMI S8 / S14 / S22 概覽:https://www.semi.org/en/products-services/standards/safety 、 https://hightechdesignsafety.com/standards/type/semi-safety-guideline/
- SEMI E84(交接 I/O):https://store-us.semi.org/products/e08400-semi-e84-specification-for-enhanced-carrier-handoff-parallel-i-o-interface 、 https://www.einnosys.com/semi-e84-standard/ 、 https://kontron-ais.com/en/resources/semi-standards/semi-e84
- SEMI E87(載具管理):https://www.peergroup.com/definition-of-standard/semi-e87/ 、 https://kontron-ais.com/en/resources/semi-standards/semi-e87
- SEMI E90 / E88 / E87 / GEM300:https://www.peergroup.com/resources/semi-standards/gem300/ 、 https://www.fortrend.com/technical-blog/understanding-semi-standards-for-load-ports.html
- SEMI E10(RAM/稼動):https://www.peergroup.com/definition-of-standard/semi-e10/ 、 https://store-us.semi.org/products/e01000-semi-e10-specification-for-definition-and-measurement-of-equipment-reliability-availability-and-maintainability-ram-and-utilization

潔淨室 / ESD / 逸氣:
- 半導體潔淨室 ISO Class / AMC / ESD:https://www.dersionclean.com/news/semiconductor-cleanroom-requirements-a-guide-to-iso-classes-amc-esd-control/ 、 https://www.14644.dk/semiconductor-manufacturing-and-cleanroom-requirements 、 https://tsi.com/electronics-manufacturing/learn/meeting-iso-14644-standards

通用 AMR 安全標準:
- ISO 3691-4 / R15.08 / ISO 13849:https://www.boxlogix.com/blog/amr-safety-standards-protocol/ 、 https://jlcrobotics.com/iso-3691-4/ 、 https://www.agvnetwork.com/r15-08-safety-amr 、 https://blog.saphira.ai/mobile-robot-safety-standards-understanding-iso-3691-4-(driverless-industrial-trucks)-and-r15-08-(industrial-mobile-robots)-implementation 、 https://webstore.ansi.org/standards/ria/ansiriar15082020

名詞(FOUP / OHT / load port / AMHS):
- https://www.fortrend.com/technical-blog/understanding-the-interface-between-load-ports-and-amhs-ohtagv-.html 、 https://grokipedia.com/page/FOUP 、 https://www.epak.com/products/efoup-wafer-handling/

> 註:部分為設備商/顧問公司的標準解說頁(非 SEMI 原文)。SEMI 標準原文需向 SEMI 購買;本篇定位、編號、正式名稱已交叉比對 SEMI store 官方頁。標準**內容細節**以原文為準。
