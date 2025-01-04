import yfinance as yf
import talib

def kdmacdbool(stock_code, start_date, end_date):
    stock = yf.download(f"{stock_code}.TW", start=start_date, end=end_date)

    print(stock)
        
    # 初始化 macd 字典
    kd = {}
    macd = {}
    bool = {}
    # 計算 MACD 指標
    kd['K'], kd['D'] = talib.STOCH(stock['High'], stock['Low'], stock['Close'], fastk_period=9, slowk_period=3, slowk_matype=0, slowd_period=3, slowd_matype=0)
    macd['MACD'], macd['signal'], macd['hist'] = talib.MACD(stock['Close'], fastperiod=12, slowperiod=26, signalperiod=9)
    bool['MIDDLEBAND'], bool['UPPERBAND'], bool['LOWERBAND'] = talib.BBANDS(stock['Close'], timeperiod=5, nbdevup=2, nbdevdn=2, matype=0)
         
        
    candlestick_data = []
    for i, row in stock.iterrows():
        try:
            timestamp = int(i.timestamp() * 1000)
            candlestick_data.append([timestamp, float(row['Open']), float(row['High']), float(row['Low']), float(row['Close'])])
        except Exception as e:
            print(f"處理資料時發生錯誤: {e}")
            print(f"問題資料: timestamp={i}, row={row}")
            continue
    
    return candlestick_data, kd['K'], kd['D'], macd['MACD'], macd['signal'], macd['hist'], bool['MIDDLEBAND'], bool['UPPERBAND'], bool['LOWERBAND']