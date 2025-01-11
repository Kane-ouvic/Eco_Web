import yfinance as yf
import talib

def kdmacdbool(stock_code, start_date, end_date, fastk_period, slowk_period, slowd_period, fastperiod, slowperiod, signalperiod, timeperiod, nbdevup, nbdevdn):
    stock = yf.download(f"{stock_code}.TW", start=start_date, end=end_date)

    # print(stock)
        
    # 初始化 macd 字典
    kd = {}
    macd = {}
    bool = {}
    # 計算 MACD 指標
    kd['K'], kd['D'] = talib.STOCH(stock['High'], stock['Low'], stock['Close'], fastk_period=fastk_period, slowk_period=slowk_period, slowk_matype=0, slowd_period=slowd_period, slowd_matype=0)
    macd['MACD'], macd['signal'], macd['hist'] = talib.MACD(stock['Close'], fastperiod=fastperiod, slowperiod=slowperiod, signalperiod=signalperiod)
    bool['MIDDLEBAND'], bool['UPPERBAND'], bool['LOWERBAND'] = talib.BBANDS(stock['Close'], timeperiod=timeperiod, nbdevup=nbdevup, nbdevdn=nbdevdn, matype=0)
         
        
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