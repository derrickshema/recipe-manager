<script lang="ts">
	import { goto } from '$app/navigation';
	import { AuthLayout } from '$lib/components/auth';
	import { Button, TextField } from '$lib/components';
	import { authStore } from '$lib/stores/authStore';

	let firstName = '';
	let lastName = '';
	let username = '';
	let email = '';
	let password = '';
	let confirmPassword = '';
	let loading = false;
	let error: string | null = null;

	$: passwordsMatch = password === confirmPassword;

	async function handleSubmit() {
		if (!firstName || !lastName || !username || !email || !password || !confirmPassword) {
			error = 'Please fill in all fields';
			return;
		}

		if (!passwordsMatch) {
			error = 'Passwords do not match';
			return;
		}

		loading = true;
		error = null;

		try {
			const user = await authStore.register({
				first_name: firstName,
				last_name: lastName,
				username,
				email,
				password
			});
			
			// Redirect based on user role (compare role as string to avoid type mismatch)
			if (String(user?.role).toLowerCase() === 'admin') {
				goto('/system/overview');
			} else {
				goto('/restaurant/dashboard');
			}
		} catch (err: any) {
			if (err.status === 409) {
				error = 'An account with this email already exists';
			} else {
				error = 'An unexpected error occurred. Please try again.';
			}
			console.error('Registration error:', err);
		} finally {
			loading = false;
		}
	}
</script>

<AuthLayout title="Create an account" subtitle="Enter your information to create your account">
	<form on:submit|preventDefault={handleSubmit} class="space-y-4">
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
			placeholder="name@example.com"
			bind:value={email}
			required
		/>

		<TextField
			id="password"
			label="Password"
			type="password"
			name="password"
			bind:value={password}
			required
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

		<Button 
			type="submit" 
			fullWidth 
			{loading}
		>
			{loading ? 'Creating Account...' : 'Create Account'}
		</Button>
	</form>

	<div slot="footer" class="text-center text-sm">
		<p class="text-muted-foreground">
			Already have an account?
			<a href="/login" class="text-primary hover:underline">Sign in</a>
		</p>
	</div>
</AuthLayout>