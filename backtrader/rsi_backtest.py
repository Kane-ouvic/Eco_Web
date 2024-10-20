import backtrader as bt
import datetime
import yfinance as yf
import matplotlib
matplotlib.use('Agg')  # 確保使用非交互式後端 Agg
import matplotlib.pyplot as plt  # 必須在設置後端後引入
# 定義策略類
class RSICrossStrategy(bt.Strategy):
    params = (
        ('short_period', 14),  # 短期 RSI 週期
        ('long_period', 30),   # 長期 RSI 週期
        ('rsi_upper', 70),     # 超買區
        ('rsi_lower', 30),     # 超賣區
        ('stake', 1000),       # 單筆下單股數
    )

    def __init__(self):
        # 定義短期和長期 RSI 指標
        self.rsi_short = bt.indicators.RSI(period=self.params.short_period)
        self.rsi_long = bt.indicators.RSI(period=self.params.long_period)
        self.crossover = bt.indicators.CrossOver(self.rsi_short, self.rsi_long)

    def next(self):
        if not self.position:  # 若無持倉
            if self.crossover > 0:  # 短期 RSI 上穿長期 RSI (黃金交叉)
                self.buy(size=self.params.stake)
        elif self.crossover < 0:  # 短期 RSI 下穿長期 RSI (死亡交叉)
            self.sell(size=self.params.stake)

# 設定 Cerebro 回測環境
cerebro = bt.Cerebro()

# 加入策略
cerebro.addstrategy(RSICrossStrategy, short_period=14, long_period=30)

# 讀取股票數據
data = bt.feeds.PandasData(dataname=yf.download('AAPL', '2020-01-01', '2023-01-01'))

# 將數據加到 Cerebro
cerebro.adddata(data)

# 設定初始資金
cerebro.broker.set_cash(100000.0)

# 設定手續費
cerebro.broker.setcommission(commission=0.001425)

# 執行回測前查看初始資金
print(f'初始資金: {cerebro.broker.getvalue():.2f}')

# 開始回測
cerebro.run()

# 執行回測後查看最終資金
print(f'最終資金: {cerebro.broker.getvalue():.2f}')

# 繪製圖表並保存到文件
fig = cerebro.plot()[0][0]  # 獲取圖表 figure
fig.savefig('backtest_result.png')  # 保存圖表為 PNG 文件