#  E-Commerce API with Real-Time Notifications

A powerful Django REST Framework e-commerce API featuring JWT authentication, Redis caching, real-time WebSocket notifications, and comprehensive order management system.


##  Tech Stack

- **Framework:** Django 4.2.7 & Django REST Framework 3.14.0
- **Database:** PostgreSQL
- **Cache:** Redis
- **Authentication:** JWT (SimpleJWT)
- **WebSockets:** Django Channels with Redis backend
- **Server:** Daphne (ASGI)

---

## Project Structure

```
ecommerce_api/
├── ecommerce_api/          # Main project config
│   ├── settings.py         # Settings & configurations
│   ├── urls.py            # Main URL routing
│   └── asgi.py            # ASGI config for WebSockets
├── users/                  # User management
│   ├── models.py          # UserProfile model
│   ├── serializers.py     # User serializers
│   └── views.py           # Auth & profile endpoints
├── products/               # Product management
│   ├── models.py          # Product & Category models
│   ├── views.py           # CRUD with caching
│   └── serializers.py     # Product serializers
├── orders/                 # Order system
│   ├── models.py          # Order, Cart models
│   ├── views.py           # Cart & order logic
│   ├── consumers.py       # WebSocket consumer
│   └── routing.py         # WebSocket routing
├── requirements.txt
├── .env.example
└── README.md
```

---

##  Setup Instructions

### Prerequisites
- Python 3.8+
- PostgreSQL
- Redis Server

### 1. Clone the Repository
```bash
git clone <your-repo-url>
cd ecommerce_api
```

### 2. Create Virtual Environment
```bash
python -m venv venv

# On Windows
venv\Scripts\activate

# On Linux/Mac
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Setup PostgreSQL Database
```sql
-- Login to PostgreSQL
psql -U postgres

-- Create database
CREATE DATABASE ecommerce_db;

-- Create user (optional)
CREATE USER ecommerce_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE ecommerce_db TO ecommerce_user;
```

### 5. Setup Redis
Make sure Redis is installed and running:
```bash
# On Ubuntu/Debian
sudo apt-get install redis-server
sudo systemctl start redis

# On macOS
brew install redis
brew services start redis

# On Windows
# Download from: https://github.com/microsoftarchive/redis/releases
```

### 6. Configure Environment Variables
Copy `.env.example` to `.env` and update values:
```bash
cp .env.example .env
```

Edit `.env` file:
```env
SECRET_KEY=your-super-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

DB_NAME=ecommerce_db
DB_USER=postgres
DB_PASSWORD=your_password
DB_HOST=localhost
DB_PORT=5432

REDIS_URL=redis://127.0.0.1:6379/1
```

### 7. Run Migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

### 8. Create Superuser (Admin)
```bash
python manage.py createsuperuser
```

### 9. Run the Server
```bash
# Use Daphne for WebSocket support
daphne -b 0.0.0.0 -p 8000 ecommerce_api.asgi:application

# OR use Django development server (limited WebSocket support)
python manage.py runserver
```

The API will be available at: `http://localhost:8000/`

---

## API Documentation

### Base URL
```
http://localhost:8000/api/
```

### Authentication Endpoints

#### Register User
```http
POST /api/auth/register/
Content-Type: application/json

{
    "username": "john_doe",
    "email": "john@example.com",
    "password": "securepass123",
    "password2": "securepass123",
    "first_name": "John",
    "last_name": "Doe"
}
```

**Response:**
```json
{
    "message": "User registered succesfully!",
    "user": {
        "username": "john_doe",
        "email": "john@example.com"
    },
    "tokens": {
        "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc...",
        "access": "eyJ0eXAiOiJKV1QiLCJhbGc..."
    }
}
```

#### Login
```http
POST /api/auth/login/
Content-Type: application/json

{
    "username": "john_doe",
    "password": "securepass123"
}
```

#### Refresh Token
```http
POST /api/auth/token/refresh/
Content-Type: application/json

{
    "refresh": "your-refresh-token"
}
```

#### Get/Update Profile
```http
GET /api/auth/profile/
Authorization: Bearer <access-token>

PUT /api/auth/profile/
Authorization: Bearer <access-token>
Content-Type: application/json

{
    "first_name": "John",
    "last_name": "Doe",
    "phone_number": "+1234567890",
    "address": "123 Main St",
    "city": "New York",
    "postal_code": "10001",
    "country": "USA"
}
```

---

### Product Endpoints

#### List Products (with filtering & pagination)
```http
GET /api/products/?page=1
GET /api/products/?category=1
GET /api/products/?min_price=10&max_price=100
GET /api/products/?in_stock=true
GET /api/products/?search=laptop
```

#### Get Product Details
```http
GET /api/products/1/
```

#### Create Product (Admin Only)
```http
POST /api/products/
Authorization: Bearer <admin-access-token>
Content-Type: application/json

{
    "name": "Gaming Laptop",
    "description": "High performance gaming laptop",
    "price": 1299.99,
    "stock": 50,
    "category": 1
}
```

#### Update Product (Admin Only)
```http
PUT /api/products/1/
Authorization: Bearer <admin-access-token>
Content-Type: application/json

{
    "name": "Gaming Laptop Pro",
    "price": 1499.99,
    "stock": 45
}
```

#### Delete Product (Admin Only)
```http
DELETE /api/products/1/
Authorization: Bearer <admin-access-token>
```

#### Low Stock Products
```http
GET /api/products/low_stock/
```

---

### Category Endpoints

#### List Categories
```http
GET /api/products/categories/
```

#### Create Category (Admin Only)
```http
POST /api/products/categories/
Authorization: Bearer <admin-access-token>
Content-Type: application/json

{
    "name": "Electronics",
    "description": "Electronic devices and gadgets"
}
```

---

### Shopping Cart Endpoints

#### Get Cart
```http
GET /api/orders/cart/
Authorization: Bearer <access-token>
```

#### Add Item to Cart
```http
POST /api/orders/cart/add_item/
Authorization: Bearer <access-token>
Content-Type: application/json

{
    "product_id": 1,
    "quantity": 2
}
```

#### Update Cart Item
```http
PUT /api/orders/cart/update_item/
Authorization: Bearer <access-token>
Content-Type: application/json

{
    "item_id": 1,
    "quantity": 3
}
```

#### Remove Item from Cart
```http
DELETE /api/orders/cart/remove_item/?item_id=1
Authorization: Bearer <access-token>
```

#### Clear Cart
```http
DELETE /api/orders/cart/clear/
Authorization: Bearer <access-token>
```

---

### Order Endpoints

#### List Orders (User's orders)
```http
GET /api/orders/
Authorization: Bearer <access-token>
```

#### Get Order Details
```http
GET /api/orders/1/
Authorization: Bearer <access-token>
```

#### Place Order (from cart)
```http
POST /api/orders/
Authorization: Bearer <access-token>
Content-Type: application/json

{
    "shipping_address": "123 Main Street, Apt 4B, New York, NY 10001",
    "phone_number": "+1234567890"
}
```

#### Update Order Status (Admin Only)
```http
PATCH /api/orders/1/update_status/
Authorization: Bearer <admin-access-token>
Content-Type: application/json

{
    "status": "shipped"
}
```

---

### WebSocket Connection

Connect to WebSocket for real-time order notifications:

```javascript
// WebSocket URL
ws://localhost:8000/ws/orders/notifications/

// Example JavaScript client
const socket = new WebSocket('ws://localhost:8000/ws/orders/notifications/');

socket.onopen = function(e) {
    console.log('Connected to order notifications');
};

socket.onmessage = function(event) {
    const data = JSON.parse(event.data);
    console.log('Notification:', data);
    
    if (data.type === 'order_update') {
        console.log(`Order #${data.order_id} is now ${data.status}`);
        alert(data.message);
    }
};
```

**Notification Format:**
```json
{
    "type": "order_update",
    "order_id": 1,
    "status": "shipped",
    "message": "Your order #1 is now shipped"
}
```

---

##  Testing the API

### Using cURL

```bash
# Register a user
curl -X POST http://localhost:8000/api/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "email": "test@example.com",
    "password": "testpass123",
    "password2": "testpass123"
  }'

# Login
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "password": "testpass123"
  }'

# Get products (with token)
curl -X GET http://localhost:8000/api/products/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### Using Postman

1. Import the API endpoints
2. Set environment variable for `access_token`
3. Use Bearer Token authentication
4. Test all endpoints

---

