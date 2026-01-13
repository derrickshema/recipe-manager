<script lang="ts">
	import { enhance } from '$app/forms';
	import { goto } from '$app/navigation';
	import { AuthLayout } from '$lib/components/auth';
	import { Button, TextField } from '$lib/components';
	import { authStore } from '$lib/stores/authStore';
	import type { AuthUser } from '$lib/types';

	// Form state from server action
	interface FormData {
		error?: string;
		firstName?: string;
		lastName?: string;
		username?: string;
		email?: string;
		success?: boolean;
		user?: AuthUser;
	}

	let { form }: { form: FormData | null } = $props();

	let password = $state('');
	let confirmPassword = $state('');
	let loading = $state(false);

	let passwordsMatch = $derived(password === confirmPassword || confirmPassword === '');
</script>

<AuthLayout title="Create Customer Account" subtitle="Start ordering from your favorite restaurants">
	<form
		method="POST"
		use:enhance={() => {
			loading = true;

			return async ({ result, update }) => {
				loading = false;
				
				if (result.type === 'success') {
					const data = result.data as FormData;
					if (data?.success && data?.user) {
						authStore.setUser(data.user);
						goto('/home');
						return;
					}
				}
				await update();
			};
		}}
		class="space-y-4"
	>
		<div class="grid grid-cols-2 gap-4">
			<TextField
				id="firstName"
				label="First Name"
				name="firstName"
				placeholder="John"
				value={form?.firstName ?? ''}
				required
			/>

			<TextField
				id="lastName"
				label="Last Name"
				name="lastName"
				placeholder="Doe"
				value={form?.lastName ?? ''}
				required
			/>
		</div>

		<TextField
			id="username"
			label="Username"
			name="username"
			placeholder="johndoe"
			value={form?.username ?? ''}
			required
		/>

		<TextField
			id="email"
			label="Email"
			type="email"
			name="email"
			placeholder="name@example.com"
			value={form?.email ?? ''}
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
			error={!passwordsMatch ? 'Passwords do not match' : undefined}
			required
		/>

		{#if form?.error}
			<div class="text-sm text-destructive">{form.error}</div>
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
