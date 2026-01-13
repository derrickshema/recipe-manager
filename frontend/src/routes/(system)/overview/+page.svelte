<script lang="ts">
    // SSR data from +page.server.ts and layout
    let { data } = $props();

    // Derived from SSR data
    let user = $derived(data.user);
    let stats = $derived(data.stats);
</script>

<div class="container mx-auto py-8">
    <h1 class="text-2xl font-bold mb-4">System Overview</h1>
    <p class="text-muted-foreground mb-8">Welcome back, {user?.first_name}!</p>

    {#if data.error}
        <div class="bg-destructive/10 text-destructive p-4 rounded-lg mb-6">
            {data.error}
        </div>
    {/if}

    <!-- Stats Grid -->
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        <div class="bg-card p-6 rounded-lg shadow">
            <h3 class="text-sm font-medium text-muted-foreground">Total Restaurants</h3>
            <p class="text-3xl font-bold mt-2">{stats?.totalRestaurants ?? 0}</p>
        </div>
        
        <a href="/restaurants" class="bg-card p-6 rounded-lg shadow hover:shadow-lg transition-shadow">
            <h3 class="text-sm font-medium text-muted-foreground">Pending Approvals</h3>
            <p class="text-3xl font-bold mt-2 text-yellow-600">{stats?.pendingApprovals ?? 0}</p>
            <span class="text-sm text-primary mt-2 inline-block">Review →</span>
        </a>
        
        <div class="bg-card p-6 rounded-lg shadow">
            <h3 class="text-sm font-medium text-muted-foreground">Approved</h3>
            <p class="text-3xl font-bold mt-2 text-green-600">{stats?.approvedRestaurants ?? 0}</p>
        </div>
        
        <div class="bg-card p-6 rounded-lg shadow">
            <h3 class="text-sm font-medium text-muted-foreground">Suspended</h3>
            <p class="text-3xl font-bold mt-2 text-gray-600">{stats?.suspendedRestaurants ?? 0}</p>
        </div>
    </div>

    <!-- Quick Actions -->
    <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
        <a href="/restaurants" class="bg-card p-6 rounded-lg shadow hover:shadow-lg transition-shadow">
            <h2 class="text-lg font-semibold mb-2">Restaurants</h2>
            <p class="text-muted-foreground">Manage restaurant registrations and access</p>
            <span class="text-primary hover:underline mt-4 inline-block">View Restaurants →</span>
        </a>
    </div>
</div>