from django.urls import path
from .views import *

urlpatterns = [
    path('register/', UserRegistation.as_view(), name='user-registration'),
    path('register/<int:pk>/', UserRegistation.as_view(), name='user-registration'),
    path('login/', Login.as_view(), name='user-login'),

    path('admin/log', LogAPIView.as_view(), name='for admin log'),
    path('stock/', StockAPIView.as_view(), name='out of stock'),
    path('stock1/', Stock1.as_view(), name='stock'),

    path('highest',UpdateStockPricesView.as_view(), name='single-user'),
    path('richest',ForAllUpdateStockPricesView.as_view(), name='multiple-user'),

    path('geolocation',GeoFensingChecking.as_view(), name='geo location'),
    path('admin/remove',AdminRemoval.as_view(),name='unblock user' ),
    path('admin/password',ChangePassword.as_view(),name='unblock user' )

]
