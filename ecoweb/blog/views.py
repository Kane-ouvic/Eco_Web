from django.shortcuts import render
from django.http import JsonResponse
import yfinance as yf
import pandas as pd
import numpy as np

from django.shortcuts import render
from django.http import JsonResponse
import yfinance as yf
import pandas as pd
import numpy as np

def calculate_strategy(request):
    if request.method == 'POST':
        stock1 = request.POST.get('stock1')
        stock2 = request.POST.get('stock2')
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')
        n_std = int(request.POST.get('n_std'))
        window_size = int(request.POST.get('window_size'))
        capital = 100000  # 假設本金為 10 萬

        # 從 Yahoo Finance 取得股票資料
        data1 = yf.download(stock1, start=start_date, end=end_date)
        data2 = yf.download(stock2, start=start_date, end=end_date)

        # 計算差值及布林帶
        spread = (data1['Close'].apply(np.log) - data2['Close'].apply(np.log))
        rolling_mean = spread.rolling(window=window_size).mean().fillna(method='bfill')
        rolling_std = spread.rolling(window=window_size).std().fillna(method='bfill')
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
        unrealized_profit = 0  # 用於追蹤未實現損益的變化
        profit_and_loss = []  # 儲存每個時間點的未實現損益

        for i in range(len(spread)):
            if not open_position:
                # 開倉條件：spread 超過上線或低於下線
                profit_and_loss.append(unrealized_profit)  # 進場前保持未實現損益不變
                if spread.iloc[i] > upper_band.iloc[i] and hold_days == 0:  # 確保持倉天數為0時才能開倉
                    # 賣出 AAPL，買入 GLD
                    aapl_shares = capital / data1['Close'].iloc[i]
                    gld_shares = capital / data2['Close'].iloc[i]
                    signals.append({
                        'date': data1.index[i].strftime('%Y-%m-%d'),
                        'type': 'OPEN',
                        'action_aapl': 'SELL',
                        'price_aapl': data1['Close'].iloc[i],
                        'action_gld': 'BUY',
                        'price_gld': data2['Close'].iloc[i],
                        'aapl_shares': aapl_shares,
                        'gld_shares': gld_shares
                    })
                    open_position = True
                    hold_days = 1  # 開倉後開始計算持倉天數
                elif spread.iloc[i] < lower_band.iloc[i] and hold_days == 0:
                    # 買入 AAPL，賣出 GLD
                    aapl_shares = capital / data1['Close'].iloc[i]
                    gld_shares = capital / data2['Close'].iloc[i]
                    signals.append({
                        'date': data1.index[i].strftime('%Y-%m-%d'),
                        'type': 'OPEN',
                        'action_aapl': 'BUY',
                        'price_aapl': data1['Close'].iloc[i],
                        'action_gld': 'SELL',
                        'price_gld': data2['Close'].iloc[i],
                        'aapl_shares': aapl_shares,
                        'gld_shares': gld_shares
                    })
                    open_position = True
                    hold_days = 1
            else:
                # 增加最低持倉天數，避免每天都進出場
                hold_days += 1
                # 計算持倉期間的未實現損益
                unrealized_profit = (aapl_shares * data1['Close'].iloc[i]) - (gld_shares * data2['Close'].iloc[i])
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
                        'gld_shares': gld_shares
                    })
                    open_position = False
                    hold_days = 0  # 平倉後持倉天數重置
                elif spread.iloc[i] > rolling_mean.iloc[i]:
                    signals.append({
                        'date': data1.index[i].strftime('%Y-%m-%d'),
                        'type': 'CLOSE',
                        'action_aapl': 'SELL',
                        'price_aapl': data1['Close'].iloc[i],
                        'action_gld': 'BUY',
                        'price_gld': data2['Close'].iloc[i],
                        'aapl_shares': aapl_shares,
                        'gld_shares': gld_shares
                    })
                    open_position = False
                    hold_days = 0

        # 準備資料以傳送到前端進行繪圖
        context = {
            'stock1': stock1,
            'stock2': stock2,
            'start_date': start_date,
            'end_date': end_date,
            'n_std': n_std,
            'window_size': window_size,
            'dates': timestamps,
            'stock1_prices': list(data1['Close'].fillna(0)),
            'stock2_prices': list(data2['Close'].fillna(0)),
            'spread': list(spread.fillna(0)),
            'rolling_mean': list(rolling_mean),
            'upper_band': list(upper_band),
            'lower_band': list(lower_band),
            'signals': signals,
            'profit_and_loss': profit_and_loss  # 加入未實現損益
        }

        return JsonResponse(context)

    return render(request, 'blog/post_list.html')





def test(request):
    print("hi")
    # return render(request, 'blog')
    return render(request, 'blog/post_list.html')
    