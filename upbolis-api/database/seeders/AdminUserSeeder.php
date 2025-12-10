<?php

namespace Database\Seeders;

use App\Models\User;
use App\Models\Wallet;
use Illuminate\Database\Seeder;
use Illuminate\Support\Facades\Hash;

class AdminUserSeeder extends Seeder
{
    public function run(): void
    {
        $admin = User::firstOrCreate(
            ['email' => 'admin@upbolis.com'],
            [
                'name'     => 'Admin UPBolis',
                'password' => Hash::make('Admin1234'),
                'role'     => 'admin',
            ]
        );

        Wallet::firstOrCreate(
            ['user_id' => $admin->id],
            ['balance' => 1000] // saldo inicial para pruebas
        );
    }
}
