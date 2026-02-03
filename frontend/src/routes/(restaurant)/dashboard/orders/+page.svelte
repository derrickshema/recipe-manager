<script lang="ts">
	import { Button } from '$lib/components';
	import { OrderStatus, type Order } from '$lib/types';
	import { onMount, onDestroy } from 'svelte';
	import { browser } from '$app/environment';
	
	let { data } = $props();
	
	// Local state for orders (to update after status changes)
	let orders = $state<Order[]>(data.orders || []);
	let selectedStatus = $state<string>('all');
	let updatingOrderId = $state<number | null>(null);
	let error = $state<string | null>(null);
	let wsConnected = $state(false);
	
	// WebSocket connection
	let ws: WebSocket | null = null;
	
	// Connect to WebSocket for real-time updates
	function connectWebSocket() {
		if (!browser || !data.restaurant?.id) return;
		
		const wsUrl = `ws://localhost:8000/ws/restaurant/${data.restaurant.id}`;
		ws = new WebSocket(wsUrl);
		
		ws.onopen = () => {
			wsConnected = true;
			console.log('WebSocket connected');
		};
		
		ws.onmessage = (event) => {
			try {
				const message = JSON.parse(event.data);
				if (message.type === 'new_order') {
					// Add new order to the list
					orders = [message.data, ...orders];
					// Play notification sound or show toast
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
	
	// Status configuration
	const statusConfig: Record<string, { label: string; color: string; bgColor: string }> = {
		pending: { label: 'Pending', color: 'text-yellow-800', bgColor: 'bg-yellow-100' },
		paid: { label: 'Paid', color: 'text-blue-800', bgColor: 'bg-blue-100' },
		preparing: { label: 'Preparing', color: 'text-purple-800', bgColor: 'bg-purple-100' },
		ready: { label: 'Ready', color: 'text-green-800', bgColor: 'bg-green-100' },
		completed: { label: 'Completed', color: 'text-gray-800', bgColor: 'bg-gray-100' },
		cancelled: { label: 'Cancelled', color: 'text-red-800', bgColor: 'bg-red-100' }
	};
	
	// Valid status transitions
	const validTransitions: Record<string, string[]> = {
		pending: ['paid', 'cancelled'],
		paid: ['preparing', 'cancelled'],
		preparing: ['ready'],
		ready: ['completed'],
		completed: [],
		cancelled: []
	};
	
	// Filter orders by status
	let filteredOrders = $derived(
		selectedStatus === 'all' 
			? orders 
			: orders.filter(o => o.status === selectedStatus)
	);
	
	// Count orders by status
	let statusCounts = $derived({
		all: orders.length,
		pending: orders.filter(o => o.status === 'pending').length,
		paid: orders.filter(o => o.status === 'paid').length,
		preparing: orders.filter(o => o.status === 'preparing').length,
		ready: orders.filter(o => o.status === 'ready').length,
		completed: orders.filter(o => o.status === 'completed').length,
		cancelled: orders.filter(o => o.status === 'cancelled').length
	});
	
	// Format price
	function formatPrice(price: number): string {
		return new Intl.NumberFormat('en-US', {
			style: 'currency',
			currency: 'USD'
		}).format(price);
	}
	
	// Format date
	function formatDate(dateString: string): string {
		return new Date(dateString).toLocaleString('en-US', {
			month: 'short',
			day: 'numeric',
			hour: '2-digit',
			minute: '2-digit'
		});
	}
	
	// Update order status
	async function updateStatus(orderId: number, newStatus: string) {
		updatingOrderId = orderId;
		error = null;
		
		try {
			const response = await fetch(`/api/orders/${orderId}/status`, {
				method: 'PUT',
				headers: { 'Content-Type': 'application/json' },
				body: JSON.stringify({ status: newStatus })
			});
			
			if (!response.ok) {
				const data = await response.json();
				throw new Error(data.message || 'Failed to update status');
			}
			
			const updatedOrder = await response.json();
			
			// Update local state
			orders = orders.map(o => o.id === orderId ? updatedOrder : o);
		} catch (err) {
			error = err instanceof Error ? err.message : 'Failed to update status';
		} finally {
			updatingOrderId = null;
		}
	}
	
	// Get next status action button
	function getNextStatusAction(order: Order): { label: string; status: string } | null {
		const transitions = validTransitions[order.status] || [];
		if (transitions.length === 0) return null;
		
		// Return primary action (first non-cancel option, or cancel if only option)
		const primaryTransition = transitions.find(t => t !== 'cancelled') || transitions[0];
		
		const actionLabels: Record<string, string> = {
			paid: 'Mark as Paid',
			preparing: 'Start Preparing',
			ready: 'Mark Ready',
			completed: 'Complete Order',
			cancelled: 'Cancel Order'
		};
		
		return {
			label: actionLabels[primaryTransition] || primaryTransition,
			status: primaryTransition
		};
	}
</script>

<svelte:head>
	<title>Orders | Restaurant Dashboard</title>
</svelte:head>

<div class="space-y-6">
	<div class="flex items-center justify-between">
		<h1 class="text-2xl font-bold">Orders</h1>
		<div class="flex items-center gap-2">
			<span class="w-2 h-2 rounded-full {wsConnected ? 'bg-green-500' : 'bg-red-500'}"></span>
			<span class="text-sm text-muted-foreground">
				{wsConnected ? 'Live updates' : 'Reconnecting...'}
			</span>
		</div>
	</div>
	
	{#if error}
		<div class="bg-red-50 border border-red-200 text-red-800 px-4 py-3 rounded-lg">
			{error}
		</div>
	{/if}
	
	<!-- Status Filter Tabs -->
	<div class="flex gap-2 flex-wrap">
		{#each [
			{ key: 'all', label: 'All' },
			{ key: 'pending', label: 'Pending' },
			{ key: 'paid', label: 'Paid' },
			{ key: 'preparing', label: 'Preparing' },
			{ key: 'ready', label: 'Ready' },
			{ key: 'completed', label: 'Completed' }
		] as tab}
			<button
				onclick={() => selectedStatus = tab.key}
				class="px-4 py-2 rounded-lg text-sm font-medium transition-colors {selectedStatus === tab.key 
					? 'bg-primary text-white' 
					: 'bg-muted hover:bg-muted/80'}"
			>
				{tab.label}
				{#if statusCounts[tab.key as keyof typeof statusCounts] > 0}
					<span class="ml-1 px-2 py-0.5 rounded-full text-xs {selectedStatus === tab.key ? 'bg-white/20' : 'bg-primary/10 text-primary'}">
						{statusCounts[tab.key as keyof typeof statusCounts]}
					</span>
				{/if}
			</button>
		{/each}
	</div>
	
	<!-- Orders List -->
	{#if filteredOrders.length === 0}
		<div class="text-center py-16 bg-muted/30 rounded-lg">
			<svg xmlns="http://www.w3.org/2000/svg" class="h-16 w-16 mx-auto text-muted-foreground mb-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
				<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
			</svg>
			<h2 class="text-xl font-semibold mb-2">No orders</h2>
			<p class="text-muted-foreground">
				{selectedStatus === 'all' ? 'No orders yet' : `No ${selectedStatus} orders`}
			</p>
		</div>
	{:else}
		<div class="space-y-4">
			{#each filteredOrders as order (order.id)}
				{@const status = statusConfig[order.status] || statusConfig.pending}
				{@const nextAction = getNextStatusAction(order)}
				{@const canCancel = validTransitions[order.status]?.includes('cancelled')}
				
				<div class="border rounded-lg p-4 bg-white">
					<div class="flex items-start justify-between gap-4">
						<!-- Order Info -->
						<div class="flex-1">
							<div class="flex items-center gap-3 mb-2">
								<span class="font-semibold text-lg">Order #{order.id}</span>
								<span class={`px-2 py-1 rounded-full text-xs font-medium ${status.bgColor} ${status.color}`}>
									{status.label}
								</span>
							</div>
							<p class="text-sm text-muted-foreground mb-3">
								{formatDate(order.created_at)}
							</p>
							
							<!-- Order Items -->
							<div class="space-y-1 mb-3">
								{#each order.items as item}
									<div class="text-sm flex justify-between">
										<span>{item.quantity}x @ {formatPrice(item.unit_price)}</span>
										<span>{formatPrice(item.subtotal)}</span>
									</div>
								{/each}
							</div>
							
							<!-- Notes -->
							{#if order.notes}
								<div class="text-sm bg-muted/50 p-2 rounded mb-3">
									<span class="font-medium">Notes:</span> {order.notes}
								</div>
							{/if}
							
							<!-- Total -->
							<div class="font-semibold text-lg">
								Total: {formatPrice(order.total_amount)}
							</div>
						</div>
						
						<!-- Actions -->
						<div class="flex flex-col gap-2">
							{#if nextAction}
								<Button
									onclick={() => updateStatus(order.id, nextAction.status)}
									disabled={updatingOrderId === order.id}
									size="sm"
								>
									{#if updatingOrderId === order.id}
										<svg class="animate-spin h-4 w-4 mr-1" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
											<circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
											<path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
										</svg>
									{/if}
									{nextAction.label}
								</Button>
							{/if}
							
							{#if canCancel && nextAction?.status !== 'cancelled'}
								<button
									onclick={() => updateStatus(order.id, 'cancelled')}
									disabled={updatingOrderId === order.id}
									class="text-sm text-red-600 hover:text-red-800 disabled:opacity-50"
								>
									Cancel Order
								</button>
							{/if}
						</div>
					</div>
				</div>
			{/each}
		</div>
	{/if}
</div>
