# 用 GitHub Actions 驗證與「看」gz sim 模型(可重用 playbook)

把 Gazebo(新版 `gz sim`)的模型 / 世界 / 機器人,放到 **GitHub Actions** 上自動驗證——尤其當你**沒有 GPU、本機 CPU 也吃緊**時,讓 GitHub 的機器代勞。這份是從實際把 AWS Small Warehouse 遷到 Harmonic、搭一台舵輪叉車、再讓它「在倉庫裡走給人看」的過程,萃取出的可重用做法與一路踩過的雷。

> 活範例(完整 `validate.yml` + 腳本):[aws_warehouse_model_for_gazebo_harmonic](https://github.com/wicanr2/aws_warehouse_model_for_gazebo_harmonic)。相關:[用 Gazebo + ROS2 模擬 AMR](../50-physical-ai/simulation-gazebo-ros2.md)。

---

## 第一原則:把「需不需要 render」當分水嶺

免費 GitHub runner **沒有 GPU**。這條線決定一切——不需 render 的事 100% 可靠,需 render 的事又慢又不穩:

| 任務 | 需 render? | 免費 runner |
|---|---|---|
| SDF 結構驗證(`gz sdf -k`)、XML 良構、`model://` 路徑 | 否 | ✅ 完全可靠 |
| world headless **載入**(`gz sim -s`,驗 include 解析) | 否 | ✅ 可靠 |
| 機器人**會不會動 / 走什麼軌跡**(下指令、記位姿) | 否(純物理) | ✅ 可靠 |
| 相機**出圖 / 錄影**(視覺成品) | 是 | ❌ 不可靠(軟體渲染慢且間歇) |

**設計原則:不需 render 的盡量自動化上 CI;需 render 的視覺產出,別硬塞免費 runner**(改 GPU runner / 帶 GL 的 Docker / 本機一次性截圖)。但「視覺化」不一定要 render——見 §4 的軌跡圖。

---

## 1. 靜態驗證(最便宜、最可靠的一關)

不開模擬就能抓一堆錯。一支 `scripts/validate.sh` 做三件事:

1. 每個 `model.sdf` 過 `gz sdf -k`(抓結構錯、**慣性張量違反三角不等式**等)。
2. 每個 world 用嚴格 XML 解析器(Python `xml.dom.minidom`)驗良構(抓 **XML 註解內的 `--`** 這種 `gz sdf` 容忍、但其他工具會拒的)。
3. world 裡每個 `model://NAME` 都對應得到本機 `models/NAME/` 或 `robot/NAME/` 目錄。

> 注意:`gz sdf` **解析不了 `model://`**(那是 gz-sim 執行期 + `GZ_SIM_RESOURCE_PATH` 的 findFile callback;獨立 sdformat 工具沒有,會報 `callback is empty`)。所以 world 的 include 解析「能不能成」只能交給真正的 `gz sim`(下節)。

## 2. headless 載入 world(驗 include 真的接得上)

`gz sim -s -r --iterations 300 <world>`(server-only、跑幾百步退出),grep log 有沒有 `Unable to find uri` / `Error Code` / `Failed to load`。這一步**不需 render**(world 沒有相機 sensor 時 Sensors system 閒置),所以可靠。它是唯一能證明「整個倉庫 include 全解析、載得起來」的方法。

## 3. 機器人「會動」(純物理,可靠)

下指令、比對前後位姿:`gz topic` 發速度/角度指令給機器人,跑幾秒,用 `gz topic -e -t /model/<name>/pose` 讀位姿(機器人模型要掛 `gz-sim-pose-publisher-system`),算位移 ≥ 門檻就算「會動」。純物理、無渲染 → 可靠。

## 4. 「看」機器人走軌跡(不需 render 的視覺化)

要讓人「看到」機器人在場景裡走,**不一定要 render 3D 畫面**:把它的**位姿軌跡記錄下來、用 matplotlib 畫成俯視路徑圖**(純 CPU)。做法:

- 背景跑 `gz topic -e -t /model/<name>/pose > poses.txt`,同時下驅動指令。
- 收工後用腳本解析 `poses.txt` 取 (x,y) 序列,加上場景障礙位置(從 world SDF 的 `<model><pose>` regex 抽出),畫成路徑 + 起點/終點 + 方向箭頭。

這是無 GPU 也能「看到機器人在倉庫走」的可靠方式。

> **物理等價技巧**:重場景(如貼了一堆 mesh 的倉庫)在免費 runner 上 sim 跑得很慢(見 §5),機器人在 wall-time 內幾乎走不動。但因為 **dartsim 忽略 mesh 碰撞**(§5),機器人「在倉庫開」與「在一塊平面地板上開」**物理完全等價**。所以可以**在輕量世界(只有地板+機器人)把路徑開出來**(sim 快、跑得遠),再把路徑**疊到重場景的佈局圖**上。

---

## 5. 物理層的雷(dartsim,Harmonic 預設)

- **dartsim 不支援 mesh 碰撞**:SDF 的 `<collision>` 若是 `<mesh>`,dartsim 直接忽略(log:`Mesh construction from an SDF has not been implemented yet for dartsim`)。AWS 倉庫的地板、貨架 collision 全是 mesh → 等於**沒有碰撞體**:機器人會穿過貨架、甚至沒有地板可踩(原地騰空空轉)。**要真碰撞要嘛換 bullet 物理引擎、要嘛自己補 primitive(plane/box)collision。** 本 playbook 的軌跡圖是補一塊 `<plane>` 地板讓機器人有得開。
- **重場景 → RTF 極低**:幾十個大 mesh 模型,光是載入 + SceneBroadcaster 廣播狀態就把 2 核 runner 拖到 sim 只跑 **~4% 真實時間**(55s wall ≈ 2s sim)。所以重場景裡「跑 wall-time 等它走」不切實際——用 §4 的物理等價技巧繞開。

## 6. headless 渲染(真的要 3D 畫面時)的 recipe 與雷

能動的組合:

```bash
export LIBGL_ALWAYS_SOFTWARE=true
export GALLIUM_DRIVER=llvmpipe      # 關鍵:EGL surfaceless 預設掉到最慢的 swrast
gz sim -s -r --headless-rendering <world>   # EGL surfaceless,免 X / xvfb(僅 ogre2)
```

- 裝 Mesa:`libgl1-mesa-dri libegl1 libegl-mesa0 mesa-utils`。
- 相機 `<sensor type="camera">` 加 `<save enabled="true"><path>…</path></save>`,world 掛 `gz-sim-sensors-system`(沒掛就不 render)。
- 給暖機時間:render 在獨立 thread,首張影格要等 ogre2/llvmpipe 暖機;用 real-time 跑、輪詢磁碟出圖,**別用 `--iterations`**(它跑完會在 render thread 出圖前就關 server)。
- **誠實的雷**:即使 recipe 對,**免費 runner 純軟體渲染又慢又間歇**——首張影格十幾秒、常整輪生不出圖。可成功一兩次,但不可靠。**影片更不切實際**(每張 ~15s)。要穩定 → GPU runner / 帶 GL 的 Docker / 本機一次性截圖。

## 7. 工程習慣與雷總表

| 雷 | 說明 |
|---|---|
| `gz` 預設不寫 stdout | 要 `-v 4` 才把訊息 echo 到 console;否則 redirect 出來的 log 是空的 |
| 背景跑 + SIGKILL/SIGTERM 丟 log | 緩衝未 flush → log 看似 0-byte(不是真的沒輸出);影格則是「已寫的留著、最後一張可能丟」 |
| `gz sdf -p` 驗 world 會誤判 | 它解析不了 `model://`;world 結構/include 驗證要分開做(§1、§2) |
| 先本機跑通再寫 CI | CI 腳本自己有盲點(如上條),先在本機踩過,CI 才不會綠得不明不白或紅得冤枉 |
| `<physics type>` 必填 | SDFormat 必填屬性,別為了「引擎由 plugin 決定」就刪掉;留 `ode` 字串即可 |

---

## 來源

- gz headless rendering:https://gazebosim.org/api/sim/9/headless_rendering.html
- Mesa llvmpipe / 環境變數:https://docs.mesa3d.org/drivers/llvmpipe.html 、 https://docs.mesa3d.org/envvars.html
- gz 資源路徑(`GZ_SIM_RESOURCE_PATH` / `model://`):https://gazebosim.org/api/sim/8/resources.html
- 活範例:https://github.com/wicanr2/aws_warehouse_model_for_gazebo_harmonic
