# orders/admin.py
from django.contrib import admin
from .models import Order


class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'listing', 'buyer', 'status', 'created', 'modified')
    list_filter = ('status', 'buyer', 'is_delivered')
    search_fields = ('id', 'buyer__username')
    readonly_fields = ('created', 'modified')


admin.site.register(Order, OrderAdmin)
