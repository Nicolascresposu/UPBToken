<?php

namespace App\Http\Middleware;

use Closure;
use Illuminate\Http\Request;

class IsSeller
{
    public function handle(Request $request, Closure $next)
    {
        if ($request->user()?->role !== 'seller' && $request->user()?->role !== 'admin') {
            // Permitimos que admin también pueda usar rutas de seller
            return response()->json(['message' => 'No autorizado (solo seller/admin)'], 403);
        }

        return $next($request);
    }
}
