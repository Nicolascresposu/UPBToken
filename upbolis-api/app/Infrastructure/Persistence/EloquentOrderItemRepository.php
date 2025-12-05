<?php

namespace App\Infrastructure\Persistence;

use App\Domain\Order\OrderItemRepositoryInterface;
use App\Models\OrderItem;

class EloquentOrderItemRepository implements OrderItemRepositoryInterface
{
    public function create(array $data): OrderItem
    {
        return OrderItem::create($data);
    }
}
