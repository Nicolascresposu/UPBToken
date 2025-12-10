<?php

namespace App\Http\Controllers\Api\Seller;

use App\Http\Controllers\Controller;
use Illuminate\Http\Request;

class WebhookController extends Controller
{
    public function store(Request $request)
    {
        $request->validate([
            'url' => 'nullable|url|max:1000',
        ]);

        $user = $request->user();
        $user->webhook_url = $request->input('url');
        $user->save();

        return response()->json(['message' => 'Webhook updated', 'webhook_url' => $user->webhook_url]);
    }
}
