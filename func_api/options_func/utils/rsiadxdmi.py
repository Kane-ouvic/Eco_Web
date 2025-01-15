import yfinance as yf
import talib
from datetime import datetime

def rsiadxdmi(stock_code, start_date, end_date, rsi_period, adx_period):
    stock = yf.download(f"{stock_code}.TW", start=start_date, end=end_date)
        
    rsi = talib.RSI(stock['Close'], timeperiod=rsi_period)
    adx = talib.ADX(stock['High'], stock['Low'], stock['Close'], timeperiod=adx_period)
    plus_di = talib.PLUS_DI(stock['High'], stock['Low'], stock['Close'], timeperiod=adx_period)
    minus_di = talib.MINUS_DI(stock['High'], stock['Low'], stock['Close'], timeperiod=adx_period)
    
    candlestick_data = []
    volume_data = []
    signals = {'rsi_signals': [], 'adx_signals': []}
    
    for idx, (i, row) in enumerate(stock.iterrows()):
        try:
            if isinstance(i, datetime):
                timestamp = int(i.timestamp() * 1000)
                candlestick_data.append([timestamp, float(row['Open']), float(row['High']), float(row['Low']), float(row['Close'])])
                volume_data.append([timestamp, float(row['Volume'])])
                # 計算 RSI 進出場訊號
                if idx > 0:
                    if rsi[idx] > 70 and rsi[idx-1] <= 70:
                        signals['rsi_signals'].append((timestamp, row['Close'], 'sell', i.strftime('%Y-%m-%d %H:%M:%S')))
                    elif rsi[idx] < 30 and rsi[idx-1] >= 30:
                        signals['rsi_signals'].append((timestamp, row['Close'], 'buy', i.strftime('%Y-%m-%d %H:%M:%S')))
                
                # 計算 ADX 進出場訊號
                if idx > 0:
                    if plus_di[idx] > minus_di[idx] and plus_di[idx-1] <= minus_di[idx-1]:
                        signals['adx_signals'].append((timestamp, row['Close'], 'buy', i.strftime('%Y-%m-%d %H:%M:%S')))
                    elif plus_di[idx] < minus_di[idx] and plus_di[idx-1] >= minus_di[idx-1]:
                        signals['adx_signals'].append((timestamp, row['Close'], 'sell', i.strftime('%Y-%m-%d %H:%M:%S')))
            else:
                raise ValueError("Index is not a datetime object")
                
        except Exception as e:
            print(f"處理資料時發生錯誤: {e}")
            print(f"問題資料: timestamp={i}, row={row}")
            continue
    
    return candlestick_data, volume_data, rsi, adx, plus_di, minus_di, signals