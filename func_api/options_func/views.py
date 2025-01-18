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
from .utils.rsi_backtrader import rsi_backtrader
from .utils.kline import kline
from django.http import QueryDict
from django.utils.dateparse import parse_date
from django.utils import timezone
from django.http import HttpResponse
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

        # 轉換參數為適當的類型
        try:
            n_std = int(n_std)
            window_size = int(window_size)
        except ValueError as e:
            return Response({'error': f'Invalid value for n_std or window_size: {str(e)}'}, status=400)
        context = distance_method(stock1, stock2, start_date, end_date, n_std, window_size)
        
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

class RsiBacktraderView(APIView):
    def post(self, request):
        stock_symbol = request.data.get('stockCode')
        start_date = request.data.get('startDate')
        end_date = request.data.get('endDate')
        short_rsi = int(request.data.get('short_rsi'))
        long_rsi = int(request.data.get('long_rsi'))
        rsi_upper = int(request.data.get('rsi_upper'))
        rsi_lower = int(request.data.get('rsi_lower'))
        stake = int(request.data.get('stake'))
        initial_cash = float(request.data.get('initial_cash'))
        commission = float(request.data.get('commission'))
        result = rsi_backtrader(stock_symbol, start_date, end_date, short_rsi, long_rsi, rsi_upper, rsi_lower, stake, initial_cash, commission)
        response = HttpResponse(content_type='image/png')
        result.savefig(response, format='png')
        response['Content-Disposition'] = 'inline; filename="backtest_result.png"'
        return response

class AddTrackView(APIView):
    def post(self, request):
        try:
            # 從請求中獲取數據
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

        token = os.getenv('FIN_TOKEN')

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
        end_date = request.data.get('endDate')
        ma_length = int(request.data.get('maLength'))
        ma_type = request.data.get('maType')
        method = request.data.get('method')
        
        ma, ceiling_price, floor_price, candlestick_data, volume_data, signals = ceilingfloor(stock_code, start_date, end_date, ma_length, ma_type, method)
        
        
        return Response({
            'success': True,
            'ma': ma.fillna(-2147483648),
            'ceiling_price': ceiling_price.fillna(-2147483648),
            'floor_price': floor_price.fillna(-2147483648),
            'candlestick_data': candlestick_data,
            'volume_data': volume_data,
            'signals': signals
        }, status=status.HTTP_200_OK)
        

class KdMacdBoolView(APIView):
    def post(self, request):
        print(request.data)
        stock_code = request.data.get('stockCode')
        start_date = request.data.get('startDate')
        end_date = request.data.get('endDate')
        fastk_period = int(request.data.get('fastk_period'))
        slowk_period = int(request.data.get('slowk_period'))
        slowd_period = int(request.data.get('slowd_period'))
        fastperiod = int(request.data.get('fastperiod'))
        slowperiod = int(request.data.get('slowperiod'))
        signalperiod = int(request.data.get('signalperiod'))
        timeperiod = int(request.data.get('timeperiod'))
        nbdevup = int(request.data.get('nbdevup'))
        nbdevdn = int(request.data.get('nbdevdn'))
        print(stock_code, start_date, end_date)
        
        # # 初始化 macd 字典
        kd = {}
        macd = {}
        bool = {}
        candlestick_data, volume_data, kd['K'], kd['D'], macd['MACD'], macd['signal'], macd['hist'], bool['MIDDLEBAND'], bool['UPPERBAND'], bool['LOWERBAND'], signals = kdmacdbool(stock_code, start_date, end_date, fastk_period, slowk_period, slowd_period, fastperiod, slowperiod, signalperiod, timeperiod, nbdevup, nbdevdn)
        
        return Response({
            'success': True,
            'candlestick_data': candlestick_data,
            'volume_data': volume_data,
            'kd_K': kd['K'].fillna(-2147483648),
            'kd_D': kd['D'].fillna(-2147483648),
            'macd_data': macd['MACD'].fillna(-2147483648),
            'macd_signal': macd['signal'].fillna(-2147483648),
            'macd_hist': macd['hist'].fillna(-2147483648),
            'bool_mid': bool['MIDDLEBAND'].fillna(-2147483648),
            'bool_upper': bool['UPPERBAND'].fillna(-2147483648),
            'bool_lower': bool['LOWERBAND'].fillna(-2147483648),
            'kd_signals': signals['kd_signals'],
            'macd_signals': signals['macd_signals'],
            'bool_signals': signals['bool_signals']
        }, status=status.HTTP_200_OK)
        
    
class RsiAdxDmiView(APIView):
    def post(self, request):
        print(request.data)
        stock_code = request.data.get('stockCode')
        start_date = request.data.get('startDate')
        end_date = request.data.get('endDate')
        rsi_period = int(request.data.get('rsi_period'))
        adx_period = int(request.data.get('adx_period'))
        # stock = yf.download(f"{stock_code}.TW", start=start_date)
        
        candlestick_data, volume_data, rsi, adx, plus_di, minus_di, signals = rsiadxdmi(stock_code, start_date, end_date, rsi_period, adx_period)
        
        return Response({
            'success': True,
            'candlestick_data': candlestick_data,
            'volume_data': volume_data,
            'rsi': rsi.fillna(-2147483648),
            'adx': adx.fillna(-2147483648),
            'plus_di': plus_di.fillna(-2147483648),
            'minus_di': minus_di.fillna(-2147483648),
            'rsi_signals': signals['rsi_signals'],
            'adx_signals': signals['adx_signals']
        }, status=status.HTTP_200_OK)


class EntryExitView(APIView):
    def post(self, request):
        print(request.data)
        stock_code = request.data.get('stockCode')
        start_date = request.data.get('startDate')
        end_date = request.data.get('endDate')
        ma_length = int(request.data.get('maLength'))
        ma_type = request.data.get('maType')
        method = request.data.get('method')
        fastk_period = int(request.data.get('fastk_period'))
        slowk_period = int(request.data.get('slowk_period'))
        slowd_period = int(request.data.get('slowd_period'))
        fastperiod = int(request.data.get('fastperiod'))
        slowperiod = int(request.data.get('slowperiod'))
        signalperiod = int(request.data.get('signalperiod'))
        timeperiod = int(request.data.get('timeperiod'))
        nbdevup = int(request.data.get('nbdevup'))
        nbdevdn = int(request.data.get('nbdevdn'))
        rsi_period = int(request.data.get('rsi_period'))
        adx_period = int(request.data.get('adx_period'))
        
        ma, ceiling_price, floor_price, candlestick_data, volume_data, signals1 = ceilingfloor(stock_code, start_date, end_date, ma_length, ma_type, method)
        kd = {}
        macd = {}
        bool = {}
        candlestick_data, volume_data, kd['K'], kd['D'], macd['MACD'], macd['signal'], macd['hist'], bool['MIDDLEBAND'], bool['UPPERBAND'], bool['LOWERBAND'], signals2 = kdmacdbool(stock_code, start_date, end_date, fastk_period, slowk_period, slowd_period, fastperiod, slowperiod, signalperiod, timeperiod, nbdevup, nbdevdn)
        candlestick_data, volume_data, rsi, adx, plus_di, minus_di, signals3 = rsiadxdmi(stock_code, start_date, end_date, rsi_period, adx_period)
        candlestick_data, volume_data, kline_patterns = kline(stock_code, start_date, end_date)
        
        return Response({
            'success': True,
            'candlestick_data': candlestick_data,
            'volume_data': volume_data,
            'ma': ma.fillna(-2147483648),
            'ceiling_price': ceiling_price.fillna(-2147483648),
            'floor_price': floor_price.fillna(-2147483648),
            'kd_K': kd['K'].fillna(-2147483648),
            'kd_D': kd['D'].fillna(-2147483648),
            'macd_data': macd['MACD'].fillna(-2147483648),
            'macd_signal': macd['signal'].fillna(-2147483648),
            'macd_hist': macd['hist'].fillna(-2147483648),
            'bool_mid': bool['MIDDLEBAND'].fillna(-2147483648),
            'bool_upper': bool['UPPERBAND'].fillna(-2147483648),
            'bool_lower': bool['LOWERBAND'].fillna(-2147483648),
            'rsi': rsi.fillna(-2147483648),
            'adx': adx.fillna(-2147483648),
            'plus_di': plus_di.fillna(-2147483648),
            'minus_di': minus_di.fillna(-2147483648),
            'ceilingfloor_signals': signals1,
            'kd_signals': signals2['kd_signals'],
            'macd_signals': signals2['macd_signals'],
            'bool_signals': signals2['bool_signals'],
            'rsi_signals': signals3['rsi_signals'],
            'adx_signals': signals3['adx_signals'],
            'kline_patterns': kline_patterns
        }, status=status.HTTP_200_OK)
    

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
            
            stock_code = request.data.get('stockCode')
            start_date = parse_date(request.data.get('startDate'))
            end_date = parse_date(request.data.get('endDate'))
            
            ma_length = int(request.data.get('maLength'))
            ma_type = request.data.get('maType')
            method = request.data.get('method')
            
            fastk_period = int(request.data.get('fastk_period'))
            slowk_period = int(request.data.get('slowk_period'))
            slowd_period = int(request.data.get('slowd_period'))
            
            fastperiod = int(request.data.get('fastperiod'))
            slowperiod = int(request.data.get('slowperiod'))
            signalperiod = int(request.data.get('signalperiod'))
            
            timeperiod = int(request.data.get('timeperiod'))
            nbdevup = int(request.data.get('nbdevup'))
            nbdevdn = int(request.data.get('nbdevdn'))
            
            rsi_period = int(request.data.get('rsi_period'))
            adx_period = int(request.data.get('adx_period'))
            
            track_date = timezone.now()

            # 檢查必要的字段否存在
            if not all([stock_code, start_date, end_date]):
                return Response({'success': False, 'error': '缺少必要的字段'})

            # 創建新的 EntryExitTrack 記錄
            tracker = EntryExitTrack.objects.create(
                user=request.user,
                stock_code=stock_code,
                start_date=start_date,
                end_date=end_date,
                method=method,
                ma_length=ma_length,
                ma_type=ma_type,
                fastk_period=fastk_period,
                slowk_period=slowk_period,
                slowd_period=slowd_period,
                fastperiod=fastperiod,
                slowperiod=slowperiod,
                signalperiod=signalperiod,
                timeperiod=timeperiod,
                nbdevup=nbdevup,
                nbdevdn=nbdevdn,
                rsi_period=rsi_period,
                adx_period=adx_period,
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

            track = EntryExitTrack.objects.filter(id=track_id, user=request.user).first()
            # print(track)
            if not track:
                return Response({'success': False, 'error': '找不到指定的追蹤記錄或您沒有權限刪除此記錄'}, status=status.HTTP_404_NOT_FOUND)

            track.delete()
            print(f"User {request.user.username} successfully untracked record {track_id}")
            return Response({'success': True, 'message': '成功取消追蹤'}, status=status.HTTP_200_OK)
        except Exception as e:
            print(f"Error untracking: {str(e)}")
            return Response({'success': False, 'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class KlineView(APIView):
    def post(self, request):
        stock_code = request.data.get('stockCode')
        start_date = request.data.get('startDate')
        end_date = request.data.get('endDate')
        candlestick_data, volume_data, kline_patterns = kline(stock_code, start_date, end_date)
        return Response({'success': True, 'candlestick_data': candlestick_data, 'volume_data': volume_data, 'kline_patterns': kline_patterns}, status=status.HTTP_200_OK)