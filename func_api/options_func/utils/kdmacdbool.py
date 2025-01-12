import yfinance as yf
import talib
from datetime import datetime
def kdmacdbool(stock_code, start_date, end_date, fastk_period, slowk_period, slowd_period, fastperiod, slowperiod, signalperiod, timeperiod, nbdevup, nbdevdn):
    stock = yf.download(f"{stock_code}.TW", start=start_date, end=end_date)

    # 初始化指標字典
    kd = {}
    macd = {}
    bool = {}
    signals = {'kd_signals': [], 'macd_signals': [], 'bool_signals': []}

    # 計算 MACD 指標
    kd['K'], kd['D'] = talib.STOCH(stock['High'], stock['Low'], stock['Close'], fastk_period=fastk_period, slowk_period=slowk_period, slowk_matype=0, slowd_period=slowd_period, slowd_matype=0)
    macd['MACD'], macd['signal'], macd['hist'] = talib.MACD(stock['Close'], fastperiod=fastperiod, slowperiod=slowperiod, signalperiod=signalperiod)
    bool['MIDDLEBAND'], bool['UPPERBAND'], bool['LOWERBAND'] = talib.BBANDS(stock['Close'], timeperiod=timeperiod, nbdevup=nbdevup, nbdevdn=nbdevdn, matype=0)
         
    candlestick_data = []
    for idx, (i, row) in enumerate(stock.iterrows()):
        try:
            if isinstance(i, datetime):
                actual_time = i.strftime('%Y-%m-%d %H:%M:%S')
                timestamp = int(i.timestamp() * 1000)
                candlestick_data.append([timestamp, float(row['Open']), float(row['High']), float(row['Low']), float(row['Close'])])

                # 計算 KD 指標進出場訊號
                if idx > 0:
                    if kd['K'][idx] > kd['D'][idx] and kd['K'][idx-1] <= kd['D'][idx-1]:
                        signals['kd_signals'].append((timestamp, stock['Close'][idx], 'buy', actual_time))
                    elif kd['K'][idx] < kd['D'][idx] and kd['K'][idx-1] >= kd['D'][idx-1]:
                        signals['kd_signals'].append((timestamp, stock['Close'][idx], 'sell', actual_time))

                # 計算 MACD 指標進出場訊號
                if idx > 0:
                    if macd['MACD'][idx] > macd['signal'][idx] and macd['MACD'][idx-1] <= macd['signal'][idx-1]:
                        signals['macd_signals'].append((timestamp, stock['Close'][idx], 'buy', actual_time))
                    elif macd['MACD'][idx] < macd['signal'][idx] and macd['MACD'][idx-1] >= macd['signal'][idx-1]:
                        signals['macd_signals'].append((timestamp, stock['Close'][idx], 'sell', actual_time))

                # 計算布林帶進出場訊號
                if idx > 0:
                    if row['Close'] > bool['UPPERBAND'][idx] and stock['Close'][idx-1] <= bool['UPPERBAND'][idx-1]:
                        signals['bool_signals'].append((timestamp, stock['Close'][idx], 'sell', actual_time))
                    elif row['Close'] < bool['LOWERBAND'][idx] and stock['Close'][idx-1] >= bool['LOWERBAND'][idx-1]:
                        signals['bool_signals'].append((timestamp, stock['Close'][idx], 'buy', actual_time))
            else:
                raise ValueError("Index is not a datetime object")

        except Exception as e:
            print(f"處理資料時發生錯誤: {e}")
            print(f"問題資料: timestamp={i}, row={row}")
            continue
        
    return candlestick_data, kd['K'], kd['D'], macd['MACD'], macd['signal'], macd['hist'], bool['MIDDLEBAND'], bool['UPPERBAND'], bool['LOWERBAND'], signals