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
    # path('login/', views.login_view, name='login'),
    # path('logout/', views.logout_view, name='logout'),
    # path('register/', views.register, name='register'),
    
]
