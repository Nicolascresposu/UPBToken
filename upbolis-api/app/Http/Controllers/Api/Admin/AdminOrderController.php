<?php

namespace App\Http\Controllers\Api\Admin;

use App\Http\Controllers\Controller;
use App\Models\Order;
use Illuminate\Http\Request;

class AdminOrderController extends Controller
{
    // GET /api/admin/orders
    public function index()
    {
        $orders = Order::with(['user', 'items.product'])
            ->latest()
            ->get();

        return response()->json($orders);
    }

    // GET /api/admin/orders/{order}
    public function show(Order $order)
    {
        $order->load(['user', 'items.product']);

        return response()->json($order);
    }

    // PATCH /api/admin/orders/{order}/status
    public function updateStatus(Request $request, Order $order)
    {
        $data = $request->validate([
            'status' => 'required|in:pending,paid,cancelled,refunded',
        ]);

        $order->status = $data['status'];
        $order->save();

        return response()->json([
            'message' => 'Estado de la orden actualizado',
            'order'   => $order,
        ]);
    }
}
