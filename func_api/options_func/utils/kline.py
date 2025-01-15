import yfinance as yf
import talib
from datetime import datetime

def kline(stock_code, start_date, end_date):
    stock = yf.download(f"{stock_code}.TW", start=start_date, end=end_date)

    candlestick_data = []
    kline_patterns = []
    volume_data = []
    for idx, (i, row) in enumerate(stock.iterrows()):
        try:
            if isinstance(i, datetime):
                timestamp = int(i.timestamp() * 1000)
                open_price = float(row['Open'])
                high_price = float(row['High'])
                low_price = float(row['Low'])
                close_price = float(row['Close'])
                candlestick_data.append([timestamp, open_price, high_price, low_price, close_price])
                volume_data.append([timestamp, float(row['Volume'])])

                # 簡單的K線型態判斷
                if close_price > open_price:
                    kline_patterns.append((timestamp, close_price, 'bullish', i.strftime('%Y-%m-%d %H:%M:%S')))
                elif close_price < open_price:
                    kline_patterns.append((timestamp, close_price, 'bearish', i.strftime('%Y-%m-%d %H:%M:%S')))
                else:
                    kline_patterns.append((timestamp, close_price, 'doji', i.strftime('%Y-%m-%d %H:%M:%S')))
            else:
                raise ValueError("Index is not a datetime object")

        except Exception as e:
            print(f"處理資料時發生錯誤: {e}")
            print(f"問題資料: timestamp={i}, row={row}")
            continue

    return candlestick_data, volume_data, kline_patterns