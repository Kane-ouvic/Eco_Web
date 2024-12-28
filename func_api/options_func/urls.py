from django.urls import path
from . import views

urlpatterns = [
    # path('', views.post_list, name='post_list'),
    path('simple_json_api/', views.simple_json_api, name='simple_json_api'),
    path('calculate_strategy/', views.calculate_strategy, name='calculate_strategy'),
    path('rsi_backtest/', views.rsi2_backtest, name='rsi_backtest'),
    path('test1/', views.TestView.as_view(), name='test1'),
    path('add_track/', views.AddTrackView.as_view(), name='add_track'),
    path('stock_selection/', views.StockSelectionView.as_view(), name='stock_selection'),
    path('stock_pricing/', views.StockPricingView.as_view(), name='stock_pricing'),
    path('pe_ratio_chart/', views.PeRatioChartView.as_view(), name='pe_ratio_chart'),
    path('ceiling_floor/', views.CeilingFloorView.as_view(), name='ceiling_floor'),
    path('kd_macd_bool/', views.KdMacdBoolView.as_view(), name='kd_macd_bool'),
]
