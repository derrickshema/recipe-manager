<script lang="ts">
	import { enhance } from '$app/forms';
	import { page } from '$app/state';
	import { isAuthenticated, user, authStore } from '$lib/stores/authStore';
	import { cartItemCount } from '$lib/stores/cartStore';

	export let showNav = true;
</script>

<div class="min-h-screen flex flex-col">
	{#if showNav}
		<header class="border-b bg-white">
			<div class="container mx-auto px-4 py-4 flex items-center justify-between">
				<a href="/" class="text-xl font-bold hover:opacity-80 transition-opacity">Recipe Manager</a>

				<nav class="flex items-center gap-6">
					{#if $isAuthenticated}
						<div class="flex items-center gap-4">
							<!-- Home Link -->
							<a 
								href="/home" 
								class="text-sm font-medium text-gray-600 hover:text-primary transition-colors"
								class:text-primary={String(page.url.pathname) === '/home'}
							>
								Home
							</a>
							
							<!-- Orders Link -->
							<a 
								href="/orders" 
								class="text-sm font-medium text-gray-600 hover:text-primary transition-colors"
								class:text-primary={String(page.url.pathname) === '/orders'}
							>
								My Orders
							</a>
							
							<!-- Cart Link with Badge -->
							<a 
								href="/cart" 
								class="relative text-gray-600 hover:text-primary transition-colors"
								class:text-primary={String(page.url.pathname) === '/cart'}
							>
								<svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
									<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 3h2l.4 2M7 13h10l4-8H5.4M7 13L5.4 5M7 13l-2.293 2.293c-.63.63-.184 1.707.707 1.707H17m0 0a2 2 0 100 4 2 2 0 000-4zm-8 2a2 2 0 11-4 0 2 2 0 014 0z" />
								</svg>
								{#if $cartItemCount > 0}
									<span class="absolute -top-2 -right-2 bg-primary text-white text-xs font-bold rounded-full w-5 h-5 flex items-center justify-center">
										{$cartItemCount > 9 ? '9+' : $cartItemCount}
									</span>
								{/if}
							</a>
							
							<!-- User Profile -->
							<div class="flex items-center gap-3">
								<!-- Avatar Circle -->
								<div class="w-10 h-10 rounded-full bg-gray-200 flex items-center justify-center">
									<span class="text-sm font-semibold text-gray-700">
										{$user?.first_name?.[0]}{$user?.last_name?.[0]}
									</span>
								</div>
								<!-- User Name -->
								<span class="text-sm font-medium text-gray-900">
									{$user?.first_name} {$user?.last_name}
								</span>
							</div>
							
							<!-- Logout Form (uses server action) -->
							<form
								method="POST"
								action="/logout"
								use:enhance={() => {
									// Clear client-side auth store immediately
									authStore.setUser(null);
									return async ({ update }) => {
										await update();
									};
								}}
							>
								<button
									type="submit"
									class="px-4 py-2 text-sm font-medium rounded-md border border-gray-300 hover:bg-gray-50 transition-colors"
								>
									Logout
								</button>
							</form>
						</div>
					{:else}
						<a
							href="/login"
							class="text-sm font-medium transition-colors hover:text-primary"
							class:active={String(page.url.pathname) === '/login'}
						>
							Login
						</a>
						<a
							href="/register"
							class="px-4 py-2 text-sm font-medium rounded-md bg-primary text-white hover:bg-primary/90 transition-colors"
							class:active={String(page.url.pathname) === '/register'}
						>
							Get Started
						</a>
					{/if}
				</nav>
			</div>
		</header>
	{/if}

	<main class="flex-1">
		<slot />
	</main>

	<footer class="border-t">
		<div class="container mx-auto px-4 py-4 text-center text-sm text-muted-foreground">
			© {new Date().getFullYear()} Recipe Manager. All rights reserved.
		</div>
	</footer>
</div>