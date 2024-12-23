# Python理專: 基於PEG與RSI選股程式

![contribution](https://img.shields.io/badge/contributions-welcome-blue)
![python](https://img.shields.io/badge/Python-3.9_or_later-green)
![pillow](https://img.shields.io/badge/Pillow-9.0_or_later-green)

finlab 是一個針對臺灣股市量化分析而設計的 Python 套件，包含日線股價、月營收、季財報等資料，能搭配簡易的回測介面，讓投資人能更快速開發、測試、部署投資策略。

本程式利用 finlab 套件撰寫並實作「雙策略」：
本益成長比 (PEG) 基本面策略
三頻率 RSI 技術面策略

藉由取得股市資料、選股策略篩選、回測績效、資料視覺化、策略流動性風險檢測與停損機制進行量化選股

## (1) 程式的功能 Features

本程式主要功能如下：

**獲得股市資料**：透過 finlab.data.get(...) 取得股價、基本面、財報等資料。

**根據選股策略選股**：
- 以營收成長動能 + 重新定義的 PEG 策略 (本益成長比)
- 三頻率 RSI (短、中、長) 策略
回測績效：利用 backtest.sim(position, resample='...') 執行回測。

**資料視覺化**：透過 report.display() 或自行搭配其他繪圖工具。

**策略流動性風險檢測**：參考成交量等數據 。

**停損機制**：程式設定單日跌幅達 10% 即停損點。

## (2) 使用方式 Usage

### 1. 安裝 finlab

```bash
pip install finlab
```

### 2. 匯入套件

```python
import pandas as pd
from finlab import data, backtest
```

取得資料時，可使用 data.get('price:收盤價') 或 data.get('monthly_revenue:當月營收') 等指令。

- 日線資料 (e.g. price:收盤價)
- 月營收資料 (e.g. monthly_revenue:當月營收)
- 季財報資料 (e.g. fundamental_features:營業利益成長率)

### 3. 執行程式

- 先執行資料前處理與策略條件設定部分 (讀取股價、財報、計算 RSI、PEG、篩選條件 … 等)
- 透過 backtest.sim(...) 進行回測
- 最後透過 report.display() 檢視回測結果

### 4. 或是直接於Finlab執行
- 進入[Finlab](https://ai.finlab.tw/)並登入
- 創建策略
- 執行程式

## (3) 程式的架構 Program Architecture

整體程式碼可拆解為以下區塊：

**資料載入**

- 讀取股價相關資料 (e.g. 收盤價)
- 讀取基本面／財報資料 (e.g. 本益比、本業成長率、營收 … 等)

**策略計算**

- 本益成長比 (PEG) 策略: 
    - 短期營收動能超越長期營收動能
    - PEG (本益成長比) 經過改良：本益比 ÷ 營業利益成長率
- 三頻率 RSI 策略: 
    - RSI 短週期 (14 天)、中週期 (50 天)、長週期 (200 天)
    - 設定 RSI 絕對數值的進出場條件

**擬定進出場條件**
- 同步考量多重條件 (例如 &、|、.hold_until() 等)
- 置入停損機制 (e.g. 單日跌幅 > 10%)

**回測**
- 定義好 position 後，以 backtest.sim(position, resample='M' or 'Q') 執行月/季/週回測

**報告與視覺化**
- report.display() 顯示回測結果 (報酬、最大回撤 … 等)
- 可自行搭配 matplotlib、plotly 等進行更進階圖表繪製

## (4) 開發過程 Development Process

**策略發想到原型**
- 先以 chatGPT o1 撰寫草稿，蒐集技術面 (RSI、移動平均) 與財務面 (PEG、P/B、月營收增長率) 等可行因子。
- 初步測試多種週期、停損機制與篩選手法，並比較彼此績效與風險。
**資料擷取與對齊**
-以 finlab.data.get() 擷取多頻資料(每日、每月、每季)，並用 pandas 進行對齊(如 rolling, shift, apply)。
**因子設計與篩選**
- 三頻率 RSI：使用短、中、長不同週期 RSI，以「絕對值判斷」(如 > 50, < 70) 取代交叉訊號。
- PEG 改良：以「營業利益率成長」替代「稅後淨利成長」作為分母，排除業外雜訊。
- 其他條件：股價門檻、均線、P/B、流動性等。
**回測與優化**
- backtest.sim(position, resample='M'/'Q') 回測不同重平衡頻率。
- 調整 RSI 週期、停損幅度、選股數量 (前 5、10、20 檔) 進行多次測試，提升組合穩定度。
**流動性與風險管理**
- 若策略資金量大，則先以「成交金額 > 一定門檻」篩選，避免因成交不足影響進出場。
- 停損/停利設定與檔數分散亦是必要的風險控管步驟。
**策略整合與發佈**
- 針對「本益成長比(PEG)」與「三頻率 RSI」兩大策略，可各自獨立回測，也可在同一程式中合併 (如交集或聯集)。

## (5) 參考資料來源 References

1. [Finlab 官方教學文件](https://doc.finlab.tw/getting-start/) - Finlab套件說明
2. [三頻率RSI策略](https://ai.finlab.tw/notebook/?uid=TJN4FDuqrwU8DML7DAjUYFIMutp2&sid=%E4%B8%89%E9%A0%BB%E7%8E%87RSI%E7%AD%96%E7%95%A5) - 三頻率RSI策略.
3. [本益成長比](https://ai.finlab.tw/notebook/?uid=TJN4FDuqrwU8DML7DAjUYFIMutp2&sid=%E6%9C%AC%E7%9B%8A%E6%88%90%E9%95%B7%E6%AF%94) - 本益成長比策略.
4. ChatGPT o1 - 程式碼原型草稿生成，以及debug.

## (6) 程式修改或增強的內容 Enhancements and Contributions

**PEG 新定義**

傳統 PEG 以 EPS 成長率當分母；本程式改以「營業利益成長率」，可排除非經常性損益。

**三頻率 RSI 策略**

以 RSI 14、50、200 三週期絕對值範圍判斷強弱，不採用「黃金交叉 / 死亡交叉」。

**停損機制 (10%)**

單日股價跌幅達 10% 即停損，可有效避免重大虧損。

**自訂檔數限制**

篩選 PEG 最小前 10 檔 (或 RS 排行前 10) 等，使用者可自由調整。

**流動性風險檢測**

本範例僅示範股價 > 5 元的基本篩選，可進一步新增「成交金額或成交量」條件以避開冷門股。

**程式結構最佳化**
- 將指標計算、策略篩選、回測等邏輯分模組化 (function / class)，使程式更易維護。
- 加入參數設定檔(e.g. config.yaml 或 config.json)，可快速設定不同的週期、停損幅度、本益成長比篩選分數、檔數限制等，方便批量測試與快速迭代。

透過上述程式，可直接觀察以 PEG 與 三頻率 RSI 兩大策略為基礎的投資結果。
在實務中，建議再加入 成交量 / 流動性 閾值、 資金控管 與 風險分散 機制，以更貼近真實交易需求。
若想更深入了解 finlab 的操作，可參考 FinLab 官方教學文件，或成為付費會員取得更多資料。