<script lang="ts">
	import { enhance } from '$app/forms';
	import { goto } from '$app/navigation';
	import { onMount } from 'svelte';
	import { AuthLayout } from '$lib/components/auth';
	import { Button, TextField } from '$lib/components';
	import { restaurantRegistrationStore, type RestaurantRegistrationData } from '$lib/stores/restaurantRegistrationStore';
	import { authStore } from '$lib/stores/authStore';
	import type { AuthUser } from '$lib/types';

	// Form state from server action
	interface FormData {
		error?: string;
		restaurantName?: string;
		cuisineType?: string;
		address?: string;
		restaurantPhone?: string;
		success?: boolean;
		user?: AuthUser;
	}

	let { form }: { form: FormData | null } = $props();

	let restaurantName = $state('');
	let cuisineType = $state('');
	let address = $state('');
	let restaurantPhone = $state('');
	let loading = $state(false);
	
	// Owner data from step 1 (stored in client-side store)
	let ownerData = $state<Partial<RestaurantRegistrationData>>({});

	// Check if user came from step 1
	onMount(async () => {
		const data = await restaurantRegistrationStore.getData();
		if (!data.first_name || !data.email) {
			// User didn't complete step 1, redirect back
			goto('/register/restaurant');
			return;
		}
		ownerData = data;
	});

	function handleBack() {
		// Save current restaurant info before going back
		restaurantRegistrationStore.updateRestaurantInfo({
			restaurant_name: restaurantName,
			cuisine_type: cuisineType,
			address,
			restaurant_phone: restaurantPhone
		});
		goto('/register/restaurant');
	}
</script>

<AuthLayout
	title="Restaurant Owner Registration"
	subtitle="Step 2 of 2: Restaurant Details"
>
	<form
		method="POST"
		use:enhance={() => {
			loading = true;

			return async ({ result, update }) => {
				loading = false;
				
				if (result.type === 'success') {
					const data = result.data as FormData;
					if (data?.success && data?.user) {
						// Reset the registration store
						restaurantRegistrationStore.reset();
						// Set user in auth store
						authStore.setUser(data.user);
						goto('/dashboard');
						return;
					}
				}
				await update();
			};
		}}
		class="space-y-4"
	>
		<!-- Hidden fields for owner data from step 1 -->
		<input type="hidden" name="firstName" value={ownerData.first_name ?? ''} />
		<input type="hidden" name="lastName" value={ownerData.last_name ?? ''} />
		<input type="hidden" name="username" value={ownerData.username ?? ''} />
		<input type="hidden" name="email" value={ownerData.email ?? ''} />
		<input type="hidden" name="password" value={ownerData.password ?? ''} />
		<input type="hidden" name="phoneNumber" value={ownerData.phone_number ?? ''} />
		
		<!-- Progress Indicator -->
		<div class="mb-6">
			<div class="flex items-center justify-between mb-2">
				<span class="text-sm text-muted-foreground">Step 1: Owner Info</span>
				<span class="text-sm font-medium text-primary">Step 2: Restaurant Details</span>
			</div>
			<div class="w-full bg-muted rounded-full h-2">
				<div class="bg-primary h-2 rounded-full" style="width: 100%"></div>
			</div>
		</div>

		<TextField
			id="restaurantName"
			label="Restaurant Name"
			name="restaurantName"
			placeholder="Joe's Pizza"
			bind:value={restaurantName}
			required
		/>

		<TextField
			id="cuisineType"
			label="Cuisine Type (Optional)"
			name="cuisineType"
			placeholder="Italian, Mexican, Chinese, etc."
			bind:value={cuisineType}
		/>

		<TextField
			id="address"
			label="Restaurant Address (Optional)"
			name="address"
			placeholder="123 Main St, City, State ZIP"
			bind:value={address}
		/>

		<TextField
			id="restaurantPhone"
			label="Restaurant Phone (Optional)"
			type="tel"
			name="restaurantPhone"
			placeholder="+1 (555) 123-4567"
			bind:value={restaurantPhone}
		/>

		<div class="bg-muted p-4 rounded-lg">
			<p class="text-sm text-muted-foreground">
				<strong>Note:</strong> Your account will be reviewed by our team. You'll receive an email
				once your restaurant is approved and ready to accept orders.
			</p>
		</div>

		{#if form?.error}
			<div class="text-sm text-destructive">{form.error}</div>
		{/if}

		<div class="flex gap-3">
			<Button type="button" variant="secondary" on:click={handleBack} class="flex-1">
				← Back
			</Button>
			<Button type="submit" {loading} class="flex-1">
				{loading ? 'Creating Account...' : 'Complete Registration'}
			</Button>
		</div>
	</form>

	<div slot="footer" class="text-center text-sm">
		<p class="text-muted-foreground">
			Already have an account?
			<a href="/login" class="text-primary hover:underline">Sign in</a>
		</p>
	</div>
</AuthLayout>
