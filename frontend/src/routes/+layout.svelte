<script lang="ts">
	import '../app.css';
	import favicon from '$lib/assets/favicon.svg';
	import { Layout } from '$lib/components';
	import { authStore } from '$lib/stores/authStore';
	import { browser } from '$app/environment';
	import type { LayoutData } from './$types';

	let { children, data }: { children: any; data: LayoutData } = $props();

	// Hydrate auth store with server-fetched user data
	$effect(() => {
		if (browser && data.user) {
			authStore.setUser(data.user);
		} else if (browser && !data.user) {
			authStore.setUser(null);
		}
	});
</script>

<svelte:head>
	<title>Recipe Manager - Professional Kitchen Management</title>
	<link rel="icon" href={favicon} />
	<meta name="description" content="Professional recipe and kitchen management system for restaurants" />
</svelte:head>

<Layout>
	{@render children?.()}
</Layout>
