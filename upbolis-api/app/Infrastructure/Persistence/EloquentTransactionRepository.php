<?php

namespace App\Infrastructure\Persistence;

use App\Domain\Transaction\TransactionRepositoryInterface;
use App\Models\Transaction;

class EloquentTransactionRepository implements TransactionRepositoryInterface
{
    public function create(array $data): Transaction
    {
        return Transaction::create($data);
    }
}
