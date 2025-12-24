<script lang="ts">
	import { Button } from '$lib/components';
	import { isAuthenticated, user } from '$lib/stores/authStore';
	import { goto } from '$app/navigation';
	import { SystemRole } from '$lib/types';

	// Redirect authenticated users based on role
	$: if ($isAuthenticated && $user) {
		if ($user.role === SystemRole.SUPERADMIN) {
			goto('/system/overview');
		} else if ($user.role === SystemRole.USER) {
			goto('/restaurant/dashboard');
		}
		// CUSTOMER role stays on this page to browse restaurants
	}
</script>

<div class="container mx-auto px-4">
	<!-- Hero Section -->
	<div class="flex flex-col items-center justify-center min-h-[70vh] text-center">
		<h1 class="text-4xl md:text-6xl font-bold mb-6">
			Order Food from Your Favorite Restaurants
		</h1>
		
		<p class="text-xl md:text-2xl text-muted-foreground max-w-2xl mb-8">
			Discover amazing restaurants, order delicious meals, and get them delivered to your door.
		</p>

		<div class="flex flex-col sm:flex-row gap-4">
			{#if !$isAuthenticated}
				<Button href="/register" size="lg">Get Started</Button>
				<Button href="/login" variant="secondary" size="lg">Log In</Button>
			{:else}
				<div class="text-lg font-medium mb-4">
					Welcome back, {$user?.first_name}! 👋
				</div>
			{/if}
		</div>
	</div>

	<!-- Restaurant Listings Section -->
	<div class="py-16">
		<h2 class="text-3xl font-bold mb-8 text-center">Browse Restaurants</h2>
		
		<!-- Placeholder for restaurant listings -->
		<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
			<!-- Restaurant Card Placeholder -->
			<div class="border rounded-lg p-6 hover:shadow-lg transition-shadow">
				<div class="h-40 bg-muted rounded-lg mb-4"></div>
				<h3 class="text-xl font-semibold mb-2">Restaurant Name</h3>
				<p class="text-muted-foreground mb-4">Cuisine Type • $$ • 30-45 min</p>
				<Button fullWidth>View Menu</Button>
			</div>

			<div class="border rounded-lg p-6 hover:shadow-lg transition-shadow">
				<div class="h-40 bg-muted rounded-lg mb-4"></div>
				<h3 class="text-xl font-semibold mb-2">Restaurant Name</h3>
				<p class="text-muted-foreground mb-4">Cuisine Type • $$ • 30-45 min</p>
				<Button fullWidth>View Menu</Button>
			</div>

			<div class="border rounded-lg p-6 hover:shadow-lg transition-shadow">
				<div class="h-40 bg-muted rounded-lg mb-4"></div>
				<h3 class="text-xl font-semibold mb-2">Restaurant Name</h3>
				<p class="text-muted-foreground mb-4">Cuisine Type • $$ • 30-45 min</p>
				<Button fullWidth>View Menu</Button>
			</div>
		</div>

		<div class="text-center mt-8">
			<p class="text-muted-foreground">
				Restaurant listings will be populated here. This is a placeholder for the customer experience.
			</p>
		</div>
	</div>

	<!-- Features Section for Restaurants -->
	<div class="bg-muted/30 py-16 rounded-lg">
		<div class="text-center mb-12">
			<h2 class="text-3xl font-bold mb-4">Own a Restaurant?</h2>
			<p class="text-xl text-muted-foreground mb-6">
				Join our platform and reach thousands of hungry customers
			</p>
			<Button href="/register/restaurant" size="lg">List Your Restaurant</Button>
		</div>

		<div class="grid grid-cols-1 md:grid-cols-3 gap-8 px-6">
			<div class="flex flex-col items-center text-center p-6">
				<h3 class="text-xl font-semibold mb-4">Reach More Customers</h3>
				<p class="text-muted-foreground">
					Get discovered by customers looking for great food in your area
				</p>
			</div>

			<div class="flex flex-col items-center text-center p-6">
				<h3 class="text-xl font-semibold mb-4">Manage Orders Easily</h3>
				<p class="text-muted-foreground">
					Simple dashboard to manage orders, menu, and customer interactions
				</p>
			</div>

			<div class="flex flex-col items-center text-center p-6">
				<h3 class="text-xl font-semibold mb-4">Grow Your Business</h3>
				<p class="text-muted-foreground">
					Analytics and insights to help you make data-driven decisions
				</p>
			</div>
		</div>
	</div>
</div>
