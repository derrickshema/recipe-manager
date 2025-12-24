<script lang="ts">
	import { goto } from '$app/navigation';
	import { AuthLayout } from '$lib/components/auth';
	import { Button, TextField } from '$lib/components';
	import { authStore } from '$lib/stores/authStore';
	import { SystemRole } from '$lib/types';

	let username = '';
	let password = '';
	let loading = false;
	let error: string | null = null;

	async function handleSubmit() {
		if (!username || !password) {
			error = 'Please fill in all fields';
			return;
		}

		loading = true;
		error = null;

		try {
			const user = await authStore.login({ username, password });
			
			// Redirect based on user role
			if (user?.role) {
				switch (user.role) {
					case SystemRole.SUPERADMIN:
						goto('/system/overview');
						break;
					case SystemRole.CUSTOMER:
						goto('/');  // Customer home page
						break;
					case SystemRole.USER:
						goto('/restaurant/dashboard');  // Restaurant staff
						break;
					default:
						goto('/');
				}
			} else {
				goto('/');
			}
		} catch (err: any) {
			if (err.status === 401) {
				error = 'Invalid username or password';
			} else {
				error = 'An unexpected error occurred. Please try again.';
			}
			console.error('Login error:', err);
		} finally {
			loading = false;
		}
	}
</script>

<AuthLayout
	title="Welcome back"
	subtitle="Enter your username and password to sign in to your account"
>
	<form on:submit|preventDefault={handleSubmit} class="space-y-4">
		<TextField
			id="username"
			label="Username"
			type="text"
			name="username"
			placeholder="johndoe"
			bind:value={username}
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

		{#if error}
			<div class="text-sm text-destructive">{error}</div>
		{/if}

		<Button 
			type="submit" 
			fullWidth 
			{loading}
		>
			{loading ? 'Signing In...' : 'Sign In'}
		</Button>
	</form>

	<div slot="footer" class="text-center text-sm">
		<p class="text-muted-foreground">
			Don't have an account?
			<a href="/register" class="text-primary hover:underline">Sign up</a>
		</p>
	</div>
</AuthLayout>