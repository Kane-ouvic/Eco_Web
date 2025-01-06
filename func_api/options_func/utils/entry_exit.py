import yfinance as yf
import talib
import numpy as np

def entry_exit(stock_code, start_date, end_date, strategy):

        
    stock = yf.download(f"{stock_code}.TW", start=start_date, end=end_date)
    
    if strategy == 'ceil_floor':
        # ma, ceiling_price, floor_price, candlestick_data, ceiling_signals, floor_signals = ceilingfloor(stock_code, start_date, end_date, ma_length, ma_type, method)
        ma = talib.SMA(stock['Close'], timeperiod=20)
        candlestick_data = []
        for i, row in stock.iterrows():
            try:
                timestamp = int(i.timestamp() * 1000)
                candlestick_data.append([timestamp, float(row['Open']), float(row['High']), float(row['Low']), float(row['Close'])])
            except Exception as e:
                print(f"處理資料時發生錯誤: {e}")
                print(f"問題資料: timestamp={i}, row={row}")
                continue
        
        bias = (stock['Close'] - ma) / ma
        bias_ratio = bias.values
        positive_bias_ratio = bias_ratio[bias_ratio > 0]
        negative_bias_ratio = bias_ratio[bias_ratio < 0]

        # 排序並取得95%分位的正乖離率和5%分位的負乖離率
        if positive_bias_ratio.size > 0 and negative_bias_ratio.size > 0:
            ceiling_ratio = np.percentile(positive_bias_ratio, 95)
            floor_ratio = np.percentile(negative_bias_ratio, 5)
                
            # 計算天花板地板價格
            ceiling_price = ma * (1 + ceiling_ratio)
            floor_price = ma * (1 + floor_ratio)
                
                
                
            print(f"天花板乖離率: {ceiling_ratio:.2%}")
            print(f"地板乖離率: {floor_ratio:.2%}")
        else:
            ceiling_price = floor_price = ma
            ceiling_signals = []
            floor_signals = []
            print("無法計算天花板地板線 - 資料不足")
            
         # 找出突破訊號
        ceiling_signals = []
        floor_signals = []
                    
        for i in range(len(stock)):
            timestamp = int(stock.index[i].timestamp() * 1000)
            if stock['Close'][i] > ceiling_price[i]:
                ceiling_signals.append([timestamp, stock['Close'][i], 1])  # 1代表突破天花板
            elif stock['Close'][i] < floor_price[i]:
                floor_signals.append([timestamp, stock['Close'][i], -1])  # -1代表突破地板

        
        return ma, ceiling_price, floor_price, candlestick_data, ceiling_signals, floor_signals
        
    elif strategy == 'kd':
        kd = {}
        kd['K'], kd['D'] = talib.STOCH(stock['High'], stock['Low'], stock['Close'], fastk_period=9, slowk_period=3, slowk_matype=0, slowd_period=3, slowd_matype=0)
        candlestick_data = []
        for i, row in stock.iterrows():
            try:
                timestamp = int(i.timestamp() * 1000)
                candlestick_data.append([timestamp, float(row['Open']), float(row['High']), float(row['Low']), float(row['Close'])])
            except Exception as e:
                print(f"處理資料時發生錯誤: {e}")
                print(f"問題資料: timestamp={i}, row={row}")
                continue
        return candlestick_data, kd['K'], kd['D']
    
    elif strategy == 'macd':
        macd = {}
        macd['MACD'], macd['signal'], macd['hist'] = talib.MACD(stock['Close'], fastperiod=12, slowperiod=26, signalperiod=9)
        candlestick_data = []
        for i, row in stock.iterrows():
            try:
                timestamp = int(i.timestamp() * 1000)
                candlestick_data.append([timestamp, float(row['Open']), float(row['High']), float(row['Low']), float(row['Close'])])
            except Exception as e:
                print(f"處理資料時發生錯誤: {e}")
                print(f"問題資料: timestamp={i}, row={row}")
                continue
        return candlestick_data, macd['MACD'], macd['signal'], macd['hist']
    
    elif strategy == 'booling':
        
        bool = {}
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
        print("boollllllllllllllllll")
        return candlestick_data, bool['MIDDLEBAND'], bool['UPPERBAND'], bool['LOWERBAND']
    
    
    elif strategy == 'rsi':
        
        rsi = talib.RSI(stock['Close'], timeperiod=14)
        candlestick_data = []
        for i, row in stock.iterrows():
            try:
                timestamp = int(i.timestamp() * 1000)
                candlestick_data.append([timestamp, float(row['Open']), float(row['High']), float(row['Low']), float(row['Close'])])
            except Exception as e:
                print(f"處理資料時發生錯誤: {e}")
                print(f"問題資料: timestamp={i}, row={row}")
                continue
        return candlestick_data, rsi
    
    elif strategy == 'adx_dmi':
        
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
        return candlestick_data, adx, plus_di, minus_di
        
    elif strategy == 'kline':
        pass