# VLM 與 LLM:讓機器人聽得懂話、看得懂沒學過的東西

傳統機器人的感知是封閉的——訓練時教過「棧板」,它就只認得棧板。大型語言與視覺模型改變的是這件事:**不必事先列舉,用講的就行。**

這兩篇是嚴格的前後關係:

| # | 篇 | 內容 |
|---|---|---|
| 1 | [LLM 與 VLM 給機器人](llm-vlm-for-robots.md) | 原理層:文字怎麼變 token、自注意力在解什麼問題、影像怎麼也變成 token、VLA 與開放詞彙感知對機器人的意義 |
| 2 | [在 NVIDIA GB10 上架本地 LLM](local-llm-on-nvidia-gb10.md) | 落地層:為什麼推論是**記憶體頻寬** bound 而不是算力 bound、統一記憶體的取捨、量化能省多少、GB10 規格與軟體堆疊 |

第一篇的結尾留了一個伏筆直接接到第二篇——**模型要跑在哪台機器上,答案不是「看算力」**。

## 相關

- 模型在模擬裡訓練:[Physical AI / sim-to-real](../50-physical-ai/sim-to-real.md)
- 機率與高斯的數學底:[數學基礎](../90-foundations/gaussian-from-first-principles.md)
