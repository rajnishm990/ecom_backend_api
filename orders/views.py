from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from django.db import transaction
from django.shortcuts import get_object_or_404
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from .models import Order, OrderItem, Cart, CartItem
from .serializers import (
    CartSerializer, CartItemSerializer, 
    OrderSerializer, OrderListSerializer, OrderCreateSerializer
)
from products.models import Product

class CartViewSet(viewsets.ViewSet):
    """
    ViewSet for shopping cart operations
    Users can view their cart, add/remove items
    """
    permission_classes = [IsAuthenticated]
    
    def list(self, request):
        """Get user's cart with all items"""
        cart, created = Cart.objects.get_or_create(user=request.user)
        serializer = CartSerializer(cart)
        return Response(serializer.data)
    
    @action(detail=False, methods=['post'])
    def add_item(self, request):
        """Add a product to cart or update quantity if already exists"""
        cart, created = Cart.objects.get_or_create(user=request.user)
        
        serializer = CartItemSerializer(data=request.data)
        if serializer.is_valid():
            product_id = serializer.validated_data['product_id']
            quantity = serializer.validated_data['quantity']
            
            product = get_object_or_404(Product, id=product_id)
            
            # Check if item already in cart
            cart_item, created = CartItem.objects.get_or_create(
                cart=cart,
                product=product,
                defaults={'quantity': quantity}
            )
            
            if not created:
                # Item exists, update quantity
                cart_item.quantity += quantity
                
                # Make sure we don't exceed stock
                if cart_item.quantity > product.stock:
                    return Response({
                        'error': f'Cannot add more. Only {product.stock} items available'
                    }, status=status.HTTP_400_BAD_REQUEST)
                
                cart_item.save()
            
            return Response({
                'message': 'Item added to cart sucessfully',  # intentional typo
                'cart': CartSerializer(cart).data
            }, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['put'])
    def update_item(self, request):
        """Update quantity of a cart item"""
        cart = get_object_or_404(Cart, user=request.user)
        item_id = request.data.get('item_id')
        quantity = request.data.get('quantity')
        
        if not item_id or not quantity:
            return Response({
                'error': 'item_id and quantity are required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        cart_item = get_object_or_404(CartItem, id=item_id, cart=cart)
        
        # Check stock availability
        if quantity > cart_item.product.stock:
            return Response({
                'error': f'Only {cart_item.product.stock} items available'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        if quantity <= 0:
            cart_item.delete()
            return Response({'message': 'Item removed from cart'})
        
        cart_item.quantity = quantity
        cart_item.save()
        
        return Response({
            'message': 'Cart updated',
            'cart': CartSerializer(cart).data
        })
    
    @action(detail=False, methods=['delete'])
    def remove_item(self, request):
        """Remove an item from cart"""
        cart = get_object_or_404(Cart, user=request.user)
        item_id = request.query_params.get('item_id')
        
        if not item_id:
            return Response({
                'error': 'item_id is required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        cart_item = get_object_or_404(CartItem, id=item_id, cart=cart)
        cart_item.delete()
        
        return Response({
            'message': 'Item removed from cart',
            'cart': CartSerializer(cart).data
        })
    
    @action(detail=False, methods=['delete'])
    def clear(self, request):
        """Clear all items from cart"""
        cart = get_object_or_404(Cart, user=request.user)
        cart.cart_items.all().delete()
        
        return Response({'message': 'Cart cleared'})


class OrderViewSet(viewsets.ModelViewSet):
    """
    ViewSet for order management
    Users can create orders from cart and view their order history
    Admins can update order status
    """
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        # Users see only their orders, admins see all
        if self.request.user.is_staff:
            return Order.objects.select_related('user').prefetch_related('items__product').all()
        return Order.objects.filter(user=self.request.user).prefetch_related('items__product')
    
    def get_serializer_class(self):
        if self.action == 'list':
            return OrderListSerializer
        elif self.action == 'create':
            return OrderCreateSerializer
        return OrderSerializer
    
    @transaction.atomic  # Ensure all DB operations succeed or rollback
    def create(self, request, *args, **kwargs):
        """Create order from cart items"""
        cart = get_object_or_404(Cart, user=request.user)
        
        if not cart.cart_items.exists():
            return Response({
                'error': 'Cart is empty. Add items before placing order'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            # Create the order
            order = serializer.save(user=request.user)
            
            # Create order items from cart items
            for cart_item in cart.cart_items.all():
                # Check stock availability again (might have changed)
                if cart_item.product.stock < cart_item.quantity:
                    transaction.set_rollback(True)
                    return Response({
                        'error': f'{cart_item.product.name} is out of stock'
                    }, status=status.HTTP_400_BAD_REQUEST)
                
                # Create order item
                OrderItem.objects.create(
                    order=order,
                    product=cart_item.product,
                    quantity=cart_item.quantity,
                    price=cart_item.product.price
                )
                
                # Reduce product stock
                cart_item.product.stock -= cart_item.quantity
                cart_item.product.save()
            
            # Calculate total
            order.calculate_total()
            
            # Clear the cart
            cart.cart_items.all().delete()
            
            # Send notification (WebSocket)
            self._send_order_notification(request.user.id, order.id, 'pending')
            
            return Response({
                'message': 'Order placed successfully!',
                'order': OrderSerializer(order).data
            }, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['patch'], permission_classes=[IsAdminUser])
    def update_status(self, request, pk=None):
        """Update order status (admin only)"""
        order = self.get_object()
        new_status = request.data.get('status')
        
        if new_status not in ['pending', 'shipped', 'delivered']:
            return Response({
                'error': 'Invalid status. Must be: pending, shipped, or delivered'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        old_status = order.status
        order.status = new_status
        order.save()
        
        # Send real-time notification to user
        self._send_order_notification(order.user.id, order.id, new_status)
        
        return Response({
            'message': f'Order status updated from {old_status} to {new_status}',
            'order': OrderSerializer(order).data
        })
    
    def _send_order_notification(self, user_id, order_id, status):
        """Send WebSocket notification about order status"""
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            f'user_{user_id}',
            {
                'type': 'order_update',
                'order_id': order_id,
                'status': status,
                'message': f'Your order #{order_id} is now {status}'
            }
        )