from rest_framework import serializers
from .models import Order, OrderItem, Cart, CartItem
from products.models import Product
from products.serializers import ProductSerializer

# Serializer for cart items
class CartItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)
    product_id = serializers.IntegerField(write_only=True)
    subtotal = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    
    class Meta:
        model = CartItem
        fields = ['id', 'product', 'product_id', 'quantity', 'subtotal', 'added_at']
    
    def validate_quantity(self, value):
        if value <= 0:
            raise serializers.ValidationError("Quantity must be at least 1")
        return value
    
    def validate(self, data):
        # Check if product exists and has enough stock
        product_id = data.get('product_id')
        quantity = data.get('quantity', 1)
        
        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            raise serializers.ValidationError("Product not found")
        
        if product.stock < quantity:
            raise serializers.ValidationError(f"Only {product.stock} items available in stock")
        
        return data


# Serializer for shopping cart
class CartSerializer(serializers.ModelSerializer):
    cart_items = CartItemSerializer(many=True, read_only=True)
    total = serializers.SerializerMethodField()
    item_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Cart
        fields = ['id', 'cart_items', 'total', 'item_count', 'created_at', 'updated_at']
    
    def get_total(self, obj):
        return obj.get_total()
    
    def get_item_count(self, obj):
        return obj.item_count()


# Serializer for order items
class OrderItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)
    subtotal = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    
    class Meta:
        model = OrderItem
        fields = ['id', 'product', 'product_name', 'quantity', 'price', 'subtotal']


# Serializer for creating orders
class OrderCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ['shipping_address', 'phone_number']
    
    def validate_shipping_address(self, value):
        if len(value.strip()) < 10:
            raise serializers.ValidationError("Please provide a complete shipping adress")  
        return value


# Serializer for displaying orders
class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    user_name = serializers.CharField(source='user.username', read_only=True)
    
    class Meta:
        model = Order
        fields = ['id', 'user_name', 'status', 'total_price', 'shipping_address', 
                 'phone_number', 'items', 'created_at', 'updated_at']
        read_only_fields = ['total_price', 'created_at', 'updated_at']


# Simple order list serializer (without items detail)
class OrderListSerializer(serializers.ModelSerializer):
    items_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Order
        fields = ['id', 'status', 'total_price', 'items_count', 'created_at']
    
    def get_items_count(self, obj):
        return obj.items.count()