<script lang="ts">
    import { enhance } from '$app/forms';
    import { Button } from '$lib/components';
    import Modal from '$lib/components/modals/Modal.svelte';
    import { OrgRole } from '$lib/types';

    // SSR data from +page.server.ts
    let { data, form } = $props();

    // Reactive state
    let showInviteModal = $state(false);
    let submitting = $state(false);
    let inviteEmail = $state('');
    let inviteRole = $state<string>(OrgRole.EMPLOYEE);

    // Derived from SSR data
    let restaurant = $derived(data.restaurant);
    let members = $derived(data.members ?? []);

    function getRoleBadgeClass(role: string): string {
        switch (role) {
            case OrgRole.RESTAURANT_ADMIN:
                return 'bg-purple-100 text-purple-800';
            case OrgRole.EMPLOYEE:
                return 'bg-blue-100 text-blue-800';
            default:
                return 'bg-gray-100 text-gray-800';
        }
    }

    function formatRole(role: string): string {
        switch (role) {
            case OrgRole.RESTAURANT_ADMIN:
                return 'Admin';
            case OrgRole.EMPLOYEE:
                return 'Employee';
            default:
                return role;
        }
    }

    function closeInviteModal() {
        showInviteModal = false;
        inviteEmail = '';
        inviteRole = OrgRole.EMPLOYEE;
    }

    function openInviteModal() {
        console.log('openInviteModal called, showInviteModal:', showInviteModal);
        showInviteModal = true;
        console.log('showInviteModal after:', showInviteModal);
    }

    // Close modal on successful action
    $effect(() => {
        if (form?.success && (form?.action === 'invite' || form?.action === 'add')) {
            closeInviteModal();
        }
    });
</script>

<div class="space-y-6">
    <!-- Header -->
    <div class="flex justify-between items-center">
        <div>
            <a href="/dashboard" class="text-sm text-muted-foreground hover:text-foreground mb-2 inline-block">
                ← Back to Dashboard
            </a>
            <h1 class="text-3xl font-bold">Staff Management</h1>
            {#if restaurant}
                <p class="text-muted-foreground mt-1">{restaurant.restaurant_name}</p>
            {/if}
        </div>
        <Button onclick={openInviteModal}>+ Invite Staff Member</Button>
    </div>

    <!-- Messages -->
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

    <!-- Staff List -->
    {#if members.length === 0}
        <div class="text-center py-12 bg-muted/30 rounded-lg">
            <p class="text-muted-foreground mb-4">No staff members yet</p>
            <Button onclick={openInviteModal}>Invite your first staff member</Button>
        </div>
    {:else}
        <div class="bg-card border rounded-lg overflow-hidden">
            <table class="w-full">
                <thead class="bg-muted/50">
                    <tr>
                        <th class="text-left py-3 px-4 font-medium">Name</th>
                        <th class="text-left py-3 px-4 font-medium">Email</th>
                        <th class="text-left py-3 px-4 font-medium">Role</th>
                        <th class="text-right py-3 px-4 font-medium">Actions</th>
                    </tr>
                </thead>
                <tbody>
                    {#each members as member (member.id)}
                        <tr class="border-t hover:bg-muted/30">
                            <td class="py-3 px-4 font-medium">
                                {member.user_name || 'Unknown'}
                            </td>
                            <td class="py-3 px-4 text-muted-foreground">
                                {member.user_email || '-'}
                            </td>
                            <td class="py-3 px-4">
                                <span class="px-2 py-1 rounded-full text-xs font-medium {getRoleBadgeClass(member.role)}">
                                    {formatRole(member.role)}
                                </span>
                            </td>
                            <td class="py-3 px-4">
                                <div class="flex gap-2 justify-end">
                                    <!-- Role Update Form -->
                                    <form 
                                        method="POST" 
                                        action="?/updateRole"
                                        class="flex gap-2"
                                        use:enhance={() => {
                                            submitting = true;
                                            return async ({ update }) => {
                                                await update();
                                                submitting = false;
                                            };
                                        }}
                                    >
                                        <input type="hidden" name="restaurantId" value={restaurant?.id} />
                                        <input type="hidden" name="membershipId" value={member.id} />
                                        <select 
                                            name="role" 
                                            class="px-2 py-1 border rounded text-sm"
                                            value={member.role}
                                        >
                                            <option value={OrgRole.EMPLOYEE}>Employee</option>
                                            <option value={OrgRole.RESTAURANT_ADMIN}>Admin</option>
                                        </select>
                                        <Button type="submit" variant="secondary" size="sm" disabled={submitting}>
                                            Update
                                        </Button>
                                    </form>

                                    <!-- Remove Form -->
                                    <form 
                                        method="POST" 
                                        action="?/remove"
                                        use:enhance={() => {
                                            if (!confirm('Are you sure you want to remove this staff member?')) {
                                                return () => {};
                                            }
                                            submitting = true;
                                            return async ({ update }) => {
                                                await update();
                                                submitting = false;
                                            };
                                        }}
                                    >
                                        <input type="hidden" name="restaurantId" value={restaurant?.id} />
                                        <input type="hidden" name="membershipId" value={member.id} />
                                        <Button 
                                            type="submit"
                                            variant="danger" 
                                            size="sm"
                                            disabled={submitting}
                                        >
                                            Remove
                                        </Button>
                                    </form>
                                </div>
                            </td>
                        </tr>
                    {/each}
                </tbody>
            </table>
        </div>
    {/if}
</div>

<!-- Invite Staff Modal -->
{#if showInviteModal}
    <Modal open={true} title="Invite Staff Member" onClose={closeInviteModal}>
        <form 
            method="POST" 
            action="?/invite"
            class="space-y-4"
            use:enhance={() => {
                submitting = true;
                return async ({ update }) => {
                    await update();
                    submitting = false;
                };
            }}
        >
            <input type="hidden" name="restaurantId" value={restaurant?.id} />
            
            <div>
                <label for="email" class="block text-sm font-medium mb-1">Email Address *</label>
                <input 
                    type="email" 
                    id="email" 
                    name="email" 
                    bind:value={inviteEmail}
                    placeholder="staff@example.com"
                    class="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-primary"
                    required
                />
                <p class="text-xs text-muted-foreground mt-1">
                    An invitation email will be sent to this address.
                </p>
            </div>

            <div>
                <label for="role" class="block text-sm font-medium mb-1">Role *</label>
                <select 
                    id="role" 
                    name="role" 
                    bind:value={inviteRole}
                    class="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-primary"
                >
                    <option value={OrgRole.EMPLOYEE}>Employee - Can view recipes</option>
                    <option value={OrgRole.RESTAURANT_ADMIN}>Admin - Full access to manage restaurant</option>
                </select>
            </div>

            <div class="bg-blue-50 dark:bg-blue-900/20 text-blue-800 dark:text-blue-200 p-3 rounded text-sm">
                <strong>How it works:</strong>
                <ul class="list-disc ml-4 mt-1 space-y-1">
                    <li>The user will receive an email invitation</li>
                    <li>If they don't have an account, they can register first</li>
                    <li>Once they accept, they'll be added to your restaurant</li>
                </ul>
            </div>

            <div class="flex justify-end gap-2 pt-4">
                <Button type="button" variant="secondary" onclick={closeInviteModal}>Cancel</Button>
                <Button type="submit" disabled={submitting}>
                    {submitting ? 'Sending...' : 'Send Invitation'}
                </Button>
            </div>
        </form>
    </Modal>
{/if}
