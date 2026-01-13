<script lang="ts">
	import { enhance } from '$app/forms';
	import { page } from '$app/state';
	import { isAuthenticated, user, authStore } from '$lib/stores/authStore';

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