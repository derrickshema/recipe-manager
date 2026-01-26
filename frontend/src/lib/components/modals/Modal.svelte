<script lang="ts">
	import { onMount } from 'svelte';
	import { fade, scale } from 'svelte/transition';
	import Button from '../buttons/Button.svelte';

	export let open = false;
	export let title: string;
	export let size: 'sm' | 'md' | 'lg' | 'xl' = 'md';
	export let onClose: () => void;

	const sizes = {
		sm: 'max-w-sm',
		md: 'max-w-lg',
		lg: 'max-w-2xl',
		xl: 'max-w-4xl'
	};

	function closeModal() {
		onClose();
	}

	function handleEscape(e: KeyboardEvent) {
		if (e.key === 'Escape') {
			closeModal();
		}
	}

	onMount(() => {
		document.addEventListener('keydown', handleEscape);
		return () => {
			document.removeEventListener('keydown', handleEscape);
		};
	});
</script>

{#if open}
	<div
		class="fixed inset-0 z-50 bg-background/80 backdrop-blur-sm"
		transition:fade={{ duration: 200 }}
		on:click={closeModal}
		on:keydown={handleEscape}
		role="presentation"
	>
		<div
			class="fixed left-[50%] top-[50%] z-50 grid w-full translate-x-[-50%] translate-y-[-50%] gap-4 border bg-background p-6 shadow-lg duration-200 sm:rounded-lg {sizes[size]} max-h-[85vh] overflow-y-auto"
			transition:scale={{ duration: 200 }}
			on:click|stopPropagation
			on:keydown|stopPropagation
			role="dialog"
			tabindex="0"
			aria-modal="true"
			aria-labelledby="modal-title"
		>
			<!-- Header -->
			<div class="flex flex-col space-y-1.5 text-center sm:text-left">
				<h2 id="modal-title" class="text-lg font-semibold leading-none tracking-tight">{title}</h2>
				{#if $$slots.description}
					<div class="text-sm text-muted-foreground">
						<slot name="description" />
					</div>
				{/if}
			</div>

			<!-- Content -->
			<slot />

			<!-- Footer -->
			{#if $$slots.footer}
				<div class="flex flex-col-reverse sm:flex-row sm:justify-end sm:space-x-2">
					<slot name="footer">
						<Button variant="ghost" onclick={closeModal}>Cancel</Button>
					</slot>
				</div>
			{/if}
		</div>
	</div>
{/if}