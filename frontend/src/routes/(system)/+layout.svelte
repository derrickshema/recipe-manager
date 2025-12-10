<script lang="ts">
    import { authStore, user } from '$lib/stores/authStore';
    import { goto } from '$app/navigation';
    
    async function handleLogout() {
        await authStore.signOut();
        goto('/login');
    }
</script>

<div class="min-h-screen bg-background">
    <header class="border-b">
        <div class="container mx-auto px-4 py-4 flex justify-between items-center">
            <h1 class="text-xl font-semibold">Recipe Manager Admin</h1>
            <nav class="space-x-4">
                <a href="/system/overview" class="text-sm font-medium hover:text-primary">Overview</a>
                <a href="/system/restaurants" class="text-sm font-medium hover:text-primary">Restaurants</a>
                <a href="/system/users" class="text-sm font-medium hover:text-primary">Users</a>
                <a href="/system/settings" class="text-sm font-medium hover:text-primary">Settings</a>
            </nav>
            <div class="text-sm flex items-center gap-4">
                {#if $user}
                    <span>{$user.first_name} {$user.last_name}</span>
                    <button 
                        onclick={handleLogout}
                        class="text-sm font-medium text-destructive hover:text-destructive/90"
                    >
                        Logout
                    </button>
                {/if}
            </div>
        </div>
    </header>

    <main class="container mx-auto px-4 py-8">
        <slot />
    </main>
</div>