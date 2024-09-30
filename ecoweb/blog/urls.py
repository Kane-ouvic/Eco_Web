from django.urls import path
from . import views

urlpatterns = [
    # path('', views.post_list, name='post_list'),
    path('calculate-strategy/', views.calculate_strategy, name='calculate_strategy'),
    path('test/', views.test, name='test'),
    
]
