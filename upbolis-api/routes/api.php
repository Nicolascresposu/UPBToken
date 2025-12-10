<?php

use App\Http\Controllers\Api\AuthController;
use App\Http\Controllers\Api\WalletController;
use App\Http\Controllers\Api\ProductController;
use App\Http\Controllers\Api\OrderController;
use App\Http\Controllers\Api\TransactionController;
use App\Http\Controllers\Api\Admin\UserAdminController;
use App\Http\Controllers\Api\Admin\AdminWalletController;
use App\Http\Controllers\Api\Admin\AdminOrderController;
use App\Http\Controllers\Api\Admin\AdminTransactionController;
use App\Http\Controllers\Api\Seller\SellerOrderController;

use Illuminate\Support\Facades\Route;

// ---------- AUTH PÚBLICO (sin login) ----------

Route::prefix('auth')->group(function () {
    Route::post('register', [AuthController::class, 'register']); // crea buyer
    Route::post('login',    [AuthController::class, 'login']);
});

// ---------- TODO LO DEMÁS: LOGIN OBLIGATORIO ----------

Route::middleware('auth:sanctum')->group(function () {

    // --- Perfil básico ---
    Route::get('auth/me',      [AuthController::class, 'me']);
    Route::post('auth/logout', [AuthController::class, 'logout']);

    // ---------- WALLET / UPBolis ----------
    Route::get('wallet',           [WalletController::class, 'show']);      // ver saldo y datos
    Route::post('wallet/transfer', [WalletController::class, 'transfer']);  // transferir UPBolis a otro usuario
    Route::get('transactions',     [TransactionController::class, 'index']); // historial de movimientos de MI wallet

    // ---------- PRODUCTOS (acceso general) ----------
    // Todos los usuarios logueados pueden ver el catálogo
    Route::get('products',           [ProductController::class, 'index']);   // lista de productos activos
    Route::get('products/{product}', [ProductController::class, 'show']);    // ver detalle de un producto

    // ---------- ÓRDENES DEL COMPRADOR (buyer) ----------
    Route::get('orders',          [OrderController::class, 'index']);  // mis órdenes
    Route::get('orders/{order}',  [OrderController::class, 'show']);   // detalle de mi orden
    Route::post('orders',         [OrderController::class, 'store']);  // crear una compra (descarga de saldo + stock)

    // ==================================================
    //                       SELLER
    // ==================================================
    Route::middleware('seller')->prefix('seller')->group(function () {

        // --- Productos del seller ---
        Route::get('products',                 [ProductController::class, 'myProducts']); // productos creados por mí
        Route::post('products',                [ProductController::class, 'store']);      // crear producto
        Route::put('products/{product}',       [ProductController::class, 'update']);     // editar producto propio
        Route::delete('products/{product}',    [ProductController::class, 'destroy']);    // eliminar producto propio

        // --- Órdenes relacionadas con mis productos ---
        Route::get('orders',                   [SellerOrderController::class, 'index']);  // órdenes donde hay productos míos
        Route::get('orders/{order}',           [SellerOrderController::class, 'show']);   // detalle filtrado por mis items
    });

    // ==================================================
    //                        ADMIN
    // ==================================================
    Route::middleware('admin')->prefix('admin')->group(function () {

        // --- Gestión de usuarios ---
        Route::get('users',                    [UserAdminController::class, 'index']);     // listar usuarios
        Route::get('users/{user}',             [UserAdminController::class, 'show']);      // ver detalle usuario
        Route::patch('users/{user}/role',      [UserAdminController::class, 'updateRole']); // cambiar rol (buyer/seller/admin)
        Route::patch('users/{user}/deactivate',[UserAdminController::class, 'deactivate']); // desactivar usuario (opcional)

        // --- Gestión de wallets / saldo ---
        Route::get('wallets',                  [AdminWalletController::class, 'index']);    // listar wallets
        Route::get('wallets/{user}',           [AdminWalletController::class, 'show']);     // ver wallet de un usuario
        Route::post('wallets/{user}/deposit',  [AdminWalletController::class, 'deposit']);  // cargar UPBolis a un usuario
        Route::post('wallets/{user}/withdraw', [AdminWalletController::class, 'withdraw']); // restar saldo (ajuste admin)

        // --- Gestión de productos (global) ---
        Route::get('products',                 [ProductController::class, 'index']);        // ver catálogo
        Route::patch('products/{product}/toggle-active', [ProductController::class, 'toggleActive']); // activar/desactivar producto

        // --- Gestión global de órdenes ---
        Route::get('orders',                   [AdminOrderController::class, 'index']);     // todas las órdenes
        Route::get('orders/{order}',           [AdminOrderController::class, 'show']);      // detalle de una orden
        Route::patch('orders/{order}/status',  [AdminOrderController::class, 'updateStatus']); // cambiar status (paid/cancelled/etc.)

        // --- Gestión global de transacciones ---
        Route::get('transactions',             [AdminTransactionController::class, 'index']); // todas las transacciones
        Route::get('users/{user}/transactions',[AdminTransactionController::class, 'byUser']); // transacciones de un usuario específico
    });
});
