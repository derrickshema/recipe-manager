<script lang="ts">
	import { enhance } from '$app/forms';
	import { Button } from '$lib/components';
	import { ApprovalStatus, type Restaurant } from '$lib/types';

	// SSR data from +page.server.ts
	let { data, form } = $props();

	// Reactive state for UI
	let activeTab = $state<'pending' | 'all'>('pending');
	let submitting = $state<number | null>(null);

	// Derived data from SSR
	let restaurants = $derived(data.restaurants ?? []);
	let pendingRestaurants = $derived(data.pendingRestaurants ?? []);

	function getStatusBadge(status: ApprovalStatus): string {
		switch (status) {
			case ApprovalStatus.APPROVED:
				return 'bg-green-100 text-green-800';
			case ApprovalStatus.PENDING:
				return 'bg-yellow-100 text-yellow-800';
			case ApprovalStatus.REJECTED:
				return 'bg-red-100 text-red-800';
			case ApprovalStatus.SUSPENDED:
				return 'bg-gray-100 text-gray-800';
			default:
				return 'bg-gray-100 text-gray-800';
		}
	}

	function formatDate(dateString: string): string {
		return new Date(dateString).toLocaleDateString('en-US', {
			year: 'numeric',
			month: 'short',
			day: 'numeric',
			hour: '2-digit',
			minute: '2-digit'
		});
	}
</script>

<div class="space-y-6">
	<!-- Back Button -->
	<div>
		<a href="/overview" class="inline-flex items-center text-sm text-muted-foreground hover:text-foreground transition-colors">
			<svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
				<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
			</svg>
			Back to Overview
		</a>
	</div>
	
	<div class="flex justify-between items-center">
		<div>
			<h1 class="text-3xl font-bold">Restaurant Management</h1>
			<p class="text-muted-foreground mt-2">Review and manage restaurant registrations</p>
		</div>
	</div>

	<!-- Success/Error Messages -->
	{#if form?.success}
		<div class="bg-green-100 text-green-800 p-4 rounded-lg">
			{form.message}
		</div>
	{/if}
	{#if form?.error}
		<div class="bg-destructive/10 text-destructive p-4 rounded-lg">
			{form.error}
		</div>
	{/if}
	{#if data.error}
		<div class="bg-destructive/10 text-destructive p-4 rounded-lg">
			{data.error}
		</div>
	{/if}

	<!-- Tabs -->
	<div class="border-b">
		<nav class="flex gap-4">
			<button
				class="pb-3 px-1 border-b-2 font-medium text-sm transition-colors {activeTab === 'pending'
					? 'border-primary text-primary'
					: 'border-transparent text-muted-foreground hover:text-foreground'}"
				onclick={() => (activeTab = 'pending')}
			>
				Pending Approvals
				{#if pendingRestaurants.length > 0}
					<span
						class="ml-2 inline-flex items-center justify-center px-2 py-1 text-xs font-bold leading-none text-white bg-red-600 rounded-full"
					>
						{pendingRestaurants.length}
					</span>
				{/if}
			</button>
			<button
				class="pb-3 px-1 border-b-2 font-medium text-sm transition-colors {activeTab === 'all'
					? 'border-primary text-primary'
					: 'border-transparent text-muted-foreground hover:text-foreground'}"
				onclick={() => (activeTab = 'all')}
			>
				All Restaurants ({restaurants.length})
			</button>
		</nav>
	</div>

	<!-- Pending Approvals Tab -->
	{#if activeTab === 'pending'}
		{#if pendingRestaurants.length === 0}
			<div class="text-center py-12 bg-muted/30 rounded-lg">
				<p class="text-muted-foreground">No pending restaurant approvals</p>
			</div>
		{:else}
			<div class="space-y-4">
				{#each pendingRestaurants as restaurant (restaurant.id)}
					<div class="border rounded-lg p-6 hover:shadow-md transition-shadow">
						<div class="flex justify-between items-start">
							<div class="flex-1">
								<div class="flex items-center gap-3 mb-2">
									<h3 class="text-xl font-semibold">{restaurant.restaurant_name}</h3>
									<span class="px-2 py-1 rounded-full text-xs font-medium {getStatusBadge(restaurant.approval_status)}">
										{restaurant.approval_status}
									</span>
								</div>
								
								<div class="grid grid-cols-2 gap-4 mt-4 text-sm">
									{#if restaurant.cuisine_type}
										<div>
											<span class="text-muted-foreground">Cuisine:</span>
											<span class="ml-2 font-medium">{restaurant.cuisine_type}</span>
										</div>
									{/if}
									{#if restaurant.phone}
										<div>
											<span class="text-muted-foreground">Phone:</span>
											<span class="ml-2 font-medium">{restaurant.phone}</span>
										</div>
									{/if}
									{#if restaurant.address}
										<div class="col-span-2">
											<span class="text-muted-foreground">Address:</span>
											<span class="ml-2 font-medium">{restaurant.address}</span>
										</div>
									{/if}
									<div>
										<span class="text-muted-foreground">Registered:</span>
										<span class="ml-2 font-medium">{formatDate(restaurant.created_at)}</span>
									</div>
								</div>
							</div>

							<div class="flex gap-2 ml-4">
								<form 
									method="POST" 
									action="?/approve"
									use:enhance={() => {
										submitting = restaurant.id;
										return async ({ update }) => {
											await update();
											submitting = null;
										};
									}}
								>
									<input type="hidden" name="restaurantId" value={restaurant.id} />
									<Button
										type="submit"
										variant="primary"
										size="sm"
										disabled={submitting === restaurant.id}
									>
										{submitting === restaurant.id ? '...' : '✓ Approve'}
									</Button>
								</form>
								<form 
									method="POST" 
									action="?/reject"
									use:enhance={() => {
										if (!confirm('Are you sure you want to reject this restaurant?')) {
											return () => {};
										}
										submitting = restaurant.id;
										return async ({ update }) => {
											await update();
											submitting = null;
										};
									}}
								>
									<input type="hidden" name="restaurantId" value={restaurant.id} />
									<Button
										type="submit"
										variant="danger"
										size="sm"
										disabled={submitting === restaurant.id}
									>
										{submitting === restaurant.id ? '...' : '✗ Reject'}
									</Button>
								</form>
							</div>
						</div>
					</div>
				{/each}
			</div>
		{/if}
	{/if}

	<!-- All Restaurants Tab -->
	{#if activeTab === 'all'}
		{#if restaurants.length === 0}
			<div class="text-center py-12 bg-muted/30 rounded-lg">
				<p class="text-muted-foreground">No restaurants found</p>
			</div>
		{:else}
			<div class="overflow-x-auto">
				<table class="w-full">
					<thead class="border-b">
						<tr>
							<th class="text-left py-3 px-4 font-medium">Restaurant</th>
							<th class="text-left py-3 px-4 font-medium">Cuisine</th>
							<th class="text-left py-3 px-4 font-medium">Status</th>
							<th class="text-left py-3 px-4 font-medium">Registered</th>
							<th class="text-left py-3 px-4 font-medium">Actions</th>
						</tr>
					</thead>
					<tbody>
						{#each restaurants as restaurant (restaurant.id)}
							<tr class="border-b hover:bg-muted/30">
								<td class="py-3 px-4">
									<div>
										<div class="font-medium">{restaurant.restaurant_name}</div>
										{#if restaurant.address}
											<div class="text-sm text-muted-foreground">{restaurant.address}</div>
										{/if}
									</div>
								</td>
								<td class="py-3 px-4 text-sm">{restaurant.cuisine_type || '-'}</td>
								<td class="py-3 px-4">
									<span class="px-2 py-1 rounded-full text-xs font-medium {getStatusBadge(restaurant.approval_status)}">
										{restaurant.approval_status}
									</span>
								</td>
								<td class="py-3 px-4 text-sm text-muted-foreground">
									{formatDate(restaurant.created_at)}
								</td>
								<td class="py-3 px-4">
									<div class="flex gap-2">
										{#if restaurant.approval_status === ApprovalStatus.PENDING}
											<form 
												method="POST" 
												action="?/approve"
												use:enhance={() => {
													submitting = restaurant.id;
													return async ({ update }) => {
														await update();
														submitting = null;
													};
												}}
											>
												<input type="hidden" name="restaurantId" value={restaurant.id} />
												<Button
													type="submit"
													variant="primary"
													size="sm"
													disabled={submitting === restaurant.id}
												>
													Approve
												</Button>
											</form>
											<form 
												method="POST" 
												action="?/reject"
												use:enhance={() => {
													if (!confirm('Are you sure you want to reject this restaurant?')) {
														return () => {};
													}
													submitting = restaurant.id;
													return async ({ update }) => {
														await update();
														submitting = null;
													};
												}}
											>
												<input type="hidden" name="restaurantId" value={restaurant.id} />
												<Button
													type="submit"
													variant="danger"
													size="sm"
													disabled={submitting === restaurant.id}
												>
													Reject
												</Button>
											</form>
										{:else if restaurant.approval_status === ApprovalStatus.APPROVED}
											<form 
												method="POST" 
												action="?/suspend"
												use:enhance={() => {
													if (!confirm('Are you sure you want to suspend this restaurant?')) {
														return () => {};
													}
													submitting = restaurant.id;
													return async ({ update }) => {
														await update();
														submitting = null;
													};
												}}
											>
												<input type="hidden" name="restaurantId" value={restaurant.id} />
												<Button
													type="submit"
													variant="secondary"
													size="sm"
													disabled={submitting === restaurant.id}
												>
													Suspend
												</Button>
											</form>
										{:else if restaurant.approval_status === ApprovalStatus.SUSPENDED}
											<form 
												method="POST" 
												action="?/reactivate"
												use:enhance={() => {
													submitting = restaurant.id;
													return async ({ update }) => {
														await update();
														submitting = null;
													};
												}}
											>
												<input type="hidden" name="restaurantId" value={restaurant.id} />
												<Button
													type="submit"
													variant="primary"
													size="sm"
													disabled={submitting === restaurant.id}
												>
													Reactivate
												</Button>
											</form>
										{/if}
									</div>
								</td>
							</tr>
						{/each}
					</tbody>
				</table>
			</div>
		{/if}
	{/if}
</div>