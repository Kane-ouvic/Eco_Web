from django.urls import path
from . import views

urlpatterns = [
    # path('', views.post_list, name='post_list'),
    path('calculate_strategy/', views.calculate_strategy, name='calculate_strategy'),
    path('test/', views.test, name='test'),
    path('rsi_backtest/', views.rsi_backtest, name='rsi_backtest'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.register, name='register'),
    
]
