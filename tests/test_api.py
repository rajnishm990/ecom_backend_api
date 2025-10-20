from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework import status
from products.models import Category, Product
from orders.models import Cart, Order

class UserAuthenticationTests(TestCase):
    """Test cases for user registration and login"""
    
    def setUp(self):
        self.client = APIClient()
        self.register_url = '/api/auth/register/'
        self.login_url = '/api/auth/login/'
    
    def test_user_registration(self):
        """Test user can register with valid data"""
        data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'testpass123',
            'password2': 'testpass123',
            'first_name': 'Test',
            'last_name': 'User'
        }
        response = self.client.post(self.register_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('tokens', response.data)
        self.assertTrue(User.objects.filter(username='testuser').exists())
    
    def test_user_login(self):
        """Test user can login with correct credentials"""
        # Create user first
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        # Try to login
        data = {
            'username': 'testuser',
            'password': 'testpass123'
        }
        response = self.client.post(self.login_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('tokens', response.data)


class ProductTests(TestCase):
    """Test cases for product management"""
    
    def setUp(self):
        self.client = APIClient()
        
        # Create admin user
        self.admin = User.objects.create_superuser(
            username='admin',
            email='admin@test.com',
            password='admin123'
        )
        
        # Create regular user
        self.user = User.objects.create_user(
            username='user',
            email='user@test.com',
            password='user123'
        )
        
        # Create category
        self.category = Category.objects.create(
            name='Electronics',
            description='Electronic items'
        )
    
    def test_list_products_public(self):
        """Test anyone can view products list"""
        response = self.client.get('/api/products/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_create_product_admin_only(self):
        """Test only admins can create products"""
        # Try without authentication
        data = {
            'name': 'Test Product',
            'description': 'Test description',
            'price': 99.99,
            'stock': 10,
            'category': self.category.id
        }
        response = self.client.post('/api/products/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        
        # Try with regular user
        self.client.force_authenticate(user=self.user)
        response = self.client.post('/api/products/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        
        # Try with admin
        self.client.force_authenticate(user=self.admin)
        response = self.client.post('/api/products/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
    
    def test_product_filtering(self):
        """Test product filtering by category and price"""
        # Create some products
        Product.objects.create(
            name='Laptop',
            description='High-end laptop',
            price=1200.00,
            stock=50,
            category=self.category
        )
        Product.objects.create(
            name='Mouse',
            description='Wireless mouse',
            price=25.00,
            stock=100,
            category=self.category
        )
        
        # Filter by price range
        response = self.client.get('/api/products/?min_price=30&max_price=1500')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Should only return laptop (price > 30)
        
        # Filter by category
        response = self.client.get(f'/api/products/?category={self.category.id}')
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class CartTests(TestCase):
    """Test cases for shopping cart functionality"""
    
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@test.com',
            password='pass123'
        )
        self.client.force_authenticate(user=self.user)
        
        # Create category and product
        self.category = Category.objects.create(name='Test Category')
        self.product = Product.objects.create(
            name='Test Product',
            description='Test',
            price=50.00,
            stock=10,
            category=self.category
        )
    
    def test_add_item_to_cart(self):
        """Test adding items to cart"""
        data = {
            'product_id': self.product.id,
            'quantity': 2
        }
        response = self.client.post('/api/orders/cart/add_item/', data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('cart', response.data)
        
        # Verify cart was created
        self.assertTrue(Cart.objects.filter(user=self.user).exists())
    
    def test_add_item_exceeds_stock(self):
        """Test cannot add more items than available stock"""
        data = {
            'product_id': self.product.id,
            'quantity': 20  # More than stock (10)
        }
        response = self.client.post('/api/orders/cart/add_item/', data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class OrderTests(TestCase):
    """Test cases for order placement"""
    
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@test.com',
            password='pass123'
        )
        self.client.force_authenticate(user=self.user)
        
        # Create product
        self.category = Category.objects.create(name='Test')
        self.product = Product.objects.create(
            name='Test Product',
            description='Test',
            price=100.00,
            stock=10,
            category=self.category
        )
        
        # Add item to cart
        cart = Cart.objects.create(user=self.user)
        from orders.models import CartItem
        CartItem.objects.create(
            cart=cart,
            product=self.product,
            quantity=2
        )
    
    def test_place_order_from_cart(self):
        """Test placing an order from cart"""
        data = {
            'shipping_address': '123 Test Street, Test City, 12345',
            'phone_number': '+1234567890'
        }
        response = self.client.post('/api/orders/', data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Verify order was created
        self.assertTrue(Order.objects.filter(user=self.user).exists())
        
        # Verify stock was reduced
        self.product.refresh_from_db()
        self.assertEqual(self.product.stock, 8)  # 10 - 2
        
        # Verify cart was cleared
        cart = Cart.objects.get(user=self.user)
        self.assertEqual(cart.cart_items.count(), 0)
    
    def test_cannot_order_empty_cart(self):
        """Test cannot place order with empty cart"""
        # Clear cart first
        cart = Cart.objects.get(user=self.user)
        cart.cart_items.all().delete()
        
        data = {
            'shipping_address': '123 Test Street',
            'phone_number': '+1234567890'
        }
        response = self.client.post('/api/orders/', data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
