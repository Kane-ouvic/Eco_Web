from django.urls import path
from . import views

urlpatterns = [
    # path('', views.post_list, name='post_list'),
    path('calculate_strategy/', views.calculate_strategy, name='calculate_strategy'),
    path('test/', views.test, name='test'),
    path('rsi_backtest/', views.rsi_backtest, name='rsi_backtest'),
    path('monitor/', views.monitor, name='monitor'),
    path('stock_selection/', views.stock_selection, name='stock_selection'),
    path('stock_pricing/', views.stock_pricing, name='stock_pricing'),
    path('stock_peratio/', views.pe_ratio, name='pe_ratio'),
    path('ceiling_floor/', views.ceiling_floor, name='ceiling_floor'),
    path('kd_macd_bool/', views.kd_macd_bool, name='kd_macd_bool'),
    path('rsi_adx_dmi/', views.rsi_adx_dmi, name='rsi_adx_dmi'),
    path('pricing_strategy/', views.pricing_strategy, name='pricing_strategy'),
    path('entry_exit/', views.entry_exit, name='entry_exit'),
    path('kline/', views.kline, name='kline'),
    path('rsi_backtrader/', views.rsi_backtrader, name='rsi_backtrader'),
    # path('login/', views.login_view, name='login'),
    # path('logout/', views.logout_view, name='logout'),
    # path('register/', views.register, name='register'),
    
]
