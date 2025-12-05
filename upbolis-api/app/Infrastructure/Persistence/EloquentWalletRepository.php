<?php

namespace App\Infrastructure\Persistence;

use App\Domain\Exceptions\BusinessException;
use App\Domain\Wallet\WalletRepositoryInterface;
use App\Models\Wallet;

class EloquentWalletRepository implements WalletRepositoryInterface
{
    public function getByUserIdOrFail(int $userId): Wallet
    {
        $wallet = Wallet::where('user_id', $userId)->first();

        if (! $wallet) {
            throw new BusinessException('Wallet no encontrada para el usuario '.$userId);
        }

        return $wallet;
    }

    public function getOrCreateByUserId(int $userId): Wallet
    {
        return Wallet::firstOrCreate(
            ['user_id' => $userId],
            ['balance' => 0]
        );
    }

    public function save(Wallet $wallet): void
    {
        $wallet->save();
    }
}
