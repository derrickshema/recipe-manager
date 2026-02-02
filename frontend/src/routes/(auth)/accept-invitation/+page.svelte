<script lang="ts">
    import { enhance } from '$app/forms';
    import { Button } from '$lib/components';
    import AuthLayout from '$lib/components/auth/AuthLayout.svelte';

    let { data, form } = $props();
    
    let submitting = $state(false);

    // Format role for display
    function formatRole(role: string): string {
        switch (role) {
            case 'restaurant_admin':
                return 'Admin';
            case 'employee':
                return 'Employee';
            default:
                return role;
        }
    }
</script>

<AuthLayout 
    title="Staff Invitation" 
    subtitle={data.invitation ? `You've been invited to join ${data.invitation.restaurant_name}` : 'Accept your invitation'}
>
    {#if data.error}
        <div class="text-center space-y-4">
            <div class="bg-destructive/10 text-destructive p-4 rounded-lg">
                {data.error}
            </div>
            <p class="text-muted-foreground text-sm">
                The invitation link may have expired or is invalid.
                Please contact the person who invited you for a new invitation.
            </p>
            <a href="/login" class="inline-flex items-center justify-center rounded-md text-sm font-medium ring-offset-background transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 border border-input bg-background hover:bg-accent hover:text-accent-foreground h-10 px-4 py-2">
                Go to Login
            </a>
        </div>
    {:else if data.invitation}
        <div class="space-y-6">
            <!-- Invitation Details -->
            <div class="bg-muted/30 p-6 rounded-lg space-y-4">
                <div class="flex items-center gap-3">
                    <div class="w-12 h-12 bg-primary/10 rounded-full flex items-center justify-center">
                        <span class="text-2xl">🍴</span>
                    </div>
                    <div>
                        <h3 class="font-semibold text-lg">{data.invitation.restaurant_name}</h3>
                        <p class="text-sm text-muted-foreground">Restaurant</p>
                    </div>
                </div>
                
                <hr class="border-border" />
                
                <div class="grid grid-cols-2 gap-4 text-sm">
                    <div>
                        <p class="text-muted-foreground">Invited Email</p>
                        <p class="font-medium">{data.invitation.email}</p>
                    </div>
                    <div>
                        <p class="text-muted-foreground">Role</p>
                        <p class="font-medium">{formatRole(data.invitation.role)}</p>
                    </div>
                </div>
                
                <div class="bg-blue-50 dark:bg-blue-900/20 text-blue-800 dark:text-blue-200 p-3 rounded text-sm">
                    {#if data.invitation.role === 'restaurant_admin'}
                        <strong>As an Admin</strong>, you'll be able to manage restaurant settings, staff, and recipes.
                    {:else}
                        <strong>As an Employee</strong>, you'll be able to view recipes and restaurant information.
                    {/if}
                </div>
            </div>

            {#if form?.error}
                <div class="bg-destructive/10 text-destructive p-4 rounded-lg">
                    {form.error}
                </div>
            {/if}

            <!-- Accept Form -->
            <form 
                method="POST" 
                action="?/accept"
                use:enhance={() => {
                    submitting = true;
                    return async ({ update }) => {
                        await update();
                        submitting = false;
                    };
                }}
            >
                <input type="hidden" name="token" value={data.token} />
                
                <div class="space-y-4">
                    <Button type="submit" class="w-full" disabled={submitting}>
                        {submitting ? 'Accepting...' : 'Accept Invitation'}
                    </Button>
                    
                    <a href="/" class="inline-flex w-full items-center justify-center rounded-md text-sm font-medium ring-offset-background transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 border border-input bg-background hover:bg-accent hover:text-accent-foreground h-10 px-4 py-2">
                        Decline
                    </a>
                </div>
            </form>
            
            <p class="text-xs text-center text-muted-foreground">
                By accepting, you'll be added as a {formatRole(data.invitation.role).toLowerCase()} at {data.invitation.restaurant_name}.
            </p>
        </div>
    {:else}
        <div class="text-center space-y-4">
            <p class="text-muted-foreground">Loading invitation details...</p>
        </div>
    {/if}

    <svelte:fragment slot="footer">
        <p class="px-8 text-center text-sm text-muted-foreground">
            Don't have an account?{' '}
            <a href="/register?redirect=/accept-invitation?token={data.token}" class="underline underline-offset-4 hover:text-primary">
                Register first
            </a>
        </p>
    </svelte:fragment>
</AuthLayout>
