# UPBolis - Sistema de Productos y Compras

## Descripción General

Estamos desarrollando un sistema completo de creación y gestión de productos para vendedores (sellers) y un catálogo de compra para compradores (buyers), aqui en UPBolis.

## Características Implementadas

### 1. **Dashboard del Vendedor**
- **Crear Productos**: Formulario para crear nuevos productos con:
  - Nombre (requerido)
  - Descripción (opcional)
  - Precio en UPBolis (requerido, mínimo 0.01)
  - Stock (requerido)
  
- **Gestionar Productos**: Vista de todos tus productos con opciones para:
  - Ver información del producto
  - Eliminar productos

- **Interfaz Moderna (maso)**: Diseño responsivo con dos columnas (formulario + lista de productos)

### 2. **Dashboard del Comprador**
- **Ver Saldo**: Visualizar saldo actual de UPBolis
- **Catálogo de Productos**: Grid que muestra:
  - Nombre del producto
  - Vendedor
  - Descripción
  - Precio
  - Stock disponible
  
- **Comprar Productos**: 
  - Seleccionar cantidad
  - Confirmación antes de compra
  - Visualizar total

- **Historial de Compras (WIP)**: Ver todas tus órdenes previas con:
  - ID de orden
  - Fecha
  - Estado
  - Detalles de items
  - Total gastado

### 3. **API Laravel (Backend)**
Los siguientes endpoints ya están implementados en `routes/api.php`:

**Para Vendedores:**
- `GET /api/seller/products` - Listar productos del vendedor
- `POST /api/seller/products` - Crear producto
- `PUT /api/seller/products/{product}` - Editar producto
- `DELETE /api/seller/products/{product}` - Eliminar producto

**Para Compradores:**
- `GET /api/products` - Listar todos los productos disponibles
- `GET /api/products/{product}` - Ver detalle de producto
- `GET /api/orders` - Ver mis órdenes
- `POST /api/orders` - Crear orden de compra

**Datos Disponibles:**
- Wallet (saldo)
- Transacciones
- Productos con información del vendedor

### 4. **Base de Datos**
Tablas existentes:
- `users` - Con roles: admin, seller, buyer
- `products` - Con `seller_id` relacionado
- `orders` - Órdenes de compra
- `order_items` - Items dentro de una orden
- `wallets` - Saldo de cada usuario
- `transactions` - Historial de movimientos

### 5. **Datos de Prueba**
Se han creado usuarios y productos de prueba mediante seeders: 

**Usuarios:**
- Seller: `seller@upbolis.com` / `Seller1234`
- Comprador: Puedes registrarte con cualquier email

**Productos de Prueba (creados por el vendedor) (no estan en el sitio rn pero si haces el seeding si estan):**
1. Laptop Gaming - 500 UPBolis (5 en stock)
2. Teclado Mecánico - 80 UPBolis (15 en stock)
3. Mouse Inalámbrico - 40 UPBolis (20 en stock)
4. Monitor 4K 27" - 350 UPBolis (3 en stock)
5. Auriculares Premium - 150 UPBolis (10 en stock)
6. SSD 1TB NVMe - 100 UPBolis (8 en stock)

## Instrucciones de Uso

### Configuración Inicial

1. **Andá al directorio del API Laravel:**
   ```bash
   cd upbolis-api
   ```

2. **Ejecutá migraciones:**
   ```bash
   php artisan migrate
   ```

3. **Ejecutá seeders para crear usuarios y productos de prueba:**
   ```bash
   php artisan db:seed
   ```

4. **Iniciar el servidor Laravel:**
   ```bash
   php artisan serve
   ```
   Esto correrá en `http://127.0.0.1:8000`

5. **En otra terminal, ir al directorio Django y iniciarlo:**
   ```bash
   cd ..\upbolis_web
   py manage.py runserver 8001
   ```
   O en el puerto que prefirás. A mi me gusta 8001. Accedé en `http://localhost:8001`

### Flujo de Uso 

#### Como Comprador:
1. Entra en `http://localhost:8001/login`
2. Si no tienes cuenta, regístráte
3. Ve a tu dashboard de comprador
4. Verás:
   - Tu saldo de UPBolis en la tarjeta "Mi Saldo"
   - Catálogo de productos disponibles
5. Para comprar:
   - Selecciona la cantidad del producto
   - Haz clic en "Comprar"
   - Confirma la compra en el modal
   - Se descontará del saldo y se creará la orden
6. Visualiza tus compras con "Ver historial"

#### Como Vendedor:
1. Entra en `http://localhost:8001/login`
2. Usa credenciales: `seller@upbolis.com` / `Seller1234`
3. Ve a tu dashboard de vendedor
4. En la sección "Crear Producto":
   - Ingresa nombre del producto
   - Agregar descripción (opcional)
   - Establece precio en UPBolis
   - Define cantidad de stock
   - Haz clic en "Crear Producto"
5. Verás tus productos en la sección "Mis Productos"
6. Puedes eliminar productos desde ahí

## Detalles Técnicos

### Frontend (Django Templates)
- **seller_dashboard.html**: Interfaz para crear y gestionar productos
- **buyer_dashboard.html**: Catálogo y carrito de compras
- **base.html**: Template base con localStorage para tokens

### Backend (Laravel)
- **ProductController**: Gestión de productos
- **OrderController**: Gestión de órdenes
- **Seeders**: AdminUserSeeder, SellerUserSeeder, ProductSeeder

### Autenticación
- Token JWT se guarda en `localStorage` del navegador (para no resolicitar uno en cada cambio de pagina)
- Enviado en header `Authorization: Bearer {token}`
- Sessions Django para mantener datos de usuario

## Flujo de Datos

```
Usuario (Django Frontend) 
    ↓
Login: Django → Laravel API
    ↓
Token guardado en localStorage
    ↓
Operaciones (fetch requests):
  - Crear producto: POST /api/seller/products
  - Ver productos: GET /api/products
  - Comprar: POST /api/orders
  - Ver órdenes: GET /api/orders
    ↓
Laravel API procesa y devuelve JSON
    ↓
Django Frontend actualiza la UI
```

## Próximos Pasos Opcionales / TO-DO (En orden de prioridad)

~~0. **(Urgente) Dashboard de administrador para agregar y remover el cargo de seller a usuarios.**~~  
~~1. **(Igual de urgente) Webhooks para los sellers para que puedan ser notificados cuando su producto es comprado**~~  
~~2. **(Relativamente urgente) Editar productos**: Agregar modal para editar productos existentes (Como aumentar le stock)~~  
~~3. **Filtros**: Buscar/filtrar productos por nombre o precio (fzf? busqueda normal?)~~  
4. **Validaciones**: Más validaciones en frontend (ej: saldo insuficiente)  
5. **Imagen de productos**: Permitir subir imágenes  
6. **Reviews**: Sistema de reseñas y valoraciones  
~~8. **Carrito**: Agregar múltiples items al carrito antes de confirmar~~ Descartado. Muy complicado con el sistema de webhooks actual.  

## Solución de Problemas

### No aparecen los productos
- Verifica que los seeders se corrieron: `php artisan db:seed`
- Comprueba que el usuario seller existe en la base de datos

### Puerto 8000 ya está en uso
Cambia el puerto de Laravel bichote:
```bash
php artisan serve --port=8001
```
Y actualiza `API_BASE` en los templates

---

¡Si tenes mas problemas ggwp! 🎉

