# order/urls.py
from django.urls import path
from . import views

order_list = views.OrderViewSet.as_view({
    'get': 'list',
    'post': 'create'
})

order_update = views.OrderViewSet.as_view({
    'put': 'update',
    'patch': 'partial_update'
})

urlpatterns = [
    path('sales/', views.get_sales_orders, name='get_sales_orders'),
    path('purchases/', order_list, name='get_purchase_orders'),
    path('create/', order_list, name='create_order'),
    path('sales/update/<int:pk>', order_update, name='update_sales_status'),
    path('purchases/update/<int:pk>', order_update, name='update_purchase_status'),
]
