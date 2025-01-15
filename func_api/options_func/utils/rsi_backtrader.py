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

    def __init__(self, short_rsi=None, long_rsi=None, rsi_upper=None, rsi_lower=None, stake=None):
        # 使用提供的參數或默認值
        self.params.short_period = short_rsi if short_rsi is not None else self.params.short_period
        self.params.long_period = long_rsi if long_rsi is not None else self.params.long_period
        self.params.rsi_upper = rsi_upper if rsi_upper is not None else self.params.rsi_upper
        self.params.rsi_lower = rsi_lower if rsi_lower is not None else self.params.rsi_lower
        self.params.stake = stake if stake is not None else self.params.stake

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

def rsi_backtrader(stock_symbol, start_date, end_date, short_rsi, long_rsi, rsi_upper, rsi_lower, stake, initial_cash, commission):
    # 設定 Cerebro 回測環境
    cerebro = bt.Cerebro()

    # 加入策略
    cerebro.addstrategy(RSICrossStrategy, short_rsi=short_rsi, long_rsi=long_rsi, rsi_upper=rsi_upper, rsi_lower=rsi_lower, stake=stake)

    # 讀取股票數據
    data = bt.feeds.PandasData(dataname=yf.download(stock_symbol, start_date, end_date))

    # 將數據加到 Cerebro
    cerebro.adddata(data)

    # 設定初始資金
    cerebro.broker.set_cash(initial_cash)

    # 設定手續費
    cerebro.broker.setcommission(commission=commission)

    # 執行回測前查看初始資金
    # print(f'初始資金: {cerebro.broker.getvalue():.2f}')

    # 開始回測
    cerebro.run()

    # 執行回測後查看最終資金
    # print(f'最終資金: {cerebro.broker.getvalue():.2f}')

    # 繪製圖表並保存到文件
    fig = cerebro.plot()[0][0]  # 獲取圖表 figure
    fig.savefig('./backtest_result.png')  # 保存圖表為 PNG 文件
    return fig
