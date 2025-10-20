"""
Dummy Data Seeder Script
This script creates sample data for testing the e-commerce API
Run: python manage.py shell < seed_database.py
Or: docker-compose exec web python manage.py shell < seed_database.py
"""

import os
import sys
import django
import random

# Django setup
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ecommerce_backend.settings")
django.setup()

import random
from django.contrib.auth.models import User
from products.models import Category, Product
from orders.models import Cart, CartItem, Order, OrderItem
from users.models import UserProfile

print("=" * 60)
print("Starting Database Seeding...")
print("=" * 60)

# Create Superuser
print("\nCreating superuser...")
if not User.objects.filter(username='admin').exists():
    admin = User.objects.create_superuser(
        username='admin',
        email='admin@admin.com',
        password='admin123',
        first_name='Admin',
        last_name='User'
    )
    print(f" Superuser created: {admin.username}")
else:
    admin = User.objects.get(username='admin')
    print(f" Superuser already exists: {admin.username}")

# Create Regular Users
print("\n Creating regular users...")
users_data = [
    {'username': 'john_doe', 'email': 'john@example.com', 'password': 'pass123', 'first_name': 'John', 'last_name': 'Doe'},
    {'username': 'jane_smith', 'email': 'jane@example.com', 'password': 'pass123', 'first_name': 'Jane', 'last_name': 'Smith'},
    {'username': 'bob_wilson', 'email': 'bob@example.com', 'password': 'pass123', 'first_name': 'Bob', 'last_name': 'Wilson'},
    {'username': 'alice_brown', 'email': 'alice@example.com', 'password': 'pass123', 'first_name': 'Alice', 'last_name': 'Brown'},
    {'username': 'charlie_davis', 'email': 'charlie@example.com', 'password': 'pass123', 'first_name': 'Charlie', 'last_name': 'Davis'},
]

created_users = []
for user_data in users_data:
    user, created = User.objects.get_or_create(
        username=user_data['username'],
        defaults={
            'email': user_data['email'],
            'first_name': user_data['first_name'],
            'last_name': user_data['last_name']
        }
    )
    if created:
        user.set_password(user_data['password'])
        user.save()
        print(f"✓ User created: {user.username}")
    else:
        print(f"  User exists: {user.username}")
    
    # Create/update profile
    profile, prof_created = UserProfile.objects.get_or_create(
        user=user,
        defaults={
            'phone_number': f'+1-555-{random.randint(1000, 9999)}',
            'address': f'{random.randint(100, 999)} Main Street',
            'city': random.choice(['New York', 'Los Angeles', 'Chicago', 'Houston', 'Phoenix']),
            'postal_code': f'{random.randint(10000, 99999)}',
            'country': 'USA'
        }
    )
    created_users.append(user)

print(f"Total users: {len(created_users)}")

# Create Categories
print("\n Creating categories...")
categories_data = [
    {'name': 'Electronics', 'description': 'Electronic devices, computers, phones, and accessories'},
    {'name': 'Clothing', 'description': 'Fashion, apparel, shoes, and accessories'},
    {'name': 'Books', 'description': 'Books, magazines, educational materials, and e-books'},
    {'name': 'Home & Kitchen', 'description': 'Home appliances, furniture, and kitchen essentials'},
    {'name': 'Sports & Outdoors', 'description': 'Sports equipment, outdoor gear, and fitness products'},
    {'name': 'Toys & Games', 'description': 'Toys, board games, video games, and hobby items'},
    {'name': 'Beauty & Health', 'description': 'Cosmetics, skincare, health supplements, and wellness products'},
    {'name': 'Automotive', 'description': 'Car accessories, tools, and automotive parts'},
]

categories = []
for cat_data in categories_data:
    category, created = Category.objects.get_or_create(
        name=cat_data['name'],
        defaults={'description': cat_data['description']}
    )
    if created:
        print(f" Category created: {category.name}")
    else:
        print(f"  Category exists: {category.name}")
    categories.append(category)

# Create Products
print("\n Creating products...")
products_data = [
    # Electronics
    {'name': 'iPhone 15 Pro Max', 'description': 'Latest Apple smartphone with A17 Pro chip, titanium design', 'price': 1199.99, 'stock': 45, 'category': 'Electronics'},
    {'name': 'Samsung Galaxy S24 Ultra', 'description': 'Premium Android flagship with S Pen and AI features', 'price': 1099.99, 'stock': 38, 'category': 'Electronics'},
    {'name': 'MacBook Pro 16" M3', 'description': 'Powerful laptop for professionals with M3 Max chip', 'price': 2499.99, 'stock': 22, 'category': 'Electronics'},
    {'name': 'Dell XPS 15', 'description': 'High-performance Windows laptop with InfinityEdge display', 'price': 1799.99, 'stock': 30, 'category': 'Electronics'},
    {'name': 'iPad Air 5th Gen', 'description': 'Versatile tablet with M1 chip and Apple Pencil support', 'price': 599.99, 'stock': 55, 'category': 'Electronics'},
    {'name': 'AirPods Pro 2', 'description': 'Premium wireless earbuds with active noise cancellation', 'price': 249.99, 'stock': 120, 'category': 'Electronics'},
    {'name': 'Sony WH-1000XM5', 'description': 'Industry-leading noise canceling headphones', 'price': 399.99, 'stock': 65, 'category': 'Electronics'},
    {'name': 'Apple Watch Series 9', 'description': 'Advanced fitness and health tracking smartwatch', 'price': 429.99, 'stock': 80, 'category': 'Electronics'},
    {'name': 'Nintendo Switch OLED', 'description': 'Hybrid gaming console with vibrant OLED screen', 'price': 349.99, 'stock': 42, 'category': 'Electronics'},
    {'name': 'PlayStation 5', 'description': 'Next-gen gaming console with 4K gaming', 'price': 499.99, 'stock': 15, 'category': 'Electronics'},
    
    # Clothing
    {'name': 'Levi\'s 501 Jeans', 'description': 'Classic straight fit denim jeans', 'price': 69.99, 'stock': 150, 'category': 'Clothing'},
    {'name': 'Nike Air Max 90', 'description': 'Iconic sneakers with visible Air cushioning', 'price': 129.99, 'stock': 95, 'category': 'Clothing'},
    {'name': 'Adidas Ultraboost', 'description': 'Premium running shoes with Boost technology', 'price': 189.99, 'stock': 78, 'category': 'Clothing'},
    {'name': 'North Face Jacket', 'description': 'Waterproof winter jacket for outdoor adventures', 'price': 279.99, 'stock': 45, 'category': 'Clothing'},
    {'name': 'Ralph Lauren Polo Shirt', 'description': 'Classic cotton polo shirt', 'price': 89.99, 'stock': 200, 'category': 'Clothing'},
    
    # Books
    {'name': 'The Great Gatsby', 'description': 'Classic American novel by F. Scott Fitzgerald', 'price': 14.99, 'stock': 300, 'category': 'Books'},
    {'name': 'Atomic Habits', 'description': 'Bestselling self-help book by James Clear', 'price': 19.99, 'stock': 250, 'category': 'Books'},
    {'name': 'Python Crash Course', 'description': 'Comprehensive Python programming guide', 'price': 39.99, 'stock': 120, 'category': 'Books'},
    {'name': 'Harry Potter Box Set', 'description': 'Complete 7-book collection by J.K. Rowling', 'price': 89.99, 'stock': 85, 'category': 'Books'},
    
    # Home & Kitchen
    {'name': 'KitchenAid Mixer', 'description': 'Professional stand mixer for baking', 'price': 399.99, 'stock': 35, 'category': 'Home & Kitchen'},
    {'name': 'Dyson V15 Vacuum', 'description': 'Cordless vacuum with laser detection', 'price': 649.99, 'stock': 28, 'category': 'Home & Kitchen'},
    {'name': 'Ninja Air Fryer', 'description': 'Multi-function air fryer for healthy cooking', 'price': 129.99, 'stock': 90, 'category': 'Home & Kitchen'},
    {'name': 'Instant Pot Duo', 'description': '7-in-1 electric pressure cooker', 'price': 89.99, 'stock': 110, 'category': 'Home & Kitchen'},
    
    # Sports & Outdoors
    {'name': 'Yeti Cooler 45', 'description': 'Rugged cooler for outdoor adventures', 'price': 349.99, 'stock': 42, 'category': 'Sports & Outdoors'},
    {'name': 'Hydro Flask 32oz', 'description': 'Insulated stainless steel water bottle', 'price': 44.99, 'stock': 180, 'category': 'Sports & Outdoors'},
    {'name': 'Peloton Bike', 'description': 'Connected fitness bike with live classes', 'price': 1445.00, 'stock': 12, 'category': 'Sports & Outdoors'},
    
    # Toys & Games
    {'name': 'LEGO Star Wars Set', 'description': 'Millennium Falcon building set', 'price': 159.99, 'stock': 65, 'category': 'Toys & Games'},
    {'name': 'PlayStation 5 Controller', 'description': 'DualSense wireless controller', 'price': 69.99, 'stock': 145, 'category': 'Toys & Games'},
    {'name': 'Monopoly Board Game', 'description': 'Classic family board game', 'price': 24.99, 'stock': 220, 'category': 'Toys & Games'},
    
    # Beauty & Health
    {'name': 'Dyson Hair Dryer', 'description': 'Professional fast-drying hair dryer', 'price': 429.99, 'stock': 38, 'category': 'Beauty & Health'},
    {'name': 'Fitbit Charge 6', 'description': 'Advanced fitness tracker with GPS', 'price': 159.99, 'stock': 92, 'category': 'Beauty & Health'},
    
    # Automotive
    {'name': 'Garmin Dash Cam', 'description': 'HD dash camera with GPS', 'price': 199.99, 'stock': 55, 'category': 'Automotive'},
    {'name': 'Car Phone Mount', 'description': 'Magnetic phone holder for car', 'price': 19.99, 'stock': 300, 'category': 'Automotive'},
]

products = []
for prod_data in products_data:
    category = Category.objects.get(name=prod_data['category'])
    product, created = Product.objects.get_or_create(
        name=prod_data['name'],
        defaults={
            'description': prod_data['description'],
            'price': prod_data['price'],
            'stock': prod_data['stock'],
            'category': category
        }
    )
    if created:
        print(f" Product created: {product.name}")
    else:
        print(f"  Product exists: {product.name}")
    products.append(product)

print(f" Total products: {len(products)}")

# Create Shopping Carts with Items
print("\n Creating shopping carts...")
for i, user in enumerate(created_users[:3]):  # First 3 users get carts
    cart, created = Cart.objects.get_or_create(user=user)
    
    # Add random products to cart
    num_items = random.randint(1, 4)
    cart_products = random.sample(products, num_items)
    
    for product in cart_products:
        if product.stock > 0:
            quantity = random.randint(1, min(3, product.stock))
            cart_item, item_created = CartItem.objects.get_or_create(
                cart=cart,
                product=product,
                defaults={'quantity': quantity}
            )
            if item_created:
                print(f"  ✓ Added {quantity}x {product.name} to {user.username}'s cart")

# Create Orders
print("\n Creating sample orders...")
for i, user in enumerate(created_users[:4]):  # First 4 users get orders
    # Create 1-2 orders per user
    num_orders = random.randint(1, 2)
    
    for j in range(num_orders):
        # Select random products
        order_products = random.sample(products, random.randint(1, 4))
        
        # Create order
        order = Order.objects.create(
            user=user,
            status=random.choice(['pending', 'shipped', 'delivered']),
            shipping_address=f"{random.randint(100, 999)} {random.choice(['Main', 'Oak', 'Elm', 'Pine'])} Street, {random.choice(['New York', 'LA', 'Chicago'])}, {random.randint(10000, 99999)}",
            phone_number=f"+1-555-{random.randint(1000, 9999)}"
        )
        
        # Add order items
        total = 0
        for product in order_products:
            if product.stock > 0:
                quantity = random.randint(1, min(2, product.stock))
                OrderItem.objects.create(
                    order=order,
                    product=product,
                    quantity=quantity,
                    price=product.price
                )
                total += float(product.price) * quantity
        
        order.total_price = total
        order.save()
        
        print(f"  ✓ Order #{order.id} created for {user.username} (${total:.2f})")

print("\n" + "=" * 60)
print(" Database seeding completed!")
print("=" * 60)

# Print summary
print("\n Summary:")
print(f"   Users: {User.objects.count()}")
print(f"   Categories: {Category.objects.count()}")
print(f"   Products: {Product.objects.count()}")
print(f"   Active Carts: {Cart.objects.count()}")
print(f"   Orders: {Order.objects.count()}")
print(f"   Order Items: {OrderItem.objects.count()}")

print("\n Test Accounts:")
print("  Admin:")
print("    username: admin")
print("    password: admin123")
print("\n  Regular Users:")
for user_data in users_data[:3]:
    print(f"    username: {user_data['username']}, password: pass123")

print("\n" + "=" * 60)