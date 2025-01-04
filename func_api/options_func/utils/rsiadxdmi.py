import yfinance as yf
import talib

def rsiadxdmi(stock_code, start_date, end_date):
    stock = yf.download(f"{stock_code}.TW", start=start_date, end=end_date)
        
    rsi = talib.RSI(stock['Close'], timeperiod=14)
    adx = talib.ADX(stock['High'], stock['Low'], stock['Close'], timeperiod=14)
    plus_di = talib.PLUS_DI(stock['High'], stock['Low'], stock['Close'], timeperiod=14)
    minus_di = talib.MINUS_DI(stock['High'], stock['Low'], stock['Close'], timeperiod=14)
    candlestick_data = []
    for i, row in stock.iterrows():
        try:
            timestamp = int(i.timestamp() * 1000)
            candlestick_data.append([timestamp, float(row['Open']), float(row['High']), float(row['Low']), float(row['Close'])])
        except Exception as e:
            print(f"處理資料時發生錯誤: {e}")
            print(f"問題資料: timestamp={i}, row={row}")
            continue
    
    return candlestick_data, rsi, adx, plus_di, minus_di