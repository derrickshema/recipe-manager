<script lang="ts">
	import '../app.css';
	import favicon from '$lib/assets/favicon.svg';
	import { Layout } from '$lib/components';

	let { children } = $props();
</script>

<svelte:head>
	<title>Recipe Manager - Professional Kitchen Management</title>
	<link rel="icon" href={favicon} />
	<meta name="description" content="Professional recipe and kitchen management system for restaurants" />
</svelte:head>

<Layout>
	{@render children?.()}
</Layout>
