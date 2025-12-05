<?php

namespace App\Domain\Order;

use App\Models\OrderItem;

interface OrderItemRepositoryInterface
{
    public function create(array $data): OrderItem;
}
