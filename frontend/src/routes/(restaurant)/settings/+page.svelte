<script lang="ts">
    import { enhance } from '$app/forms';
    import { Button } from '$lib/components';
    import { ApprovalStatus } from '$lib/types';

    // SSR data from +page.server.ts
    let { data, form } = $props();

    // Reactive state
    let submitting = $state(false);
    let uploadingLogo = $state(false);
    let removingLogo = $state(false);
    let logoPreview = $state<string | null>(null);

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
            // Reset logo preview when data refreshes
            logoPreview = null;
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

    function handleLogoSelect(event: Event) {
        const input = event.target as HTMLInputElement;
        const file = input.files?.[0];
        if (file) {
            const reader = new FileReader();
            reader.onload = (e) => {
                logoPreview = e.target?.result as string;
            };
            reader.readAsDataURL(file);
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
        <!-- Logo Section -->
        <div class="bg-card border rounded-lg p-6 space-y-4">
            <h2 class="text-lg font-semibold">Restaurant Logo</h2>
            
            <div class="flex items-start gap-6">
                <!-- Logo Preview -->
                <div class="flex-shrink-0">
                    {#if logoPreview}
                        <img 
                            src={logoPreview} 
                            alt="Logo preview" 
                            class="w-32 h-32 object-cover rounded-lg border"
                        />
                    {:else if restaurant.logo_url}
                        <img 
                            src={restaurant.logo_url} 
                            alt="{restaurant.restaurant_name} logo" 
                            class="w-32 h-32 object-cover rounded-lg border"
                        />
                    {:else}
                        <div class="w-32 h-32 bg-muted rounded-lg border flex items-center justify-center">
                            <svg class="w-12 h-12 text-muted-foreground" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
                            </svg>
                        </div>
                    {/if}
                </div>

                <!-- Upload/Remove Actions -->
                <div class="flex-1 space-y-3">
                    <p class="text-sm text-muted-foreground">
                        Upload a logo for your restaurant. Recommended size: 256x256 pixels. Max file size: 5MB.
                    </p>

                    <!-- Upload Form -->
                    <form 
                        method="POST" 
                        action="?/uploadLogo"
                        enctype="multipart/form-data"
                        use:enhance={() => {
                            uploadingLogo = true;
                            return async ({ update }) => {
                                await update();
                                uploadingLogo = false;
                                logoPreview = null;
                            };
                        }}
                        class="flex items-center gap-3"
                    >
                        <input type="hidden" name="restaurantId" value={restaurant.id} />
                        <input 
                            type="file" 
                            name="logo" 
                            id="logo"
                            accept="image/jpeg,image/png,image/gif,image/webp"
                            onchange={handleLogoSelect}
                            class="text-sm file:mr-4 file:py-2 file:px-4 file:rounded-lg file:border-0 file:text-sm file:font-medium file:bg-primary file:text-primary-foreground hover:file:bg-primary/90 file:cursor-pointer"
                        />
                        <Button type="submit" size="sm" disabled={uploadingLogo}>
                            {uploadingLogo ? 'Uploading...' : 'Upload'}
                        </Button>
                    </form>

                    <!-- Remove Logo -->
                    {#if restaurant.logo_url}
                        <form 
                            method="POST" 
                            action="?/removeLogo"
                            use:enhance={() => {
                                removingLogo = true;
                                return async ({ update }) => {
                                    await update();
                                    removingLogo = false;
                                };
                            }}
                        >
                            <input type="hidden" name="restaurantId" value={restaurant.id} />
                            <input type="hidden" name="logoUrl" value={restaurant.logo_url} />
                            <Button type="submit" variant="danger" size="sm" disabled={removingLogo}>
                                {removingLogo ? 'Removing...' : 'Remove Logo'}
                            </Button>
                        </form>
                    {/if}
                </div>
            </div>
        </div>

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
