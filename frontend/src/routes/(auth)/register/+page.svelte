<script lang="ts">
	import { goto } from '$app/navigation';
	import { AuthLayout } from '$lib/components/auth';

	function selectCustomer() {
		goto('/register/customer');
	}

	function selectRestaurant() {
		goto('/register/restaurant');
	}
</script>

<AuthLayout title="Join RecipeManager" subtitle="Choose how you want to get started">
	<div class="space-y-4">
		<!-- Customer Registration Option -->
		<button
			on:click={selectCustomer}
			class="w-full p-6 border-2 border-border rounded-lg hover:border-primary hover:bg-accent transition-all text-left group"
		>
			<div class="flex items-start gap-4">
				<div class="text-4xl">🍕</div>
				<div class="flex-1">
					<h3 class="text-lg font-semibold mb-2 group-hover:text-primary transition-colors">
						Order Food as a Customer
					</h3>
					<p class="text-sm text-muted-foreground">
						Browse restaurants, order your favorite meals, and track deliveries
					</p>
				</div>
				<div class="text-muted-foreground group-hover:text-primary transition-colors">
					<svg
						xmlns="http://www.w3.org/2000/svg"
						width="24"
						height="24"
						viewBox="0 0 24 24"
						fill="none"
						stroke="currentColor"
						stroke-width="2"
						stroke-linecap="round"
						stroke-linejoin="round"
					>
						<path d="m9 18 6-6-6-6" />
					</svg>
				</div>
			</div>
		</button>

		<!-- Restaurant Owner Registration Option -->
		<button
			on:click={selectRestaurant}
			class="w-full p-6 border-2 border-border rounded-lg hover:border-primary hover:bg-accent transition-all text-left group"
		>
			<div class="flex items-start gap-4">
				<div class="text-4xl">🏪</div>
				<div class="flex-1">
					<h3 class="text-lg font-semibold mb-2 group-hover:text-primary transition-colors">
						List My Restaurant
					</h3>
					<p class="text-sm text-muted-foreground">
						Manage your restaurant, update menus, and receive orders from customers
					</p>
				</div>
				<div class="text-muted-foreground group-hover:text-primary transition-colors">
					<svg
						xmlns="http://www.w3.org/2000/svg"
						width="24"
						height="24"
						viewBox="0 0 24 24"
						fill="none"
						stroke="currentColor"
						stroke-width="2"
						stroke-linecap="round"
						stroke-linejoin="round"
					>
						<path d="m9 18 6-6-6-6" />
					</svg>
				</div>
			</div>
		</button>
	</div>

	<div slot="footer" class="text-center text-sm">
		<p class="text-muted-foreground">
			Already have an account?
			<a href="/login" class="text-primary hover:underline">Sign in</a>
		</p>
	</div>
</AuthLayout>