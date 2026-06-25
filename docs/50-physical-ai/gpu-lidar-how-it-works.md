# gpu_lidar 怎麼運作:用 GPU render 深度,不是逐 ray 求交(讀原始碼)

模擬裡的 LiDAR(Gazebo 的 `gpu_lidar`)為什麼叫「**GPU** lidar」、為什麼要 GPU?直覺會說「LiDAR 打很多 ray,所以是 ray tracing」——但讀完 gz 的原始碼會發現:**它其實是叫 GPU 把場景的「深度」render 出來,再讀那張深度圖當距離**,跟典型的 ray tracing 不一樣。這篇從第一性原理講起,並對照真正的實作程式碼。

> 前置:[LiDAR 完整解析](../10-hardware/lidar-landscape.md)(真實 LiDAR 怎麼測距)、[在 Gazebo 倉庫用 slam_toolbox 建圖](gazebo-slam-warehouse.md)(gpu_lidar 在 SLAM 的角色)。
> 讀的原始碼(Gazebo Harmonic 對應分支):[`gz-sensors/src/GpuLidarSensor.cc`](https://github.com/gazebosim/gz-sensors/blob/gz-sensors8/src/GpuLidarSensor.cc)、[`gz-rendering/ogre2/src/Ogre2GpuRays.cc`](https://github.com/gazebosim/gz-rendering/blob/gz-rendering8/ogre2/src/Ogre2GpuRays.cc)。

---

## 1. 第一性原理:模擬一顆 LiDAR 要算什麼

真實 2D LiDAR 的物理:從一個點,往 N 個方向(例如 360 條,每隔 1°)各射一束光,量「打到最近表面、反射回來」的距離。輸出就是 N 個距離值(`LaserScan`)。

所以模擬器要回答的問題只有一個,重複 N 次:

> **沿著「這個方向」這條射線,第一個碰到的場景表面有多遠?**

## 2. 兩種算法:逐 ray 求交 vs render 深度

**做法 A — CPU 逐 ray 求幾何交點(直覺、慢)**:對每一條 ray,跟場景裡每個三角形算「射線–三角形交點」,取最近的。複雜度 ~ O(ray 數 × 三角形數)。一顆 360 線的 LiDAR、場景幾十萬個三角形,每幀就是上億次運算。雖然有 BVH 之類加速結構,但仍是「逐 ray」的活。

**做法 B — 用 GPU render 場景的「深度」(gz 走這條)**:這裡有個關鍵觀察——

> **GPU 的 rasterizer(光柵器)本來就在做「對每個螢幕像素,算出最近的表面、以及它的深度」**(那叫 depth buffer / Z-buffer,是畫 3D 畫面時用來決定誰遮住誰的東西)。

也就是說:把相機擺在 LiDAR 的位置、朝場景 render 一次,GPU 順手產生的**深度緩衝**,每個像素值就是「那個方向到最近表面的距離」——這正是 LiDAR 要的東西!不必逐 ray 自己算交點,**讓畫圖的硬體免費附贈**。

<p align="center"><img src="../../img/gpu-lidar-pipeline.svg" width="780" alt="gpu_lidar 管線:雷射方向→GPU 1st pass 把場景深度 render 成 cubemap→2nd pass 用 cubeUV 貼圖每條 ray 取樣對應 texel 得距離→range buffer→LaserScan/PointCloud"></p>

## 3. 為什麼是 GPU

- **rasterizer 是專用硬體、海量並行**:它一次處理整張影像的所有像素(深度測試是內建功能),這正好是「一次拿到所有 ray 的距離」。CPU 逐 ray 求交是序列的活,差好幾個數量級。
- **深度測試是「免費」的副產品**:GPU 畫任何 3D 場景都要算 Z-buffer 決定遮擋;gpu_lidar 只是把這個本來就會算的東西讀出來用。

代價:它需要一個能 render 的 GPU(或軟體模擬的 rasterizer)。這也是它叫 `gpu_lidar`、以及[沒 GPU 就跑不順](#6-回扣為什麼沒-gpu--ci-軟體渲染就慢)的根本原因。

## 4. gz 實際怎麼做(讀碼)

### 4.1 感測器層:`GpuLidarSensor` 包一個會 render 的 `GpuRays`

`GpuLidarSensor.cc` 的 `CreateLidar()` 建立一個 `GpuRays`(gz-rendering 的物件),並做一件很關鍵、很能說明「這是 render」的事:

```cpp
this->dataPtr->gpuRays->SetNearClipPlane(this->RangeMin());
this->dataPtr->gpuRays->SetFarClipPlane(this->RangeMax());
```

**把 LiDAR 的最小/最大量程,設成相機的近/遠裁切面**——因為它真的是用一台相機在 render。`Update()` 每幀呼叫 `this->Render()`(GPU render),把結果(每方向的深度)拿來發布。

### 4.2 1st pass:把場景深度 render 成 **cubemap**

`Ogre2GpuRays.cc` 裡,真正幹活的是把場景深度 render 出來。但有個幾何問題:**一台透視相機的 FOV 有限,涵蓋不了 360°**(甚至超過 90° 就開始嚴重變形)。gz 的解法是 **cubemap**——把場景深度 render 到一個立方體的多個面上,程式註解寫得很白:

> *"Each cubemap texture covers 90 deg FOV"*(每面涵蓋 90° 視野)

所以 360° 水平掃描 → 用立方體的側面拼起來(最多 6 面,`cubeFaceIdx` 只算 LiDAR FOV 需要的那幾面)。每面是一次深度 render(`firstPassTextures`,一面一張)。1st pass 的解析度會依取樣數動態決定(程式裡 clamp 在 128~1024)。

> **深度要「線性化」**:GPU 的 depth buffer 不是線性的距離(近處精度高、遠處被壓縮),所以 1st pass 的 shader 用相機投影參數把它**還原成真實距離**。程式註解:*"The projectParams is used to linearize depth buffer data"*。

### 4.3 2nd pass:每條 ray 去 cubemap 取樣

有了「立方體六面的深度圖」,還要把它變回「LiDAR 的 N 條 ray、每條一個距離」。這是 2nd pass:

- 預先算好一張 **`cubeUVTexture`**(註解:*"Texture packed with cubemap face and uv data"*)——對每一條輸出 ray(某個方位角 azimuth + 俯仰角 inclination),記好「該去**哪一面**、取樣那面的**哪個 UV**」。
- 2nd pass 是一個全螢幕 quad shader:對每條 ray,照 `cubeUVTexture` 的指示去對應的 cube face 取樣,讀出那個方向的(線性化)深度 = **該 ray 的距離**。

輸出是一張 range buffer:每條 ray 一個距離(外加強度/laser retro)。

### 4.4 近裁切要用「球面」

一個容易忽略的細節:相機的近裁切面是**平面**,但 LiDAR 的 `range_min` 是**球面半徑**(各方向等距)。直接用平面近裁切,斜射的 ray 會被錯誤裁掉。gz 為此寫了一個自訂 shader `Ogre2GzHlmsSphericalClipMinDistance`,把近裁切改成球面距離。這種小地方正是「模擬要對得起物理」的功夫。

### 4.5 深度 → 距離 → 點雲

回到 `GpuLidarSensor.cc`:拿到每條 ray 的深度後,`FillPointCloudMsg()` 用**球座標轉直角座標**把它變成 3D 點:

```cpp
x = depth * cos(inclination) * cos(azimuth);
y = depth * cos(inclination) * sin(azimuth);
z = depth * sin(inclination);
```

`LaserScan`(2D)直接用距離陣列;`PointCloud`(3D)用上面的轉換。這就是 `/scan`、`/points` 的由來。

## 5. 為什麼這「不算真正的 ray tracing」

很多人(包括 SDF 標籤直覺)會說 LiDAR 模擬是 ray tracing。嚴格講:

- **概念上**對:每個方向一條 ray、量到最近表面——這是 ray casting 的語意。
- **實作上**不是典型 ray tracing:gz 沒有對每條 ray 去場景做「射線–幾何求交」,而是用 **rasterization(把場景深度畫出來)+ cubemap + 深度取樣**。這在通用 GPU 上快得多,也不需要 RTX 那種硬體 ray tracing 單元。
- 真正的硬體 ray tracing(RTX / `VK_KHR_ray_tracing`)是另一條路:逐 ray 在 BVH 上追蹤交點,對「反射、折射、非直線光路」更精確,但需要特定硬體。gz 的 `gpu_lidar` 為了**通用、夠快、夠準**,選了 rasterized depth 這條。

> 所以「`gpu_lidar` = ray tracing」是個方便但不精確的說法;精確講是「**用 GPU rasterizer render 深度來模擬 ray 測距**」。

## 6. 回扣:為什麼沒 GPU / CI 軟體渲染就慢

既然 `gpu_lidar` 的距離是「render 出來的」,它就**需要一個 render 後端(ogre2)能用的 GPU**。沒有實體 GPU 時,Mesa 用 **llvmpipe** 在 CPU 上「軟體模擬」整個 rasterizer——能跑,但把「本來硬體並行的深度 render」變成 CPU 算,於是又慢又吃 CPU。這正是我們在 [GitHub Actions × gz sim playbook](../_meta/github-actions-gz-sim-playbook.md) 看到的:**免費 runner 上 `gpu_lidar` 出 `/scan` 不穩**,因為它骨子裡是 render。

也因此,把 LiDAR 換成「不需 render 的 CPU ray-cast 感測器」一直是無 GPU CI 的願望——但 gz 新版主力就是 `gpu_lidar`(rendering-based),這條限制短期改不掉。

---

## 來源(實際讀過的檔)

- `gz-sensors` `GpuLidarSensor.cc`(感測器層、近/遠裁切=量程、深度→點雲):https://github.com/gazebosim/gz-sensors/blob/gz-sensors8/src/GpuLidarSensor.cc
- `gz-rendering` `Ogre2GpuRays.cc`(cubemap 1st pass 深度、2nd pass 取樣、線性化、球面近裁切):https://github.com/gazebosim/gz-rendering/blob/gz-rendering8/ogre2/src/Ogre2GpuRays.cc
- `gz-rendering` `BaseGpuRays.hh`(GpuRays 介面:角度/ray 數/clip 設定):https://github.com/gazebosim/gz-rendering/blob/gz-rendering8/include/gz/rendering/base/BaseGpuRays.hh
- 概念對照:GPU depth/Z-buffer 與 rasterization(維基):https://en.wikipedia.org/wiki/Z-buffering
