<?php

namespace App\Application\Orders;

use App\Domain\Exceptions\BusinessException;
use App\Domain\Order\OrderItemRepositoryInterface;
use App\Domain\Order\OrderRepositoryInterface;
use App\Domain\Product\ProductRepositoryInterface;
use App\Domain\Transaction\TransactionRepositoryInterface;
use App\Domain\Wallet\WalletRepositoryInterface;
use App\Models\Order;
use App\Models\User;
use Illuminate\Support\Facades\DB;

class CreateOrderService
{
    public function __construct(
        private WalletRepositoryInterface $wallets,
        private ProductRepositoryInterface $products,
        private OrderRepositoryInterface $orders,
        private OrderItemRepositoryInterface $orderItems,
        private TransactionRepositoryInterface $transactions,
    ) {}

    /**
     * @param User $buyer
     * @param array<int,array{product_id:int,quantity:int}> $items
     */
    public function handle(User $buyer, array $items): Order
    {
        return DB::transaction(function () use ($buyer, $items) {
            if (empty($items)) {
                throw new BusinessException('La orden debe tener al menos un producto.');
            }

            $buyerWallet = $this->wallets->getByUserIdOrFail($buyer->id);

            $total        = 0;
            $sellerTotals = [];
            $itemsData    = [];

            foreach ($items as $item) {
                $product = $this->products->findOrFail($item['product_id']);

                if (! $product->is_active) {
                    throw new BusinessException("El producto {$product->name} no está activo.");
                }

                $qty = (int) $item['quantity'];

                if ($qty <= 0) {
                    throw new BusinessException("Cantidad inválida para {$product->name}.");
                }

                if ($product->stock < $qty) {
                    throw new BusinessException("Stock insuficiente para {$product->name}.");
                }

                if (! $product->seller_id) {
                    throw new BusinessException("El producto {$product->name} no tiene seller asignado.");
                }

                $subtotal = $product->price * $qty;
                $total   += $subtotal;

                $sellerId = $product->seller_id;

                if (! isset($sellerTotals[$sellerId])) {
                    $sellerTotals[$sellerId] = 0;
                }
                $sellerTotals[$sellerId] += $subtotal;

                $itemsData[] = [
                    'product'    => $product,
                    'quantity'   => $qty,
                    'unit_price' => $product->price,
                    'subtotal'   => $subtotal,
                    'seller_id'  => $sellerId,
                ];
            }

            if ($buyerWallet->balance < $total) {
                throw new BusinessException('Saldo insuficiente en la wallet.');
            }

            // Descontar al comprador
            $buyerWallet->balance -= $total;
            $this->wallets->save($buyerWallet);

            // Pagar a sellers
            $transactions = [];

            foreach ($sellerTotals as $sellerId => $amountForSeller) {
                $sellerWallet = $this->wallets->getOrCreateByUserId($sellerId);

                $sellerWallet->balance += $amountForSeller;
                $this->wallets->save($sellerWallet);

                $transactions[] = $this->transactions->create([
                    'from_wallet_id' => $buyerWallet->id,
                    'to_wallet_id'   => $sellerWallet->id,
                    'amount'         => $amountForSeller,
                    'type'           => 'transfer',
                    'description'    => 'Pago por compra de productos',
                ]);
            }

            $mainTransactionId = count($transactions) === 1
                ? $transactions[0]->id
                : null;

            $order = $this->orders->create([
                'user_id'       => $buyer->id,
                'total_amount'  => $total,
                'status'        => 'paid',
                'transaction_id'=> $mainTransactionId,
            ]);

            foreach ($itemsData as $itemData) {
                $this->orderItems->create([
                    'order_id'   => $order->id,
                    'product_id' => $itemData['product']->id,
                    'quantity'   => $itemData['quantity'],
                    'unit_price' => $itemData['unit_price'],
                    'subtotal'   => $itemData['subtotal'],
                ]);

                $product = $itemData['product'];
                $product->stock -= $itemData['quantity'];
                $this->products->save($product);
            }

            return $order->load('items.product');
        });
    }
}
