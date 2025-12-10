<?php

namespace App\Http\Controllers\Api\Seller;

use App\Http\Controllers\Controller;
use App\Models\Order;
use Illuminate\Http\Request;

class SellerOrderController extends Controller
{
    // GET /api/seller/orders
    public function index(Request $request)
    {
        $sellerId = $request->user()->id;

        $orders = Order::whereHas('items.product', function ($q) use ($sellerId) {
                $q->where('seller_id', $sellerId);
            })
            ->with('items.product')
            ->latest()
            ->get();

        return response()->json($orders);
    }

    // GET /api/seller/orders/{order}
    public function show(Request $request, Order $order)
    {
        $sellerId = $request->user()->id;

        $hasItems = $order->items()
            ->whereHas('product', function ($q) use ($sellerId) {
                $q->where('seller_id', $sellerId);
            })
            ->exists();

        if (! $hasItems && $request->user()->role !== 'admin') {
            return response()->json(['message' => 'No autorizado'], 403);
        }

        $order->load('items.product');

        return response()->json($order);
    }
}
