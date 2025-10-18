from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny
from django_filters.rest_framework import DjangoFilterBackend
from django.core.cache import cache
from django.db.models import Q
from .models import Category, Product
from .serializers import CategorySerializer, ProductSerializer, ProductDetailSerializer

# Cache timeout - 1 hour (3600 seconds)
CACHE_TTL = 3600


class CategoryViewSet(viewsets.ModelViewSet):
   
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    
    def get_permissions(self):
        # everone can see , Admin can modify
        if self.action in ['list', 'retrieve']:
            permission_classes = [AllowAny]
        else:
            permission_classes = [IsAdminUser]
        return [permission() for permission in permission_classes]
    
    def list(self, request, *args, **kwargs):
        # Try to get categories from cache first
        cache_key = 'categories_list'
        categories = cache.get(cache_key)
        
        if categories is None:
            # Cache miss - fetch from database
            queryset = self.get_queryset()
            serializer = self.get_serializer(queryset, many=True)
            categories = serializer.data
            
            # Store in cache for 1 hour
            cache.set(cache_key, categories, CACHE_TTL)
        
        return Response(categories)
    
    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        
        # Invalidate cache when new category is created
        cache.delete('categories_list')
        
        return response
    
    def update(self, request, *args, **kwargs):
        response = super().update(request, *args, **kwargs)
        
        # Invalidate cache when category is updated
        cache.delete('categories_list')
        
        return response
    
    def destroy(self, request, *args, **kwargs):
        response = super().destroy(request, *args, **kwargs)
        
        # Invalidate cache when category is deleted
        cache.delete('categories_list')
        
        return response


class ProductViewSet(viewsets.ModelViewSet):
    
    queryset = Product.objects.select_related('category').all()  
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description']
    ordering_fields = ['price', 'created_at', 'stock']
    
    def get_serializer_class(self):
        # Use detailed serializer for single product view
        if self.action == 'retrieve':
            return ProductDetailSerializer
        return ProductSerializer
    
    def get_permissions(self):
        # Everyone can view products, only admins can modify
        if self.action in ['list', 'retrieve']:
            permission_classes = [AllowAny]
        else:
            permission_classes = [IsAdminUser]
        return [permission() for permission in permission_classes]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filter by category if provided
        category_id = self.request.query_params.get('category', None)
        if category_id:
            queryset = queryset.filter(category_id=category_id)
        
        # Filter by price range
        min_price = self.request.query_params.get('min_price', None)
        max_price = self.request.query_params.get('max_price', None)
        
        if min_price:
            queryset = queryset.filter(price__gte=min_price)
        if max_price:
            queryset = queryset.filter(price__lte=max_price)
        
        # Filter by stock availablity
        in_stock = self.request.query_params.get('in_stock', None)
        if in_stock is not None:
            if in_stock.lower() == 'true':
                queryset = queryset.filter(stock__gt=0)
            elif in_stock.lower() == 'false':
                queryset = queryset.filter(stock=0)
        
        return queryset
    
    def list(self, request, *args, **kwargs):
        # Create cache key based on query params
        query_params = request.query_params.dict()
        cache_key = f"products_list_{hash(frozenset(query_params.items()))}"
        
        # Try to get from cache
        cached_data = cache.get(cache_key)
        
        if cached_data is not None:
            return Response(cached_data)
        
        # Cache miss - get from database
        response = super().list(request, *args, **kwargs)
        
        # Store in cache for 1 hour
        cache.set(cache_key, response.data, CACHE_TTL)
        
        return response
    
    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        
        # Invalidate all product list caches
        self._invalidate_product_cache()
        
        return response
    
    def update(self, request, *args, **kwargs):
        response = super().update(request, *args, **kwargs)
        
        # Invalidate caches when product is updated
        self._invalidate_product_cache()
        
        return response
    
    def destroy(self, request, *args, **kwargs):
        response = super().destroy(request, *args, **kwargs)
        
        # Invalidate caches when product is deleted
        self._invalidate_product_cache()
        
        return response
    
    def _invalidate_product_cache(self):
        """Helper method to clear product caches"""
        # Delete all keys that start with 'products_list'
        keys_pattern = 'ecommerce:products_list*'
        # Note: Again I am keeping it simple . definitely not apt for production 
        cache.delete_pattern('products_list*')
    
    @action(detail=False, methods=['get'])
    def low_stock(self, request):
        """Custom endpoint to get products with low stock (less than 10)"""
        products = self.get_queryset().filter(stock__lt=10, stock__gt=0)
        serializer = self.get_serializer(products, many=True)
        return Response(serializer.data)