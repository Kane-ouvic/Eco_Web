# settings_options_func.py

from .settings import *  # 繼承通用設定

# 調整 INSTALLED_APPS 以僅包含 options_func 相關應用
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'options_func',  # Options_func 應用
    # 其他 options_func 相關應用
]

# 其他特定於 options_func 的設定