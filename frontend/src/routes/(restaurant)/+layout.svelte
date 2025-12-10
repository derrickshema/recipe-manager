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
            <h1 class="text-xl font-semibold">Recipe Manager</h1>
            <nav class="space-x-4">
                <a href="/restaurant/dashboard" class="text-sm font-medium hover:text-primary">Dashboard</a>
                <a href="/restaurant/recipes" class="text-sm font-medium hover:text-primary">Recipes</a>
                <a href="/restaurant/staff" class="text-sm font-medium hover:text-primary">Staff</a>
                <a href="/restaurant/settings" class="text-sm font-medium hover:text-primary">Settings</a>
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
