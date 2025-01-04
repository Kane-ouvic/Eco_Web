
import yfinance as yf

def stock_pricing(stock_code, year):
    # 使用yfinance抓取股票資料
    stock = yf.Ticker(f"{stock_code}.TW")
        
    # 取得歷史資料
    hist = stock.history(period=f"{year}y")

    # 取得最新價格
    latest_price = hist['Close'][-1] 
    latest_price = round(latest_price, 2)
        
    # 計算股利法
    try:
        dividends = stock.dividends
        avg_dividend = dividends.mean()
        div_cheap = avg_dividend * 15
        div_fair = avg_dividend * 20
        div_expensive = avg_dividend * 30
    except:
        div_cheap = div_fair = div_expensive = 0
            
    high = hist['High'].max()
    low = hist['Low'].min()
    hl_cheap = low
    hl_fair = (hist['High'].mean() + hist['Low'].mean())/2
    hl_expensive = high
        
    # 計算本淨比法
    try:
        bps = stock.info.get('bookValue')  # yfinance 提供最新每股淨值
        pb_ratio = stock.info['priceToBook']
        book_value = latest_price/pb_ratio
            
        highest_pbr = (hist['High'] / bps).mean()  # 平均最高 PBR
        lowest_pbr = (hist['Low'] / bps).mean()   # 平均最低 PBR
        average_pbr = (hist['Close'] / bps).mean()  # 平均 PBR
            
            
        pb_cheap = book_value * 0.8  # 0.8倍淨值
        pb_fair = book_value * 1.5   # 1.5倍淨值
        pb_expensive = book_value * 2.2  # 2.2倍淨值
        
    except:
        pb_cheap = pb_fair = pb_expensive = 0
            
    # 計算本益比法
    try:
        pe_ratio = stock.info['trailingPE']
        eps = latest_price/pe_ratio
        pe_cheap = eps * 10   # 10倍本益比
        pe_fair = eps * 15    # 15倍本益比
        pe_expensive = eps * 20  # 20倍本益比
    except:
        pe_cheap = pe_fair = pe_expensive = 0
            
    div_total = div_expensive + (div_expensive - div_fair)*1.5
    hl_total = hl_expensive + (hl_expensive - hl_fair)*1.5
    pb_total = pb_expensive + (pb_expensive - pb_fair)*1.5
    pe_total = pe_expensive + (pe_expensive - pe_fair)*1.5
        
    max_total = max(div_total, hl_total, pb_total, pe_total)
        
    residual_div = max_total - div_total
    residual_hl = max_total - hl_total
    residual_pb = max_total - pb_total
    residual_pe = max_total - pe_total
        
        
    pricing_data = [
        {'name': '股利法', 'cheap': div_cheap, 'fair': div_fair - div_cheap,'fair_expensive': (div_expensive - div_fair), 'expensive': (div_expensive - div_fair)*1.5 + residual_div },
        {'name': '高低價法', 'cheap': hl_cheap, 'fair': hl_fair - hl_cheap, 'fair_expensive': (hl_expensive - hl_fair), 'expensive': (hl_expensive - hl_fair)*1.5 + residual_hl }, 
        {'name': '本淨比法', 'cheap': pb_cheap, 'fair': pb_fair - pb_cheap, 'fair_expensive': (pb_expensive - pb_fair), 'expensive': (pb_expensive - pb_fair)*1.5 + residual_pb },
        {'name': '本益比法', 'cheap': pe_cheap, 'fair': pe_fair - pe_cheap, 'fair_expensive': (pe_expensive - pe_fair), 'expensive': (pe_expensive - pe_fair)*1.5 + residual_pe }
    ]
        
    return latest_price, pricing_data