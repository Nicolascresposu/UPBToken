<?php

namespace App\Http\Controllers\Api;

use App\Application\Wallet\TransferUPBolisService;
use App\Domain\Exceptions\BusinessException;
use App\Http\Controllers\Controller;
use Illuminate\Http\Request;

class WalletController extends Controller
{
    public function __construct(
        private TransferUPBolisService $transferService
    ) {}

    // GET /api/wallet
    public function show(Request $request)
    {
        $wallet = $request->user()->wallet;

        return response()->json([
            'wallet' => $wallet,
        ]);
    }

    // POST /api/wallet/transfer
    public function transfer(Request $request)
    {
        $data = $request->validate([
            'to_user_id'  => 'required|exists:users,id',
            'amount'      => 'required|numeric|min:0.01',
            'description' => 'nullable|string',
        ]);

        try {
            $this->transferService->handle(
                $request->user(),
                (int) $data['to_user_id'],
                (float) $data['amount'],
                $data['description'] ?? null
            );
        } catch (BusinessException $e) {
            return response()->json([
                'message' => $e->getMessage(),
            ], 422);
        }

        return response()->json([
            'message' => 'Transferencia realizada',
        ]);
    }
}
