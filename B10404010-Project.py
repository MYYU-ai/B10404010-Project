import pandas as pd
from finlab import data, backtest

################################################
# 一、資料載入
################################################
def load_data():
    """
    1) 載入日收盤價
    2) 載入股價淨值比 P/B
    """
    close = data.get('price:收盤價')
    pbr = data.get('price_earning_ratio:股價淨值比')
    return close, pbr


################################################
# 二、自定義 RSI 計算函式
################################################
def calc_rsi(series, period=14):
    """
    簡易版 RSI 計算：
    RSI = 100 - 100/(1+RS)，其中 RS = 平均漲幅 / 平均跌幅
    """
    delta = series.diff()
    gain = delta.clip(lower=0).rolling(period).mean()
    loss = -delta.clip(upper=0).rolling(period).mean()  # 取絕對值(正值)
    rs = gain / (loss + 1e-9)  # 防止分母為 0
    rsi = 100 - 100 / (1 + rs)
    return rsi


################################################
# 三、計算多週期 RSI
################################################
def compute_multi_rsi(close):
    """
    回傳三種週期 (14, 50, 200 天) 的 RSI
    """
    rsi_short = close.apply(calc_rsi, period=14)
    rsi_mid   = close.apply(calc_rsi, period=50)
    rsi_long  = close.apply(calc_rsi, period=200)
    return rsi_short, rsi_mid, rsi_long


################################################
# 四、計算 60 日均線 (季線)
################################################
def compute_ma60(close):
    ma_60 = close.rolling(60).mean()
    return ma_60


################################################
# 五、設定策略條件
################################################
def set_conditions(rsi_short, rsi_mid, rsi_long, close, ma_60, pbr):
    """
    設定各種條件並回傳
    - cond_all_rsi: 三個 RSI 的綜合條件
    - cond_price_above_5: 股價 > 5
    - cond_price_above_ma60: 股價大於 60 日均線
    - cond_valid_pbr: P/B 不為空
    """
    # (1) 三週期 RSI 條件
    cond_rsi_short = (rsi_short < 70)
    cond_rsi_mid   = (rsi_mid > 50)
    cond_rsi_long  = (rsi_long > 50)
    cond_all_rsi = cond_rsi_short & cond_rsi_mid & cond_rsi_long

    # (2) 股價淨值比條件
    cond_price_above_5 = (close > 5)
    cond_price_above_ma60 = (close > ma_60)
    cond_valid_pbr = pbr.notna()  # pbr 為有效數值

    return cond_all_rsi, cond_price_above_5, cond_price_above_ma60, cond_valid_pbr


################################################
# 六、前置篩選 (結合 RSI 與 P/B)
################################################
def pre_filter(cond_all_rsi, cond_price_above_5, cond_price_above_ma60, cond_valid_pbr):
    """
    先「同時符合 RSI 與股價前置條件」：
      RSI 三條件 + 股價 > 5 + 站上季線 + P/B 不為空
    """
    cond_pre_filter = (
        cond_all_rsi &
        cond_price_above_5 &
        cond_price_above_ma60 &
        cond_valid_pbr
    )
    return cond_pre_filter


################################################
# 七、篩選後的 P/B
################################################
def filter_pbr_with_conditions(pbr, cond_pre_filter):
    """
    將符合條件者保留 P/B，否則設為 NaN
    """
    filtered_pbr = pbr.where(cond_pre_filter, other=pd.NA)
    return filtered_pbr


################################################
# 八、選出 P/B 最小 (最便宜) 的前 n 檔
################################################
def pick_lowest_pbr(filtered_pbr, n=10):
    """
    回傳一個 DataFrame[布林值]，
    True 表示該日期該股票的 P/B 屬於排名最前 n 名
    """
    lowest_pbr_n = (filtered_pbr.rank(axis=1, ascending=True) <= n)
    return lowest_pbr_n


################################################
# 九、停損機制 (例如跌 10% 即出場)
################################################
def stop_loss_condition(close, drop_pct=0.10):
    """
    當日收盤價 相對前日大跌 drop_pct (預設 10%) 即停損
    """
    cond_stop_loss = (close.pct_change() <= -drop_pct)
    return cond_stop_loss


################################################
# 十、產生最終持股表 position
################################################
def generate_position(lowest_pbr_n, stop_loss_cond):
    """
    1) 將 P/B 前 n 檔視為買進條件 (buy_condition)
    2) 加入停損機制：跌超過 drop_pct 則出場
    """
    buy_condition = lowest_pbr_n.fillna(False)
    position = buy_condition.hold_until(stop_loss_cond)
    return position


################################################
# 十一、主程式，串接所有步驟並進行回測
################################################
def main():
    # 1) 讀取資料
    close, pbr = load_data()
    
    # 2) 計算多週期 RSI
    rsi_short, rsi_mid, rsi_long = compute_multi_rsi(close)
    
    # 3) 計算 60 日均線
    ma_60 = compute_ma60(close)
    
    # 4) 設定策略條件
    cond_all_rsi, cond_price_above_5, cond_price_above_ma60, cond_valid_pbr = \
        set_conditions(rsi_short, rsi_mid, rsi_long, close, ma_60, pbr)
    
    # 5) 前置篩選
    cond_pre_filter = pre_filter(cond_all_rsi, cond_price_above_5, cond_price_above_ma60, cond_valid_pbr)
    
    # 6) 篩選後的 P/B
    filtered_pbr = filter_pbr_with_conditions(pbr, cond_pre_filter)
    
    # 7) 選出最便宜的前 10 檔
    lowest_pbr_10 = pick_lowest_pbr(filtered_pbr, n=10)
    
    # 8) 停損機制 (跌 10% 停損)
    stop_loss_cond = stop_loss_condition(close, drop_pct=0.10)
    
    # 9) 產生持股表
    position = generate_position(lowest_pbr_10, stop_loss_cond)
    
    # 10) 回測：每季換股
    report = backtest.sim(position, resample='Q')
    report.display()


################################################
# 可以自行呼叫 main() 執行
################################################
if __name__ == "__main__":
    main()
