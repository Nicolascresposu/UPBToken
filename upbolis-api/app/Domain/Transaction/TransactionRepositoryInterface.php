<?php

namespace App\Domain\Transaction;

use App\Models\Transaction;

interface TransactionRepositoryInterface
{
    public function create(array $data): Transaction;
}
