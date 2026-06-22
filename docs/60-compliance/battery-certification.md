# 電池認證法規(移動機器人)

機器人能不能上市,電池這一關的法規常是隱形門檻。本篇整理室內移動機器人(AMR / 送餐機器人 / AGV)鋰電池包的安全認證:UL 2271 與 UL 2580 的適用界線、為什麼選 LFP + 金屬外殼,以及兩家供應商的認證現況。

> 起點是一則現場資訊:同事提到「電池採 LFP(磷酸鋰鐵)、外殼金屬材質、符合 UL 2580 或 UL 2271,供應商 BSLBATT / Flux Power」。本篇把這條線索查證並展開。
> 標準版本與強制範圍會更新,**實際出貨認證以 UL / 檢測機構 / 主管機關當下公告為準**。
> 延伸閱讀:[電源與安全](../10-hardware/power-and-safety.md)(電壓法規 SELV、急停、保護)、[半導體 AMR 規範](semiconductor-amr-standards.md)。

---

## 1. 一句話分界:UL 2271 vs UL 2580

兩張都是**電池包(EESA,電能儲存組件)層級**的安全標準,差別在「車有多重、電壓多高、濫用測試多嚴」:

| | **UL 2271** | **UL 2580** |
|---|---|---|
| 正式名稱 | Batteries for Use in **Light Electric Vehicle (LEV)** Applications | Batteries for Use in **Electric Vehicles** |
| 定位 | 輕型電動載具電池 | 電動車 / 工業車輛電池 |
| 典型用途 | 電動自行車、滑板車、平衡車 | 電動汽車、堆高機、AGV、AMR |
| 典型電壓 | ≤ ~60V(業界口徑 <100V) | 較高,工業級 |
| 馬達功率門檻 | 約 ≤750W | 無此上限 |
| 濫用測試 | 電池包完整性 + 基本保護 | 加機械濫用(振動/衝擊/跌落/擠壓)+ 環境(熱衝擊/鹽霧/浸水)+ 危害(外部火燒、**熱擴散** thermal propagation) |

**兩者不可互換。** 一個是「較輕、較低壓」那端,一個是「較重、較高壓、工業級」那端。

## 2. 送餐機器人該套哪一張?——依機型逐案判定

查證後的誠實結論:**沒有單一定論**,物料搬運/移動機器人市場兩條路線都有真實案例,取決於該機型的電壓 / 載重 / 目標市場:

- **走 UL 2271**:較輕、低電壓(24V 級)的搬運設備。Flux Power 的 24V LiFT Pack(Class III 棧板車)是**全球第一個拿到 UL 2271 的堆高機電池包**(2018,UL 官方新聞稿),歸於 "Light EV" 系列。
- **走 UL 2580**:工業級、較高電壓 / 較重載(配重式堆高機、較大型 AGV/AMR)。BSLBATT 的堆高機 / AGV·AMR LFP 電池、Flux Power 較重的 X-Series 走這條。

> 對「室內送餐機器人」這種**低電壓(常 24V/48V)、輕載、低速**的 AMR,從電壓/功率門檻看比較靠近 **UL 2271 的 LEV 區間**;但若要對齊工業 AGV/AMR 規格或客戶指定,會被導向 **UL 2580**。**具體哪一張,要依該機型實際電壓/規格與目標市場確認(逐案、待查證)**,不宜一概而論。同事說的「UL 2580 或 UL 2271」正反映了這個「看情況」的現實。

## 3. 為什麼選 LFP(而非三元鋰 NMC)——第一性原理是「本質安全」

移動機器人在**室內、貼近人(送餐尤其)、環境溫度多變**的場域跑,本質安全比能量密度重要。LFP 的根本優勢在熱失控(thermal runaway,電芯自我加速放熱失控起火)這條線上:

| 安全指標 | LFP(磷酸鋰鐵) | NMC(三元鋰) |
|---|---|---|
| 熱失控起始溫度 | 約 **270°C** | 約 **150–210°C** |
| 分解是否釋氧 | **不釋氧** → 不助燃 | 釋氧 → 助燃、更易燒 |
| 熱失控釋能 | 約 10–15 kJ/Ah | 約 20–25 kJ/Ah(約兩倍) |
| 可燃氣體量 | 比 NMC **少約 80%** | 多 |

根本邏輯:**門檻高 + 不釋氧 + 釋能少 → 單一電芯失效不容易擴散成整包大火**。代價是能量密度較低(同容量較重/較大),但對「低速、可頻繁回充」的室內機器人通常可接受;LFP 循環壽命長、成本低,也利於高頻充放的送餐/搬運工況。

## 4. 為什麼是金屬外殼——被動防護的最後一道

電池包外殼是**被動containment**的最後屏障,對認證有三層意義,正好對應 UL 的測試項目:

1. **機械防護**:抵抗振動/衝擊/跌落/擠壓——UL 2580 機械安全測試的考核對象;金屬剛性高,有利通過。
2. **不助燃**:塑膠外殼最低要 UL 94 V-0/V-1 阻燃等級;**金屬本身不燃**,這關天然有利。
3. **熱擴散抑制**:單一電芯熱失控數秒可衝到 700–900°C,外殼要延緩起火、限制蔓延、爭取 BMS 反應時間——對應 UL 2580 熱擴散測試與 UL 2596(外殼熱失控 BETR 測試)。

## 5. 供應商認證現況(查證)

| 供應商 | 認證宣稱 | 查證註記 |
|---|---|---|
| **BSLBATT**(惠州,中國;LFP 專業廠) | **UL 2580 + IEC 62619**(B-LFP24/36/48/80 系列型號);另稱符合 UL/CEC/IEC/CE/UN38.3。有 AGV·AMR 產品線 | 官網對自動抓取回 HTTP 403,以多頁搜尋摘要 + 第三方貿易媒體(Material Handling Wholesaler)交叉佐證。**確切 UL 檔案號/有效型號,引用前建議到 UL Product iQ 線上資料庫逐型核對** |
| **Flux Power**(美國 Nasdaq: FLUX) | **UL 2271**(24V LiFT Pack,UL 官方新聞稿證實為全球首例堆高機電池 UL 2271 Listing)+ **UL 2580**(X-Series)；皆 LiFePO4 | UL 官方新聞稿可佐證 UL 2271 首例;官網列 UL 2580/2271/583/1971/UN38.3 |

> Flux Power 同時持兩張(UL 2271 輕型 + UL 2580 重型),正好示範第 2 節「依電壓/載重分流選標準」。

## 6. 別忘了的配套認證(一個完整出貨組合)

電池只過 UL 2271/2580 還不夠,實務分層:

| 層級 | 認證 | 性質 |
|---|---|---|
| 電芯 | IEC 62133 / 62619、UL 1642 | 電芯/電池安全 |
| 電池包 | UL 2271 或 UL 2580(+ UL 1973 視應用) | 包層級安全 |
| BMS 功能安全 | UL 991(硬體)+ UL 1998(軟體) | 保護電路的功能安全 |
| 運輸 | **UN 38.3** | 空海運**強制**(8 項測試);幾乎必備 |
| 區域准入 | CE/UKCA(歐英)、BSMI(台)、PSE(日) | 進入市場強制;**充電器/電源**尤其受 BSMI/PSE 管(呼應 [電源與安全 §18](../10-hardware/power-and-safety.md)) |

常見完整組合 ≈ **UN 38.3 + IEC 62619 +(UL 2271 或 UL 2580)+ 目標市場區域認證**。

## 7. 待查證 / 風險標記

- BSLBATT 確切 UL 2580 檔案號與有效型號清單:官網 403,建議用 UL Product iQ 逐型核對。
- 「送餐機器人」官方歸 UL 2271 還是 UL 2580:依電壓/規格/市場逐案判定,**無單一權威定論**,引用前對特定機型確認。
- BSMI 強制品項、PSE 菱形/圓形範圍細節:此處為通則,落地查當期法規清單。

## 8. 來源

UL 範圍:[UL 2271 (GlobalSpec)](https://standards.globalspec.com/std/14658607/ul-2271)、[UL 2271 (Battery Design)](https://www.batterydesign.net/legislation-rules-and-regulations/ul-2271/)、[UL 2580](https://www.shopulstandards.com/ProductDetail.aspx?productId=UL2580_3_S_20200311)、[CSA: EV battery standards](https://www.csagroup.org/article/navigating-safety-standards-for-ev-batteries-and-electric-vehicle-supply-equipment/)
LFP vs NMC 安全:[Battery Design](https://www.batterydesign.net/objective-safety-analysis-of-nmc-vs-lfp/)、[EHV Technology](https://www.electrichybridvehicletechnology.com/technical-articles/lfp-vs-nmc-thermal-runaway.html)
供應商:[UL 官方:Flux Power 首例 UL 2271](https://www.ul.com/news/ul-issues-first-ul-2271-listing-lithium-ion-forklift-battery-pack-flux-power-1)、[Flux Power 電池技術](https://www.fluxpower.com/battery-technology)、[MHW: BSLBATT UL 認證報導](https://www.mhwmag.com/nuts-bolts/bsl-battery-receives-certification-for-lifepo4-forklift-batteries/)
配套:[UN 38.3 (TÜV SÜD)](https://www.tuvsud.com/en/services/testing/battery-testing/battery-transportation-safety-testing-iec-62133)、[UL 1973 (TÜV SÜD)](https://www.tuvsud.com/en-us/services/testing/energy-storage/ul-1973)
