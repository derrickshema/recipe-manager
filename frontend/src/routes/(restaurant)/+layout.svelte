<script lang="ts">
    import { enhance } from '$app/forms';
    import { authStore, user } from '$lib/stores/authStore';
</script>

<div class="min-h-screen bg-background">
    <header class="border-b">
        <div class="container mx-auto px-4 py-4 flex justify-between items-center">
            <h1 class="text-xl font-semibold">Recipe Manager</h1>
            <nav class="space-x-4">
                <a href="/dashboard" class="text-sm font-medium hover:text-primary">Dashboard</a>
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
        <slot />
    </main>
</div>
