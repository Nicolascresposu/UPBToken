<?php

namespace App\Domain\Order;

use App\Models\Order;

interface OrderRepositoryInterface
{
    public function create(array $data): Order;
}
