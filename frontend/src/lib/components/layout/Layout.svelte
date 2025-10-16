<script lang="ts">
	import { page } from '$app/state';
	import { isAuthenticated, user } from '$lib/stores/authStore';
	import { SystemRole } from '$lib/types/roles';

	export let showNav = true;
</script>

<div class="min-h-screen flex flex-col">
	{#if showNav}
		<header class="border-b">
			<div class="container mx-auto px-4 py-4 flex items-center justify-between">
				<a href="/" class="text-xl font-bold">Recipe Manager</a>

				<nav class="flex items-center space-x-4">
					{#if $isAuthenticated}
						<a
							href="/dashboard"
							class="text-sm font-medium transition-colors hover:text-primary"
							class:active={String(page.url.pathname) === '/dashboard'}
						>
							Dashboard
						</a>
						{#if $user?.role === SystemRole.SUPERADMIN}
							<a
								href="/admin"
								class="text-sm font-medium transition-colors hover:text-primary"
								class:active={page.url.pathname.startsWith('/admin')}
							>
								Admin
							</a>
						{/if}
						<div class="flex items-center space-x-2">
							<span class="text-sm">{$user?.first_name} {$user?.last_name}</span>
							<button
								class="text-sm font-medium text-destructive hover:text-destructive/90"
								on:click={() => {/* Add logout handler */}}
							>
								Logout
							</button>
						</div>
					{:else}
						<a
							href="/login"
							class="text-sm font-medium transition-colors hover:text-primary"
							class:active={page.url.pathname === '/login'}
						>
							Login
						</a>
						<a
							href="/register"
							class="text-sm font-medium transition-colors hover:text-primary"
							class:active={page.url.pathname === '/register'}
						>
							Register
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