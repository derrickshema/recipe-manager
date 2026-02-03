<script lang="ts">
	import { Button } from '$lib/components';
	import type { Restaurant, Recipe } from '$lib/types';
	import { addToCart, cart, cartItemCount } from '$lib/stores/cartStore';

	let { data } = $props();

	let restaurant = $derived(data.restaurant as Restaurant | null);
	let recipes = $derived(data.recipes as Recipe[] ?? []);
	let error = $derived(data.error as string | undefined);
	
	// Track which items are being added (for button feedback)
	let addingItems = $state<Record<number, boolean>>({});
	
	// Format price for display
	function formatPrice(price: number): string {
		return new Intl.NumberFormat('en-US', {
			style: 'currency',
			currency: 'USD'
		}).format(price);
	}
	
	// Handle add to cart with feedback
	function handleAddToCart(recipe: Recipe) {
		if (!restaurant) return;
		
		addingItems[recipe.id] = true;
		addToCart(recipe, restaurant.id, restaurant.restaurant_name);
		
		// Show feedback briefly
		setTimeout(() => {
			addingItems[recipe.id] = false;
		}, 500);
	}
</script>

<svelte:head>
	<title>{restaurant?.restaurant_name ?? 'Restaurant'} | Menu</title>
</svelte:head>

<div class="container mx-auto px-4 py-8">
	<!-- Header with Back and Cart -->
	<div class="flex justify-between items-center mb-6">
		<a href="/home" class="inline-flex items-center text-muted-foreground hover:text-foreground">
			<svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 mr-2" viewBox="0 0 20 20" fill="currentColor">
				<path fill-rule="evenodd" d="M9.707 16.707a1 1 0 01-1.414 0l-6-6a1 1 0 010-1.414l6-6a1 1 0 011.414 1.414L5.414 9H17a1 1 0 110 2H5.414l4.293 4.293a1 1 0 010 1.414z" clip-rule="evenodd" />
			</svg>
			Back to Restaurants
		</a>
		
		<!-- Cart Button -->
		<a 
			href="/cart" 
			class="inline-flex items-center gap-2 px-4 py-2 bg-primary text-primary-foreground rounded-lg hover:bg-primary/90 transition-colors"
		>
			<svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
				<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 3h2l.4 2M7 13h10l4-8H5.4M7 13L5.4 5M7 13l-2.293 2.293c-.63.63-.184 1.707.707 1.707H17m0 0a2 2 0 100 4 2 2 0 000-4zm-8 2a2 2 0 11-4 0 2 2 0 014 0z" />
			</svg>
			Cart
			{#if $cartItemCount > 0}
				<span class="bg-white text-primary text-xs font-bold px-2 py-0.5 rounded-full">
					{$cartItemCount}
				</span>
			{/if}
		</a>
	</div>

	{#if error || !restaurant}
		<!-- Error State -->
		<div class="text-center py-16">
			<h1 class="text-2xl font-bold text-destructive mb-4">Restaurant Not Found</h1>
			<p class="text-muted-foreground mb-6">The restaurant you're looking for doesn't exist or is not available.</p>
			<a href="/home" class="inline-flex items-center justify-center rounded-md font-medium bg-primary text-primary-foreground hover:bg-primary/90 h-10 px-4 py-2">Browse Restaurants</a>
		</div>
	{:else}
		<!-- Restaurant Header -->
		<div class="mb-8">
			<div class="flex flex-col md:flex-row gap-6 items-start">
				<!-- Restaurant Logo/Image -->
				<div class="w-full md:w-48 h-48 bg-muted rounded-lg flex items-center justify-center overflow-hidden">
					{#if restaurant.logo_url}
						<img 
							src={restaurant.logo_url} 
							alt={restaurant.restaurant_name} 
							class="w-full h-full object-cover"
						/>
					{:else}
						<svg xmlns="http://www.w3.org/2000/svg" class="h-16 w-16 text-muted-foreground" fill="none" viewBox="0 0 24 24" stroke="currentColor">
							<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" />
						</svg>
					{/if}
				</div>

				<!-- Restaurant Info -->
				<div class="flex-1">
					<h1 class="text-3xl md:text-4xl font-bold mb-2">{restaurant.restaurant_name}</h1>
					
					<div class="flex flex-wrap gap-4 text-muted-foreground mb-4">
						{#if restaurant.cuisine_type}
							<span class="inline-flex items-center">
								<svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
									<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
								</svg>
								{restaurant.cuisine_type}
							</span>
						{/if}
						
						{#if restaurant.address}
							<span class="inline-flex items-center">
								<svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
									<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
									<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
								</svg>
								{restaurant.address}
							</span>
						{/if}
						
						{#if restaurant.phone}
							<span class="inline-flex items-center">
								<svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
									<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z" />
								</svg>
								{restaurant.phone}
							</span>
						{/if}
					</div>
				</div>
			</div>
		</div>

		<!-- Menu Section -->
		<div class="border-t pt-8">
			<h2 class="text-2xl font-bold mb-6">Menu</h2>
			
			{#if recipes.length === 0}
				<div class="text-center py-12 bg-muted/30 rounded-lg">
					<svg xmlns="http://www.w3.org/2000/svg" class="h-12 w-12 mx-auto text-muted-foreground mb-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
						<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
					</svg>
					<p class="text-muted-foreground">No menu items available yet.</p>
				</div>
			{:else}
				<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
					{#each recipes as recipe (recipe.id)}
						<div class="border rounded-lg overflow-hidden hover:shadow-lg transition-shadow flex flex-col">
							<!-- Recipe Image -->
							<div class="h-48 bg-muted flex items-center justify-center overflow-hidden">
								{#if recipe.image_url}
									<img 
										src={recipe.image_url} 
										alt={recipe.title} 
										class="w-full h-full object-cover"
									/>
								{:else}
									<svg xmlns="http://www.w3.org/2000/svg" class="h-12 w-12 text-muted-foreground" fill="none" viewBox="0 0 24 24" stroke="currentColor">
										<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
									</svg>
								{/if}
							</div>
							
							<!-- Recipe Info -->
							<div class="p-4 flex-1 flex flex-col">
								<div class="flex justify-between items-start mb-2">
									<h3 class="text-lg font-semibold">{recipe.title}</h3>
									<span class="text-lg font-bold text-primary">{formatPrice(recipe.price)}</span>
								</div>
								
								{#if recipe.description}
									<p class="text-muted-foreground text-sm mb-3 line-clamp-2 flex-1">{recipe.description}</p>
								{:else}
									<div class="flex-1"></div>
								{/if}
								
								<!-- Recipe Meta -->
								<div class="flex flex-wrap gap-3 text-xs text-muted-foreground mb-4">
									{#if recipe.prep_time || recipe.cook_time}
										<span class="inline-flex items-center">
											<svg xmlns="http://www.w3.org/2000/svg" class="h-3 w-3 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
												<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
											</svg>
											{(recipe.prep_time || 0) + (recipe.cook_time || 0)} min
										</span>
									{/if}
									
									{#if recipe.servings}
										<span class="inline-flex items-center">
											<svg xmlns="http://www.w3.org/2000/svg" class="h-3 w-3 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
												<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
											</svg>
											Serves {recipe.servings}
										</span>
									{/if}
								</div>
								
								<!-- Add to Cart Button -->
								<Button 
									fullWidth 
									onclick={() => handleAddToCart(recipe)}
									disabled={addingItems[recipe.id]}
								>
									{#if addingItems[recipe.id]}
										<svg class="animate-spin h-4 w-4 mr-2" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
											<circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
											<path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
										</svg>
										Added!
									{:else}
										<svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
											<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
										</svg>
										Add to Cart
									{/if}
								</Button>
							</div>
						</div>
					{/each}
				</div>
			{/if}
		</div>
	{/if}
</div>

<style>
	.line-clamp-2 {
		display: -webkit-box;
		-webkit-line-clamp: 2;
		line-clamp: 2;
		-webkit-box-orient: vertical;
		overflow: hidden;
	}
</style>
