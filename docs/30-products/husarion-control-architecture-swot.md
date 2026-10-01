# Panther 與 ROSbot XL 控制架構差異與 SWOT

Panther 用一台專責底盤的 Linux 內建電腦，經 CAN 連接獨立馬達控制器；ROSbot XL 則由車載 Linux 電腦經 Ethernet 與 STM32 數位控制板交換資料，板上再連接馬達與感測器。兩種分工會影響輪指令在哪裡產生、底盤韌體如何維護，以及更換應用電腦時需要重設哪些底盤服務。[Panther 官方方塊圖](https://husarion.com/manuals/panther/#block-diagram)、[ROSbot XL 官方方塊圖](https://husarion.com/manuals/rosbot-xl/#block-diagram)。

本文比較開發整合與後續維護的差異。查閱日期：2026-10-01；Panther 依據 v1.2 與現行 ROS 2 文件，ROSbot XL 依據現行產品資料與 `rosbot_ros` Jazzy 文件。SWOT 是依架構作出的工程分析，尚無整車延遲、停止距離、故障率或成本的實測比較；選用哪種架構仍需按專案需求判斷。整車資料另見 [Panther](husarion-panther.md)與 [ROSbot XL](husarion-rosbot-xl.md)。

## 1 先把兩條控制鏈畫完整

### 1.1 Panther 的應用電腦與底盤電腦分工

```text
User Computer：Nav2、視覺、任務與自訂應用
       ↕ ROS 2／Ethernet，經 RUTX11
Built-in Computer：底盤 ROS 2、車體速度轉輪指令、里程
       ↕ CAN／CANopen
前、後獨立馬達控制器：馬達控制與狀態回報
       ↕
4 顆 BLDC 馬達＋編碼器

EMU／Safety Board：另外接收急停、看門狗與驅動故障
```

Panther 直接連接馬達控制器的是 Built-in Computer。User Computer 上的應用程式透過內建電腦提供的 ROS 介面控制底盤；EMU 則有自己的硬體觸發、鎖存與外部連動設定。[官方電腦分工](https://husarion.com/manuals/panther/panther-options/#user-computers)、[硬體介面](https://husarion.com/manuals/panther/software/ros2/packages-overview/#husarion_ugv_hardware_interfaces)、[EMU](https://husarion.com/manuals/panther/panther-emu/)。

### 1.2 ROSbot XL 的應用電腦與 MCU 控制板分工

```text
車載電腦：Nav2、視覺、ROS 2 底盤控制與里程
       ↕ ROS 硬體介面＋MCU 通訊橋接
       ↕ Ethernet，經 Digital Board 的交換器
STM32F407：韌體側控制、馬達與感測器介面
       ↕ 板上馬達驅動電路
4 顆 DC 馬達＋編碼器；IMU 等周邊也接至數位板
```

現行官方 README 說明 MCU 使用 MAVLink，由 `rosbot_mavlink_bridge` 橋接至 ROS 2；舊韌體曾支援 micro-ROS。Ethernet 提供硬體連線，MAVLink／micro-ROS 決定其上的資料交換方式，兩者需分別核對。車體運動學控制器仍在 ROS 2 端，STM32 負責韌體側控制與硬體介面。[ROSbot XL 手冊](https://husarion.com/manuals/rosbot-xl/)、[現行驅動 README](https://github.com/husarion/rosbot_ros#run-the-robot)、[官方 ROS API](https://github.com/husarion/rosbot_ros/blob/jazzy/ROS_API.md)。

## 2 差異落在哪些責任上

下表依官方資料列出硬體與軟體分工，「實際影響」欄說明整合時需考慮的工程問題。

| 比較面向 | Panther | ROSbot XL | 實際影響 |
|---|---|---|---|
| 應用運算 | 選配 User Computer | 車載電腦（SBC／NUC） | 兩者均能更換應用算力，但電腦端承擔的底盤服務不同 |
| 專責底盤 Linux | 有 Built-in Computer | 底盤 ROS 驅動與應用共用車載電腦 | Panther 多一個可分開管理的系統，也多一套開機、更新與診斷工作 |
| 車體速度換算輪指令 | 內建電腦的 `drive_controller` | 車載電腦的差速／麥克納姆控制器 | 更換應用電腦對 ROSbot XL 的底盤執行環境影響較直接 |
| 馬達控制的硬體邊界 | 經 CAN 到前後獨立驅動器 | 經 Ethernet 到 STM32 與板上驅動電路 | Panther 的驅動器配置、ROSbot XL 的 MCU 韌體各自成為維護責任 |
| 馬達與感測器整合 | 馬達控制器、IMU、底盤電腦各有連接 | 數位板集中連接馬達、編碼器、IMU 等 | 集中化減少分散接線介面，也集中板卡故障的影響 |
| 公開應用介面 | ROS 2 速度、里程、硬體狀態與服務 | ROS 2 速度、里程、狀態；MCU 資料另由橋接轉換 | 應用開發皆可使用 ROS；底層的版號與協定要分別維護 |
| 安全鏈 | 公開 EMU、USI、CPU 看門狗與硬體設定 | 本次手冊列數位板、電源板及重設功能 | Panther 有較清楚的公開急停整合入口；不能據此直接宣稱安全認證等級 |
| 電源與關機 | 多電壓使用者面板，兩台電腦有關機協調 | 可選 5 V／12／19 V 電腦供電，共用電源板 | 更換電腦都需核對供電；Panther 還需維護跨電腦關機與時間同步 |

比較控制品質時，需量測應用發布指令到車輪回授的端到端延遲與抖動，並檢查失聯和重啟行為。應用指令、車體控制與輪速控制各有執行頻率，結果還受排程、封包、控制器設定與負載影響，單看 Ethernet 或 CAN 的傳輸速度無法判斷。

## 3 Panther 架構的 SWOT

以下將內部條件分為優勢（Strengths）與劣勢（Weaknesses），將外部需求和環境變化分為機會（Opportunities）與威脅（Threats）。各項影響均依官方架構分析，成立條件列在右欄。

| 類別 | 分析 | 實際影響與成立條件 |
|---|---|---|
| 優勢 S | 應用與底盤各有運算環境 | 更換 GPU 電腦或重啟應用時，可保留底盤執行環境；前提是底盤 ROS 與供電正常 |
| 優勢 S | 馬達控制器獨立成模組 | 馬達控制與功率電路的分工明確，應用端可透過 ROS 使用底盤，減少直接維護功率控制的工作 |
| 優勢 S | EMU／USI 有公開接線說明 | 上裝可依硬體介面設計急停連動，但需核對修訂版、開關設定與接點額度 |
| 劣勢 W | 元件與版本組合較多 | 應用 OS、底盤 OS／ROS、馬達控制器及安全板都需記錄設定，故障定位也需逐層檢查 |
| 劣勢 W | 多一台電腦需要維護 | 需處理網路、時間同步與關機協調，並增加供電、空間與維護項目；成本差額尚未量測 |
| 劣勢 W | 指令仍經過底盤 Linux | 內建電腦的排程與通訊仍會影響指令傳遞，需維持即時核心與逾時設定 |
| 機會 O | 感知與 AI 的算力需求增加 | 可升級獨立 User Computer，減少對底盤執行環境的改動 |
| 機會 O | 上裝與第三方驅動器整合需求 | 新設備若符合機械、供電與安全介面，較容易按模組整合；換馬達驅動器仍需驗證相容性 |
| 機會 O | 不同應用需要共用底盤 | 固定底盤介面與版本後，可對接不同導航或任務軟體 |
| 威脅 T | 零件停產或相容性變動 | 控制器、電腦或網路設備更換後，可能需要重新配線、調整驅動並驗證 |
| 威脅 T | 戶外電源、線束與網路干擾 | 震動、接點、電壓降與網路中斷都可能影響運作，需一起驗證機構防護與控制容錯 |
| 威脅 T | 上裝整合時誤判急停效果 | 急停後外部設備可能仍帶電或仍有動作，需一起驗證 EMU、USI 接線與設備安全輸入 |

硬體事實依據：[電腦分工](https://husarion.com/manuals/panther/panther-options/#user-computers)、[底盤硬體介面](https://husarion.com/manuals/panther/software/ros2/packages-overview/#husarion_ugv_hardware_interfaces)、[時間同步及關機](https://husarion.com/manuals/panther/software/user_computer/setup/)、[EMU 設定](https://husarion.com/manuals/panther/panther-emu/)。

## 4 ROSbot XL 架構的 SWOT

ROSbot XL 由 STM32 承擔硬體側控制。能否滿足特定即時或安全要求，需查韌體、排程與故障處理方式，再以實測確認。

| 類別 | 分析 | 實際影響與成立條件 |
|---|---|---|
| 優勢 S | Linux 與 MCU 分擔不同工作 | MCU 承擔硬體側控制，應用端使用 ROS；電腦更新時會繼續動作還是停車，需查韌體並實測 |
| 優勢 S | 馬達與感測器集中於數位板 | 小平台較容易整合與教學，也減少多個獨立馬達控制器之間的設定工作 |
| 優勢 S | 不同電腦都以 Ethernet 連接 | 換 Raspberry Pi、Jetson 或 NUC 時可沿用連線方式，但仍要核對 ROS、橋接、韌體與供電 |
| 劣勢 W | 底盤服務與應用共用電腦 | CPU、記憶體、磁碟負載或 OS 更新都可能影響底盤 ROS，需做資源管理與壓力測試 |
| 劣勢 W | 韌體與橋接程式需配對 | 調整訊息或協定時需同步兩端，micro-ROS 轉為 MAVLink 的版本變化就是維護時要處理的例子 |
| 劣勢 W | 數位板故障影響較集中 | 馬達、感測器與部分通訊可能一起受影響，除錯時需區分 MCU、驅動電路與交換器 |
| 機會 O | 教育與嵌入式開發需求 | 可在同一平台學習 ROS、MCU、通訊橋接與控制分工；修改底層時需保留版本與驗證紀錄 |
| 機會 O | 網路診斷與嵌入式工具成熟 | 可使用 Ethernet 診斷與新的橋接工具，採用前需確認 MCU 資源與協定相容性 |
| 機會 O | 小型感知與操作應用增加 | 官方電腦、相機與手臂套件可作為整合起點，仍需核對載重、散熱與電源 |
| 威脅 T | ROS 與韌體版本持續變動 | 舊教學與封存儲存庫可能描述不同介面；版號不相容時，可能無法控制或讀回資料 |
| 威脅 T | 外部 Ethernet 流量或錯誤連線 | 需測試外部插座、SBC 與 MCU 共用交換器時的負載、隔離與存取控制；掉包風險尚待驗證 |
| 威脅 T | 用於比研究場域風險更高的環境 | 需重新確認機構、防護與安全功能；STM32、逾時或重設按鈕不足以證明可取代獨立安全鏈 |

硬體與版本事實依據：[數位板與方塊圖](https://husarion.com/manuals/rosbot-xl/#block-diagram)、[供電與擴充](https://husarion.com/manuals/rosbot-xl/#user-compartment)、[現行驅動與韌體配對](https://github.com/husarion/rosbot_ros#run-the-robot)、[舊儲存庫封存說明](https://github.com/husarion/rosbot_xl_ros)。

## 5 用具體故障情境比較

下表可作為故障測試清單，各項結果尚待實測。

| 情境 | Panther 要檢查 | ROSbot XL 要檢查 |
|---|---|---|
| AI／影像程式吃滿 CPU | User Computer 是否持續輸出速度；底盤電腦的 ROS 通訊是否正常 | 共用電腦上的底盤控制器與橋接是否受到資源競爭影響 |
| 應用程式停止發布速度 | 指令逾時與仲裁後的車體反應；其他來源是否仍在發布 | 仲裁與車體控制器的逾時；其他速度來源是否重新取得控制權 |
| 底盤電腦／ROS 驅動停止 | EMU CPU 看門狗、驅動器與急停鎖存 | 電腦端控制器／橋接停止後，MCU 是否及時進入預期狀態 |
| 車內通訊線斷開 | 分別測 User↔Built-in 的 Ethernet 與 Built-in↔驅動器的 CAN | SBC↔STM32 的 Ethernet 失聯、重連及舊命令處理 |
| 更新電腦或韌體 | ROS 版本、底盤控制器設定、名稱空間與關機協調 | ROS、橋接協定及 MCU 韌體配對；更新失敗與回復流程 |
| 按急停／外接上裝停止 | EMU、AUX、USI 與上裝的實際連動 | 先確認實際可用的停車／安全介面，再驗證上裝的獨立停止方式 |

測試時可記錄控制延遲與抖動、失聯後的停止時間和距離、重啟後是否出現非預期動作，以及應用負載對底盤控制的影響。更新或替換零件所需的工程時間，也可用來比較維護工作量。每次測試應固定輪型、載荷與輸入，分別記錄正常負載和壓力條件。兩車的功率、速度與尺寸不同，停止距離的差異需連同這些條件判讀。

## 6 依需求理解適用性

下表按需求列出可考慮的方向與待查資料，供後續選型或設計評估使用。

| 需求 | 架構上的判讀 | 還需查證 |
|---|---|---|
| 應用算力常換、底盤環境希望少改 | Panther 的獨立底盤電腦提供明確分工 | 實際可用接口、兩端版號、供電與關機 |
| 想學習或修改 MCU 韌體與通訊 | ROSbot XL 的 Linux↔STM32 邊界更貼近此研究課題 | 韌體原始碼、板卡修訂版、橋接契約與刷寫回復 |
| 想替換不同馬達與驅動器 | Panther 的獨立驅動器邊界提供模組化研究起點 | CANopen 物件、控制模式、功率與安全設定，不保證直接替換 |
| 要裝高功率或高重心上裝 | 先查整車機構、電源與安全能力，再比較控制架構 | 載荷、力矩、散熱、急停與使用場域 |
| 要達成特定安全或即時指標 | 兩款皆需以具體故障策略與量測證明 | 安全功能契約、故障注入、停止距離與相關認證資料 |

延伸閱讀：[上下位機通訊協議](../10-core/20-firmware/host-mcu-protocol.md)、[下位機運動控制](../10-core/20-firmware/low-level-control.md)、[電源與安全](../10-core/10-hardware/power-and-safety.md)、[產品索引](README.md)。
