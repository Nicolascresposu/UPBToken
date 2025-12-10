<?php

namespace App\Http\Controllers\Api;

use App\Http\Controllers\Controller;
use App\Models\Product;
use Illuminate\Http\Request;

class ProductController extends Controller
{
    // GET /api/products
    public function index()
    {
        $products = Product::where('is_active', true)
            ->where('stock', '>', 0)
            ->with('seller')
            ->get();

        return response()->json($products);
    }

    // GET /api/products/{product}
    public function show(Product $product)
    {
        $product->load('seller');

        return response()->json($product);
    }

    // SELLER: GET /api/seller/products
    public function myProducts(Request $request)
    {
        $products = Product::where('seller_id', $request->user()->id)
            ->orderBy('id', 'desc')
            ->get();

        return response()->json($products);
    }

    // SELLER: POST /api/seller/products
    public function store(Request $request)
    {
        $data = $request->validate([
            'name'        => 'required|string|max:255',
            'description' => 'nullable|string',
            'price'       => 'required|numeric|min:0.01',
            'stock'       => 'required|integer|min:0',
            'is_active'   => 'sometimes|boolean',
        ]);

        $product = Product::create([
            'seller_id'   => $request->user()->id,
            'name'        => $data['name'],
            'description' => $data['description'] ?? null,
            'price'       => $data['price'],
            'stock'       => $data['stock'],
            'is_active'   => $data['is_active'] ?? true,
        ]);

        return response()->json($product, 201);
    }

    // SELLER: PUT /api/seller/products/{product}
    public function update(Request $request, Product $product)
    {
        if ($product->seller_id !== $request->user()->id && $request->user()->role !== 'admin') {
            return response()->json(['message' => 'No autorizado'], 403);
        }

        $data = $request->validate([
            'name'        => 'sometimes|string|max:255',
            'description' => 'nullable|string',
            'price'       => 'sometimes|numeric|min:0.01',
            'stock'       => 'sometimes|integer|min:0',
            'is_active'   => 'sometimes|boolean',
        ]);

        $product->fill($data);
        $product->save();

        return response()->json($product);
    }

    // SELLER: DELETE /api/seller/products/{product}
    public function destroy(Request $request, Product $product)
    {
        if ($product->seller_id !== $request->user()->id && $request->user()->role !== 'admin') {
            return response()->json(['message' => 'No autorizado'], 403);
        }

        $product->delete();

        return response()->json([
            'message' => 'Producto eliminado',
        ]);
    }
}
