<script lang="ts">
	import { goto } from '$app/navigation';
	import { AuthLayout } from '$lib/components/auth';
	import { Button, TextField } from '$lib/components';
	import { restaurantRegistrationStore } from '$lib/stores/restaurantRegistrationStore';

	let firstName = '';
	let lastName = '';
	let username = '';
	let email = '';
	let phoneNumber = '';
	let password = '';
	let confirmPassword = '';
	let error: string | null = null;

	$: passwordsMatch = password === confirmPassword;

	function handleNext() {
		if (!firstName || !lastName || !username || !email || !password || !confirmPassword) {
			error = 'Please fill in all required fields';
			return;
		}

		if (!passwordsMatch) {
			error = 'Passwords do not match';
			return;
		}

		// Save owner info to store
		restaurantRegistrationStore.updateOwnerInfo({
			first_name: firstName,
			last_name: lastName,
			username,
			email,
			password,
			phone_number: phoneNumber
		});

		// Go to next step
		goto('/register/restaurant/business');
	}
</script>

<AuthLayout
	title="Restaurant Owner Registration"
	subtitle="Step 1 of 2: Your Information"
>
	<form on:submit|preventDefault={handleNext} class="space-y-4">
		<!-- Progress Indicator -->
		<div class="mb-6">
			<div class="flex items-center justify-between mb-2">
				<span class="text-sm font-medium text-primary">Step 1: Owner Info</span>
				<span class="text-sm text-muted-foreground">Step 2: Restaurant Details</span>
			</div>
			<div class="w-full bg-muted rounded-full h-2">
				<div class="bg-primary h-2 rounded-full" style="width: 50%"></div>
			</div>
		</div>

		<div class="grid grid-cols-2 gap-4">
			<TextField
				id="firstName"
				label="First Name"
				name="firstName"
				placeholder="John"
				bind:value={firstName}
				required
			/>

			<TextField
				id="lastName"
				label="Last Name"
				name="lastName"
				placeholder="Doe"
				bind:value={lastName}
				required
			/>
		</div>

		<TextField
			id="username"
			label="Username"
			name="username"
			placeholder="johndoe"
			bind:value={username}
			required
		/>

		<TextField
			id="email"
			label="Email"
			type="email"
			name="email"
			placeholder="john@restaurant.com"
			bind:value={email}
			required
		/>

		<TextField
			id="phoneNumber"
			label="Phone Number (Optional)"
			type="tel"
			name="phoneNumber"
			placeholder="+1 (555) 123-4567"
			bind:value={phoneNumber}
		/>

		<TextField
			id="password"
			label="Password"
			type="password"
			name="password"
			bind:value={password}
			required
			helperText="Must be at least 8 characters with uppercase, lowercase, number, and special character"
		/>

		<TextField
			id="confirmPassword"
			label="Confirm Password"
			type="password"
			name="confirmPassword"
			bind:value={confirmPassword}
			error={!passwordsMatch && confirmPassword ? 'Passwords do not match' : undefined}
			required
		/>

		{#if error}
			<div class="text-sm text-destructive">{error}</div>
		{/if}

		<Button type="submit" fullWidth>
			Next: Restaurant Details →
		</Button>
	</form>

	<div slot="footer" class="text-center text-sm space-y-2">
		<p class="text-muted-foreground">
			Already have an account?
			<a href="/login" class="text-primary hover:underline">Sign in</a>
		</p>
		<p class="text-muted-foreground">
			<a href="/register" class="text-primary hover:underline">← Back to registration options</a>
		</p>
	</div>
</AuthLayout>
