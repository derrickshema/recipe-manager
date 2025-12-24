<script lang="ts">
	import { goto } from '$app/navigation';
	import { onMount } from 'svelte';
	import { AuthLayout } from '$lib/components/auth';
	import { Button, TextField } from '$lib/components';
	import { restaurantRegistrationStore } from '$lib/stores/restaurantRegistrationStore';
	import { authStore } from '$lib/stores/authStore';

	let restaurantName = '';
	let cuisineType = '';
	let address = '';
	let restaurantPhone = '';
	let loading = false;
	let error: string | null = null;

	// Check if user came from step 1
	onMount(async () => {
		const data = await restaurantRegistrationStore.getData();
		if (!data.first_name || !data.email) {
			// User didn't complete step 1, redirect back
			goto('/register/restaurant');
		}
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

	async function handleSubmit() {
		if (!restaurantName) {
			error = 'Restaurant name is required';
			return;
		}

		loading = true;
		error = null;

		try {
			// Get all registration data
			const data = await restaurantRegistrationStore.getData();

			// Update with restaurant info
			const completeData = {
				...data,
				restaurant_name: restaurantName,
				cuisine_type: cuisineType,
				address,
				restaurant_phone: restaurantPhone
			};

			// Register restaurant owner (creates user + restaurant + membership)
			const user = await authStore.registerRestaurantOwner(completeData);

			// Reset the registration store
			restaurantRegistrationStore.reset();

			// Redirect to restaurant dashboard
			goto('/restaurant/dashboard');
		} catch (err: any) {
			if (err.status === 409) {
				error = 'An account with this email or username already exists';
			} else {
				error = err.message || 'An unexpected error occurred. Please try again.';
			}
			console.error('Registration error:', err);
		} finally {
			loading = false;
		}
	}
</script>

<AuthLayout
	title="Restaurant Owner Registration"
	subtitle="Step 2 of 2: Restaurant Details"
>
	<form on:submit|preventDefault={handleSubmit} class="space-y-4">
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

		{#if error}
			<div class="text-sm text-destructive">{error}</div>
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
