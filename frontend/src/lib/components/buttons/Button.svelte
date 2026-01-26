<script lang="ts">
	import type { Snippet } from 'svelte';
	import type { HTMLButtonAttributes } from 'svelte/elements';

	interface Props extends HTMLButtonAttributes {
		variant?: 'primary' | 'secondary' | 'danger' | 'ghost';
		size?: 'sm' | 'md' | 'lg';
		loading?: boolean;
		fullWidth?: boolean;
		children?: Snippet;
	}

	let {
		type = 'button',
		variant = 'primary',
		size = 'md',
		disabled = false,
		loading = false,
		fullWidth = false,
		children,
		...restProps
	}: Props = $props();

	const baseStyles = 'inline-flex items-center justify-center rounded-md font-medium transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50';
	
	const variants = {
		primary: 'bg-primary text-primary-foreground hover:bg-primary/90',
		secondary: 'bg-secondary text-secondary-foreground hover:bg-secondary/80',
		danger: 'bg-destructive text-destructive-foreground hover:bg-destructive/90',
		ghost: 'hover:bg-accent hover:text-accent-foreground'
	};
	
	const sizes = {
		sm: 'h-9 px-3 text-sm',
		md: 'h-10 px-4 py-2',
		lg: 'h-11 px-8'
	};

	let className = $derived([
		baseStyles,
		variants[variant],
		sizes[size],
		fullWidth ? 'w-full' : '',
	].join(' '));
</script>

<button
	{type}
	class={className}
	disabled={disabled || loading}
	{...restProps}
>
	{#if loading}
		<span class="mr-2">
			<svg class="animate-spin h-4 w-4" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
				<circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
				<path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
			</svg>
		</span>
	{/if}
	{@render children?.()}
</button>