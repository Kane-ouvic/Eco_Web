import yfinance as yf
import talib
import numpy as np

def ceilingfloor(stock_code, start_date, ma_length, ma_type, method):

        
    stock = yf.download(f"{stock_code}.TW", start=start_date)
        
    if ma_type == 'sma':
        ma = talib.SMA(stock['Close'], timeperiod=ma_length)
    elif ma_type == 'wma':
        ma = talib.WMA(stock['Close'], timeperiod=ma_length)
        
    candlestick_data = []
    for i, row in stock.iterrows():
        try:
            timestamp = int(i.timestamp() * 1000)
            candlestick_data.append([timestamp, float(row['Open']), float(row['High']), float(row['Low']), float(row['Close'])])
        except Exception as e:
            print(f"處理資料時發生錯誤: {e}")
            print(f"問題資料: timestamp={i}, row={row}")
            continue

    # 計算天花板地板線
    if method == 'method1':
        # 計算乖離率 bias
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
        
    elif method == 'method2':
            
        bias = (stock['Close'] - ma) / ma
        bias_ratio = bias.values
        positive_bias_ratio = bias_ratio[bias_ratio > 0]
        negative_bias_ratio = bias_ratio[bias_ratio < 0]
            
        neg_bias_mean = np.mean(negative_bias_ratio)
        pos_bias_mean = np.mean(positive_bias_ratio)
            
        neg_bias_std = np.std(negative_bias_ratio)
        pos_bias_std = np.std(positive_bias_ratio)
            
        ceiling_price = ma * (1 + pos_bias_mean +  2* pos_bias_std)
        floor_price = ma * (1 - neg_bias_mean - 2 * neg_bias_std)
        
    elif method == 'method3':
        # 計算乖離率 bias
        bias = (stock['Close'] - ma) / ma
        bias_ratio = bias.values
        positive_bias_ratio = bias_ratio[bias_ratio > 0]
        negative_bias_ratio = bias_ratio[bias_ratio < 0]
        print(positive_bias_ratio.size)
        print(negative_bias_ratio.size)
         # 排序並取得95%分位的正乖離率和5%分位的負乖離率
        if positive_bias_ratio.size > 0 and negative_bias_ratio.size > 0:
            ceiling_ratio = np.percentile(positive_bias_ratio, 99)
            floor_ratio = np.percentile(negative_bias_ratio, 1)
                
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