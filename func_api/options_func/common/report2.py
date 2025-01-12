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
    
    # 建立字典來存儲資料
    data_dict = []
    
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
        data_dict.append(entry)
        ma, ceiling_price, floor_price, candlestick_data, signals1 = ceilingfloor(
            entry['stock_code'], entry['start_date'], entry['end_date'], 
            int(entry['ma_length']), entry['ma_type'], entry['method']
        )
        print(signals1)
    
    # print(data_dict)

    cursor.close()
    conn.close()

# 指定新的結束時間
new_enddate = '2024-12-31'
update_enddate_in_entry_exit_track(new_enddate)