# 產品專章

這一區按產品整理整車規格、控制板與車載電腦的分工，以及加裝感測器或其他設備時的限制。查特定車型的接線與控制方式，從下表進入；共通原理可查[系統架構](../00-overview/system-architecture.md)與[硬體總覽](../10-core/10-hardware/README.md)。

| 產品 | 閱讀重點 |
|---|---|
| [Husarion Panther](husarion-panther.md) | 戶外四輪平台；內建電腦與 User Computer 分工、CAN 馬達控制、EMU 急停、V-slot 安裝導軌 |
| [Husarion ROSbot XL](husarion-rosbot-xl.md) | 教育與研究平台；車載電腦與 STM32 控制板、Ethernet 通訊、可切換輪型、上蓋安裝板與擴充供電 |
| [Panther 與 ROSbot XL 控制架構 SWOT](husarion-control-architecture-swot.md) | 比較底盤 Linux＋CAN 驅動器與 Linux＋Ethernet＋STM32 的責任、開發與維護取捨 |

兩款產品的電腦配置、電壓、通訊協定、急停功能與安裝結構不同，整合時需查對應車型的章節。

## 官方圖片與截圖

章節中的方塊圖保留 Husarion 原圖；電腦規格圖是官方網頁章節的實際截圖。各圖旁附原始來源，圖片權利屬原權利人。

圖片來源、擷取時間、瀏覽器版本及 SHA-256 保存在 [husarion-source-captures.json](../../img/husarion-source-captures.json)。擷取程式為 [capture-husarion-docs.cjs](../../scripts/capture-husarion-docs.cjs)，使用既有 `ghcr.io/puppeteer/puppeteer:23.11.1` 映像檔，在 Docker 內啟動 Chromium。

重生圖片時，先確認專案路徑、程式與 `img/` 都存在，且輸出檔與目錄屬於目前使用者，再執行：

```bash
test -d /home/anr2/robot-notes/img &&
test -f /home/anr2/robot-notes/scripts/capture-husarion-docs.cjs &&
timeout 180s docker run --rm --name robot-notes-husarion-capture \
  --network bridge --memory 2g --cpus 2 --pids-limit 256 \
  --user "$(id -u):$(id -g)" --read-only \
  --tmpfs /tmp:rw,nosuid,size=512m \
  --cap-drop ALL --security-opt no-new-privileges \
  -e PUPPETEER_CACHE_DIR=/home/pptruser/.cache/puppeteer \
  -e XDG_CONFIG_HOME=/tmp/husarion-chrome-config \
  -e XDG_CACHE_HOME=/tmp/husarion-chrome-cache \
  --mount type=bind,src=/home/anr2/robot-notes,dst=/work \
  --entrypoint node ghcr.io/puppeteer/puppeteer:23.11.1 \
  /work/scripts/capture-husarion-docs.cjs /work/img
```

此步驟需要網路，會更新兩張電腦截圖、兩張方塊圖、Panther 方塊圖原始檔及來源紀錄。Panther 原圖為透明底白字，文件顯示版本以深色背景擷取，保留原圖內容。官方網頁可能改版，重生後須重新檢查型號、圖片範圍及章節內的規格。
