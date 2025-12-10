<script lang="ts">
    import { page } from '$app/state';
    let user = page.data.user;
</script>

<div class="container mx-auto py-8">
    <h1 class="text-2xl font-bold mb-4">Restaurant Dashboard</h1>
    <p class="text-muted-foreground mb-8">Manage your restaurant's recipes and staff</p>

    <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div class="bg-card p-6 rounded-lg shadow">
            <h2 class="text-lg font-semibold mb-2">Recipes</h2>
            <p class="text-muted-foreground">Manage your restaurant's recipes</p>
            <a href="/restaurant/recipes" class="text-primary hover:underline mt-4 inline-block">View Recipes →</a>
        </div>

        <div class="bg-card p-6 rounded-lg shadow">
            <h2 class="text-lg font-semibold mb-2">Staff</h2>
            <p class="text-muted-foreground">Manage your restaurant's staff</p>
            <a href="/restaurant/staff" class="text-primary hover:underline mt-4 inline-block">Manage Staff →</a>
        </div>

        <div class="bg-card p-6 rounded-lg shadow">
            <h2 class="text-lg font-semibold mb-2">Settings</h2>
            <p class="text-muted-foreground">Restaurant settings and preferences</p>
            <a href="/restaurant/settings" class="text-primary hover:underline mt-4 inline-block">Settings →</a>
        </div>
    </div>
</div>