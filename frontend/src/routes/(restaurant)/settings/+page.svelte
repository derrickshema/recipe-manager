<script lang="ts">
    import { enhance } from '$app/forms';
    import { Button } from '$lib/components';
    import { ApprovalStatus } from '$lib/types';

    // SSR data from +page.server.ts
    let { data, form } = $props();

    // Reactive state
    let submitting = $state(false);

    // Derived from SSR data
    let restaurant = $derived(data.restaurant);

    // Form values (initialized from SSR data)
    let formValues = $state({
        restaurantName: '',
        cuisineType: '',
        address: '',
        phone: ''
    });

    // Initialize form values from restaurant data
    $effect(() => {
        if (restaurant) {
            formValues = {
                restaurantName: restaurant.restaurant_name || '',
                cuisineType: restaurant.cuisine_type || '',
                address: restaurant.address || '',
                phone: restaurant.phone || ''
            };
        }
    });

    function getStatusBadge(status: ApprovalStatus): { class: string; text: string } {
        switch (status) {
            case ApprovalStatus.APPROVED:
                return { class: 'bg-green-100 text-green-800', text: 'Approved' };
            case ApprovalStatus.PENDING:
                return { class: 'bg-yellow-100 text-yellow-800', text: 'Pending Approval' };
            case ApprovalStatus.REJECTED:
                return { class: 'bg-red-100 text-red-800', text: 'Rejected' };
            case ApprovalStatus.SUSPENDED:
                return { class: 'bg-gray-100 text-gray-800', text: 'Suspended' };
            default:
                return { class: 'bg-gray-100 text-gray-800', text: status };
        }
    }
</script>

<div class="space-y-6 max-w-2xl">
    <!-- Header -->
    <div>
        <a href="/dashboard" class="text-sm text-muted-foreground hover:text-foreground mb-2 inline-block">
            ← Back to Dashboard
        </a>
        <h1 class="text-3xl font-bold">Restaurant Settings</h1>
        {#if restaurant}
            {@const badge = getStatusBadge(restaurant.approval_status)}
            <div class="flex items-center gap-3 mt-2">
                <p class="text-muted-foreground">{restaurant.restaurant_name}</p>
                <span class="px-2 py-1 rounded-full text-xs font-medium {badge.class}">
                    {badge.text}
                </span>
            </div>
        {/if}
    </div>

    <!-- Messages -->
    {#if form?.success}
        <div class="bg-green-100 text-green-800 p-4 rounded-lg">
            {form.message}
        </div>
    {/if}
    {#if form?.error}
        <div class="bg-destructive/10 text-destructive p-4 rounded-lg">
            {form.error}
        </div>
    {/if}
    {#if data.error}
        <div class="bg-destructive/10 text-destructive p-4 rounded-lg">
            {data.error}
        </div>
    {/if}

    {#if !restaurant}
        <div class="text-center py-12 bg-muted/30 rounded-lg">
            <p class="text-muted-foreground">No restaurant found</p>
        </div>
    {:else}
        <!-- Settings Form -->
        <form 
            method="POST" 
            action="?/update"
            class="bg-card border rounded-lg p-6 space-y-6"
            use:enhance={() => {
                submitting = true;
                return async ({ update }) => {
                    await update();
                    submitting = false;
                };
            }}
        >
            <input type="hidden" name="restaurantId" value={restaurant.id} />

            <div>
                <label for="restaurantName" class="block text-sm font-medium mb-1">
                    Restaurant Name *
                </label>
                <input 
                    type="text" 
                    id="restaurantName" 
                    name="restaurantName" 
                    bind:value={formValues.restaurantName}
                    class="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-primary"
                    required
                />
            </div>

            <div>
                <label for="cuisineType" class="block text-sm font-medium mb-1">
                    Cuisine Type
                </label>
                <input 
                    type="text" 
                    id="cuisineType" 
                    name="cuisineType" 
                    bind:value={formValues.cuisineType}
                    placeholder="e.g., Italian, Mexican, Japanese"
                    class="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-primary"
                />
            </div>

            <div>
                <label for="address" class="block text-sm font-medium mb-1">
                    Address
                </label>
                <textarea 
                    id="address" 
                    name="address" 
                    bind:value={formValues.address}
                    rows="2"
                    placeholder="123 Main Street, City, State 12345"
                    class="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-primary"
                ></textarea>
            </div>

            <div>
                <label for="phone" class="block text-sm font-medium mb-1">
                    Phone Number
                </label>
                <input 
                    type="tel" 
                    id="phone" 
                    name="phone" 
                    bind:value={formValues.phone}
                    placeholder="(555) 123-4567"
                    class="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-primary"
                />
            </div>

            <div class="pt-4 border-t">
                <Button type="submit" disabled={submitting}>
                    {submitting ? 'Saving...' : 'Save Changes'}
                </Button>
            </div>
        </form>

        <!-- Restaurant Info -->
        <div class="bg-muted/30 rounded-lg p-6 space-y-4">
            <h2 class="text-lg font-semibold">Restaurant Information</h2>
            <div class="grid grid-cols-2 gap-4 text-sm">
                <div>
                    <span class="text-muted-foreground">Created:</span>
                    <span class="ml-2">
                        {new Date(restaurant.created_at).toLocaleDateString()}
                    </span>
                </div>
                <div>
                    <span class="text-muted-foreground">Last Updated:</span>
                    <span class="ml-2">
                        {new Date(restaurant.updated_at).toLocaleDateString()}
                    </span>
                </div>
                {#if restaurant.approval_status}
                    {@const badge = getStatusBadge(restaurant.approval_status)}
                    <div>
                        <span class="text-muted-foreground">Status:</span>
                        <span class="ml-2 px-2 py-0.5 rounded-full text-xs font-medium {badge.class}">
                            {badge.text}
                        </span>
                    </div>
                {/if}
            </div>
        </div>
    {/if}
</div>
