<script lang="ts">
	export let title: string;
	export let subtitle: string = '';
</script>

<div class="container mx-auto flex min-h-screen w-screen flex-col items-center justify-center">
	<div class="mx-auto flex w-full flex-col justify-center space-y-6 sm:w-[350px]">
		<div class="flex flex-col space-y-2 text-center">
			<h1 class="text-2xl font-semibold tracking-tight">{title}</h1>
			{#if subtitle}
				<p class="text-sm text-muted-foreground">{subtitle}</p>
			{/if}
		</div>
		<div class="grid gap-6">
			<slot />
		</div>
		<slot name="footer" />
	</div>
</div>