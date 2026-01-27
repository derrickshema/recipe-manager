<script lang="ts">
	import { enhance } from '$app/forms';
	import { page } from '$app/stores';
	import { goto } from '$app/navigation';
	import { AuthLayout } from '$lib/components/auth';
	import { Button, TextField } from '$lib/components';

	interface FormData {
		error?: string;
		success?: boolean;
		message?: string;
	}

	let { form }: { form: FormData | null } = $props();
	let loading = $state(false);
	let password = $state('');
	let confirmPassword = $state('');
	let validationError = $state('');

	// Get token from URL query params
	let token = $derived($page.url.searchParams.get('token') || '');

	// Validate passwords match on input
	function validatePasswords() {
		if (password && confirmPassword && password !== confirmPassword) {
			validationError = 'Passwords do not match';
		} else if (password && password.length < 8) {
			validationError = 'Password must be at least 8 characters';
		} else {
			validationError = '';
		}
	}
</script>

<AuthLayout
	title="Reset Password"
	subtitle="Enter your new password below"
>
	{#if !token}
		<!-- No Token State -->
		<div class="space-y-4 text-center">
			<div class="mx-auto w-12 h-12 bg-destructive/10 rounded-full flex items-center justify-center">
				<svg class="w-6 h-6 text-destructive" fill="none" stroke="currentColor" viewBox="0 0 24 24">
					<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
				</svg>
			</div>
			<h3 class="text-lg font-medium">Invalid Reset Link</h3>
			<p class="text-sm text-muted-foreground">
				This password reset link is invalid or has expired. Please request a new one.
			</p>
			<Button onclick={() => goto('/forgot-password')} fullWidth>
				Request New Link
			</Button>
		</div>
	{:else if form?.success}
		<!-- Success State -->
		<div class="space-y-4 text-center">
			<div class="mx-auto w-12 h-12 bg-green-100 rounded-full flex items-center justify-center">
				<svg class="w-6 h-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
					<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
				</svg>
			</div>
			<h3 class="text-lg font-medium">Password Reset Complete</h3>
			<p class="text-sm text-muted-foreground">
				{form.message}
			</p>
			<Button onclick={() => goto('/login')} fullWidth>
				Sign In
			</Button>
		</div>
	{:else}
		<!-- Form State -->
		<form
			method="POST"
			use:enhance={() => {
				loading = true;
				return async ({ update }) => {
					loading = false;
					await update();
				};
			}}
			class="space-y-4"
		>
			<!-- Hidden token field -->
			<input type="hidden" name="token" value={token} />

			<TextField
				id="password"
				label="New Password"
				type="password"
				name="password"
				placeholder="Enter new password"
				bind:value={password}
				oninput={validatePasswords}
				required
			/>

			<TextField
				id="confirmPassword"
				label="Confirm Password"
				type="password"
				name="confirmPassword"
				placeholder="Confirm new password"
				bind:value={confirmPassword}
				oninput={validatePasswords}
				required
			/>

			{#if validationError}
				<div class="text-sm text-destructive">{validationError}</div>
			{/if}

			{#if form?.error}
				<div class="text-sm text-destructive">{form.error}</div>
			{/if}

			<Button 
				type="submit" 
				fullWidth 
				{loading}
				disabled={!!validationError || !password || !confirmPassword}
			>
				{loading ? 'Resetting...' : 'Reset Password'}
			</Button>
		</form>
	{/if}

	<div slot="footer" class="text-center text-sm">
		<p class="text-muted-foreground">
			Remember your password?
			<a href="/login" class="text-primary hover:underline">Sign in</a>
		</p>
	</div>
</AuthLayout>
