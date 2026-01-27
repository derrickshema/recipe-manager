<script lang="ts">
	import { enhance } from '$app/forms';
	import { goto } from '$app/navigation';
	import { AuthLayout } from '$lib/components/auth';
	import { Button, TextField } from '$lib/components';
	import { authStore } from '$lib/stores/authStore';
	import { SystemRole } from '$lib/types';
	import type { AuthUser } from '$lib/types';

	// Form state from server action
	interface FormData {
		error?: string;
		username?: string;
		success?: boolean;
		user?: AuthUser;
	}

	let { form }: { form: FormData | null } = $props();

	let loading = $state(false);

	function handleRedirect(user: AuthUser | null | undefined) {
		// Redirect based on user role
		if (user?.role) {
			switch (user.role) {
				case SystemRole.SUPERADMIN:
					goto('/overview');
					break;
				case SystemRole.CUSTOMER:
					goto('/home');
					break;
				case SystemRole.RESTAURANT_OWNER:
					goto('/dashboard');
					break;
				default:
					goto('/');
			}
		} else {
			goto('/');
		}
	}
</script>

<AuthLayout
	title="Welcome back"
	subtitle="Enter your username and password to sign in to your account"
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
						// Update client-side auth store with user data (NOT the token)
						authStore.setUser(data.user);
						handleRedirect(data.user);
						return;
					}
				}
				// Let SvelteKit handle the form state update for errors
				await update();
			};
		}}
		class="space-y-4"
	>
		<TextField
			id="username"
			label="Username"
			type="text"
			name="username"
			placeholder="johndoe"
			value={form?.username ?? ''}
			required
		/>

		<TextField
			id="password"
			label="Password"
			type="password"
			name="password"
			required
		/>

		<div class="text-right">
			<a href="/forgot-password" class="text-sm text-primary hover:underline">
				Forgot password?
			</a>
		</div>

		{#if form?.error}
			<div class="text-sm text-destructive">{form.error}</div>
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