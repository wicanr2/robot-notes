# 韌體:上位機的意圖怎麼變成馬達實際在轉

上位機算出「往前 0.5 m/s、右轉 0.3 rad/s」之後,這一層負責把它變成兩顆輪子各自該轉多快,並且**每 10 毫秒都要準時做完一次**。

| # | 篇 | 一句話 |
|---|---|---|
| 1 | [下位機運動控制](low-level-control.md) | 差速正逆解、PID 為什麼一定要 I 項、odometry 怎麼積出來 |
| 2 | [上下位機通訊協定](host-mcu-protocol.md) | 自己設計一套序列協定會踩到的三個坑,以及每個欄位在還哪個債 |
| 3 | [STM32 上的 REST 與 TLS](stm32-rest-tls.md) | 一顆 MCU 要直接講 HTTPS,RAM 夠不夠、該選哪組 cipher suite |
| 4 | [板子模擬:Renode](board-simulation-renode.md) | 手上沒有實體板子怎麼跑韌體、怎麼把韌體測試放進 CI |

> 前面是[硬體](../10-hardware/)(東西是什麼),後面是[導航](../30-navigation/)(該往哪走)。這一層夾在中間,兩邊的約束都要吃。
