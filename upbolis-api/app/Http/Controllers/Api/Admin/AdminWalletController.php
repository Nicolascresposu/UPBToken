<?php

namespace App\Http\Controllers\Api\Admin;

use App\Http\Controllers\Controller;
use App\Models\Transaction;
use App\Models\User;
use App\Models\Wallet;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\DB;

class AdminWalletController extends Controller
{
    // GET /api/admin/wallets
    public function index()
    {
        $wallets = Wallet::with('user')->orderBy('id', 'asc')->get();

        return response()->json($wallets);
    }

    // GET /api/admin/wallets/{user}
    public function show(User $user)
    {
        $wallet = Wallet::firstOrCreate(
            ['user_id' => $user->id],
            ['balance' => 0]
        );

        $wallet->load('user');

        return response()->json($wallet);
    }

    // POST /api/admin/wallets/{user}/deposit
    public function deposit(Request $request, User $user)
    {
        $data = $request->validate([
            'amount'      => 'required|numeric|min:0.01',
            'description' => 'nullable|string',
        ]);

        $admin = $request->user();

        $wallet = Wallet::firstOrCreate(
            ['user_id' => $user->id],
            ['balance' => 0]
        );

        DB::transaction(function () use ($wallet, $data, $admin) {
            $wallet->balance += $data['amount'];
            $wallet->save();

            Transaction::create([
                'from_wallet_id' => null,
                'to_wallet_id'   => $wallet->id,
                'amount'         => $data['amount'],
                'type'           => 'deposit',
                'description'    => $data['description'] ?? 'Depósito admin: '.$admin->email,
            ]);
        });

        return response()->json([
            'message' => 'Depósito realizado',
            'wallet'  => $wallet->fresh(),
        ]);
    }

    // POST /api/admin/wallets/{user}/withdraw
    public function withdraw(Request $request, User $user)
    {
        $data = $request->validate([
            'amount'      => 'required|numeric|min:0.01',
            'description' => 'nullable|string',
        ]);

        $admin = $request->user();

        $wallet = Wallet::firstOrCreate(
            ['user_id' => $user->id],
            ['balance' => 0]
        );

        DB::transaction(function () use ($wallet, $data, $admin) {
            if ($wallet->balance < $data['amount']) {
                abort(422, 'Saldo insuficiente para retirar.');
            }

            $wallet->balance -= $data['amount'];
            $wallet->save();

            Transaction::create([
                'from_wallet_id' => $wallet->id,
                'to_wallet_id'   => null,
                'amount'         => $data['amount'],
                'type'           => 'withdraw',
                'description'    => $data['description'] ?? 'Retiro admin: '.$admin->email,
            ]);
        });

        return response()->json([
            'message' => 'Retiro realizado',
            'wallet'  => $wallet->fresh(),
        ]);
    }
}
