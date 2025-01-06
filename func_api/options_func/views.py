import os
import sys
from dotenv import load_dotenv
sys.path.append('/home/ouvic/Eco_Web/finlab/')  # 添加這行以將路徑添加到模組搜索路徑
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from rest_framework.decorators import api_view
from rest_framework.response import Response
import yfinance as yf
from django.contrib.auth.decorators import login_required
from rest_framework.views import APIView
import json
import logging
from .utils.distance_method import distance_method
from .utils.rsi_method import rsi_method
from .utils.stockpricing import stock_pricing
from .utils.peratiochart import peratio_chart
from .utils.kdmacdbool import kdmacdbool
from .utils.ceilingfloor import ceilingfloor
from .utils.rsiadxdmi import rsiadxdmi
from .utils.stock_selection import stock_selection
from django.http import QueryDict
from django.utils.dateparse import parse_date
from django.utils import timezone
from .models import UserTracker, EntryExitTrack  # 添加這行在文件頂部
from rest_framework import status        
from fin import *  # 從指定路徑導入 fin 模組
from finlab import data, login
import talib
import numpy as np
import pandas as pd
from .utils.pricing_strategy import pricing_strategy
from .utils.entry_exit import entry_exit
# 添加項目根目錄到 Python 路徑
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
sys.path.append(project_root)

# 載入 .env 文件
load_dotenv(os.path.join(project_root, '.env'))

@api_view(['POST'])
def simple_json_api(request):
    print(request.body)
    person = {'name': 'John', 'age': 30, 'city': 'New York'}
    return Response(person)

@api_view(['POST'])
def calculate_strategy(request):
    try:
        # 檢查內容類型並相應地解析數據
        if request.content_type == 'application/json':
            data = json.loads(request.body)
        else:
            data = request.POST       
        print(data)

        print(f"Received data: {data}")

        # 從數據中獲取參數
        stock1 = data.get('stock1')
        stock2 = data.get('stock2')
        start_date = data.get('start_date')
        end_date = data.get('end_date')
        n_std = data.get('n_std')
        window_size = data.get('window_size')

        # 檢查是否所有必要的參數都存在
        if not all([stock1, stock2, start_date, end_date, n_std, window_size]):
            missing_params = [param for param in ['stock1', 'stock2', 'start_date', 'end_date', 'n_std', 'window_size'] if not data.get(param)]
            return Response({'error': f'Missing parameters: {", ".join(missing_params)}'}, status=400)

        # print("--------------------------")
        # 轉換參數為適當的類型
        try:
            n_std = int(n_std)
            window_size = int(window_size)
        except ValueError as e:
            return Response({'error': f'Invalid value for n_std or window_size: {str(e)}'}, status=400)
        context = distance_method(stock1, stock2, start_date, end_date, n_std, window_size)
        # print("--------------------------")
        
        return Response(context)
    except json.JSONDecodeError:
        return Response({'error': 'Invalid JSON format'}, status=400)
    except Exception as e:
        logging.exception("An error occurred in calculate_strategy")
        return Response({'error': str(e)}, status=500)

@api_view(['POST'])
def rsi2_backtest(request):
        logging.info("收到 POST 請求")
        try:
            # 從請求中獲取參數
            etf_symbol = request.POST.get('etf_symbol', '0050.TW')
            start_date = request.POST.get('start_date', '2013-01-01')
            end_date = request.POST.get('end_date', '2022-05-01')
            short_rsi = int(request.POST.get('short_rsi', 120))
            long_rsi = int(request.POST.get('long_rsi', 150))
            exit_threshold = float(request.POST.get('exit_threshold', 0.999))

            logging.info(f"參數: etf_symbol={etf_symbol}, start_date={start_date}, end_date={end_date}, short_rsi={short_rsi}, long_rsi={long_rsi}, exit_threshold={exit_threshold}")
            result = rsi_method(etf_symbol, start_date, end_date, short_rsi, long_rsi, exit_threshold)
            
            return Response(result)
        except ValueError as ve:
            logging.error(f"數據處理錯誤: {str(ve)}")
            return Response({'error': str(ve)}, status=400)
        except Exception as e:
            logging.error(f"回測過程中發生錯誤: {str(e)}", exc_info=True)
            return Response({'error': str(e)}, status=500)

class TestView(APIView):
    def get(self, request):
        return Response({'message': 'Hello, world!'})
    
    def post(self, request):
        print(request.data)
        return Response({'message': 'Hello, world!'})

class AddTrackView(APIView):
    def post(self, request):
        try:
            # 從請求中獲取數據
            print(f"Received data: {request.data}")
            method = request.data.get('method', 'distance')  # 默認為 'distance'
            stock1 = request.data.get('stock1')
            stock2 = request.data.get('stock2')
            start_date = parse_date(request.data.get('start_date'))
            end_date = parse_date(request.data.get('end_date'))
            window_size = int(request.data.get('window_size'))
            n_std = float(request.data.get('n_std'))
            track_date = timezone.now()

            # 檢查必要的字段否存在
            if not all([stock1, stock2, start_date, end_date, window_size, n_std]):
                return Response({'success': False, 'error': '缺少必要的字段'})

            # 創建新的 UserTracker 記錄
            tracker = UserTracker.objects.create(
                user=request.user,
                method=method,
                stock1=stock1,
                stock2=stock2,
                start_date=start_date,
                end_date=end_date,
                window_size=window_size,
                n_std=n_std,
                track_date=track_date
            )
            print(f"Successfully created tracker: {tracker.id}")
            return Response({'success': True, 'message': '成功添加追蹤'})
        except Exception as e:
            print(f"Error adding track: {str(e)}")
            return Response({'success': False, 'error': str(e)})
    
    def delete(self, request):
        print("Cookies:", request.COOKIES)  # 查看共享的 Cookie 是否正確
        print("Session ID:", request.COOKIES.get('shared_sessionid'))  # 檢查 Session ID
        print("User:", request.user)  # 檢查是否正確辨識用戶
        # print(session_key)
        try:
            track_id = request.data.get('track_id')
            
            if not track_id:
                return Response({'success': False, 'error': '未提供追蹤 ID'}, status=status.HTTP_400_BAD_REQUEST)

            track = UserTracker.objects.filter(id=track_id, user=request.user).first()
            # print(track)
            if not track:
                return Response({'success': False, 'error': '找不到指定的追蹤記錄或您沒有權限刪除此記錄'}, status=status.HTTP_404_NOT_FOUND)

            track.delete()
            print(f"User {request.user.username} successfully untracked record {track_id}")
            return Response({'success': True, 'message': '成功取消追蹤'}, status=status.HTTP_200_OK)
        except Exception as e:
            print(f"Error untracking: {str(e)}")
            return Response({'success': False, 'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        

class StockSelectionView(APIView):
    def post(self, request):
        print(request.data)
        monthly_revenue = request.data.get('monthlyRevenue')
        stock_price = request.data.get('closingPrice')
        roa = request.data.get('roa')

        # token = os.getenv('FIN_TOKEN')
        token = '9KabngzgazwRsIf2lE3zr2qHHaCXRn/+qBTHJ5lSdCdrjKIgFQfGFg/SuQVA5htW#free'
        if not token:
            return Response({'error': 'FIN_TOKEN 未設置'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        login(token)
        
        try:
            # 初始化 FinLab Data
            rev1 = data.get('monthly_revenue:當月營收')
            rev_ma = rev1.average(2)
            condition1 = rev_ma > float(monthly_revenue)

            # 獲取收盤價數據
            closing_price = data.get('price:收盤價')
            condition2 = closing_price > float(stock_price)

            # 獲取最新日期的行
            latest_date = rev1.index.max()
            latest_row = rev1.loc[latest_date]
            selected_stocks = condition1 & condition2
            
            # 提取最新日期中所有 True 的股票代碼、公司名稱和最新收盤價
            selected_stocks = []
            for stock_code, is_selected in latest_row.items():
                if is_selected:
                    try:
                        latest_closing_price = closing_price.loc[latest_date, stock_code]
                        # 確保收盤價大於設定值
                        if latest_closing_price <= float(stock_price):
                            print(f"股票代碼 {stock_code} 的收盤價小於或等於設定值: {latest_closing_price}，跳過")
                            continue
                        # 檢查最新收盤價是否為有效數值
                        import math
                        if not math.isfinite(latest_closing_price):
                            print(f"股票代碼 {stock_code} 的收盤價無效: {latest_closing_price}，跳過")
                            continue
                        selected_stocks.append({
                            'date': latest_date,
                            'stock_code': stock_code,
                            'latest_closing_price': latest_closing_price
                        })
                    except KeyError:
                        print(f"無法獲取股票代碼 {stock_code} 的最新收盤價，跳過此股票")
            
            return Response({'selected_stocks': selected_stocks})
        
        except Exception as e:
            print(f"Error during stock selection: {str(e)}")
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class StockPricingView(APIView):
    def post(self, request):
        # print(request.data)
        # 從請求中獲取數據
        stock_code = request.data.get('stockCode')
        year = request.data.get('year')
        latest_price, pricing_data = stock_pricing(stock_code, year)
        
        return Response({
            'success': True,
            'latest_price': latest_price,
            'pricing_data': pricing_data
        }, status=status.HTTP_200_OK)

class PeRatioChartView(APIView):
    def post(self, request):
        stock_code = request.data.get('stockCode')
        latest_price, pricing_data, dates, pe_lines, candlestick_data = peratio_chart(stock_code)

        return Response({
            'success': True,
            'latest_price': latest_price,
            'pricing_data': pricing_data,
            'dates': dates,
            'pe_lines': pe_lines,
            'candlestick_data': candlestick_data
        }, status=status.HTTP_200_OK)
        

class CeilingFloorView(APIView):
    def post(self, request):
        stock_code = request.data.get('stockCode')
        start_date = request.data.get('startDate')
        ma_length = int(request.data.get('maLength'))
        ma_type = request.data.get('maType')
        method = request.data.get('method')
        
        ma, ceiling_price, floor_price, candlestick_data, ceiling_signals, floor_signals = ceilingfloor(stock_code, start_date, ma_length, ma_type, method)
        
        
        return Response({
            'success': True,
            'ma': ma.fillna(-2147483648),
            'ceiling_price': ceiling_price.fillna(-2147483648),
            'floor_price': floor_price.fillna(-2147483648),
            'candlestick_data': candlestick_data,
            'ceiling_signals': ceiling_signals,
            'floor_signals': floor_signals
        }, status=status.HTTP_200_OK)
        

class KdMacdBoolView(APIView):
    def post(self, request):
        print(request.data)
        stock_code = request.data.get('stockCode')
        start_date = request.data.get('startDate')
        end_date = request.data.get('endDate')
        print(stock_code, start_date, end_date)
        # stock = yf.download(f"{stock_code}.TW", start=start_date)
        
        # # 初始化 macd 字典
        kd = {}
        macd = {}
        bool = {}
        candlestick_data, kd['K'], kd['D'], macd['MACD'], macd['signal'], macd['hist'], bool['MIDDLEBAND'], bool['UPPERBAND'], bool['LOWERBAND'] = kdmacdbool(stock_code, start_date, end_date)
        
        return Response({
            'success': True,
            'candlestick_data': candlestick_data,
            'kd_K': kd['K'].fillna(-2147483648),
            'kd_D': kd['D'].fillna(-2147483648),
            'macd_data': macd['MACD'].fillna(-2147483648),
            'macd_signal': macd['signal'].fillna(-2147483648),
            'macd_hist': macd['hist'].fillna(-2147483648),
            'bool_mid': bool['MIDDLEBAND'].fillna(-2147483648),
            'bool_upper': bool['UPPERBAND'].fillna(-2147483648),
            'bool_lower': bool['LOWERBAND'].fillna(-2147483648)
        }, status=status.HTTP_200_OK)
        
    
class RsiAdxDmiView(APIView):
    def post(self, request):
        print(request.data)
        stock_code = request.data.get('stockCode')
        start_date = request.data.get('startDate')
        end_date = request.data.get('endDate')
        # stock = yf.download(f"{stock_code}.TW", start=start_date)
        
        candlestick_data, rsi, adx, plus_di, minus_di = rsiadxdmi(stock_code, start_date, end_date)
        
        return Response({
            'success': True,
            'candlestick_data': candlestick_data,
            'rsi': rsi.fillna(-2147483648),
            'adx': adx.fillna(-2147483648),
            'plus_di': plus_di.fillna(-2147483648),
            'minus_di': minus_di.fillna(-2147483648)
        }, status=status.HTTP_200_OK)


class EntryExitView(APIView):
    def post(self, request):
        print(request.data)
        stock_code = request.data.get('stockCode')
        start_date = request.data.get('startDate')
        end_date = request.data.get('endDate')
        strategy = request.data.get('strategy')
        if strategy == 'ceil_floor':
            ma, ceiling_price, floor_price, candlestick_data, ceiling_signals, floor_signals = entry_exit(stock_code, start_date, end_date, strategy)
            return Response({
                'success': True,
                'candlestick_data': candlestick_data,
                'ma': ma.fillna(-2147483648),
                'ceiling_price': ceiling_price.fillna(-2147483648),
                'floor_price': floor_price.fillna(-2147483648),
                'ceiling_signals': ceiling_signals,
                'floor_signals': floor_signals
            }, status=status.HTTP_200_OK)
        elif strategy == 'kd':
            kd = {}
            candlestick_data, kd['K'], kd['D'] = entry_exit(stock_code, start_date, end_date, strategy)
            return Response({
                'success': True,
                'candlestick_data': candlestick_data,
                'kd_K': kd['K'].fillna(-2147483648),
                'kd_D': kd['D'].fillna(-2147483648)
            }, status=status.HTTP_200_OK)
        elif strategy == 'macd':
            macd = {}
            candlestick_data, macd['MACD'], macd['signal'], macd['hist'] = entry_exit(stock_code, start_date, end_date, strategy)
            return Response({
                'success': True,
                'candlestick_data': candlestick_data,
                'macd_data': macd['MACD'].fillna(-2147483648),
                'macd_signal': macd['signal'].fillna(-2147483648),
                'macd_hist': macd['hist'].fillna(-2147483648)
            }, status=status.HTTP_200_OK)
        elif strategy == 'booling':
            bool = {}
            candlestick_data, bool['MIDDLEBAND'], bool['UPPERBAND'], bool['LOWERBAND'] = entry_exit(stock_code, start_date, end_date, strategy)
            return Response({
                'success': True,
                'candlestick_data': candlestick_data,
                'bool_mid': bool['MIDDLEBAND'].fillna(-2147483648),
                'bool_upper': bool['UPPERBAND'].fillna(-2147483648),
                'bool_lower': bool['LOWERBAND'].fillna(-2147483648)
            }, status=status.HTTP_200_OK)
        elif strategy == 'rsi':
            candlestick_data, rsi = entry_exit(stock_code, start_date, end_date, strategy)
            return Response({
                'success': True,
                'candlestick_data': candlestick_data,
                'rsi': rsi.fillna(-2147483648)
            }, status=status.HTTP_200_OK)
        elif strategy == 'adx_dmi':
            candlestick_data, adx, plus_di, minus_di = entry_exit(stock_code, start_date, end_date, strategy)
            return Response({
                'success': True,
                'candlestick_data': candlestick_data,
                'adx': adx.fillna(-2147483648),
                'plus_di': plus_di.fillna(-2147483648),
                'minus_di': minus_di.fillna(-2147483648)
            }, status=status.HTTP_200_OK)
        elif strategy == 'kline':
            pass
            
        # return Response({'message': 'Hello, world!'})
    

class PricingStrategyView(APIView):
    def post(self, request):
        print(request.data)
        stock_code = request.data.get('stockCode')
        start_date = request.data.get('startDate')
        end_date = request.data.get('endDate')
        latest_price, pricing_data, date, heatmap_data, div_expensive, hl_expensive, pb_expensive, pe_expensive = pricing_strategy(stock_code, start_date, end_date)
        return Response({
            'success': True,
            'latest_price': latest_price,
            'pricing_data': pricing_data,
            'date': date,
            'heatmap_data': heatmap_data,
            'div_expensive': div_expensive,
            'hl_expensive': hl_expensive,
            'pb_expensive': pb_expensive,
            'pe_expensive': pe_expensive
        }, status=status.HTTP_200_OK)
        

class AddEntryExitTrackView(APIView):
    def post(self, request):
        try:
            # 從請求中獲取數據
            print(f"Received data: {request.data}")
            method = request.data.get('strategy', 'ceil_floor')  # 默認為 'ceil_floor'
            stock_code = request.data.get('stockCode')
            start_date = parse_date(request.data.get('startDate'))
            end_date = parse_date(request.data.get('endDate'))
            track_date = timezone.now()

            # 檢查必要的字段否存在
            if not all([stock_code, start_date, end_date]):
                return Response({'success': False, 'error': '缺少必要的字段'})

            # 創建新的 EntryExitTrack 記錄
            tracker = EntryExitTrack.objects.create(
                user=request.user,
                method=method,
                stock_code=stock_code,
                start_date=start_date,
                end_date=end_date,
                track_date=track_date
            )
            print(f"Successfully created tracker: {tracker.id}")
            return Response({'success': True, 'message': '成功添加追蹤'})
        except Exception as e:
            print(f"Error adding track: {str(e)}")
            return Response({'success': False, 'error': str(e)})
