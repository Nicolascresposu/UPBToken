<?php

namespace App\Http\Controllers\Api;

use App\Http\Controllers\Controller;
use App\Models\Transaction;
use Illuminate\Http\Request;

class TransactionController extends Controller
{
    // GET /api/transactions
    public function index(Request $request)
    {
        $wallet = $request->user()->wallet;

        if (! $wallet) {
            return response()->json([
                'message' => 'El usuario no tiene wallet.',
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
