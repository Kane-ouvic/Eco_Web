from django.shortcuts import render
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from .forms import LoginForm, RegisterForm
from django.contrib.auth.decorators import login_required

import json
from datetime import datetime, date, timedelta
import logging
import re
from django.core.serializers.json import DjangoJSONEncoder


def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('http://web.nightcover.com.tw:55555/blog/test')  # 替換 'home' 為您的主頁 URL 名稱
    else:
        form = LoginForm()
    return render(request, 'auth/login.html', {'form': form})

def register(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('http://web.nightcover.com.tw:55555/blog/test')  # 替換 'home' 為您的主頁 URL 名稱
    else:
        form = RegisterForm()
    return render(request, 'auth/register.html', {"form": form})


def logout_view(request):
    logout(request)
    return redirect('login')  # 或其他您想重定向的頁面

def login_reminder(request):
    next_url = request.GET.get('next', '/')
    return render(request, 'auth/login_reminder.html', {'next_url': next_url})