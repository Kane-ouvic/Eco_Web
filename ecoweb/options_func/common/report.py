import os
import sys
import psycopg2
import pandas as pd
from datetime import datetime
from dotenv import load_dotenv

# 添加項目根目錄到 Python 路徑
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
sys.path.append(project_root)

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

def generate_and_send_report():
    conn = get_db_connection()
    cursor = conn.cursor()

    # 從資料庫獲取所有使用者追蹤的標的
    cursor.execute("""
        SELECT u.id, u.username, u.email, t.method, t.stock1, t.stock2, 
               t.start_date, t.end_date, t.window_size, t.n_std, t.track_date
        FROM auth_user u
        JOIN options_func_usertracker t ON u.id = t.user_id
    """)
    
    trackers = cursor.fetchall()
    
    # 創建一個字典來存儲每個用戶的追蹤參數
    user_data = {}
    print(trackers)
    for tracker in trackers:
        user_id, username, email, method, stock1, stock2, start_date, end_date, window_size, n_std, track_date = tracker
        if user_id not in user_data:
            user_data[user_id] = {
                '使用者': username,
                '電子郵件': email,
                '追蹤標的': []
            }
        
        user_data[user_id]['追蹤標的'].append({
            '交易策略方法': method,
            '股票1': stock1,
            '股票2': stock2,
            '開始日期': start_date,
            '結束日期': end_date,
            '窗口大小': window_size,
            '標準差倍數': n_std,
            '追蹤日期': track_date
        })
    
    # 生成並發送每個用戶的報告
    mail_handler = MailHandler()
    current_time = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    for user_id, user_info in user_data.items():
        print(user_info)
        df = pd.DataFrame(user_info['追蹤標的'])
        
        # 生成 Excel 文件
        file_name = f"user_trackers_{user_info['使用者']}_{current_time}.xlsx"
        df.to_excel(file_name, index=False)
        
        # 發送郵件
        to_address = user_info['電子郵件']
        status = mail_handler.send(to_address, file_name)
        
        if status:
            print(f"報告已成功發送至 {to_address}")
        else:
            print(f"發送報告至 {to_address} 時出現錯誤")

    cursor.close()
    conn.close()

# 調用函數以生成並發送報告
generate_and_send_report()
