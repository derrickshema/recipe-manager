<script lang="ts">
	import { Button } from '$lib/components';
	import { goto } from '$app/navigation';
	import { 
		cart, 
		cartTotal, 
		cartItemCount,
		updateCartItemQuantity, 
		removeFromCart, 
		clearCart 
	} from '$lib/stores/cartStore';
	import type { OrderCreateRequest } from '$lib/types';
	
	let { data } = $props();
	
	// State
	let isSubmitting = $state(false);
	let orderNotes = $state('');
	let error = $state<string | null>(null);
	let successMessage = $state<string | null>(null);
	
	// Format price for display
	function formatPrice(price: number): string {
		return new Intl.NumberFormat('en-US', {
			style: 'currency',
			currency: 'USD'
		}).format(price);
	}
	
	// Handle quantity change
	function handleQuantityChange(recipeId: number, newQuantity: number) {
		updateCartItemQuantity(recipeId, Math.max(0, newQuantity));
	}
	
	// Place order
	async function placeOrder() {
		// Get current cart state using $cart reactive value
		const currentCart = $cart;
		
		if (!currentCart.restaurantId || currentCart.items.length === 0) {
			error = 'Your cart is empty';
			return;
		}
		
		isSubmitting = true;
		error = null;
		
		try {
			const orderData: OrderCreateRequest = {
				restaurant_id: currentCart.restaurantId,
				items: currentCart.items.map(item => ({
					recipe_id: item.recipe.id,
					quantity: item.quantity,
					notes: item.notes
				})),
				notes: orderNotes || undefined
			};
			
			const response = await fetch('/api/orders', {
				method: 'POST',
				headers: {
					'Content-Type': 'application/json'
				},
				body: JSON.stringify(orderData)
			});
			
			if (!response.ok) {
				const data = await response.json();
				throw new Error(data.message || 'Failed to place order');
			}
			
			const order = await response.json();
			
			// Clear cart and show success
			clearCart();
			successMessage = `Order #${order.id} placed successfully!`;
			
			// Redirect to orders page after a short delay
			setTimeout(() => {
				goto('/orders');
			}, 2000);
			
		} catch (err) {
			error = err instanceof Error ? err.message : 'Failed to place order';
		} finally {
			isSubmitting = false;
		}
	}
</script>

<svelte:head>
	<title>Your Cart | Recipe Manager</title>
</svelte:head>

<div class="container mx-auto px-4 py-8">
	<h1 class="text-3xl font-bold mb-8">Your Cart</h1>
	
	{#if successMessage}
		<!-- Success Message -->
		<div class="bg-green-50 border border-green-200 text-green-800 px-4 py-3 rounded-lg mb-6">
			<div class="flex items-center">
				<svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 mr-2" viewBox="0 0 20 20" fill="currentColor">
					<path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd" />
				</svg>
				{successMessage}
			</div>
		</div>
	{:else if $cartItemCount === 0}
		<!-- Empty Cart -->
		<div class="text-center py-16 bg-muted/30 rounded-lg">
			<svg xmlns="http://www.w3.org/2000/svg" class="h-16 w-16 mx-auto text-muted-foreground mb-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
				<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 3h2l.4 2M7 13h10l4-8H5.4M7 13L5.4 5M7 13l-2.293 2.293c-.63.63-.184 1.707.707 1.707H17m0 0a2 2 0 100 4 2 2 0 000-4zm-8 2a2 2 0 11-4 0 2 2 0 014 0z" />
			</svg>
			<h2 class="text-xl font-semibold mb-2">Your cart is empty</h2>
			<p class="text-muted-foreground mb-6">Browse restaurants and add items to your cart</p>
			<a 
				href="/home" 
				class="inline-flex items-center justify-center rounded-md font-medium bg-primary text-primary-foreground hover:bg-primary/90 h-10 px-4 py-2"
			>
				Browse Restaurants
			</a>
		</div>
	{:else}
		<!-- Error Message -->
		{#if error}
			<div class="bg-red-50 border border-red-200 text-red-800 px-4 py-3 rounded-lg mb-6">
				{error}
			</div>
		{/if}
		
		<div class="grid grid-cols-1 lg:grid-cols-3 gap-8">
			<!-- Cart Items -->
			<div class="lg:col-span-2">
				<!-- Restaurant Info -->
				<div class="bg-muted/30 rounded-lg p-4 mb-4">
					<p class="text-sm text-muted-foreground">Ordering from</p>
					<p class="font-semibold">{$cart.restaurantName}</p>
				</div>
				
				<!-- Items List -->
				<div class="space-y-4">
					{#each $cart.items as item (item.recipe.id)}
						<div class="border rounded-lg p-4 flex gap-4">
							<!-- Item Image -->
							<div class="w-24 h-24 bg-muted rounded-lg flex-shrink-0 overflow-hidden">
								{#if item.recipe.image_url}
									<img 
										src={item.recipe.image_url} 
										alt={item.recipe.title} 
										class="w-full h-full object-cover"
									/>
								{:else}
									<div class="w-full h-full flex items-center justify-center">
										<svg xmlns="http://www.w3.org/2000/svg" class="h-8 w-8 text-muted-foreground" fill="none" viewBox="0 0 24 24" stroke="currentColor">
											<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
										</svg>
									</div>
								{/if}
							</div>
							
							<!-- Item Details -->
							<div class="flex-1">
								<div class="flex justify-between items-start">
									<div>
										<h3 class="font-semibold">{item.recipe.title}</h3>
										<p class="text-sm text-muted-foreground">{formatPrice(item.recipe.price)} each</p>
									</div>
									<button 
										onclick={() => removeFromCart(item.recipe.id)}
										class="text-muted-foreground hover:text-destructive transition-colors"
										aria-label="Remove item"
									>
										<svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
											<path fill-rule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clip-rule="evenodd" />
										</svg>
									</button>
								</div>
								
								<!-- Quantity Controls -->
								<div class="flex items-center gap-3 mt-3">
									<button 
										onclick={() => handleQuantityChange(item.recipe.id, item.quantity - 1)}
										class="w-8 h-8 rounded-full border flex items-center justify-center hover:bg-muted transition-colors"
										aria-label="Decrease quantity"
									>
										<svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" viewBox="0 0 20 20" fill="currentColor">
											<path fill-rule="evenodd" d="M3 10a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1z" clip-rule="evenodd" />
										</svg>
									</button>
									<span class="font-medium w-8 text-center">{item.quantity}</span>
									<button 
										onclick={() => handleQuantityChange(item.recipe.id, item.quantity + 1)}
										class="w-8 h-8 rounded-full border flex items-center justify-center hover:bg-muted transition-colors"
										aria-label="Increase quantity"
									>
										<svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" viewBox="0 0 20 20" fill="currentColor">
											<path fill-rule="evenodd" d="M10 3a1 1 0 011 1v5h5a1 1 0 110 2h-5v5a1 1 0 11-2 0v-5H4a1 1 0 110-2h5V4a1 1 0 011-1z" clip-rule="evenodd" />
										</svg>
									</button>
									<span class="ml-auto font-semibold">
										{formatPrice(item.recipe.price * item.quantity)}
									</span>
								</div>
							</div>
						</div>
					{/each}
				</div>
				
				<!-- Clear Cart -->
				<div class="mt-4">
					<button 
						onclick={() => clearCart()}
						class="text-sm text-muted-foreground hover:text-destructive transition-colors"
					>
						Clear cart
					</button>
				</div>
			</div>
			
			<!-- Order Summary -->
			<div class="lg:col-span-1">
				<div class="border rounded-lg p-6 sticky top-4">
					<h2 class="text-lg font-semibold mb-4">Order Summary</h2>
					
					<!-- Items Count -->
					<div class="flex justify-between text-sm mb-2">
						<span>Items ({$cartItemCount})</span>
						<span>{formatPrice($cartTotal)}</span>
					</div>
					
					<hr class="my-4" />
					
					<!-- Total -->
					<div class="flex justify-between font-semibold text-lg mb-6">
						<span>Total</span>
						<span>{formatPrice($cartTotal)}</span>
					</div>
					
					<!-- Order Notes -->
					<div class="mb-4">
						<label for="orderNotes" class="block text-sm font-medium mb-2">
							Special Instructions (optional)
						</label>
						<textarea 
							id="orderNotes"
							bind:value={orderNotes}
							placeholder="Any special requests..."
							class="w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary bg-background text-sm"
							rows="3"
						></textarea>
					</div>
					
					<!-- Place Order Button -->
					<Button 
						fullWidth 
						onclick={placeOrder}
						disabled={isSubmitting}
					>
						{#if isSubmitting}
							<svg class="animate-spin h-4 w-4 mr-2" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
								<circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
								<path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
							</svg>
							Placing Order...
						{:else}
							Place Order
						{/if}
					</Button>
					
					<p class="text-xs text-muted-foreground mt-4 text-center">
						Payment will be processed on the next step
					</p>
				</div>
			</div>
		</div>
	{/if}
</div>
