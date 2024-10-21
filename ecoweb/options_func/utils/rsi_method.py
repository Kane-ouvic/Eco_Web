import yfinance as yf
import pandas_ta as ta
import numpy as np
import logging
from datetime import datetime, date


def rsi_method(etf_symbol, start_date, end_date, short_rsi, long_rsi, exit_threshold):
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

        return result

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
