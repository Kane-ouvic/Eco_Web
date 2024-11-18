import yfinance as yf
import numpy as np


def distance_method(stock1, stock2, start_date, end_date, n_std, window_size):
        capital = 100000  # 假設本金為 10 萬

        # 從 Yahoo Finance 取得股票資料
        data1 = yf.download(stock1, start=start_date, end=end_date)
        data2 = yf.download(stock2, start=start_date, end=end_date)

        # 計算差值及布林帶
        spread = (data1['Close'].apply(np.log) - data2['Close'].apply(np.log))
        rolling_mean = spread.rolling(window=window_size).mean()
        rolling_std = spread.rolling(window=window_size).std()
        upper_band = rolling_mean + (n_std * rolling_std)
        lower_band = rolling_mean - (n_std * rolling_std)
        

        # 將日期轉換成 UNIX 時間戳記（毫秒）
        timestamps = list(map(int, data1.index.view(np.int64) // 10**6))

        # 儲存交易訊號
        signals = []
        open_position = False  # 用於追蹤是否有持倉
        aapl_shares = 0
        gld_shares = 0
        hold_days = 0  # 增加持倉天數追蹤
        position_type = None
        entry_capital = 0
        unrealized_profit = 0
        profit_and_loss = []

        for i in range(len(spread)):
            if not open_position:
                profit_and_loss.append(unrealized_profit)
                if spread.iloc[i] > upper_band.iloc[i]  and hold_days == 0:
                    # 賣出 AAPL，買入 GLD
                    aapl_shares = capital / (2 * data1['Close'].iloc[i])
                    gld_shares = capital / (2 * data2['Close'].iloc[i])
                    position_type = 'short_aapl_long_gld'
                    signals.append({
                        'date': data1.index[i].strftime('%Y-%m-%d'),
                        'type': 'OPEN',
                        'action_aapl': 'SELL',
                        'price_aapl': data1['Close'].iloc[i],
                        'action_gld': 'BUY',
                        'price_gld': data2['Close'].iloc[i],
                        'aapl_shares': aapl_shares,
                        'gld_shares': gld_shares,
                        'profit_loss': unrealized_profit
                    })
                    open_position = True
                    hold_days = 1
                elif spread.iloc[i] < lower_band.iloc[i]  and hold_days == 0:
                    # 買入 AAPL，賣出 GLD
                    aapl_shares = capital / (2 * data1['Close'].iloc[i])
                    gld_shares = capital / (2 * data2['Close'].iloc[i])
                    position_type = 'long_aapl_short_gld'
                    signals.append({
                        'date': data1.index[i].strftime('%Y-%m-%d'),
                        'type': 'OPEN',
                        'action_aapl': 'BUY',
                        'price_aapl': data1['Close'].iloc[i],
                        'action_gld': 'SELL',
                        'price_gld': data2['Close'].iloc[i],
                        'aapl_shares': aapl_shares,
                        'gld_shares': gld_shares,
                        'profit_loss': unrealized_profit
                    })
                    open_position = True
                    hold_days = 1
            else:
                hold_days += 1
                # 計算持倉期間的未實現損益
                if position_type == 'long_aapl_short_gld':
                    current_value = (aapl_shares * data1['Close'].iloc[i]) - (gld_shares * data2['Close'].iloc[i])
                else:  # 'short_aapl_long_gld'
                    current_value = (gld_shares * data2['Close'].iloc[i]) - (aapl_shares * data1['Close'].iloc[i])
                # current_value = (aapl_shares * data1['Close'].iloc[i]) - (gld_shares * data2['Close'].iloc[i])
                unrealized_profit = current_value
                profit_and_loss.append(unrealized_profit)

                if hold_days < 50:  # 假設最少持倉 10 天
                    continue

                # 平倉條件：spread 回歸到中線
                if spread.iloc[i] < rolling_mean.iloc[i]:
                    signals.append({
                        'date': data1.index[i].strftime('%Y-%m-%d'),
                        'type': 'CLOSE',
                        'action_aapl': 'BUY',
                        'price_aapl': data1['Close'].iloc[i],
                        'action_gld': 'SELL',
                        'price_gld': data2['Close'].iloc[i],
                        'aapl_shares': aapl_shares,
                        'gld_shares': gld_shares,
                        'profit_loss': unrealized_profit
                    })
                    realized_profit = unrealized_profit
                    capital += realized_profit
                    # unrealized_profit = 0
                    open_position = False
                    hold_days = 0
                    position_type = None
                elif spread.iloc[i] > rolling_mean.iloc[i]:
                    signals.append({
                        'date': data1.index[i].strftime('%Y-%m-%d'),
                        'type': 'CLOSE',
                        'action_aapl': 'SELL',
                        'price_aapl': data1['Close'].iloc[i],
                        'action_gld': 'BUY',
                        'price_gld': data2['Close'].iloc[i],
                        'aapl_shares': aapl_shares,
                        'gld_shares': gld_shares,
                        'profit_loss': unrealized_profit
                    })
                    realized_profit = unrealized_profit
                    capital += realized_profit
                    # unrealized_profit = 0
                    open_position = False
                    hold_days = 0
                    position_type = None

        # 準備資料以傳送到前端進行繪圖
        context = {
            'stock1': stock1,
            'stock2': stock2,
            'start_date': start_date,
            'end_date': end_date,
            'n_std': n_std,
            'window_size': window_size,
            'dates': timestamps,
            'stock1_prices': list(data1['Close'].fillna(-2147483648)),  # 移除 fillna(0)
            'stock2_prices': list(data2['Close'].fillna(-2147483648)),  # 移除 fillna(0)
            'spread': list(spread.fillna(-2147483648)),  # 移除 fillna(0)
            'rolling_mean': list(rolling_mean.fillna(-2147483648)),  # 移除 fillna(0)
            'upper_band': list(upper_band.fillna(-2147483648)),  # 移除 fillna(0)
            'lower_band': list(lower_band.fillna(-2147483648)),  # 移除 fillna(0)
            'signals': signals,
            'profit_and_loss': profit_and_loss  # 加入未實現損益
        }
        
        return context