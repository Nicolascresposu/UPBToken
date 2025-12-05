<?php

namespace App\Application\Wallet;

use App\Domain\Exceptions\BusinessException;
use App\Domain\Transaction\TransactionRepositoryInterface;
use App\Domain\Wallet\WalletRepositoryInterface;
use App\Models\User;
use Illuminate\Support\Facades\DB;

class TransferUPBolisService
{
    public function __construct(
        private WalletRepositoryInterface $wallets,
        private TransactionRepositoryInterface $transactions,
    ) {}

    public function handle(User $fromUser, int $toUserId, float $amount, ?string $description = null): void
    {
        DB::transaction(function () use ($fromUser, $toUserId, $amount, $description) {
            if ($amount <= 0) {
                throw new BusinessException('El monto debe ser mayor a cero.');
            }

            $fromWallet = $this->wallets->getByUserIdOrFail($fromUser->id);
            $toWallet   = $this->wallets->getOrCreateByUserId($toUserId);

            if ($fromWallet->id === $toWallet->id) {
                throw new BusinessException('No puedes transferirte fondos a ti mismo.');
            }

            if ($fromWallet->balance < $amount) {
                throw new BusinessException('Saldo insuficiente.');
            }

            $fromWallet->balance -= $amount;
            $this->wallets->save($fromWallet);

            $toWallet->balance += $amount;
            $this->wallets->save($toWallet);

            $this->transactions->create([
                'from_wallet_id' => $fromWallet->id,
                'to_wallet_id'   => $toWallet->id,
                'amount'         => $amount,
                'type'           => 'transfer',
                'description'    => $description ?? 'Transferencia entre usuarios',
            ]);
        });
    }
}
