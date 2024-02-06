from django.urls import path
from .views import *

urlpatterns = [
    path('register/', UserRegistation.as_view(), name='user-registration'),
    path('login/', Login.as_view(), name='user-login'),
    path('log/', LogAPIView.as_view(), name='log'),
    path('stock/', StockAPIView.as_view(), name='stock'),
]
