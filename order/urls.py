# order/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('user/<int:user_id>/', views.OrderListCreateAPIView.as_view(), name='user_orders'),
    path('<int:pk>/', views.OrderRetrieveUpdateDestroyAPIView.as_view(), name='order_detail'),
]
