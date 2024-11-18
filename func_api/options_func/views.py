from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view
from rest_framework.response import Response
import yfinance as yf
from django.contrib.auth.decorators import login_required
from rest_framework.views import APIView
import json
import logging
from .utils.distance_method import distance_method
from .utils.rsi_method import rsi_method
from django.http import QueryDict
from django.utils.dateparse import parse_date
from django.utils import timezone
from .models import UserTracker  # 添加這行在文件頂部
from rest_framework import status


@api_view(['POST'])
def simple_json_api(request):
    print(request.body)
    person = {'name': 'John', 'age': 30, 'city': 'New York'}
    return Response(person)

@csrf_exempt
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

            # 檢查必要的字段是否存在
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
        try:
            track_id = request.data.get('track_id')
            if not track_id:
                return Response({'success': False, 'error': '未提供追蹤 ID'}, status=status.HTTP_400_BAD_REQUEST)

            track = UserTracker.objects.filter(id=track_id, user=request.user).first()
            if not track:
                return Response({'success': False, 'error': '找不到指定的追蹤記錄或您沒有權限刪除此記錄'}, status=status.HTTP_404_NOT_FOUND)

            track.delete()
            print(f"User {request.user.username} successfully untracked record {track_id}")
            return Response({'success': True, 'message': '成功取消追蹤'}, status=status.HTTP_200_OK)
        except Exception as e:
            print(f"Error untracking: {str(e)}")
            return Response({'success': False, 'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
