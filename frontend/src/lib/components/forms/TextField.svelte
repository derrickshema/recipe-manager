<script lang="ts">
	export let id: string;
	export let label: string;
	export let type = 'text';
	export let value: string = '';
	export let error: string | undefined = undefined;
	export let disabled = false;
	export let required = false;
	export let placeholder = '';

	const baseInputStyles = 'flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background file:border-0 file:bg-transparent file:text-sm file:font-medium placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50';
</script>

<div class="space-y-2">
	<label
		for={id}
		class="text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70"
	>
		{label}
		{#if required}
			<span class="text-destructive">*</span>
		{/if}
	</label>

	<input
		{id}
		{type}
		bind:value
		{disabled}
		{required}
		{placeholder}
		class={`${baseInputStyles} ${error ? 'border-destructive focus-visible:ring-destructive' : ''}`}
		aria-invalid={!!error}
		aria-describedby={error ? `${id}-error` : undefined}
		{...$$restProps}
		on:blur
		on:focus
		on:input
		on:change
	/>

	{#if error}
		<p id="{id}-error" class="text-sm text-destructive">{error}</p>
	{/if}
</div>