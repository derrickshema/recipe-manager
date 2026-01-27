import { fail } from '@sveltejs/kit';
import { serverApi } from '$lib/server/api';
import type { PageServerLoad, Actions } from './$types';
import type { UserProfile } from '$lib/types';

/**
 * Extended user type with email_verified field
 */
interface AdminUser extends UserProfile {
    email_verified: boolean;
}

/**
 * Server-side load function for the user management page.
 * Fetches all users for superadmin.
 */
export const load: PageServerLoad = async ({ cookies }) => {
    try {
        const users = await serverApi.get<AdminUser[]>('/admin/users', cookies);

        return {
            users
        };
    } catch (error) {
        console.error('Error loading users:', error);
        return {
            users: [],
            error: 'Failed to load users'
        };
    }
};

/**
 * Form actions for user management operations.
 */
export const actions: Actions = {
    /**
     * Delete a user and optionally their restaurants
     */
    delete: async ({ request, cookies }) => {
        const formData = await request.formData();
        const userId = formData.get('userId');
        const deleteRestaurants = formData.get('deleteRestaurants') === 'true';

        if (!userId) {
            return fail(400, { 
                action: 'delete',
                error: 'User ID is required' 
            });
        }

        try {
            await serverApi.delete(
                `/admin/users/${userId}?delete_owned_restaurants=${deleteRestaurants}`,
                cookies
            );

            return { 
                action: 'delete',
                success: true, 
                message: 'User deleted successfully' 
            };
        } catch (error: any) {
            return fail(error.status || 500, { 
                action: 'delete',
                error: error.body?.detail || error.body?.message || 'Failed to delete user' 
            });
        }
    },

    /**
     * Suspend a user
     */
    suspend: async ({ request, cookies }) => {
        const formData = await request.formData();
        const userId = formData.get('userId');

        if (!userId) {
            return fail(400, { 
                action: 'suspend',
                error: 'User ID is required' 
            });
        }

        try {
            await serverApi.patch(
                `/admin/users/${userId}/suspend`,
                {},
                cookies
            );

            return { 
                action: 'suspend',
                success: true, 
                message: 'User suspended successfully' 
            };
        } catch (error: any) {
            return fail(error.status || 500, { 
                action: 'suspend',
                error: error.body?.detail || error.body?.message || 'Failed to suspend user' 
            });
        }
    },

    /**
     * Unsuspend a user
     */
    unsuspend: async ({ request, cookies }) => {
        const formData = await request.formData();
        const userId = formData.get('userId');
        const restoreRole = formData.get('restoreRole');

        if (!userId || !restoreRole) {
            return fail(400, { 
                action: 'unsuspend',
                error: 'User ID and restore role are required' 
            });
        }

        try {
            await serverApi.patch(
                `/admin/users/${userId}/unsuspend?restore_role=${restoreRole}`,
                {},
                cookies
            );

            return { 
                action: 'unsuspend',
                success: true, 
                message: 'User unsuspended successfully' 
            };
        } catch (error: any) {
            return fail(error.status || 500, { 
                action: 'unsuspend',
                error: error.body?.detail || error.body?.message || 'Failed to unsuspend user' 
            });
        }
    }
};
