<?php

namespace App\Domain\Wallet;

use App\Models\Wallet;

interface WalletRepositoryInterface
{
    public function getByUserIdOrFail(int $userId): Wallet;

    public function getOrCreateByUserId(int $userId): Wallet;

    public function save(Wallet $wallet): void;
}
