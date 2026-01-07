<script lang="ts">
    import { user } from '$lib/stores/authStore';
</script>

<div class="container mx-auto py-8">
    <h1 class="text-2xl font-bold mb-4">System Overview</h1>
    <p>Welcome, {$user?.first_name}!</p>

    <div class="grid grid-cols-1 md:grid-cols-3 gap-6 mt-8">
        <div class="bg-card p-6 rounded-lg shadow">
            <h2 class="text-lg font-semibold mb-2">Restaurants</h2>
            <p class="text-muted-foreground">Manage restaurant registrations and access</p>
            <a href="/restaurants" class="text-primary hover:underline mt-4 inline-block">View Restaurants →</a>
        </div>
    </div>
</div>