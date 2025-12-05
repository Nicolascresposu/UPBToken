<?php

namespace App\Http\Controllers\Api\Admin;

use App\Http\Controllers\Controller;
use App\Models\Transaction;
use App\Models\User;
use App\Models\Wallet;

class AdminTransactionController extends Controller
{
    // GET /api/admin/transactions
    public function index()
    {
        $transactions = Transaction::with(['fromWallet.user', 'toWallet.user'])
            ->orderByDesc('created_at')
            ->get();

        return response()->json($transactions);
    }

    // GET /api/admin/users/{user}/transactions
    public function byUser(User $user)
    {
        $wallet = Wallet::where('user_id', $user->id)->first();

        if (! $wallet) {
            return response()->json([
                'message'      => 'El usuario no tiene wallet.',
                'transactions' => [],
            ]);
        }

        $transactions = Transaction::with(['fromWallet.user', 'toWallet.user'])
            ->where('from_wallet_id', $wallet->id)
            ->orWhere('to_wallet_id', $wallet->id)
            ->orderByDesc('created_at')
            ->get();

        return response()->json($transactions);
    }
}
