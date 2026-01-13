<script lang="ts">
	import { Button } from '$lib/components';
	import type { Restaurant } from '$lib/types';

	// SSR data from +page.server.ts and layout
	let { data } = $props();

	// Derived from SSR data
	let user = $derived(data.user);
	let restaurants = $derived(data.restaurants ?? []);
</script>

<div class="container mx-auto px-4">
	<!-- Welcome Section -->
	<div class="flex flex-col items-center justify-center min-h-[40vh] text-center">
		<h1 class="text-4xl md:text-6xl font-bold mb-6">
			Welcome back, {user?.first_name}! 👋
		</h1>
		
		<p class="text-xl md:text-2xl text-muted-foreground max-w-2xl mb-8">
			Ready to order some delicious food?
		</p>
	</div>


	<!-- Restaurant Listings Section -->
	<div class="py-16">
		<h2 class="text-3xl font-bold mb-8 text-center">Browse Restaurants</h2>
		
		{#if restaurants.length === 0}
			<!-- Placeholder for when no restaurants are available -->
			<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
				<!-- Restaurant Card Placeholder -->
				<div class="border rounded-lg p-6 hover:shadow-lg transition-shadow">
					<div class="h-40 bg-muted rounded-lg mb-4"></div>
					<h3 class="text-xl font-semibold mb-2">Coming Soon</h3>
					<p class="text-muted-foreground mb-4">Restaurants will appear here</p>
					<Button fullWidth disabled>View Menu</Button>
				</div>
			</div>
		{:else}
			<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
				{#each restaurants as restaurant (restaurant.id)}
					<div class="border rounded-lg p-6 hover:shadow-lg transition-shadow">
						<div class="h-40 bg-muted rounded-lg mb-4"></div>
						<h3 class="text-xl font-semibold mb-2">{restaurant.restaurant_name}</h3>
						<p class="text-muted-foreground mb-4">
							{restaurant.cuisine_type || 'Various'} • $$ • 30-45 min
						</p>
						<Button fullWidth>View Menu</Button>
					</div>
				{/each}
			</div>
		{/if}
	</div>
</div>