# UPBolis API Documentation

This document describes the API endpoints for the UPBolis system. The base URL for all endpoints is:

```
http://api.gaelarianafernandomiguel.nicolascresposu.com/api
```

## Authentication

Most endpoints require authentication using a Bearer token obtained from login. Include the token in the `Authorization` header:

```
Authorization: Bearer YOUR_TOKEN_HERE
```

## Endpoints

### Public Endpoints (No Authentication Required)

#### POST /auth/register
Creates a new buyer account.

**Request Body:**
```json
{
  "name": "John Doe",
  "email": "john@example.com",
  "password": "password123",
  "password_confirmation": "password123"
}
```

**Response (201):**
```json
{
  "user": {
    "id": 1,
    "name": "John Doe",
    "email": "john@example.com",
    "role": "buyer"
  },
  "token": "your_sanctum_token"
}
```

**Example:**
```bash
curl -X POST http://api.gaelarianafernandomiguel.nicolascresposu.com/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"name":"John Doe","email":"john@example.com","password":"password123","password_confirmation":"password123"}'
```

#### POST /auth/login
Logs in a user and returns a token.

**Request Body:**
```json
{
  "email": "john@example.com",
  "password": "password123"
}
```

**Response (200):**
```json
{
  "user": {
    "id": 1,
    "name": "John Doe",
    "email": "john@example.com",
    "role": "buyer"
  },
  "token": "your_sanctum_token"
}
```

**Example:**
```bash
curl -X POST http://api.gaelarianafernandomiguel.nicolascresposu.com/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"john@example.com","password":"password123"}'
```

### Authenticated Endpoints

#### GET /auth/me
Returns the current user's profile.

**Response (200):**
```json
{
  "id": 1,
  "name": "John Doe",
  "email": "john@example.com",
  "role": "buyer",
  "webhook_url": null
}
```

**Example:**
```bash
curl -X GET http://api.gaelarianafernandomiguel.nicolascresposu.com/api/auth/me \
  -H "Authorization: Bearer YOUR_TOKEN"
```

#### POST /auth/logout
Logs out the current user (invalidates token).

**Response (200):**
```json
{
  "message": "Sesión cerrada."
}
```

**Example:**
```bash
curl -X POST http://api.gaelarianafernandomiguel.nicolascresposu.com/api/auth/logout \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Wallet Endpoints

#### GET /wallet
Returns the current user's wallet balance and details.

**Response (200):**
```json
{
  "id": 1,
  "user_id": 1,
  "balance": 100.00
}
```

**Example:**
```bash
curl -X GET http://api.gaelarianafernandomiguel.nicolascresposu.com/api/wallet \
  -H "Authorization: Bearer YOUR_TOKEN"
```

#### POST /wallet/transfer
Transfers UPBolis to another user.

**Request Body:**
```json
{
  "to_user_id": 2,
  "amount": 50.00
}
```

**Response (200):**
```json
{
  "message": "Transfer successful"
}
```

**Example:**
```bash
curl -X POST http://api.gaelarianafernandomiguel.nicolascresposu.com/api/wallet/transfer \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{"to_user_id":2,"amount":50.00}'
```

#### POST /wallet/deposit
Adds balance to the current user's wallet (PoC).

**Request Body:**
```json
{
  "amount": 100.00
}
```

**Response (200):**
```json
{
  "message": "Deposit successful"
}
```

**Example:**
```bash
curl -X POST http://api.gaelarianafernandomiguel.nicolascresposu.com/api/wallet/deposit \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{"amount":100.00}'
```

#### GET /transactions
Returns the current user's transaction history.

**Response (200):**
```json
[
  {
    "id": 1,
    "from_wallet_id": 1,
    "to_wallet_id": 2,
    "amount": 50.00,
    "type": "transfer",
    "description": "Transfer to user",
    "created_at": "2025-12-14T10:00:00Z"
  }
]
```

**Example:**
```bash
curl -X GET http://api.gaelarianafernandomiguel.nicolascresposu.com/api/transactions \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Product Endpoints (General)

#### GET /products
Returns the catalog of active products.

**Response (200):**
```json
[
  {
    "id": 1,
    "name": "Product Name",
    "description": "Product description",
    "price": 10.00,
    "stock": 5,
    "is_active": true,
    "seller": {
      "id": 2,
      "name": "Seller Name"
    }
  }
]
```

**Example:**
```bash
curl -X GET http://api.gaelarianafernandomiguel.nicolascresposu.com/api/products \
  -H "Authorization: Bearer YOUR_TOKEN"
```

#### GET /products/{product}
Returns details of a specific product.

**Response (200):**
```json
{
  "id": 1,
  "name": "Product Name",
  "description": "Product description",
  "price": 10.00,
  "stock": 5,
  "is_active": true,
  "seller": {
    "id": 2,
    "name": "Seller Name"
  }
}
```

**Example:**
```bash
curl -X GET http://api.gaelarianafernandomiguel.nicolascresposu.com/api/products/1 \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Order Endpoints (Buyer)

#### GET /orders
Returns the current user's orders.

**Response (200):**
```json
[
  {
    "id": 1,
    "total_amount": 50.00,
    "status": "paid",
    "created_at": "2025-12-14T10:00:00Z",
    "items": [
      {
        "product_id": 1,
        "quantity": 2,
        "unit_price": 25.00,
        "subtotal": 50.00
      }
    ]
  }
]
```

**Example:**
```bash
curl -X GET http://api.gaelarianafernandomiguel.nicolascresposu.com/api/orders \
  -H "Authorization: Bearer YOUR_TOKEN"
```

#### GET /orders/{order}
Returns details of a specific order.

**Response (200):**
```json
{
  "id": 1,
  "total_amount": 50.00,
  "status": "paid",
  "created_at": "2025-12-14T10:00:00Z",
  "items": [
    {
      "product_id": 1,
      "quantity": 2,
      "unit_price": 25.00,
      "subtotal": 50.00
      }
    ]
  }
```

**Example:**
```bash
curl -X GET http://api.gaelarianafernandomiguel.nicolascresposu.com/api/orders/1 \
  -H "Authorization: Bearer YOUR_TOKEN"
```

#### POST /orders
Creates a new order (purchase).

**Request Body:**
```json
{
  "items": [
    {
      "product_id": 1,
      "quantity": 2
    }
  ]
}
```

**Response (201):**
```json
{
  "id": 1,
  "total_amount": 50.00,
  "status": "paid",
  "created_at": "2025-12-14T10:00:00Z"
}
```

**Example:**
```bash
curl -X POST http://api.gaelarianafernandomiguel.nicolascresposu.com/api/orders \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{"items":[{"product_id":1,"quantity":2}]}'
```

### Seller Endpoints (Requires Seller Role)

#### GET /seller/products
Returns products created by the current seller.

**Response (200):**
```json
[
  {
    "id": 1,
    "name": "Product Name",
    "description": "Product description",
    "price": 10.00,
    "stock": 5,
    "is_active": true
  }
]
```

**Example:**
```bash
curl -X GET http://api.gaelarianafernandomiguel.nicolascresposu.com/api/seller/products \
  -H "Authorization: Bearer YOUR_TOKEN"
```

#### POST /seller/products
Creates a new product.

**Request Body:**
```json
{
  "name": "New Product",
  "description": "Product description",
  "price": 15.00,
  "stock": 10
}
```

**Response (201):**
```json
{
  "id": 1,
  "name": "New Product",
  "description": "Product description",
  "price": 15.00,
  "stock": 10,
  "is_active": true
}
```

**Example:**
```bash
curl -X POST http://api.gaelarianafernandomiguel.nicolascresposu.com/api/seller/products \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{"name":"New Product","description":"Product description","price":15.00,"stock":10}'
```

#### PUT /seller/products/{product}
Updates a product owned by the seller.

**Request Body:**
```json
{
  "name": "Updated Product",
  "stock": 20,
  "is_active": true
}
```

**Response (200):**
```json
{
  "id": 1,
  "name": "Updated Product",
  "stock": 20,
  "is_active": true
}
```

**Example:**
```bash
curl -X PUT http://api.gaelarianafernandomiguel.nicolascresposu.com/api/seller/products/1 \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{"name":"Updated Product","stock":20,"is_active":true}'
```

#### DELETE /seller/products/{product}
Soft-deletes a product (sets is_active to false).

**Response (200):**
```json
{
  "message": "Product deactivated"
}
```

**Example:**
```bash
curl -X DELETE http://api.gaelarianafernandomiguel.nicolascresposu.com/api/seller/products/1 \
  -H "Authorization: Bearer YOUR_TOKEN"
```

#### GET /seller/orders
Returns orders containing the seller's products.

**Response (200):**
```json
[
  {
    "id": 1,
    "total_amount": 50.00,
    "status": "paid",
    "buyer": {
      "id": 3,
      "name": "Buyer Name"
    },
    "items": [
      {
        "product_id": 1,
        "quantity": 2,
        "unit_price": 25.00,
        "subtotal": 50.00
      }
    ]
  }
]
```

**Example:**
```bash
curl -X GET http://api.gaelarianafernandomiguel.nicolascresposu.com/api/seller/orders \
  -H "Authorization: Bearer YOUR_TOKEN"
```

#### GET /seller/orders/{order}
Returns details of a specific order containing the seller's products.

**Response (200):**
```json
{
  "id": 1,
  "total_amount": 50.00,
  "status": "paid",
  "buyer": {
    "id": 3,
    "name": "Buyer Name"
  },
  "items": [
    {
      "product_id": 1,
      "quantity": 2,
      "unit_price": 25.00,
      "subtotal": 50.00
    }
  ]
}
```

**Example:**
```bash
curl -X GET http://api.gaelarianafernandomiguel.nicolascresposu.com/api/seller/orders/1 \
  -H "Authorization: Bearer YOUR_TOKEN"
```

#### POST /seller/webhook
Sets the webhook URL for the seller to receive purchase notifications.

**Request Body:**
```json
{
  "url": "https://your-webhook-endpoint.com/notify"
}
```

**Response (200):**
```json
{
  "message": "Webhook updated",
  "webhook_url": "https://your-webhook-endpoint.com/notify"
}
```

**Example:**
```bash
curl -X POST http://api.gaelarianafernandomiguel.nicolascresposu.com/api/seller/webhook \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{"url":"https://your-webhook-endpoint.com/notify"}'
```

### Admin Endpoints (Requires Admin Role)

#### GET /admin/users
Returns a list of all users.

**Response (200):**
```json
[
  {
    "id": 1,
    "name": "User Name",
    "email": "user@example.com",
    "role": "buyer"
  }
]
```

**Example:**
```bash
curl -X GET http://api.gaelarianafernandomiguel.nicolascresposu.com/api/admin/users \
  -H "Authorization: Bearer YOUR_TOKEN"
```

#### GET /admin/users/{user}
Returns details of a specific user.

**Response (200):**
```json
{
  "id": 1,
  "name": "User Name",
  "email": "user@example.com",
  "role": "buyer",
  "webhook_url": null
}
```

**Example:**
```bash
curl -X GET http://api.gaelarianafernandomiguel.nicolascresposu.com/api/admin/users/1 \
  -H "Authorization: Bearer YOUR_TOKEN"
```

#### PATCH /admin/users/{user}/role
Updates a user's role.

**Request Body:**
```json
{
  "role": "seller"
}
```

**Response (200):**
```json
{
  "message": "Role updated"
}
```

**Example:**
```bash
curl -X PATCH http://api.gaelarianafernandomiguel.nicolascresposu.com/api/admin/users/1/role \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{"role":"seller"}'
```

#### PATCH /admin/users/{user}/deactivate
Deactivates a user.

**Response (200):**
```json
{
  "message": "User deactivated"
}
```

**Example:**
```bash
curl -X PATCH http://api.gaelarianafernandomiguel.nicolascresposu.com/api/admin/users/1/deactivate \
  -H "Authorization: Bearer YOUR_TOKEN"
```

#### GET /admin/wallets
Returns all wallets.

**Response (200):**
```json
[
  {
    "id": 1,
    "user_id": 1,
    "balance": 100.00
  }
]
```

**Example:**
```bash
curl -X GET http://api.gaelarianafernandomiguel.nicolascresposu.com/api/admin/wallets \
  -H "Authorization: Bearer YOUR_TOKEN"
```

#### GET /admin/wallets/{user}
Returns a specific user's wallet.

**Response (200):**
```json
{
  "id": 1,
  "user_id": 1,
  "balance": 100.00
}
```

**Example:**
```bash
curl -X GET http://api.gaelarianafernandomiguel.nicolascresposu.com/api/admin/wallets/1 \
  -H "Authorization: Bearer YOUR_TOKEN"
```

#### POST /admin/wallets/{user}/deposit
Deposits money into a user's wallet.

**Request Body:**
```json
{
  "amount": 50.00
}
```

**Response (200):**
```json
{
  "message": "Deposit successful"
}
```

**Example:**
```bash
curl -X POST http://api.gaelarianafernandomiguel.nicolascresposu.com/api/admin/wallets/1/deposit \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{"amount":50.00}'
```

#### POST /admin/wallets/{user}/withdraw
Withdraws money from a user's wallet.

**Request Body:**
```json
{
  "amount": 25.00
}
```

**Response (200):**
```json
{
  "message": "Withdraw successful"
}
```

**Example:**
```bash
curl -X POST http://api.gaelarianafernandomiguel.nicolascresposu.com/api/admin/wallets/1/withdraw \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{"amount":25.00}'
```

#### GET /admin/products
Returns all products (admin view).

**Response (200):**
```json
[
  {
    "id": 1,
    "name": "Product Name",
    "description": "Product description",
    "price": 10.00,
    "stock": 5,
    "is_active": true,
    "seller": {
      "id": 2,
      "name": "Seller Name"
    }
  }
]
```

**Example:**
```bash
curl -X GET http://api.gaelarianafernandomiguel.nicolascresposu.com/api/admin/products \
  -H "Authorization: Bearer YOUR_TOKEN"
```

#### PATCH /admin/products/{product}/toggle-active
Toggles a product's active status.

**Response (200):**
```json
{
  "message": "Product status updated"
}
```

**Example:**
```bash
curl -X PATCH http://api.gaelarianafernandomiguel.nicolascresposu.com/api/admin/products/1/toggle-active \
  -H "Authorization: Bearer YOUR_TOKEN"
```

#### GET /admin/orders
Returns all orders.

**Response (200):**
```json
[
  {
    "id": 1,
    "total_amount": 50.00,
    "status": "paid",
    "user_id": 3,
    "created_at": "2025-12-14T10:00:00Z"
  }
]
```

**Example:**
```bash
curl -X GET http://api.gaelarianafernandomiguel.nicolascresposu.com/api/admin/orders \
  -H "Authorization: Bearer YOUR_TOKEN"
```

#### GET /admin/orders/{order}
Returns details of a specific order.

**Response (200):**
```json
{
  "id": 1,
  "total_amount": 50.00,
  "status": "paid",
  "user_id": 3,
  "created_at": "2025-12-14T10:00:00Z",
  "items": [
    {
      "product_id": 1,
      "quantity": 2,
      "unit_price": 25.00,
      "subtotal": 50.00
    }
  ]
}
```

**Example:**
```bash
curl -X GET http://api.gaelarianafernandomiguel.nicolascresposu.com/api/admin/orders/1 \
  -H "Authorization: Bearer YOUR_TOKEN"
```

#### PATCH /admin/orders/{order}/status
Updates an order's status.

**Request Body:**
```json
{
  "status": "cancelled"
}
```

**Response (200):**
```json
{
  "message": "Order status updated"
}
```

**Example:**
```bash
curl -X PATCH http://api.gaelarianafernandomiguel.nicolascresposu.com/api/admin/orders/1/status \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{"status":"cancelled"}'
```

#### GET /admin/transactions
Returns all transactions.

**Response (200):**
```json
[
  {
    "id": 1,
    "from_wallet_id": 1,
    "to_wallet_id": 2,
    "amount": 50.00,
    "type": "transfer",
    "description": "Transfer",
    "created_at": "2025-12-14T10:00:00Z"
  }
]
```

**Example:**
```bash
curl -X GET http://api.gaelarianafernandomiguel.nicolascresposu.com/api/admin/transactions \
  -H "Authorization: Bearer YOUR_TOKEN"
```

#### GET /admin/users/{user}/transactions
Returns transactions for a specific user.

**Response (200):**
```json
[
  {
    "id": 1,
    "from_wallet_id": 1,
    "to_wallet_id": 2,
    "amount": 50.00,
    "type": "transfer",
    "description": "Transfer",
    "created_at": "2025-12-14T10:00:00Z"
  }
]
```

**Example:**
```bash
curl -X GET http://api.gaelarianafernandomiguel.nicolascresposu.com/api/admin/users/1/transactions \
  -H "Authorization: Bearer YOUR_TOKEN"
```
