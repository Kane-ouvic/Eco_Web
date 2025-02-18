from django.urls import path
from . import views

urlpatterns = [
    # path('', views.post_list, name='post_list'),
    path('simple_json_api/', views.simple_json_api, name='simple_json_api'),
    path('calculate_strategy/', views.calculate_strategy, name='calculate_strategy'),
    path('rsi_backtest/', views.rsi2_backtest, name='rsi_backtest'),
    path('test1/', views.TestView.as_view(), name='test1'),
    path('add_track/', views.AddTrackView.as_view(), name='add_track'),
]
