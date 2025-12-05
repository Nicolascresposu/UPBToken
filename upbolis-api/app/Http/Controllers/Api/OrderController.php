<?php

namespace App\Http\Controllers\Api;

use App\Application\Orders\CreateOrderService;
use App\Domain\Exceptions\BusinessException;
use App\Http\Controllers\Controller;
use App\Models\Order;
use Illuminate\Http\Request;

class OrderController extends Controller
{
    public function __construct(
        private CreateOrderService $createOrderService
    ) {}

    // GET /api/orders
    public function index(Request $request)
    {
        $orders = $request->user()
            ->orders()
            ->with('items.product')
            ->latest()
            ->get();

        return response()->json($orders);
    }

    // GET /api/orders/{order}
    public function show(Request $request, Order $order)
    {
        if ($order->user_id !== $request->user()->id) {
            return response()->json(['message' => 'No autorizado'], 403);
        }

        $order->load('items.product');

        return response()->json($order);
    }

    // POST /api/orders
    public function store(Request $request)
    {
        $data = $request->validate([
            'items'              => 'required|array|min:1',
            'items.*.product_id' => 'required|integer',
            'items.*.quantity'   => 'required|integer|min:1',
        ]);

        try {
            $order = $this->createOrderService->handle(
                $request->user(),
                $data['items']
            );
        } catch (BusinessException $e) {
            return response()->json([
                'message' => $e->getMessage(),
            ], 422);
        }

        return response()->json($order, 201);
    }
}
