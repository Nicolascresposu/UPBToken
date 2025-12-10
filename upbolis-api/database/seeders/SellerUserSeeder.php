<?php

namespace Database\Seeders;

use App\Models\User;
use App\Models\Wallet;
use Illuminate\Database\Seeder;
use Illuminate\Support\Facades\Hash;

class SellerUserSeeder extends Seeder
{
    public function run(): void
    {
        $seller = User::firstOrCreate(
            ['email' => 'seller@upbolis.com'],
            [
                'name'     => 'Seller UPBolis',
                'password' => Hash::make('Seller1234'),
                'role'     => 'seller',
            ]
        );

        Wallet::firstOrCreate(
            ['user_id' => $seller->id],
            ['balance' => 0]
        );
    }
}
