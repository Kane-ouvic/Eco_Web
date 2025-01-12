import os
import sys
import psycopg2
import pandas as pd
from datetime import datetime
from dotenv import load_dotenv

# 添加項目根目錄到 Python 路徑
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
sys.path.append(os.path.join(project_root, 'func_api', 'options_func'))

from utils.ceilingfloor import ceilingfloor
from utils.kdmacdbool import kdmacdbool
from utils.rsiadxdmi import rsiadxdmi
from utils.kline import kline

file_path = "/home/ouvic/Eco_Web/user_tracker_data2"

# 載入 .env 文件
load_dotenv(os.path.join(project_root, '.env'))

from mail import MailHandler

def get_db_connection():
    return psycopg2.connect(
        dbname=os.getenv('DB_NAME'),
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASSWORD'),
        host=os.getenv('DB_HOST'),
        port=os.getenv('DB_PORT')
    )

def get_user_email(username):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT email FROM auth_user WHERE username = %s", (username,))
    email = cursor.fetchone()[0]
    cursor.close()
    conn.close()
    return email

def update_enddate_in_entry_exit_track(new_enddate):
    conn = get_db_connection()
    cursor = conn.cursor()

    # 更新 entry_exit_track 表中每筆資料的 endtime
    cursor.execute("""
        UPDATE entry_exit_track
        SET end_date = %s
    """, (new_enddate,))
    
    conn.commit()
    print(f"所有資料的 enddate 已更新至 {new_enddate}")
    
    # 打印 entry_exit_track 所有資料和對應的使用者名稱
    cursor.execute("""
        SELECT e.*, u.username
        FROM entry_exit_track e
        JOIN auth_user u ON e.user_id = u.id
    """)
    
    records = cursor.fetchall()
    
    # 建立字典來存儲每個使用者的 signals
    user_signals = {}
    
    for record in records:
        entry = {
            'id': record[0],
            'user_id': record[1],
            'username': record[-1],
            'stock_code': record[2],
            'start_date': record[3],
            'end_date': record[4],
            'ma_length': record[5],
            'ma_type': record[6],
            'method': record[7],
            'fastk_period': record[8],
            'slowk_period': record[9],
            'slowd_period': record[10],
            'fastperiod': record[11],
            'slowperiod': record[12],
            'signalperiod': record[13],
            'timeperiod': record[14],
            'nbdevup': record[15],
            'nbdevdn': record[16],
            'rsi_period': record[17],
            'adx_period': record[18],
            'track_date': record[19],
        }
        
        ma, ceiling_price, floor_price, candlestick_data, signals1 = ceilingfloor(
            entry['stock_code'], entry['start_date'], entry['end_date'], 
            int(entry['ma_length']), entry['ma_type'], entry['method']
        )
        kd = {}
        macd = {}
        bool = {}
        candlestick_data, kd['K'], kd['D'], macd['MACD'], macd['signal'], macd['hist'], bool['MIDDLEBAND'], bool['UPPERBAND'], bool['LOWERBAND'], signals2 = kdmacdbool(
            entry['stock_code'], entry['start_date'], entry['end_date'], 
            int(entry['fastk_period']), int(entry['slowk_period']), int(entry['slowd_period']), 
            int(entry['fastperiod']), int(entry['slowperiod']), int(entry['signalperiod']), 
            int(entry['timeperiod']), int(entry['nbdevup']), int(entry['nbdevdn'])
        )
        candlestick_data, rsi, adx, plus_di, minus_di, signals3 = rsiadxdmi(
            entry['stock_code'], entry['start_date'], entry['end_date'], 
            int(entry['rsi_period']), int(entry['adx_period'])
        )
        candlestick_data, kline_patterns = kline(
            entry['stock_code'], entry['start_date'], entry['end_date']
        )
        # 將 signals1、stock_code 和 track_date 存入對應的使用者字典中
        username = entry['username']
        if username not in user_signals:
            user_signals[username] = []
        
        from datetime import timedelta

        adjusted_enddate = (datetime.strptime(new_enddate, '%Y-%m-%d') - timedelta(days=1)).strftime('%Y-%m-%d')

        user_signals[username].append({
            'stock_code': entry['stock_code'],
            'track_date': entry['track_date'],
            'ceilingfloor_signal': signals1[-1][2] if datetime.fromtimestamp(signals1[-1][0] / 1000).strftime('%Y-%m-%d') == adjusted_enddate else "No signal",
            'kd_signal': signals2['kd_signals'][-1][2] if datetime.fromtimestamp(signals2['kd_signals'][-1][0] / 1000).strftime('%Y-%m-%d') == adjusted_enddate else "No signal",
            'macd_signal': signals2['macd_signals'][-1][2] if datetime.fromtimestamp(signals2['macd_signals'][-1][0] / 1000).strftime('%Y-%m-%d') == adjusted_enddate else "No signal",
            'bool_signal': signals2['bool_signals'][-1][2] if datetime.fromtimestamp(signals2['bool_signals'][-1][0] / 1000).strftime('%Y-%m-%d') == adjusted_enddate else "No signal",
            'rsi_signal': signals3['rsi_signals'][-1][2] if datetime.fromtimestamp(signals3['rsi_signals'][-1][0] / 1000).strftime('%Y-%m-%d') == adjusted_enddate else "No signal",
            'adx_signal': signals3['adx_signals'][-1][2] if datetime.fromtimestamp(signals3['adx_signals'][-1][0] / 1000).strftime('%Y-%m-%d') == adjusted_enddate else "No signal",
            'kline_pattern': kline_patterns[-1][2] if datetime.fromtimestamp(kline_patterns[-1][0] / 1000).strftime('%Y-%m-%d') == adjusted_enddate else "No signal"
        })
        
        print(datetime.fromtimestamp(signals1[-1][0] / 1000).strftime('%Y-%m-%d'))
        print(datetime.fromtimestamp(signals2['bool_signals'][-1][0] / 1000).strftime('%Y-%m-%d'))
        print(adjusted_enddate)
        print(new_enddate)
    # 打印每個使用者的 signals
    # for username, signals in user_signals.items():
    #     print(f"使用者 {username} 的 signals: {signals}")
    
    # 整理每個使用者的 signals 並生成報告
    mail_handler = MailHandler()
    current_time = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    for username, signals in user_signals.items():
        print(f"使用者 {username} 的 signals: {signals}")
        df = pd.DataFrame(signals)
        
        # 在將 DataFrame 寫入 Excel 之前，移除時區信息
        df['track_date'] = df['track_date'].dt.tz_localize(None)
        
        # 生成 Excel 文件
        file_name = os.path.join(file_path, f"user_signals_{username}_{current_time}.xlsx")
        df.to_excel(file_name, index=False)
        
        # 發送郵件
        to_address = get_user_email(username)  # 根據使用者名稱獲取電子郵件地址
        status = mail_handler.send(to_address, file_name)
        
        if status:
            print(f"報告已成功發送至 {to_address}")
        else:
            print(f"發送報告至 {to_address} 時出現錯誤")

    cursor.close()
    conn.close()

# 指定新的結束時間
new_enddate = '2024-12-31'
update_enddate_in_entry_exit_track(new_enddate)