from django.contrib import admin
from .models import Order, OrderItem, Cart, CartItem

# Inline admin for order items
class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ['subtotal']


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'status', 'total_price', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['user__username', 'user__email']
    inlines = [OrderItemInline]
    readonly_fields = ['total_price', 'created_at', 'updated_at']


# Inline admin for cart items
class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 0


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ['user', 'item_count', 'get_total', 'updated_at']
    search_fields = ['user__username']
    inlines = [CartItemInline]
    
    def item_count(self, obj):
        return obj.item_count()
    item_count.short_description = 'Items'