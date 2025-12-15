# Documentación de la API de UPBolis

Este documento describe los endpoints de la API del sistema UPBolis. La URL base para todos los endpoints es:

```
http://api.gaelarianafernandomiguel.nicolascresposu.com/api
```

## Autenticación

La mayoría de los endpoints requieren autenticación usando un token Bearer obtenido del login. Incluya el token en el header `Authorization`:

```
Authorization: Bearer YOUR_TOKEN_HERE
```

## Endpoints

### Endpoints Públicos (Sin Autenticación Requerida)

#### POST /auth/register
Crea una nueva cuenta de comprador.

**Cuerpo de la Solicitud:**
```json
{
  "name": "John Doe",
  "email": "john@example.com",
  "password": "password123",
  "password_confirmation": "password123"
}
```

**Respuesta (201):**
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

**Ejemplo:**
```bash
curl -X POST http://api.gaelarianafernandomiguel.nicolascresposu.com/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"name":"John Doe","email":"john@example.com","password":"password123","password_confirmation":"password123"}'
```

#### POST /auth/login
Inicia sesión de un usuario y devuelve un token.

**Cuerpo de la Solicitud:**
```json
{
  "email": "john@example.com",
  "password": "password123"
}
```

**Respuesta (200):**
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

**Ejemplo:**
```bash
curl -X POST http://api.gaelarianafernandomiguel.nicolascresposu.com/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"john@example.com","password":"password123"}'
```

### Endpoints Autenticados

#### GET /auth/me
Devuelve el perfil del usuario actual.

**Respuesta (200):**
```json
{
  "id": 1,
  "name": "John Doe",
  "email": "john@example.com",
  "role": "buyer",
  "webhook_url": null
}
```

**Ejemplo:**
```bash
curl -X GET http://api.gaelarianafernandomiguel.nicolascresposu.com/api/auth/me \
  -H "Authorization: Bearer YOUR_TOKEN"
```

#### POST /auth/logout
Cierra la sesión del usuario actual (invalida el token).

**Respuesta (200):**
```json
{
  "message": "Sesión cerrada."
}
```

**Ejemplo:**
```bash
curl -X POST http://api.gaelarianafernandomiguel.nicolascresposu.com/api/auth/logout \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Endpoints de Wallet

#### GET /wallet
Devuelve el saldo y detalles de la wallet del usuario actual.

**Respuesta (200):**
```json
{
  "id": 1,
  "user_id": 1,
  "balance": 100.00
}
```

**Ejemplo:**
```bash
curl -X GET http://api.gaelarianafernandomiguel.nicolascresposu.com/api/wallet \
  -H "Authorization: Bearer YOUR_TOKEN"
```

#### POST /wallet/transfer
Transfiere UPBolis a otro usuario.

**Cuerpo de la Solicitud:**
```json
{
  "to_user_id": 2,
  "amount": 50.00
}
```

**Respuesta (200):**
```json
{
  "message": "Transfer successful"
}
```

**Ejemplo:**
```bash
curl -X POST http://api.gaelarianafernandomiguel.nicolascresposu.com/api/wallet/transfer \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{"to_user_id":2,"amount":50.00}'
```

#### POST /wallet/deposit
Agrega saldo a la wallet del usuario actual (PoC).

**Cuerpo de la Solicitud:**
```json
{
  "amount": 100.00
}
```

**Respuesta (200):**
```json
{
  "message": "Deposit successful"
}
```

**Ejemplo:**
```bash
curl -X POST http://api.gaelarianafernandomiguel.nicolascresposu.com/api/wallet/deposit \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{"amount":100.00}'
```

#### GET /transactions
Devuelve el historial de transacciones del usuario actual.

**Respuesta (200):**
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

**Ejemplo:**
```bash
curl -X GET http://api.gaelarianafernandomiguel.nicolascresposu.com/api/transactions \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Endpoints de Productos (Generales)

#### GET /products
Devuelve el catálogo de productos activos.

**Respuesta (200):**
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

**Ejemplo:**
```bash
curl -X GET http://api.gaelarianafernandomiguel.nicolascresposu.com/api/products \
  -H "Authorization: Bearer YOUR_TOKEN"
```

#### GET /products/{product}
Devuelve detalles de un producto específico.

**Respuesta (200):**
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

**Ejemplo:**
```bash
curl -X GET http://api.gaelarianafernandomiguel.nicolascresposu.com/api/products/1 \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Endpoints de Órdenes (Comprador)

#### GET /orders
Devuelve las órdenes del usuario actual.

**Respuesta (200):**
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

**Ejemplo:**
```bash
curl -X GET http://api.gaelarianafernandomiguel.nicolascresposu.com/api/orders \
  -H "Authorization: Bearer YOUR_TOKEN"
```

#### GET /orders/{order}
Devuelve detalles de una orden específica.

**Respuesta (200):**
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

**Ejemplo:**
```bash
curl -X GET http://api.gaelarianafernandomiguel.nicolascresposu.com/api/orders/1 \
  -H "Authorization: Bearer YOUR_TOKEN"
```

#### POST /orders
Crea una nueva orden (compra).

**Cuerpo de la Solicitud:**
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

**Respuesta (201):**
```json
{
  "id": 1,
  "total_amount": 50.00,
  "status": "paid",
  "created_at": "2025-12-14T10:00:00Z"
}
```

**Ejemplo:**
```bash
curl -X POST http://api.gaelarianafernandomiguel.nicolascresposu.com/api/orders \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{"items":[{"product_id":1,"quantity":2}]}'
```

### Endpoints de Vendedor (Requiere Rol de Vendedor)

#### GET /seller/products
Devuelve productos creados por el vendedor actual.

**Respuesta (200):**
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

**Ejemplo:**
```bash
curl -X GET http://api.gaelarianafernandomiguel.nicolascresposu.com/api/seller/products \
  -H "Authorization: Bearer YOUR_TOKEN"
```

#### POST /seller/products
Crea un nuevo producto.

**Cuerpo de la Solicitud:**
```json
{
  "name": "New Product",
  "description": "Product description",
  "price": 15.00,
  "stock": 10
}
```

**Respuesta (201):**
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

**Ejemplo:**
```bash
curl -X POST http://api.gaelarianafernandomiguel.nicolascresposu.com/api/seller/products \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{"name":"New Product","description":"Product description","price":15.00,"stock":10}'
```

#### PUT /seller/products/{product}
Actualiza un producto propiedad del vendedor.

**Cuerpo de la Solicitud:**
```json
{
  "name": "Updated Product",
  "stock": 20,
  "is_active": true
}
```

**Respuesta (200):**
```json
{
  "id": 1,
  "name": "Updated Product",
  "stock": 20,
  "is_active": true
}
```

**Ejemplo:**
```bash
curl -X PUT http://api.gaelarianafernandomiguel.nicolascresposu.com/api/seller/products/1 \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{"name":"Updated Product","stock":20,"is_active":true}'
```

#### DELETE /seller/products/{product}
Elimina suavemente un producto (establece is_active en false).

**Respuesta (200):**
```json
{
  "message": "Product deactivated"
}
```

**Ejemplo:**
```bash
curl -X DELETE http://api.gaelarianafernandomiguel.nicolascresposu.com/api/seller/products/1 \
  -H "Authorization: Bearer YOUR_TOKEN"
```

#### GET /seller/orders
Devuelve órdenes que contienen productos del vendedor.

**Respuesta (200):**
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

**Ejemplo:**
```bash
curl -X GET http://api.gaelarianafernandomiguel.nicolascresposu.com/api/seller/orders \
  -H "Authorization: Bearer YOUR_TOKEN"
```

#### GET /seller/orders/{order}
Devuelve detalles de una orden específica que contiene productos del vendedor.

**Respuesta (200):**
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

**Ejemplo:**
```bash
curl -X GET http://api.gaelarianafernandomiguel.nicolascresposu.com/api/seller/orders/1 \
  -H "Authorization: Bearer YOUR_TOKEN"
```

#### POST /seller/webhook
Establece la URL del webhook para que el vendedor reciba notificaciones de compra.

**Cuerpo de la Solicitud:**
```json
{
  "url": "https://your-webhook-endpoint.com/notify"
}
```

**Respuesta (200):**
```json
{
  "message": "Webhook updated",
  "webhook_url": "https://your-webhook-endpoint.com/notify"
}
```

**Ejemplo:**
```bash
curl -X POST http://api.gaelarianafernandomiguel.nicolascresposu.com/api/seller/webhook \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{"url":"https://your-webhook-endpoint.com/notify"}'
```

### Endpoints de Administrador (Requiere Rol de Administrador)

#### GET /admin/users
Devuelve una lista de todos los usuarios.

**Respuesta (200):**
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

**Ejemplo:**
```bash
curl -X GET http://api.gaelarianafernandomiguel.nicolascresposu.com/api/admin/users \
  -H "Authorization: Bearer YOUR_TOKEN"
```

#### GET /admin/users/{user}
Devuelve detalles de un usuario específico.

**Respuesta (200):**
```json
{
  "id": 1,
  "name": "User Name",
  "email": "user@example.com",
  "role": "buyer",
  "webhook_url": null
}
```

**Ejemplo:**
```bash
curl -X GET http://api.gaelarianafernandomiguel.nicolascresposu.com/api/admin/users/1 \
  -H "Authorization: Bearer YOUR_TOKEN"
```

#### PATCH /admin/users/{user}/role
Actualiza el rol de un usuario.

**Cuerpo de la Solicitud:**
```json
{
  "role": "seller"
}
```

**Respuesta (200):**
```json
{
  "message": "Role updated"
}
```

**Ejemplo:**
```bash
curl -X PATCH http://api.gaelarianafernandomiguel.nicolascresposu.com/api/admin/users/1/role \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{"role":"seller"}'
```

#### PATCH /admin/users/{user}/deactivate
Desactiva un usuario.

**Respuesta (200):**
```json
{
  "message": "User deactivated"
}
```

**Ejemplo:**
```bash
curl -X PATCH http://api.gaelarianafernandomiguel.nicolascresposu.com/api/admin/users/1/deactivate \
  -H "Authorization: Bearer YOUR_TOKEN"
```

#### GET /admin/wallets
Devuelve todas las wallets.

**Respuesta (200):**
```json
[
  {
    "id": 1,
    "user_id": 1,
    "balance": 100.00
  }
]
```

**Ejemplo:**
```bash
curl -X GET http://api.gaelarianafernandomiguel.nicolascresposu.com/api/admin/wallets \
  -H "Authorization: Bearer YOUR_TOKEN"
```

#### GET /admin/wallets/{user}
Devuelve la wallet de un usuario específico.

**Respuesta (200):**
```json
{
  "id": 1,
  "user_id": 1,
  "balance": 100.00
}
```

**Ejemplo:**
```bash
curl -X GET http://api.gaelarianafernandomiguel.nicolascresposu.com/api/admin/wallets/1 \
  -H "Authorization: Bearer YOUR_TOKEN"
```

#### POST /admin/wallets/{user}/deposit
Deposita dinero en la wallet de un usuario.

**Cuerpo de la Solicitud:**
```json
{
  "amount": 50.00
}
```

**Respuesta (200):**
```json
{
  "message": "Deposit successful"
}
```

**Ejemplo:**
```bash
curl -X POST http://api.gaelarianafernandomiguel.nicolascresposu.com/api/admin/wallets/1/deposit \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{"amount":50.00}'
```

#### POST /admin/wallets/{user}/withdraw
Retira dinero de la wallet de un usuario.

**Cuerpo de la Solicitud:**
```json
{
  "amount": 25.00
}
```

**Respuesta (200):**
```json
{
  "message": "Withdraw successful"
}
```

**Ejemplo:**
```bash
curl -X POST http://api.gaelarianafernandomiguel.nicolascresposu.com/api/admin/wallets/1/withdraw \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{"amount":25.00}'
```

#### GET /admin/products
Devuelve todos los productos (vista de administrador).

**Respuesta (200):**
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

**Ejemplo:**
```bash
curl -X GET http://api.gaelarianafernandomiguel.nicolascresposu.com/api/admin/products \
  -H "Authorization: Bearer YOUR_TOKEN"
```

#### PATCH /admin/products/{product}/toggle-active
Alterna el estado activo de un producto.

**Respuesta (200):**
```json
{
  "message": "Product status updated"
}
```

**Ejemplo:**
```bash
curl -X PATCH http://api.gaelarianafernandomiguel.nicolascresposu.com/api/admin/products/1/toggle-active \
  -H "Authorization: Bearer YOUR_TOKEN"
```

#### GET /admin/orders
Devuelve todas las órdenes.

**Respuesta (200):**
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

**Ejemplo:**
```bash
curl -X GET http://api.gaelarianafernandomiguel.nicolascresposu.com/api/admin/orders \
  -H "Authorization: Bearer YOUR_TOKEN"
```

#### GET /admin/orders/{order}
Devuelve detalles de una orden específica.

**Respuesta (200):**
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

**Ejemplo:**
```bash
curl -X GET http://api.gaelarianafernandomiguel.nicolascresposu.com/api/admin/orders/1 \
  -H "Authorization: Bearer YOUR_TOKEN"
```

#### PATCH /admin/orders/{order}/status
Actualiza el estado de una orden.

**Cuerpo de la Solicitud:**
```json
{
  "status": "cancelled"
}
```

**Respuesta (200):**
```json
{
  "message": "Order status updated"
}
```

**Ejemplo:**
```bash
curl -X PATCH http://api.gaelarianafernandomiguel.nicolascresposu.com/api/admin/orders/1/status \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{"status":"cancelled"}'
```

#### GET /admin/transactions
Devuelve todas las transacciones.

**Respuesta (200):**
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

**Ejemplo:**
```bash
curl -X GET http://api.gaelarianafernandomiguel.nicolascresposu.com/api/admin/transactions \
  -H "Authorization: Bearer YOUR_TOKEN"
```

#### GET /admin/users/{user}/transactions
Devuelve transacciones de un usuario específico.

**Respuesta (200):**
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

**Ejemplo:**
```bash
curl -X GET http://api.gaelarianafernandomiguel.nicolascresposu.com/api/admin/users/1/transactions \
  -H "Authorization: Bearer YOUR_TOKEN"
```
