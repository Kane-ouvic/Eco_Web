from django.shortcuts import render
from django.http import JsonResponse
import yfinance as yf
import pandas as pd
import numpy as np
import pandas_ta as ta

import json
from datetime import datetime, date
import logging
import re
from django.core.serializers.json import DjangoJSONEncoder

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
        unrealized_profit = capital  # 用於追蹤未實現損益的變化
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
                        'gld_shares': gld_shares,
                        'profit_loss': unrealized_profit
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
                        'gld_shares': gld_shares,
                        'profit_loss': unrealized_profit
                    })
                    open_position = True
                    hold_days = 1
            else:
                # 增加最低持倉天數，避免每天都進出場
                hold_days += 1
                # 計算持倉期間的未實現損益
                unrealized_profit = unrealized_profit + (aapl_shares * data1['Close'].iloc[i]) - (gld_shares * data2['Close'].iloc[i])
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
                        'gld_shares': gld_shares,
                        'profit_loss': unrealized_profit
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


def rsi_backtest(request):
    logging.info("rsi_backtest 函數被調用")
    if request.method == 'POST':
        logging.info("收到 POST 請求")
        try:
            # 從請求中獲取參數
            etf_symbol = request.POST.get('etf_symbol', '0050.TW')
            start_date = request.POST.get('start_date', '2013-01-01')
            end_date = request.POST.get('end_date', '2022-05-01')
            short_rsi = int(request.POST.get('short_rsi', 120))
            long_rsi = int(request.POST.get('long_rsi', 150))
            exit_threshold = float(request.POST.get('exit_threshold', 0.999))

            logging.info(f"參數: etf_symbol={etf_symbol}, start_date={start_date}, end_date={end_date}, short_rsi={short_rsi}, long_rsi={long_rsi}, exit_threshold={exit_threshold}")

            # 獲取數據
            data = yf.download(etf_symbol, start=start_date, end=end_date)
            logging.info(f"下載的數據大小: {len(data)}")
            
            if data.empty:
                raise ValueError("無法獲取股票數據")

            # 計算 RSI
            data['rsi1'] = ta.rsi(data['Close'], length=short_rsi)
            data['rsi2'] = ta.rsi(data['Close'], length=long_rsi)
            
            if 'rsi1' not in data.columns or 'rsi2' not in data.columns:
                raise ValueError("RSI 計算失敗")

            logging.info(f"RSI 計算完成，數據樣本: {data[['Close', 'rsi1', 'rsi2']].head().to_dict()}")

            # 初始化變量
            position = 0
            trades = []
            equity_curve = [1.0]
            max_equity = 1.0
            drawdowns = [0.0]
            hold_days = 0
            profitable_hold_days = 0
            loss_hold_days = 0
            profitable_trades = 0
            loss_trades = 0
            current_consecutive_loss = 0
            max_consecutive_loss = 0
            current_consecutive_profit = 0
            max_consecutive_profit = 0
            current_drawdown = 0
            max_drawdown = 0

            # 執行回測
            for i in range(1, len(data)):
                c_time = data.index[i-1]
                c_close = data.loc[c_time, 'Close']
                c_rsi1 = data.loc[c_time, 'rsi1']
                c_rsi2 = data.loc[c_time, 'rsi2']
                n_time = data.index[i]
                n_open = data.loc[n_time, 'Open']

                if position == 1:
                    hold_days += 1

                if position == 0 and c_rsi1 > c_rsi2:
                    # 買入
                    position = 1
                    entry_price = n_open
                    entry_time = n_time
                    hold_days = 0
                elif position == 1 and c_rsi1 < c_rsi2 * exit_threshold:
                    # 賣出
                    exit_price = n_open
                    exit_time = n_time
                    returns = (exit_price / entry_price) - 1
                    trades.append({
                        'entry_time': entry_time.strftime('%Y-%m-%d'),
                        'entry_price': float(entry_price),
                        'exit_time': exit_time.strftime('%Y-%m-%d'),
                        'exit_price': float(exit_price),
                        'returns': float(returns),
                        'hold_days': hold_days
                    })
                    equity_curve.append(equity_curve[-1] * (1 + returns))
                    
                    # 更新最大資金回落和最大連續獲利
                    if equity_curve[-1] > max_equity:
                        max_equity = equity_curve[-1]
                        current_drawdown = 0
                        current_consecutive_profit += returns
                        max_consecutive_profit = max(max_consecutive_profit, current_consecutive_profit)
                    else:
                        current_drawdown = (max_equity - equity_curve[-1]) / max_equity
                        max_drawdown = max(max_drawdown, current_drawdown)
                        current_consecutive_profit = 0
                    
                    drawdowns.append(current_drawdown)
                    
                    if returns > 0:
                        profitable_hold_days += hold_days
                        profitable_trades += 1
                        current_consecutive_loss = 0
                    else:
                        loss_hold_days += hold_days
                        loss_trades += 1
                        current_consecutive_loss -= returns  # 累加負收益
                        max_consecutive_loss = max(max_consecutive_loss, current_consecutive_loss)
                    
                    position = 0
                    hold_days = 0

            # 處理未平倉部位
            if position == 1:
                # 在最後一天平倉
                exit_price = data['Close'].iloc[-1]
                exit_time = data.index[-1]
                returns = (exit_price / entry_price) - 1
                trades.append({
                    'entry_time': entry_time.strftime('%Y-%m-%d'),
                    'entry_price': float(entry_price),
                    'exit_time': exit_time.strftime('%Y-%m-%d'),
                    'exit_price': float(exit_price),
                    'returns': float(returns),
                    'hold_days': hold_days
                })
                equity_curve.append(equity_curve[-1] * (1 + returns))
                
                if equity_curve[-1] > max_equity:
                    max_equity = equity_curve[-1]
                    current_drawdown = 0
                    current_consecutive_profit += returns
                    max_consecutive_profit = max(max_consecutive_profit, current_consecutive_profit)
                else:
                    current_drawdown = (max_equity - equity_curve[-1]) / max_equity
                    max_drawdown = max(max_drawdown, current_drawdown)
                    current_consecutive_profit = 0
                
                drawdowns.append(current_drawdown)
                
                if returns > 0:
                    profitable_hold_days += hold_days
                    profitable_trades += 1
                    current_consecutive_loss = 0
                else:
                    loss_hold_days += hold_days
                    loss_trades += 1
                    current_consecutive_loss -= returns
                    max_consecutive_loss = max(max_consecutive_loss, current_consecutive_loss)
                
                position = 0

            # 計算績效指標
            total_return = (equity_curve[-1] - 1) * 100
            avg_return = np.mean([t['returns'] for t in trades]) * 100
            win_rate = (profitable_trades / len(trades)) * 100 if trades else 0
            avg_profit = np.mean([t['returns'] for t in trades if t['returns'] > 0]) * 100 if any(t['returns'] > 0 for t in trades) else 0
            avg_loss = np.mean([t['returns'] for t in trades if t['returns'] < 0]) * 100 if any(t['returns'] < 0 for t in trades) else 0
            profit_loss_ratio = abs(avg_profit / avg_loss) if avg_loss != 0 else float('inf')
            expectancy = (win_rate / 100 * avg_profit) + ((1 - win_rate / 100) * avg_loss)
            max_drawdown = max_drawdown * 100  # 轉換為百分比
            max_consecutive_loss = max_consecutive_loss * 100  # 轉換為百分比
            max_consecutive_profit = max_consecutive_profit * 100  # 轉換為百分比

            # 準備回傳的數據
            result = {
                'trades': trades,
                'equity_curve': equity_curve,
                'drawdowns': drawdowns,
                'dates': [d.strftime('%Y-%m-%d') for d in data.index],
                'price_data': data['Close'].tolist(),
                'rsi1': data['rsi1'].tolist(),
                'rsi2': data['rsi2'].tolist(),
                'performance': {
                    'total_return': round(total_return, 2),
                    'avg_return': round(avg_return, 2),
                    'win_rate': round(win_rate, 2),
                    'avg_profit': round(avg_profit, 2),
                    'avg_loss': round(avg_loss, 2),
                    'profit_loss_ratio': round(profit_loss_ratio, 2),
                    'expectancy': round(expectancy, 2),
                    # 'max_drawdown': round(max_drawdown, 2),
                    'profitable_hold_days': profitable_hold_days,
                    'loss_hold_days': loss_hold_days,
                    'max_consecutive_loss': round(max_consecutive_loss, 2),
                    'max_consecutive_profit': round(max_consecutive_profit, 2)
                }
            }
            
            print(result['performance']['profitable_hold_days'])
            print(result['performance']['loss_hold_days'])
            print(result['performance']['max_consecutive_loss'])
            print(result['performance']['max_consecutive_profit'])

            # 處理 NaN 和 Infinity
            result['equity_curve'] = np.nan_to_num(result['equity_curve']).tolist()
            result['drawdowns'] = np.nan_to_num(result['drawdowns']).tolist()
            result['rsi1'] = np.nan_to_num(result['rsi1']).tolist()
            result['rsi2'] = np.nan_to_num(result['rsi2']).tolist()
            result['price_data'] = np.nan_to_num(result['price_data']).tolist()

            # 清理數據以確保可序列化
            result = clean_for_json(result)

            # 在返回結果之前記錄一些樣本數據
            logging.info(f"trades 樣本: {trades[:5]}")
            logging.info(f"equity_curve 樣本: {equity_curve[:5]}")
            logging.info(f"drawdowns 樣本: {drawdowns[:5]}")
            logging.info(f"performance: {result['performance']}")

            # 在返回之前記錄結果
            logging.info(f"準備返回的數據: {json.dumps(result, cls=DjangoJSONEncoder)[:1000]}...")  # 只記錄前1000個字符

            return JsonResponse(result, encoder=DjangoJSONEncoder, safe=False)
        except ValueError as ve:
            logging.error(f"數據處理錯誤: {str(ve)}")
            return JsonResponse({'error': str(ve)}, status=400)
        except Exception as e:
            logging.error(f"回測過程中發生錯誤: {str(e)}", exc_info=True)
            return JsonResponse({'error': str(e)}, status=500)

    return render(request, 'blog/rsi2_backtest.html')

def clean_for_json(obj):
    if isinstance(obj, (np.int64, np.int32, np.int16, np.int8)):
        return int(obj)
    elif isinstance(obj, (np.float64, np.float32, np.float16)):
        return float(obj)
    elif isinstance(obj, (np.ndarray, list, tuple)):
        return [clean_for_json(item) for item in obj]
    elif isinstance(obj, (datetime, date)):
        return obj.isoformat()
    elif isinstance(obj, dict):
        return {key: clean_for_json(value) for key, value in obj.items()}
    elif obj is None:
        return None
    else:
        return obj

def test(request):
    print("hi")
    # return render(request, 'blog')
    return render(request, 'blog/test1.html')
