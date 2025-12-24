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
				// Note: Backend will default role to CUSTOMER
			});
			
			// Redirect customer to home page
			goto('/');
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

<AuthLayout title="Create Customer Account" subtitle="Start ordering from your favorite restaurants">
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

		<Button type="submit" fullWidth {loading}>
			{loading ? 'Creating Account...' : 'Create Account'}
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
