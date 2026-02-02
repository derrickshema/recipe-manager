<script lang="ts">
	import { Button } from '$lib/components';
	import { goto } from '$app/navigation';
	import type { Restaurant } from '$lib/types';

	// SSR data from +page.server.ts and layout
	let { data } = $props();

	// Derived from SSR data
	let user = $derived(data.user);
	let restaurants = $derived(data.restaurants ?? []);
	
	// Search and filter state - initialized from server data
	let searchQuery = $state(data.search ?? '');
	let cuisineFilter = $state(data.cuisine ?? '');
	
	// Common cuisine types for filter dropdown
	const cuisineTypes = [
		'Italian',
		'Mexican',
		'Chinese',
		'Japanese',
		'Indian',
		'Thai',
		'American',
		'French',
		'Mediterranean',
		'Korean',
		'Vietnamese',
		'Greek'
	];
	
	// Handle search/filter submission
	function handleSearch() {
		const params = new URLSearchParams();
		if (searchQuery.trim()) params.set('search', searchQuery.trim());
		if (cuisineFilter) params.set('cuisine', cuisineFilter);
		
		const queryString = params.toString() ? `?${params.toString()}` : '';
		goto(`/home${queryString}`);
	}
	
	// Clear all filters
	function clearFilters() {
		searchQuery = '';
		cuisineFilter = '';
		goto('/home');
	}
	
	// Check if any filters are active
	let hasActiveFilters = $derived(searchQuery.trim() !== '' || cuisineFilter !== '');
</script>

<div class="container mx-auto px-4">
	<!-- Welcome Section -->
	<div class="flex flex-col items-center justify-center min-h-[30vh] text-center">
		<h1 class="text-4xl md:text-6xl font-bold mb-6">
			Welcome back, {user?.first_name}! 👋
		</h1>
		
		<p class="text-xl md:text-2xl text-muted-foreground max-w-2xl mb-8">
			Ready to order some delicious food?
		</p>
	</div>

	<!-- Search and Filter Section -->
	<div class="mb-8 p-6 bg-muted/30 rounded-lg">
		<form onsubmit={(e) => { e.preventDefault(); handleSearch(); }} class="flex flex-col md:flex-row gap-4">
			<!-- Search Input -->
			<div class="flex-1">
				<label for="search" class="sr-only">Search restaurants</label>
				<div class="relative">
					<svg xmlns="http://www.w3.org/2000/svg" class="absolute left-3 top-1/2 -translate-y-1/2 h-5 w-5 text-muted-foreground" fill="none" viewBox="0 0 24 24" stroke="currentColor">
						<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
					</svg>
					<input
						type="text"
						id="search"
						bind:value={searchQuery}
						placeholder="Search restaurants..."
						class="w-full pl-10 pr-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary bg-background"
					/>
				</div>
			</div>
			
			<!-- Cuisine Filter -->
			<div class="md:w-48">
				<label for="cuisine" class="sr-only">Filter by cuisine</label>
				<select
					id="cuisine"
					bind:value={cuisineFilter}
					class="w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary bg-background"
				>
					<option value="">All Cuisines</option>
					{#each cuisineTypes as cuisine}
						<option value={cuisine}>{cuisine}</option>
					{/each}
				</select>
			</div>
			
			<!-- Search Button -->
			<Button type="submit">
				Search
			</Button>
			
			<!-- Clear Filters -->
			{#if hasActiveFilters}
				<Button variant="secondary" onclick={clearFilters}>
					Clear
				</Button>
			{/if}
		</form>
		
		<!-- Active Filters Display -->
		{#if hasActiveFilters}
			<div class="mt-4 flex flex-wrap gap-2">
				{#if searchQuery.trim()}
					<span class="inline-flex items-center px-3 py-1 rounded-full text-sm bg-primary/10 text-primary">
						Search: "{searchQuery}"
						<button 
							onclick={() => { searchQuery = ''; handleSearch(); }}
							class="ml-2 hover:text-primary/70"
						>
							×
						</button>
					</span>
				{/if}
				{#if cuisineFilter}
					<span class="inline-flex items-center px-3 py-1 rounded-full text-sm bg-primary/10 text-primary">
						Cuisine: {cuisineFilter}
						<button 
							onclick={() => { cuisineFilter = ''; handleSearch(); }}
							class="ml-2 hover:text-primary/70"
						>
							×
						</button>
					</span>
				{/if}
			</div>
		{/if}
	</div>

	<!-- Restaurant Listings Section -->
	<div class="py-8">
		<div class="flex justify-between items-center mb-8">
			<h2 class="text-3xl font-bold">
				{hasActiveFilters ? 'Search Results' : 'Browse Restaurants'}
			</h2>
			<span class="text-muted-foreground">
				{restaurants.length} restaurant{restaurants.length !== 1 ? 's' : ''} found
			</span>
		</div>
		
		{#if restaurants.length === 0}
			<!-- No Results -->
			<div class="text-center py-12 bg-muted/30 rounded-lg">
				{#if hasActiveFilters}
					<svg xmlns="http://www.w3.org/2000/svg" class="h-12 w-12 mx-auto text-muted-foreground mb-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
						<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.172 16.172a4 4 0 015.656 0M9 10h.01M15 10h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
					</svg>
					<h3 class="text-xl font-semibold mb-2">No restaurants found</h3>
					<p class="text-muted-foreground mb-4">Try adjusting your search or filters</p>
					<Button onclick={clearFilters}>Clear Filters</Button>
				{:else}
					<svg xmlns="http://www.w3.org/2000/svg" class="h-12 w-12 mx-auto text-muted-foreground mb-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
						<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" />
					</svg>
					<h3 class="text-xl font-semibold mb-2">No restaurants available</h3>
					<p class="text-muted-foreground">Check back soon for new restaurants!</p>
				{/if}
			</div>
		{:else}
			<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
				{#each restaurants as restaurant (restaurant.id)}
					<a 
						href="/restaurant/{restaurant.id}"
						class="border rounded-lg overflow-hidden hover:shadow-lg transition-shadow block"
					>
						<!-- Restaurant Image -->
						<div class="h-40 bg-muted flex items-center justify-center overflow-hidden">
							{#if restaurant.logo_url}
								<img 
									src={restaurant.logo_url} 
									alt={restaurant.restaurant_name} 
									class="w-full h-full object-cover"
								/>
							{:else}
								<svg xmlns="http://www.w3.org/2000/svg" class="h-12 w-12 text-muted-foreground" fill="none" viewBox="0 0 24 24" stroke="currentColor">
									<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" />
								</svg>
							{/if}
						</div>
						
						<!-- Restaurant Info -->
						<div class="p-6">
							<h3 class="text-xl font-semibold mb-2">{restaurant.restaurant_name}</h3>
							<p class="text-muted-foreground mb-4">
								{restaurant.cuisine_type || 'Various Cuisine'}
								{#if restaurant.address}
									<span class="block text-sm mt-1">{restaurant.address}</span>
								{/if}
							</p>
							<Button fullWidth>View Menu</Button>
						</div>
					</a>
				{/each}
			</div>
		{/if}
	</div>
</div>