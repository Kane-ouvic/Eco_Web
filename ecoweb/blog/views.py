from django.shortcuts import render
from django.http import JsonResponse
import yfinance as yf
import pandas as pd
import numpy as np

def calculate_strategy(request):
    if request.method == 'POST':
        stock1 = request.POST.get('stock1')
        stock2 = request.POST.get('stock2')
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')
        n_std = int(request.POST.get('n_std'))
        window_size = int(request.POST.get('window_size'))

        # Fetch stock data from Yahoo Finance
        data1 = yf.download(stock1, start=start_date, end=end_date)
        data2 = yf.download(stock2, start=start_date, end=end_date)

        # Calculate spread and Bollinger bands
        spread = (data1['Close'].apply(np.log) - data2['Close'].apply(np.log))
        rolling_mean = spread.rolling(window=window_size).mean().fillna(0)
        rolling_std = spread.rolling(window=window_size).std().fillna(0)
        upper_band = rolling_mean + (n_std * rolling_std)
        lower_band = rolling_mean - (n_std * rolling_std)

        # Signals (this is a simplified version, you'll need to define your own conditions)
        signals = []
        for i in range(len(spread)):
            if spread.iloc[i] > upper_band.iloc[i]:  # Example condition for sell
                signals.append({
                    'date': data1.index[i].strftime('%Y-%m-%d'),
                    'type': 'SELL',
                    'action_aapl': 'SELL',
                    'price_aapl': data1['Close'].iloc[i],
                    'action_gld': 'BUY',
                    'price_gld': data2['Close'].iloc[i]
                })
            elif spread.iloc[i] < lower_band.iloc[i]:  # Example condition for buy
                signals.append({
                    'date': data1.index[i].strftime('%Y-%m-%d'),
                    'type': 'BUY',
                    'action_aapl': 'BUY',
                    'price_aapl': data1['Close'].iloc[i],
                    'action_gld': 'SELL',
                    'price_gld': data2['Close'].iloc[i]
                })

        # Prepare the data for rendering in the template
        context = {
            'stock1': stock1,
            'stock2': stock2,
            'start_date': start_date,
            'end_date': end_date,
            'n_std': n_std,
            'window_size': window_size,
            'dates': list(data1.index.strftime('%Y-%m-%d')),
            'stock1_prices': list(data1['Close'].fillna(0)),
            'stock2_prices': list(data2['Close'].fillna(0)),
            'spread': list(spread.fillna(0)),
            'rolling_mean': list(rolling_mean),
            'upper_band': list(upper_band),
            'lower_band': list(lower_band),
            'signals': signals
        }

        return JsonResponse(context)

    return render(request, 'blog/post_list.html')
