# 多機調度:一群機器人怎麼被統一指揮

一台機器人會自己導航,不代表十台放在同一個場域就會合作。這一區處理的是那個落差:**每台車都只看得到自己,誰來讓它們不要互相擋路、不要搶同一個充電樁、不要在窄道對撞?**

答案分兩層,而且是兩個不同的問題:

- **共同語言**——主控要能跟不同廠牌的車講話。沒有標準的話,N 家主控 × M 家車就是 N×M 種私有對接。這是 [VDA5050](vda5050.md) 解的。
- **協調層**——就算都聽得懂了,誰決定哪台車去做哪筆任務、誰先過路口?這是 [Open-RMF](open-rmf.md) 解的。

## 建議閱讀順序

照這個順序讀,每一篇都建在前一篇上:

| # | 篇 | 為什麼在這個位置 |
|---|---|---|
| 1 | [ROS 2 與 DDS](ros2-dds-intro.md) | 地基。RMF 整套跑在 ROS 2 上,而 ROS 2 的節點怎麼互相找到對方、怎麼保證訊息送達,決定了上層能做什麼 |
| 2 | [VDA5050](vda5050.md) | 共同語言。訊息長什麼樣、`order` 怎麼組、`released` 與 horizon 在解什麼問題 |
| 3 | [Open-RMF](open-rmf.md) | 協調層。為什麼要在車隊「之上」再加一層,以及它怎麼透過 VDA5050 指揮異廠牌的車 |
| 4 | [地圖、座標與交通](rmf-maps-and-traffic.md) | 前一篇的四個實作細節:三層 API、三種地圖、座標系怎麼對齊、怎麼避塞車 |
| 5 | [fleet adapter 怎麼寫](rmf-adapter-cookbook.md) | 把 §3 的概念變成程式碼骨架 |
| 6 | [路網模型與交通管制](roadnet-and-traffic-control.md) | 換個角度重來一次:不談特定框架,問「空間怎麼表示、衝突怎麼偵測、卡住怎麼脫困」三個根本問題 |
| 7 | [室內 AMR 路網選型](indoor-amr-roadnet-selection.md) | 上一篇的結論套用到叉車 / 搬運車 / 送貨機器人三種場景 |
| 8 | [儲位重複預定與死鎖](slot-reservation-dispatch-strategies.md) | 交管的另一面:不是「撞到怎麼辦」,是「怎麼讓它不可能發生」。銀行家演算法、時空預約、飢餓 |
| 9 | [私有堆疊 vs ROS 2:任意起點](proprietary-vs-ros2-arbitrary-start.md) | 一個具體的現場現象(車繞大圈)拆到底,順帶說明分層職責 |
| 10 | [多容器部署](rmf-multi-container-deploy.md) | 把上面這些跑起來時會撞到的六道關卡 |
| 11 | [MQTT over TLS](mqtt-tls-emqx.md) | VDA5050 跑在 MQTT 上,把 broker 鎖好是傳輸層的功課 |
| 12 | [廣域連線:5G 與衛星](robot-wan-5g-satellite.md) | 機器人走出本地 Wi-Fi 之後的連線選項。**與前 11 篇關聯較鬆,可獨立讀** |

## 一個容易漏掉的重點:這裡有兩條匯流排

系統裡同時存在兩套 pub/sub,而它們不是同一張網:

```
Open-RMF ── DDS ──► fleet adapter ── MQTT ──► 各廠 AMR
        (ROS 2 內部)              (VDA5050)
```

**fleet adapter 是唯一的接點。** 左邊是 ROS 2 的 DDS,右邊是 VDA5050 的 MQTT——adapter 的工作就是把 RMF 的拓樸目標翻成 `order` 發出去,再把車回的 `state` 翻回 RMF 認得的位姿與電量。理解這件事之後,「為什麼要寫 adapter」「adapter 難在哪」就都有著落了。

## 相關

- 單台車怎麼導航:[共通核心 / 導航](../10-core/30-navigation/)
- 模擬環境裡驗證整套調度:[Physical AI](../50-physical-ai/)
- 通訊安全:[資安](../70-security/)
