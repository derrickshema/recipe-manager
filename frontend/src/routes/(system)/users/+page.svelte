<script lang="ts">
	import { enhance } from '$app/forms';
	import { Button } from '$lib/components';
	import { SystemRole } from '$lib/types';

	interface AdminUser {
		id: number;
		email: string;
		username: string;
		first_name: string;
		last_name: string;
		role: SystemRole;
		email_verified: boolean;
	}

	interface PageData {
		users: AdminUser[];
		error?: string;
	}

	interface FormResult {
		action?: string;
		success?: boolean;
		message?: string;
		error?: string;
	}

	// SSR data from +page.server.ts
	let { data, form }: { data: PageData; form: FormResult | null } = $props();

	// Reactive state for UI
	let activeTab = $state<'all' | 'customers' | 'owners' | 'suspended'>('all');
	let submitting = $state<number | null>(null);
	let deleteModalUser = $state<AdminUser | null>(null);
	let deleteRestaurants = $state(true);

	// Derived data
	let users = $derived(data.users ?? []);
	let filteredUsers = $derived(() => {
		switch (activeTab) {
			case 'customers':
				return users.filter(u => u.role === SystemRole.CUSTOMER);
			case 'owners':
				return users.filter(u => u.role === SystemRole.RESTAURANT_OWNER);
			case 'suspended':
				return users.filter(u => u.role === SystemRole.SUSPENDED);
			default:
				return users;
		}
	});

	// Stats
	let totalCustomers = $derived(users.filter(u => u.role === SystemRole.CUSTOMER).length);
	let totalOwners = $derived(users.filter(u => u.role === SystemRole.RESTAURANT_OWNER).length);
	let totalSuspended = $derived(users.filter(u => u.role === SystemRole.SUSPENDED).length);

	function getRoleBadge(role: SystemRole): string {
		switch (role) {
			case SystemRole.SUPERADMIN:
				return 'bg-purple-100 text-purple-800';
			case SystemRole.RESTAURANT_OWNER:
				return 'bg-blue-100 text-blue-800';
			case SystemRole.CUSTOMER:
				return 'bg-green-100 text-green-800';
			case SystemRole.SUSPENDED:
				return 'bg-red-100 text-red-800';
			default:
				return 'bg-gray-100 text-gray-800';
		}
	}

	function getRoleLabel(role: SystemRole): string {
		switch (role) {
			case SystemRole.SUPERADMIN:
				return 'Superadmin';
			case SystemRole.RESTAURANT_OWNER:
				return 'Restaurant Owner';
			case SystemRole.CUSTOMER:
				return 'Customer';
			case SystemRole.SUSPENDED:
				return 'Suspended';
			default:
				return role;
		}
	}

	function openDeleteModal(user: AdminUser) {
		deleteModalUser = user;
		deleteRestaurants = true;
	}

	function closeDeleteModal() {
		deleteModalUser = null;
	}
</script>

<div class="space-y-6">
	<!-- Back Button -->
	<div>
		<a href="/overview" class="inline-flex items-center text-sm text-muted-foreground hover:text-foreground transition-colors">
			<svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
				<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
			</svg>
			Back to Overview
		</a>
	</div>
	
	<div class="flex justify-between items-center">
		<div>
			<h1 class="text-3xl font-bold">User Management</h1>
			<p class="text-muted-foreground mt-2">Manage user accounts and permissions</p>
		</div>
	</div>

	<!-- Success/Error Messages -->
	{#if form?.success}
		<div class="bg-green-100 text-green-800 p-4 rounded-lg">
			{form.message}
		</div>
	{/if}
	{#if form?.error}
		<div class="bg-destructive/10 text-destructive p-4 rounded-lg">
			{form.error}
		</div>
	{/if}
	{#if data.error}
		<div class="bg-destructive/10 text-destructive p-4 rounded-lg">
			{data.error}
		</div>
	{/if}

	<!-- Stats Cards -->
	<div class="grid grid-cols-1 md:grid-cols-4 gap-4">
		<div class="bg-card p-4 rounded-lg shadow">
			<p class="text-sm text-muted-foreground">Total Users</p>
			<p class="text-2xl font-bold">{users.length}</p>
		</div>
		<div class="bg-card p-4 rounded-lg shadow">
			<p class="text-sm text-muted-foreground">Customers</p>
			<p class="text-2xl font-bold text-green-600">{totalCustomers}</p>
		</div>
		<div class="bg-card p-4 rounded-lg shadow">
			<p class="text-sm text-muted-foreground">Restaurant Owners</p>
			<p class="text-2xl font-bold text-blue-600">{totalOwners}</p>
		</div>
		<div class="bg-card p-4 rounded-lg shadow">
			<p class="text-sm text-muted-foreground">Suspended</p>
			<p class="text-2xl font-bold text-red-600">{totalSuspended}</p>
		</div>
	</div>

	<!-- Tabs -->
	<div class="border-b">
		<nav class="flex gap-4">
			<button
				type="button"
				class="pb-2 px-1 border-b-2 transition-colors {activeTab === 'all' ? 'border-primary text-foreground' : 'border-transparent text-muted-foreground hover:text-foreground'}"
				onclick={() => activeTab = 'all'}
			>
				All Users ({users.length})
			</button>
			<button
				type="button"
				class="pb-2 px-1 border-b-2 transition-colors {activeTab === 'customers' ? 'border-primary text-foreground' : 'border-transparent text-muted-foreground hover:text-foreground'}"
				onclick={() => activeTab = 'customers'}
			>
				Customers ({totalCustomers})
			</button>
			<button
				type="button"
				class="pb-2 px-1 border-b-2 transition-colors {activeTab === 'owners' ? 'border-primary text-foreground' : 'border-transparent text-muted-foreground hover:text-foreground'}"
				onclick={() => activeTab = 'owners'}
			>
				Restaurant Owners ({totalOwners})
			</button>
			<button
				type="button"
				class="pb-2 px-1 border-b-2 transition-colors {activeTab === 'suspended' ? 'border-primary text-foreground' : 'border-transparent text-muted-foreground hover:text-foreground'}"
				onclick={() => activeTab = 'suspended'}
			>
				Suspended ({totalSuspended})
			</button>
		</nav>
	</div>

	<!-- Users Table -->
	<div class="bg-card rounded-lg shadow overflow-hidden">
		<table class="w-full">
			<thead class="bg-muted/50">
				<tr>
					<th class="text-left p-4 font-medium">User</th>
					<th class="text-left p-4 font-medium">Email</th>
					<th class="text-left p-4 font-medium">Role</th>
					<th class="text-left p-4 font-medium">Email Verified</th>
					<th class="text-right p-4 font-medium">Actions</th>
				</tr>
			</thead>
			<tbody class="divide-y">
				{#each filteredUsers() as user (user.id)}
					<tr class="hover:bg-muted/30 transition-colors">
						<td class="p-4">
							<div>
								<p class="font-medium">{user.first_name} {user.last_name}</p>
								<p class="text-sm text-muted-foreground">@{user.username}</p>
							</div>
						</td>
						<td class="p-4 text-sm">{user.email}</td>
						<td class="p-4">
							<span class="px-2 py-1 rounded-full text-xs font-medium {getRoleBadge(user.role)}">
								{getRoleLabel(user.role)}
							</span>
						</td>
						<td class="p-4">
							{#if user.email_verified}
								<span class="text-green-600">✓ Verified</span>
							{:else}
								<span class="text-yellow-600">✗ Unverified</span>
							{/if}
						</td>
						<td class="p-4">
							<div class="flex justify-end gap-2">
								{#if user.role !== SystemRole.SUPERADMIN}
									{#if user.role === SystemRole.SUSPENDED}
										<!-- Unsuspend Form -->
										<form
											method="POST"
											action="?/unsuspend"
											use:enhance={() => {
												submitting = user.id;
												return async ({ update }) => {
													submitting = null;
													await update();
												};
											}}
										>
											<input type="hidden" name="userId" value={user.id} />
											<input type="hidden" name="restoreRole" value={SystemRole.CUSTOMER} />
											<Button
												type="submit"
												variant="secondary"
												size="sm"
												disabled={submitting === user.id}
											>
												{submitting === user.id ? 'Processing...' : 'Unsuspend'}
											</Button>
										</form>
									{:else}
										<!-- Suspend Form -->
										<form
											method="POST"
											action="?/suspend"
											use:enhance={() => {
												submitting = user.id;
												return async ({ update }) => {
													submitting = null;
													await update();
												};
											}}
										>
											<input type="hidden" name="userId" value={user.id} />
											<Button
												type="submit"
												variant="secondary"
												size="sm"
												disabled={submitting === user.id}
											>
												{submitting === user.id ? 'Processing...' : 'Suspend'}
											</Button>
										</form>
									{/if}
									
									<!-- Delete Button -->
									<Button
										variant="danger"
										size="sm"
										onclick={() => openDeleteModal(user)}
									>
										Delete
									</Button>
								{:else}
									<span class="text-sm text-muted-foreground">Protected</span>
								{/if}
							</div>
						</td>
					</tr>
				{:else}
					<tr>
						<td colspan="5" class="p-8 text-center text-muted-foreground">
							No users found
						</td>
					</tr>
				{/each}
			</tbody>
		</table>
	</div>
</div>

<!-- Delete Confirmation Modal -->
{#if deleteModalUser}
	<!-- svelte-ignore a11y_no_static_element_interactions -->
	<!-- svelte-ignore a11y_click_events_have_key_events -->
	<div 
		class="fixed inset-0 bg-black/50 flex items-center justify-center z-50" 
		onclick={closeDeleteModal}
		role="dialog"
		aria-modal="true"
		aria-labelledby="delete-modal-title"
		tabindex="-1"
	>
		<!-- svelte-ignore a11y_no_static_element_interactions -->
		<!-- svelte-ignore a11y_click_events_have_key_events -->
		<div class="bg-card rounded-lg p-6 max-w-md w-full mx-4 shadow-xl" onclick={(e) => e.stopPropagation()}>
			<h2 id="delete-modal-title" class="text-xl font-bold mb-4">Delete User</h2>
			
			<p class="text-muted-foreground mb-4">
				Are you sure you want to delete <strong>{deleteModalUser.first_name} {deleteModalUser.last_name}</strong> (@{deleteModalUser.username})?
			</p>
			
			<p class="text-sm text-destructive mb-4">
				This action cannot be undone.
			</p>
			
			{#if deleteModalUser.role === SystemRole.RESTAURANT_OWNER}
				<div class="mb-4">
					<label class="flex items-center gap-2">
						<input
							type="checkbox"
							bind:checked={deleteRestaurants}
							class="w-4 h-4 rounded border-gray-300"
						/>
						<span class="text-sm">Also delete restaurants owned by this user</span>
					</label>
				</div>
			{/if}
			
			<div class="flex justify-end gap-3">
				<Button variant="ghost" onclick={closeDeleteModal}>
					Cancel
				</Button>
				
				<form
					method="POST"
					action="?/delete"
					use:enhance={() => {
						submitting = deleteModalUser?.id ?? null;
						return async ({ update }) => {
							submitting = null;
							closeDeleteModal();
							await update();
						};
					}}
				>
					<input type="hidden" name="userId" value={deleteModalUser.id} />
					<input type="hidden" name="deleteRestaurants" value={deleteRestaurants.toString()} />
					<Button
						type="submit"
						variant="danger"
						disabled={submitting === deleteModalUser.id}
					>
						{submitting === deleteModalUser.id ? 'Deleting...' : 'Delete User'}
					</Button>
				</form>
			</div>
		</div>
	</div>
{/if}
