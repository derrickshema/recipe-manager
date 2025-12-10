<script lang="ts">
	import { Button } from '$lib/components';
	import { isAuthenticated } from '$lib/stores/authStore';
</script>

<div class="container mx-auto px-4">
	<div class="flex flex-col items-center justify-center min-h-[80vh] text-center">
		<h1 class="text-4xl md:text-6xl font-bold mb-6">
			Professional Recipe Management
		</h1>
		
		<p class="text-xl md:text-2xl text-muted-foreground max-w-2xl mb-8">
			Streamline your kitchen operations with our comprehensive recipe management system.
			Perfect for restaurants of all sizes.
		</p>

		<div class="flex flex-col sm:flex-row gap-4">
			{#if !$isAuthenticated}
				<Button href="/register" size="lg">Get Started</Button>
				<Button href="/login" variant="secondary" size="lg">Log In</Button>
			{:else}
				<Button href="/restaurant/dashboard" size="lg">Go to Dashboard</Button>
			{/if}
		</div>
	</div>

	<!-- Features Section -->
	<div class="grid grid-cols-1 md:grid-cols-3 gap-8 py-16">
		<div class="flex flex-col items-center text-center p-6">
			<h3 class="text-xl font-semibold mb-4">Recipe Standardization</h3>
			<p class="text-muted-foreground">
				Ensure consistency across your kitchen with standardized recipes and procedures.
			</p>
		</div>

		<div class="flex flex-col items-center text-center p-6">
			<h3 class="text-xl font-semibold mb-4">Team Management</h3>
			<p class="text-muted-foreground">
				Manage kitchen staff access and responsibilities with role-based permissions.
			</p>
		</div>

		<div class="flex flex-col items-center text-center p-6">
			<h3 class="text-xl font-semibold mb-4">Inventory Control</h3>
			<p class="text-muted-foreground">
				Track ingredients and manage costs with our integrated inventory system.
			</p>
		</div>
	</div>
</div>
