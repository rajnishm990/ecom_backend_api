from rest_framework import serializers
from .models import Category, Product

class CategorySerializer(serializers.ModelSerializer):
    products_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Category
        fields = ['id', 'name', 'description', 'products_count', 'created_at']
    
    def get_products_count(self, obj):
        
        return obj.products.count()



class ProductSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    in_stock = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = Product
        fields = ['id', 'name', 'description', 'price', 'stock', 
                 'category', 'category_name', 'in_stock', 
                 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']
    
    def validate_price(self, value):
        
        if value <= 0:
            raise serializers.ValidationError("Price must be greater than zero!")
        return value
    
    def validate_stock(self, value):
       
        if value < 0:
            raise serializers.ValidationError("Stock cannot be negetive!") 
        return value



class ProductDetailSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    in_stock = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = Product
        fields = ['id', 'name', 'description', 'price', 'stock', 
                 'category', 'in_stock', 'created_at', 'updated_at']