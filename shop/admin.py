from django.contrib import admin
from .models import WaterProduct, Order

@admin.register(WaterProduct)
class WaterProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'stock')

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'product', 'quantity', 'total_price', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    readonly_fields = ('created_at',)
