<script lang="ts">
	import { enhance } from '$app/forms';
	import { AuthLayout } from '$lib/components/auth';
	import { Button, TextField } from '$lib/components';

	interface FormData {
		error?: string;
		success?: boolean;
		message?: string;
		email?: string;
	}

	let { form }: { form: FormData | null } = $props();
	let loading = $state(false);
</script>

<AuthLayout
	title="Forgot Password"
	subtitle="Enter your email address and we'll send you a link to reset your password"
>
	{#if form?.success}
		<!-- Success State -->
		<div class="space-y-4 text-center">
			<div class="mx-auto w-12 h-12 bg-green-100 rounded-full flex items-center justify-center">
				<svg class="w-6 h-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
					<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
				</svg>
			</div>
			<h3 class="text-lg font-medium">Check your email</h3>
			<p class="text-sm text-muted-foreground">
				{form.message}
			</p>
			<p class="text-sm text-muted-foreground">
				Didn't receive the email? Check your spam folder or
				<button 
					type="button" 
					class="text-primary hover:underline"
					onclick={() => window.location.reload()}
				>
					try again
				</button>
			</p>
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
			<TextField
				id="email"
				label="Email Address"
				type="email"
				name="email"
				placeholder="you@example.com"
				value={form?.email ?? ''}
				required
			/>

			{#if form?.error}
				<div class="text-sm text-destructive">{form.error}</div>
			{/if}

			<Button 
				type="submit" 
				fullWidth 
				{loading}
			>
				{loading ? 'Sending...' : 'Send Reset Link'}
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
