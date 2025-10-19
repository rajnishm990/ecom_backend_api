from django.db import models
from django.contrib.auth.models import User
from products.models import Product


ORDER_STATUS = (
    ('pending', 'Pending'),
    ('shipped', 'Shipped'),
    ('delivered', 'Delivered'),
)


class Order(models.Model):
    """
    Order model - represents a customer order
    Links user with products through OrderItems
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    status = models.CharField(max_length=20, choices=ORDER_STATUS, default='pending')
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    shipping_address = models.TextField()
    phone_number = models.CharField(max_length=15)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Order #{self.id} by {self.user.username}"
    
    def calculate_total(self):
        """Calculate total price from all order items"""
        total = sum(item.subtotal for item in self.items.all())
        self.total_price = total
        self.save()
        return total
    
    class Meta:
        ordering = ['-created_at']


class OrderItem(models.Model):
    """
    OrderItem - represents individual products in an order
    Acts as a through model between Order and Product
    """
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)  # Price at time of order
    
    def __str__(self):
        return f"{self.quantity}x {self.product.name} in Order #{self.order.id}"
    
    @property
    def subtotal(self):
        """Calculate subtotal for this item"""
        return self.quantity * self.price
    
    class Meta:
        unique_together = ['order', 'product'] 


class Cart(models.Model):
    """
    Shopping cart model - temporary storage before checkout
    Each user has one cart
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='cart')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Cart of {self.user.username}"
    
    def get_total(self):
        """Calculate total price of all items in cart"""
        return sum(item.subtotal for item in self.cart_items.all())
    
    def item_count(self):
        """Total number of items in cart"""
        return sum(item.quantity for item in self.cart_items.all())


class CartItem(models.Model):
    """
    CartItem - individual products in shopping cart
    """
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='cart_items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)
    added_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.quantity}x {self.product.name}"
    
    @property
    def subtotal(self):
        """Calculate subtotal for this cart item"""
        return self.quantity * self.product.price
    
    class Meta:
        unique_together = ['cart', 'product']