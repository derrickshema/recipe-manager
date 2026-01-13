<script lang="ts">
    // SSR data from +page.server.ts
    let { data } = $props();

    // Derived from SSR data
    let user = $derived(data.user);
    let restaurant = $derived(data.restaurant);
    let stats = $derived(data.stats);
</script>

<div class="container mx-auto py-8">
    <h1 class="text-2xl font-bold mb-4">Restaurant Dashboard</h1>
    {#if restaurant}
        <p class="text-muted-foreground mb-8">Managing: <strong>{restaurant.restaurant_name}</strong></p>
    {:else}
        <p class="text-muted-foreground mb-8">No restaurant found. Please complete your restaurant registration.</p>
    {/if}

    {#if data.error}
        <div class="bg-destructive/10 text-destructive p-4 rounded-lg mb-6">
            {data.error}
        </div>
    {/if}

    <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
        <a href="/recipes" class="bg-card p-6 rounded-lg shadow hover:shadow-lg transition-shadow">
            <h2 class="text-lg font-semibold mb-2">Recipes</h2>
            <p class="text-3xl font-bold text-primary mb-2">{stats?.totalRecipes ?? 0}</p>
            <p class="text-muted-foreground">Manage your restaurant's recipes</p>
            <span class="text-primary hover:underline mt-4 inline-block">View Recipes →</span>
        </a>

        <a href="/staff" class="bg-card p-6 rounded-lg shadow hover:shadow-lg transition-shadow">
            <h2 class="text-lg font-semibold mb-2">Staff</h2>
            <p class="text-3xl font-bold text-primary mb-2">{stats?.staffCount ?? 0}</p>
            <p class="text-muted-foreground">Manage your restaurant's staff</p>
            <span class="text-primary hover:underline mt-4 inline-block">Manage Staff →</span>
        </a>

        <a href="/settings" class="bg-card p-6 rounded-lg shadow hover:shadow-lg transition-shadow">
            <h2 class="text-lg font-semibold mb-2">Settings</h2>
            <p class="text-muted-foreground">Restaurant settings and preferences</p>
            <span class="text-primary hover:underline mt-4 inline-block">Settings →</span>
        </a>
    </div>
</div>