<script lang="ts">
	import { enhance } from '$app/forms';
	import { goto } from '$app/navigation';
	import { AuthLayout } from '$lib/components/auth';
	import { Button, TextField } from '$lib/components';
	import { authStore } from '$lib/stores/authStore';
	import type { ActionData, PageData } from './$types';
	import type { AuthUser } from '$lib/types';

	interface FormResult {
		error?: string;
		restaurantName?: string;
		cuisineType?: string;
		address?: string;
		restaurantPhone?: string;
		success?: boolean;
		user?: AuthUser;
	}

	let { data, form }: { data: PageData; form: FormResult | null } = $props();

	let restaurantName = $state(form?.restaurantName ?? '');
	let cuisineType = $state(form?.cuisineType ?? '');
	let address = $state(form?.address ?? '');
	let restaurantPhone = $state(form?.restaurantPhone ?? '');
	let loading = $state(false);
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
					const resultData = result.data as FormResult;
					if (resultData?.success && resultData?.user) {
						// Set user in auth store
						authStore.setUser(resultData.user);
						goto('/dashboard');
						return;
					}
				}
				await update();
			};
		}}
		class="space-y-4"
	>
		<!-- Owner info confirmation -->
		<div class="bg-muted/50 p-3 rounded-lg text-sm">
			<p class="text-muted-foreground">
				Registering as: <span class="font-medium text-foreground">{data.ownerName}</span>
				<span class="text-muted-foreground">({data.ownerEmail})</span>
			</p>
		</div>
		
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
			<a href="/register/restaurant" class="flex-1">
				<Button type="button" variant="secondary" class="w-full">
					← Back
				</Button>
			</a>
			<Button type="submit" disabled={loading} class="flex-1">
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
