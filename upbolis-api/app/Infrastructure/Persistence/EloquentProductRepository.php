<?php

namespace App\Infrastructure\Persistence;

use App\Domain\Exceptions\BusinessException;
use App\Domain\Product\ProductRepositoryInterface;
use App\Models\Product;

class EloquentProductRepository implements ProductRepositoryInterface
{
    public function findOrFail(int $id): Product
    {
        $product = Product::find($id);

        if (! $product) {
            throw new BusinessException("Producto {$id} no encontrado.");
        }

        return $product;
    }

    public function save(Product $product): void
    {
        $product->save();
    }
}
