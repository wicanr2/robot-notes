# 產品專章

這一區按產品整理整車規格、控制板與車載電腦的分工，以及加裝感測器或其他設備時的限制。查特定車型的接線與控制方式，從下表進入；共通原理可查[系統架構](../00-overview/system-architecture.md)與[硬體總覽](../10-core/10-hardware/README.md)。

| 產品 | 閱讀重點 |
|---|---|
| [Husarion Panther](husarion-panther.md) | 戶外四輪平台；內建電腦與 User Computer 分工、CAN 馬達控制、EMU 急停、V-slot 安裝導軌 |
| [Husarion ROSbot XL](husarion-rosbot-xl.md) | 教育與研究平台；車載電腦與 STM32 控制板、Ethernet 通訊、可切換輪型、上蓋安裝板與擴充供電 |
| [Panther 與 ROSbot XL 控制架構 SWOT](husarion-control-architecture-swot.md) | 比較底盤 Linux＋CAN 驅動器與 Linux＋Ethernet＋STM32 的責任、開發與維護取捨 |

兩款產品的電腦配置、電壓、通訊協定、急停功能與安裝結構不同，整合時需查對應車型的章節。

## 兩款車並排

| 項目 | Panther | ROSbot XL |
|---|---|---|
| 定位 | 戶外無人地面載具 | 教育與研究平台 |
| 基準重量／最大載重 | 55 kg／120 kg | 5.38 kg／10 kg |
| 最大線速度 | 2 m/s | 0.8 m/s |
| 電池 | 36 V，720 或 1440 Wh | 11.1 V，86.5 Wh |
| 馬達 | 4 顆無刷馬達＋行星減速機 | 4 顆 12 V 有刷直流馬達 |
| 應用電腦 | 選配 User Computer | 車載電腦（Raspberry Pi 5、Jetson 或 NUC） |
| 底盤控制 | Built-in Computer 經 CAN 到前後馬達控制器 | 同一台車載電腦經 Ethernet 到 STM32 |
| 硬體急停 | EMU，開關可設定 | 手冊未記載急停介面 |

## 名詞速查

| 名詞 | 意思 | 延伸閱讀 |
|---|---|---|
| CAN | 多個裝置共用兩條差分線的匯流排，抗干擾，常用來連馬達控制器 | [通訊匯流排](../10-core/10-hardware/communication-buses.md) |
| CANopen | 建立在 CAN 上的應用層協定，規定怎麼設定裝置、傳速度與狀態 | [通訊匯流排](../10-core/10-hardware/communication-buses.md) |
| Roboteq | Panther 的馬達控制器廠牌，ROS 介面會回報它的狀態 | |
| MCU／SBC | MCU 是接馬達與感測器的微控制器，例如 STM32；SBC 是跑 Linux 的單板電腦 | [上下位機通訊](../10-core/20-firmware/host-mcu-protocol.md) |
| MAVLink | 輕量訊息協定，源自無人機。ROSbot XL 的 STM32 用它和電腦交換資料 | [上下位機通訊](../10-core/20-firmware/host-mcu-protocol.md) |
| micro-ROS | 跑在 MCU 上的 ROS 2 客戶端。ROSbot XL 舊韌體使用，`v2.2.0-jazzy` 起移除 | [上下位機通訊](../10-core/20-firmware/host-mcu-protocol.md) |
| 橋接（bridge） | 把 MCU 協定和 ROS 2 主題互相轉換的程式，例如 `rosbot_mavlink_bridge` | |
| BLDC／有刷馬達 | 無刷馬達靠控制器電子換相，壽命長、功率大；有刷馬達靠電刷換相，電路簡單 | [底盤與傳動](../20-forms/wheeled-amr/chassis-and-drivetrain.md) |
| PWM／H 橋 | PWM 用快速開關調平均電壓；H 橋是四個開關組成的電路，決定馬達電流方向 | [數位電路](../10-core/10-hardware/digital-circuits.md) |
| cpr | 編碼器每轉一圈的計數，解碼方式不同，數字也不同 | |
| 3S | 三顆鋰電芯串聯，標稱約 11.1 V | |
| 差速 | 靠左右輪速差轉彎。四輪車沒有轉向機構時，轉彎要靠輪子側滑 | [底盤與傳動](../20-forms/wheeled-amr/chassis-and-drivetrain.md) |
| 看門狗（Watchdog） | 定時器。沒有定期收到訊號，就判定對方失效並採取動作 | [上下位機通訊](../10-core/20-firmware/host-mcu-protocol.md) |
| 鎖存（latch） | 觸發後維持住狀態，觸發條件消失也不恢復，要重設才解除 | |
| SPDT 繼電器 | 機械開關，共同端可切到兩個接點之一，外部電路用它得知急停狀態 | |
| EMU／USI／UCI | Panther 的緊急管理單元、使用者安全介面、使用者艙介面 | [Panther §3.4](husarion-panther.md) |
| 即時核心 | 讓 Linux 任務延遲更可預期的核心設定，底盤驅動靠它維持控制週期 | |
| GPIO | 可用程式設成輸入或輸出的接腳 | |
| V-slot 2020 | 斷面 20×20 mm、四面有 V 形溝槽的鋁擠型，用 T 型螺帽固定設備 | |
| IP54／IP66 | 防護等級。第一碼防塵、第二碼防水：IP54 防塵並防濺水，IP66 完全防塵並防強力噴水 | |
| GNSS／RTK | GNSS 是衛星定位；RTK 用差分修正把定位提升到公分級 | |
| GMSL2 | 相機用的高速序列連結，線可以拉得比 USB 長 | |
| DDS | ROS 2 底層的通訊中介層，負責節點互相發現與傳資料 | [ROS 2 與 DDS](../40-fleet/ros2-dds-intro.md) |
| TF／Footprint | TF 是各座標系的轉換關係；Footprint 是車體占地輪廓，導航用它算避障 | |

Panther 與 ROSbot XL 都有 CAN，用途不同：Panther 的 CAN 連接馬達控制器，是控制鏈的一環；ROSbot XL 的 CAN 是擴充接腳上的 MCU 訊號，留給使用者外接，馬達控制不走它。

## 圖片與來源

章節中的方塊圖與電腦規格表是依 Husarion 官方手冊重繪的示意圖，用 Codex 圖像生成後逐條核對文字與連線，並不是官方原圖。接線與接腳以各圖旁的官方連結為準。

官方原圖保留在 `img/` 的 `husarion-*.png`，權利屬原權利人。來源、擷取時間、瀏覽器版本及 SHA-256 保存在 [husarion-source-captures.json](../../img/husarion-source-captures.json)，擷取程式為 [capture-husarion-docs.cjs](../../scripts/capture-husarion-docs.cjs)，使用 `ghcr.io/puppeteer/puppeteer:23.11.1` 映像檔，在 Docker 內啟動 Chromium。

重生官方圖片時，在 repo 根目錄確認程式與 `img/` 都存在，且輸出檔與目錄屬於目前使用者，再執行：

```bash
test -d img &&
test -f scripts/capture-husarion-docs.cjs &&
timeout 180s docker run --rm --name robot-notes-husarion-capture \
  --network bridge --memory 2g --cpus 2 --pids-limit 256 \
  --user "$(id -u):$(id -g)" --read-only \
  --tmpfs /tmp:rw,nosuid,size=512m \
  --cap-drop ALL --security-opt no-new-privileges \
  -e PUPPETEER_CACHE_DIR=/home/pptruser/.cache/puppeteer \
  -e XDG_CONFIG_HOME=/tmp/husarion-chrome-config \
  -e XDG_CACHE_HOME=/tmp/husarion-chrome-cache \
  --mount type=bind,src="$PWD",dst=/work \
  --entrypoint node ghcr.io/puppeteer/puppeteer:23.11.1 \
  /work/scripts/capture-husarion-docs.cjs /work/img
```

此步驟需要網路，會更新官方的兩張電腦截圖、兩張方塊圖、Panther 方塊圖原始檔及來源紀錄，不會動到重繪圖。官方網頁可能改版，重生後須重新檢查型號、圖片範圍及章節內的規格。
