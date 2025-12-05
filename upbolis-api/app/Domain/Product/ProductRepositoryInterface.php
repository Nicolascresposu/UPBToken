<?php

namespace App\Domain\Product;

use App\Models\Product;

interface ProductRepositoryInterface
{
    public function findOrFail(int $id): Product;

    public function save(Product $product): void;
}
