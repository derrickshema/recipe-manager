<script lang="ts">
	import type { Order, OrderStatus } from '$lib/types';
	import { onMount, onDestroy } from 'svelte';
	import { browser } from '$app/environment';
	
	let { data } = $props();
	
	// Local state for orders (to update in real-time)
	let orders = $state<Order[]>(data.orders || []);
	let wsConnected = $state(false);
	
	// WebSocket connection
	let ws: WebSocket | null = null;
	
	// Connect to WebSocket for real-time updates
	function connectWebSocket() {
		if (!browser || !data.user?.id) return;
		
		const wsUrl = `ws://localhost:8000/ws/customer/${data.user.id}`;
		ws = new WebSocket(wsUrl);
		
		ws.onopen = () => {
			wsConnected = true;
			console.log('WebSocket connected');
		};
		
		ws.onmessage = (event) => {
			try {
				const message = JSON.parse(event.data);
				if (message.type === 'order_update') {
					// Update the order in our list
					orders = orders.map(o => 
						o.id === message.data.id ? message.data : o
					);
				}
			} catch (e) {
				console.error('Failed to parse WebSocket message:', e);
			}
		};
		
		ws.onclose = () => {
			wsConnected = false;
			console.log('WebSocket disconnected');
			// Try to reconnect after 5 seconds
			setTimeout(connectWebSocket, 5000);
		};
		
		ws.onerror = (err) => {
			console.error('WebSocket error:', err);
		};
	}
	
	onMount(() => {
		connectWebSocket();
	});
	
	onDestroy(() => {
		if (ws) {
			ws.close();
		}
	});
	
	// Status colors and labels
	const statusConfig: Record<OrderStatus, { label: string; color: string }> = {
		pending: { label: 'Pending Payment', color: 'bg-yellow-100 text-yellow-800' },
		paid: { label: 'Paid', color: 'bg-blue-100 text-blue-800' },
		preparing: { label: 'Preparing', color: 'bg-purple-100 text-purple-800' },
		ready: { label: 'Ready for Pickup', color: 'bg-green-100 text-green-800' },
		completed: { label: 'Completed', color: 'bg-gray-100 text-gray-800' },
		cancelled: { label: 'Cancelled', color: 'bg-red-100 text-red-800' }
	};
	
	// Payment state
	let payingOrderId = $state<number | null>(null);
	
	// Handle payment - redirect to Stripe Checkout
	async function handlePayment(orderId: number) {
		payingOrderId = orderId;
		
		try {
			const response = await fetch('/api/payments/checkout', {
				method: 'POST',
				headers: { 'Content-Type': 'application/json' },
				body: JSON.stringify({ order_id: orderId })
			});
			
			if (!response.ok) {
				const data = await response.json();
				throw new Error(data.message || 'Failed to create checkout session');
			}
			
			const { checkout_url } = await response.json();
			
			// Redirect to Stripe Checkout
			window.location.href = checkout_url;
		} catch (err) {
			console.error('Payment error:', err);
			alert(err instanceof Error ? err.message : 'Payment failed');
			payingOrderId = null;
		}
	}
	
	// Format price for display
	function formatPrice(price: number): string {
		return new Intl.NumberFormat('en-US', {
			style: 'currency',
			currency: 'USD'
		}).format(price);
	}
	
	// Format date for display
	function formatDate(dateString: string): string {
		return new Date(dateString).toLocaleDateString('en-US', {
			year: 'numeric',
			month: 'short',
			day: 'numeric',
			hour: '2-digit',
			minute: '2-digit'
		});
	}
	
	// Expand/collapse order details
	let expandedOrders = $state<Set<number>>(new Set());
	
	function toggleOrderExpanded(orderId: number) {
		if (expandedOrders.has(orderId)) {
			expandedOrders.delete(orderId);
			expandedOrders = new Set(expandedOrders);
		} else {
			expandedOrders.add(orderId);
			expandedOrders = new Set(expandedOrders);
		}
	}
</script>

<svelte:head>
	<title>My Orders | Recipe Manager</title>
</svelte:head>

<div class="container mx-auto px-4 py-8">
	<div class="flex items-center justify-between mb-8">
		<h1 class="text-3xl font-bold">My Orders</h1>
		<div class="flex items-center gap-2">
			<span class="w-2 h-2 rounded-full {wsConnected ? 'bg-green-500' : 'bg-gray-300'}"></span>
			<span class="text-sm text-muted-foreground">
				{wsConnected ? 'Live updates' : 'Connecting...'}
			</span>
		</div>
	</div>
	
	{#if data.error}
		<div class="bg-red-50 border border-red-200 text-red-800 px-4 py-3 rounded-lg mb-6">
			{data.error}
		</div>
	{/if}
	
	{#if orders.length === 0}
		<!-- Empty State -->
		<div class="text-center py-16 bg-muted/30 rounded-lg">
			<svg xmlns="http://www.w3.org/2000/svg" class="h-16 w-16 mx-auto text-muted-foreground mb-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
				<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-3 7h3m-3 4h3m-6-4h.01M9 16h.01" />
			</svg>
			<h2 class="text-xl font-semibold mb-2">No orders yet</h2>
			<p class="text-muted-foreground mb-6">Your order history will appear here</p>
			<a 
				href="/home" 
				class="inline-flex items-center justify-center rounded-md font-medium bg-primary text-primary-foreground hover:bg-primary/90 h-10 px-4 py-2"
			>
				Browse Restaurants
			</a>
		</div>
	{:else}
		<!-- Orders List -->
		<div class="space-y-4">
			{#each orders as order (order.id)}
				{@const isExpanded = expandedOrders.has(order.id)}
				{@const statusInfo = statusConfig[order.status as OrderStatus] || { label: order.status, color: 'bg-gray-100 text-gray-800' }}
				
				<div class="border rounded-lg overflow-hidden">
					<!-- Order Header -->
					<button
						onclick={() => toggleOrderExpanded(order.id)}
						class="w-full p-4 flex items-center justify-between hover:bg-muted/30 transition-colors text-left"
					>
						<div class="flex items-center gap-4">
							<div>
								<span class="font-semibold">Order #{order.id}</span>
								<p class="text-sm text-muted-foreground">{formatDate(order.created_at)}</p>
							</div>
						</div>
						
						<div class="flex items-center gap-4">
							<span class={`px-3 py-1 rounded-full text-sm font-medium ${statusInfo.color}`}>
								{statusInfo.label}
							</span>
							<span class="font-semibold">{formatPrice(order.total_amount)}</span>
							<svg 
								xmlns="http://www.w3.org/2000/svg" 
								class="h-5 w-5 text-muted-foreground transition-transform {isExpanded ? 'rotate-180' : ''}" 
								viewBox="0 0 20 20" 
								fill="currentColor"
							>
								<path fill-rule="evenodd" d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z" clip-rule="evenodd" />
							</svg>
						</div>
					</button>
					
					<!-- Order Details (Expandable) -->
					{#if isExpanded}
						<div class="border-t p-4 bg-muted/10">
							<!-- Restaurant Name (if available) -->
							{#if order.restaurant_name}
								<p class="text-sm text-muted-foreground mb-3">
									From: <span class="font-medium text-foreground">{order.restaurant_name}</span>
								</p>
							{/if}
							
							<!-- Order Items -->
							<div class="space-y-2 mb-4">
								{#each order.items as item}
									<div class="flex justify-between items-center">
										<div class="flex items-center gap-2">
											<span class="text-sm text-muted-foreground">{item.quantity}x</span>
											<span>Item @ {formatPrice(item.unit_price)}</span>
										</div>
										<span class="text-sm">{formatPrice(item.subtotal)}</span>
									</div>
								{/each}
							</div>
							
							<!-- Order Notes -->
							{#if order.notes}
								<div class="bg-muted/30 p-3 rounded-lg mb-4">
									<p class="text-sm text-muted-foreground">Notes:</p>
									<p class="text-sm">{order.notes}</p>
								</div>
							{/if}
							
							<!-- Order Total -->
							<div class="flex justify-between items-center pt-3 border-t font-semibold">
								<span>Total</span>
								<span>{formatPrice(order.total_amount)}</span>
							</div>
							
							<!-- Pay Button (for pending orders) -->
							{#if order.status === 'pending'}
								<div class="mt-4 pt-4 border-t">
									<button
										onclick={() => handlePayment(order.id)}
										disabled={payingOrderId === order.id}
										class="w-full bg-green-600 hover:bg-green-700 text-white font-medium py-3 px-4 rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
									>
										{#if payingOrderId === order.id}
											<svg class="animate-spin h-5 w-5" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
												<circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
												<path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
											</svg>
											Redirecting to payment...
										{:else}
											<svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
												<path d="M4 4a2 2 0 00-2 2v1h16V6a2 2 0 00-2-2H4z" />
												<path fill-rule="evenodd" d="M18 9H2v5a2 2 0 002 2h12a2 2 0 002-2V9zM4 13a1 1 0 011-1h1a1 1 0 110 2H5a1 1 0 01-1-1zm5-1a1 1 0 100 2h1a1 1 0 100-2H9z" clip-rule="evenodd" />
											</svg>
											Pay Now - {formatPrice(order.total_amount)}
										{/if}
									</button>
								</div>
							{/if}
						</div>
					{/if}
				</div>
			{/each}
		</div>
	{/if}
</div>
