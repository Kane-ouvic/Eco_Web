from django.shortcuts import render
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from .forms import LoginForm, RegisterForm
from django.contrib.auth.decorators import login_required
from django.utils.formats import date_format

import yfinance as yf
import pandas as pd
import numpy as np
import pandas_ta as ta

import json
from datetime import datetime, date, timedelta
import logging
import re
from django.core.serializers.json import DjangoJSONEncoder
from options_func.models import UserTracker

@login_required
def calculate_strategy(request):
    return render(request, 'blog/post_list.html')

@login_required
def rsi_backtest(request):
    return render(request, 'blog/rsi2_backtest.html')

@login_required
def stock_selection(request):
    return render(request, 'blog/stock_selection.html')

@login_required
def stock_pricing(request):
    return render(request, 'blog/stock_pricing.html')

@login_required
def pe_ratio(request):
    return render(request, 'blog/stock_perrc.html')

def test(request):
    print("hi")
    # return render(request, 'blog')
    return render(request, 'blog/test1.html')

def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('test')  # 替換 'home' 為您的主頁 URL 名稱
    else:
        form = LoginForm()
    return render(request, 'blog/login.html', {'form': form})

def register(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('test')  # 替換 'home' 為您的主頁 URL 名稱
    else:
        form = RegisterForm()
    return render(request, 'blog/register.html', {"form": form})

def logout_view(request):
    logout(request)
    return redirect('login')  # 或其他您想重定向的頁面

@login_required
def monitor(request):
    user_tracks = UserTracker.objects.filter(user=request.user).order_by('-created_at')
    print(user_tracks)
    return render(request, 'blog/monitor.html', {'user_tracks': user_tracks})
