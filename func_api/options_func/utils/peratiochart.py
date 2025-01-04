import yfinance as yf

def peratio_chart(stock_code):
    stock = yf.Ticker(f"{stock_code}.TW")
    hist = stock.history(period="10y")
    latest_price = hist['Close'].iloc[-1]
    latest_price = round(latest_price, 2)

    try:
        pe_ratio = stock.info['trailingPE']
        latest_eps = latest_price/pe_ratio
        pe_cheap = latest_eps * 10   # 10倍本益比
        pe_fair = latest_eps * 15    # 15倍本益比
        pe_expensive = latest_eps * 20  # 20倍本益比
        
        eps = hist['Close'] / pe_ratio
        pe_multipliers = [27, 24.6, 22.2, 19.8, 17.4, 15]
        pe_lines = {m: (eps * m).tolist() for m in pe_multipliers}
        dates = hist.index.strftime('%Y-%m-%d').tolist()
            
        # 準備 K 棒圖數據
        candlestick_data = []
        for i, row in hist.iterrows():
            try:
                timestamp = int(i.timestamp() * 1000)
                candlestick_data.append([
                    timestamp,
                    float(row['Open']), 
                    float(row['High']),
                    float(row['Low']),
                    float(row['Close'])
                ])
            except Exception as e:
                print(f"處理資料時發生錯誤: {e}")
                print(f"問題資料: timestamp={i}, row={row}")
                continue
            # print(candlestick_data)\
        pricing_data = [
            {'name': '本益比法', 'cheap': pe_cheap, 'fair': pe_fair - pe_cheap, 'fair_expensive': (pe_expensive - pe_fair), 'expensive': (pe_expensive - pe_fair)* 1.5}
        ]

    except:
        pe_cheap = pe_fair = pe_expensive = 0
        dates = []
        candlestick_data = []
        pricing_data = []
        
    return latest_price, pricing_data, dates, pe_lines, candlestick_data