<script lang="ts">
	import { enhance } from '$app/forms';
	import { goto } from '$app/navigation';
	import { AuthLayout } from '$lib/components/auth';
	import { Button, TextField } from '$lib/components';

	interface PageData {
		autoVerified: boolean;
		error: string | null;
		message: string | null;
		justRegistered: boolean;
		registeredEmail: string | null;
	}

	interface FormData {
		error?: string;
		success?: boolean;
		message?: string;
	}

	let { data, form }: { data: PageData; form: FormData | null } = $props();
	let loading = $state(false);
	let email = $state(data.registeredEmail ?? '');
</script>

<AuthLayout
	title="Email Verification"
	subtitle={data.autoVerified 
		? "Your email has been verified" 
		: data.justRegistered
			? "Check your inbox"
			: data.error 
				? "Verification failed" 
				: "Verify your email address"
	}
>
	{#if data.autoVerified}
		<!-- Success: Email Verified -->
		<div class="space-y-4 text-center">
			<div class="mx-auto w-12 h-12 bg-green-100 rounded-full flex items-center justify-center">
				<svg class="w-6 h-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
					<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
				</svg>
			</div>
			<h3 class="text-lg font-medium">Email Verified!</h3>
			<p class="text-sm text-muted-foreground">
				{data.message || "Your email has been verified successfully."}
			</p>
			<Button onclick={() => goto('/login')} fullWidth>
				Sign In
			</Button>
		</div>
	{:else if data.justRegistered}
		<!-- Just Registered: Check Email -->
		<div class="space-y-4 text-center">
			<div class="mx-auto w-12 h-12 bg-primary/10 rounded-full flex items-center justify-center">
				<svg class="w-6 h-6 text-primary" fill="none" stroke="currentColor" viewBox="0 0 24 24">
					<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 19v-8.93a2 2 0 01.89-1.664l7-4.666a2 2 0 012.22 0l7 4.666A2 2 0 0121 10.07V19M3 19a2 2 0 002 2h14a2 2 0 002-2M3 19l6.75-4.5M21 19l-6.75-4.5M3 10l6.75 4.5M21 10l-6.75 4.5m0 0l-1.14.76a2 2 0 01-2.22 0l-1.14-.76" />
				</svg>
			</div>
			<h3 class="text-lg font-medium">Registration Successful!</h3>
			<p class="text-sm text-muted-foreground">
				We've sent a verification link to <strong>{data.registeredEmail}</strong>. 
				Please check your inbox and click the link to verify your email address.
			</p>
			<p class="text-xs text-muted-foreground">
				The link will expire in 24 hours.
			</p>
			
			<div class="pt-4 border-t">
				<p class="text-sm text-muted-foreground mb-4">
					Didn't receive the email? Check your spam folder or request a new one.
				</p>
				
				{#if form?.success}
					<div class="p-3 bg-green-50 border border-green-200 rounded-md text-sm text-green-700">
						{form.message}
					</div>
				{:else}
					<form
						method="POST"
						action="?/resend"
						use:enhance={() => {
							loading = true;
							return async ({ update }) => {
								loading = false;
								await update();
							};
						}}
						class="space-y-3"
					>
						{#if form?.error}
							<div class="p-3 bg-destructive/10 border border-destructive/20 rounded-md text-sm text-destructive">
								{form.error}
							</div>
						{/if}
						
						<input type="hidden" name="email" value={data.registeredEmail} />
						
						<Button type="submit" variant="secondary" fullWidth disabled={loading}>
							{loading ? 'Sending...' : 'Resend Verification Email'}
						</Button>
					</form>
				{/if}
			</div>
			
			<Button onclick={() => goto('/login')} variant="ghost" fullWidth>
				Back to Login
			</Button>
		</div>
	{:else if data.error}
		<!-- Error: Token Invalid/Expired -->
		<div class="space-y-4 text-center">
			<div class="mx-auto w-12 h-12 bg-destructive/10 rounded-full flex items-center justify-center">
				<svg class="w-6 h-6 text-destructive" fill="none" stroke="currentColor" viewBox="0 0 24 24">
					<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
				</svg>
			</div>
			<h3 class="text-lg font-medium">Verification Failed</h3>
			<p class="text-sm text-muted-foreground">
				{data.error}
			</p>
			
			<!-- Resend Form -->
			<div class="pt-4 border-t">
				<p class="text-sm text-muted-foreground mb-4">
					Need a new verification link? Enter your email below.
				</p>
				
				{#if form?.success}
					<div class="p-3 bg-green-50 border border-green-200 rounded-md text-sm text-green-700">
						{form.message}
					</div>
				{:else}
					<form
						method="POST"
						action="?/resend"
						use:enhance={() => {
							loading = true;
							return async ({ update }) => {
								loading = false;
								await update();
							};
						}}
						class="space-y-3"
					>
						{#if form?.error}
							<div class="p-3 bg-destructive/10 border border-destructive/20 rounded-md text-sm text-destructive">
								{form.error}
							</div>
						{/if}
						
						<TextField
							id="email"
							label=""
							type="email"
							name="email"
							placeholder="Enter your email"
							bind:value={email}
							required
						/>
						
						<Button type="submit" fullWidth disabled={loading}>
							{loading ? 'Sending...' : 'Resend Verification Email'}
						</Button>
					</form>
				{/if}
			</div>
		</div>
	{:else if form?.success}
		<!-- Resend Success (shown when user navigates here without token and uses resend form) -->
		<div class="space-y-4 text-center">
			<div class="mx-auto w-12 h-12 bg-green-100 rounded-full flex items-center justify-center">
				<svg class="w-6 h-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
					<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 19v-8.93a2 2 0 01.89-1.664l7-4.666a2 2 0 012.22 0l7 4.666A2 2 0 0121 10.07V19M3 19a2 2 0 002 2h14a2 2 0 002-2M3 19l6.75-4.5M21 19l-6.75-4.5M3 10l6.75 4.5M21 10l-6.75 4.5m0 0l-1.14.76a2 2 0 01-2.22 0l-1.14-.76" />
				</svg>
			</div>
			<h3 class="text-lg font-medium">Check Your Email</h3>
			<p class="text-sm text-muted-foreground">
				{form.message}
			</p>
			<Button onclick={() => goto('/login')} variant="secondary" fullWidth>
				Back to Login
			</Button>
		</div>
	{:else}
		<!-- Default: No token, show resend form -->
		<div class="space-y-4 text-center">
			<div class="mx-auto w-12 h-12 bg-primary/10 rounded-full flex items-center justify-center">
				<svg class="w-6 h-6 text-primary" fill="none" stroke="currentColor" viewBox="0 0 24 24">
					<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 19v-8.93a2 2 0 01.89-1.664l7-4.666a2 2 0 012.22 0l7 4.666A2 2 0 0121 10.07V19M3 19a2 2 0 002 2h14a2 2 0 002-2M3 19l6.75-4.5M21 19l-6.75-4.5M3 10l6.75 4.5M21 10l-6.75 4.5m0 0l-1.14.76a2 2 0 01-2.22 0l-1.14-.76" />
				</svg>
			</div>
			<h3 class="text-lg font-medium">Verify Your Email</h3>
			<p class="text-sm text-muted-foreground">
				We sent a verification link to your email when you registered. 
				Click the link to verify your account.
			</p>
			
			<div class="pt-4 border-t">
				<p class="text-sm text-muted-foreground mb-4">
					Didn't receive the email? Enter your email to resend.
				</p>
				
				<form
					method="POST"
					action="?/resend"
					use:enhance={() => {
						loading = true;
						return async ({ update }) => {
							loading = false;
							await update();
						};
					}}
					class="space-y-3"
				>
					{#if form?.error}
						<div class="p-3 bg-destructive/10 border border-destructive/20 rounded-md text-sm text-destructive">
							{form.error}
						</div>
					{/if}
					
					<TextField
						id="email"
						label=""
						type="email"
						name="email"
						placeholder="Enter your email"
						bind:value={email}
						required
					/>
					
					<Button type="submit" fullWidth disabled={loading}>
						{loading ? 'Sending...' : 'Resend Verification Email'}
					</Button>
				</form>
			</div>
			
			<Button onclick={() => goto('/login')} variant="ghost" fullWidth>
				Back to Login
			</Button>
		</div>
	{/if}
</AuthLayout>
