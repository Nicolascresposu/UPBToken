<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Foundation\Auth\User as Authenticatable;
use Illuminate\Notifications\Notifiable;
use Laravel\Sanctum\HasApiTokens;

class User extends Authenticatable
{
    use HasApiTokens, HasFactory, Notifiable;

    protected $fillable = [
        'name',
        'email',
        'password',
        'role', // admin, seller, buyer
    ];

    protected $hidden = [
        'password',
        'remember_token',
    ];

    protected $casts = [
        'email_verified_at' => 'datetime',
    ];

    // Relaciones

    public function wallet()
    {
        return $this->hasOne(Wallet::class);
    }

    public function products()
    {
        // productos donde este usuario es seller
        return $this->hasMany(Product::class, 'seller_id');
    }

    public function orders()
    {
        // órdenes donde este usuario es buyer
        return $this->hasMany(Order::class);
    }
}
