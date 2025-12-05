<?php

namespace App\Providers;

use App\Domain\Order\OrderItemRepositoryInterface;
use App\Domain\Order\OrderRepositoryInterface;
use App\Domain\Product\ProductRepositoryInterface;
use App\Domain\Transaction\TransactionRepositoryInterface;
use App\Domain\Wallet\WalletRepositoryInterface;
use App\Infrastructure\Persistence\EloquentOrderItemRepository;
use App\Infrastructure\Persistence\EloquentOrderRepository;
use App\Infrastructure\Persistence\EloquentProductRepository;
use App\Infrastructure\Persistence\EloquentTransactionRepository;
use App\Infrastructure\Persistence\EloquentWalletRepository;
use Illuminate\Support\ServiceProvider;

class AppServiceProvider extends ServiceProvider
{
    public function register(): void
    {
        $this->app->bind(WalletRepositoryInterface::class, EloquentWalletRepository::class);
        $this->app->bind(TransactionRepositoryInterface::class, EloquentTransactionRepository::class);
        $this->app->bind(ProductRepositoryInterface::class, EloquentProductRepository::class);
        $this->app->bind(OrderRepositoryInterface::class, EloquentOrderRepository::class);
        $this->app->bind(OrderItemRepositoryInterface::class, EloquentOrderItemRepository::class);
    }

    public function boot(): void
    {
        //
    }
}
