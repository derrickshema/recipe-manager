<script lang="ts">
    import { enhance } from '$app/forms';
    import { authStore, user } from '$lib/stores/authStore';
    import type { LayoutData } from './$types';
    import type { Snippet } from 'svelte';

    // SSR data from +layout.server.ts
    let { data, children }: { data: LayoutData; children: Snippet } = $props();

    // Derived from SSR data
    let restaurant = $derived(data.restaurant);
</script>

<div class="min-h-screen bg-background">
    <header class="border-b">
        <div class="container mx-auto px-4 py-4 flex justify-between items-center">
            <div class="flex items-center gap-3">
                {#if restaurant?.logo_url}
                    <img 
                        src={restaurant.logo_url} 
                        alt="{restaurant.restaurant_name} logo" 
                        class="h-10 w-10 object-cover rounded-lg"
                    />
                {:else}
                    <div class="h-10 w-10 bg-primary/10 rounded-lg flex items-center justify-center">
                        <span class="text-lg font-bold text-primary">
                            {restaurant?.restaurant_name?.charAt(0) || 'R'}
                        </span>
                    </div>
                {/if}
                <h1 class="text-xl font-semibold">{restaurant?.restaurant_name || 'My Restaurant'}</h1>
            </div>
            <nav class="space-x-4">
                <a href="/dashboard" class="text-sm font-medium hover:text-primary">Dashboard</a>
                <a href="/dashboard/orders" class="text-sm font-medium hover:text-primary">Orders</a>
                <a href="/recipes" class="text-sm font-medium hover:text-primary">Recipes</a>
                <a href="/staff" class="text-sm font-medium hover:text-primary">Staff</a>
                <a href="/settings" class="text-sm font-medium hover:text-primary">Settings</a>
            </nav>
            <div class="text-sm flex items-center gap-4">
                {#if $user}
                    <span>{$user.first_name} {$user.last_name}</span>
                    <form
                        method="POST"
                        action="/logout"
                        use:enhance={() => {
                            authStore.setUser(null);
                            return async ({ update }) => {
                                await update();
                            };
                        }}
                    >
                        <button 
                            type="submit"
                            class="text-sm font-medium text-destructive hover:text-destructive/90"
                        >
                            Logout
                        </button>
                    </form>
                {/if}
            </div>
        </div>
    </header>

    <main class="container mx-auto px-4 py-8">
        {@render children()}
    </main>
</div>
