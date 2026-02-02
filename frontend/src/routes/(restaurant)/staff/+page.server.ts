import { fail } from '@sveltejs/kit';
import { serverApi } from '$lib/server/api';
import type { PageServerLoad, Actions } from './$types';
import type { Restaurant, Membership } from '$lib/types';

// Extended membership type with user info
interface MembershipWithUser extends Membership {
    user_email?: string;
    user_name?: string;
}

/**
 * Server-side load function for the staff management page.
 * Fetches the user's restaurant and its staff members.
 */
export const load: PageServerLoad = async ({ cookies }) => {
    try {
        // Get the user's restaurants
        const restaurants = await serverApi.get<Restaurant[]>('/restaurants/my', cookies);
        const restaurant = restaurants.length > 0 ? restaurants[0] : null;
        
        if (!restaurant) {
            return {
                restaurant: null,
                members: [],
                error: 'No restaurant found'
            };
        }
        
        // Get memberships for the restaurant
        const members = await serverApi.get<MembershipWithUser[]>(
            `/restaurants/${restaurant.id}/memberships`,
            cookies
        );

        return {
            restaurant,
            members
        };
    } catch (error) {
        console.error('Error loading staff:', error);
        return {
            restaurant: null,
            members: [],
            error: 'Failed to load staff members'
        };
    }
};

/**
 * Form actions for staff management.
 */
export const actions: Actions = {
    /**
     * Invite a new staff member by email (sends invitation email)
     */
    invite: async ({ request, cookies }) => {
        const formData = await request.formData();
        const restaurantId = formData.get('restaurantId');
        const email = formData.get('email');
        const role = formData.get('role');

        if (!restaurantId || !email || !role) {
            return fail(400, { 
                action: 'invite',
                error: 'Restaurant ID, email, and role are required',
                values: { email, role }
            });
        }

        try {
            await serverApi.post(
                `/restaurants/${restaurantId}/invite`,
                {
                    email: String(email),
                    role: String(role)
                },
                cookies
            );

            return { 
                action: 'invite',
                success: true, 
                message: `Invitation sent to ${email}` 
            };
        } catch (error: any) {
            return fail(error.status || 500, { 
                action: 'invite',
                error: error.body?.detail || 'Failed to send invitation',
                values: { email, role }
            });
        }
    },

    /**
     * Add a new staff member by email (existing user only)
     */
    add: async ({ request, cookies }) => {
        const formData = await request.formData();
        const restaurantId = formData.get('restaurantId');
        const email = formData.get('email');
        const role = formData.get('role');

        if (!restaurantId || !email || !role) {
            return fail(400, { 
                action: 'add',
                error: 'Restaurant ID, email, and role are required',
                values: { email, role }
            });
        }

        try {
            await serverApi.post(
                `/restaurants/${restaurantId}/memberships`,
                {
                    email: String(email),
                    role: String(role)
                },
                cookies
            );

            return { 
                action: 'add',
                success: true, 
                message: 'Staff member added successfully' 
            };
        } catch (error: any) {
            return fail(error.status || 500, { 
                action: 'add',
                error: error.body?.message || 'Failed to add staff member',
                values: { email, role }
            });
        }
    },

    /**
     * Update a staff member's role
     */
    updateRole: async ({ request, cookies }) => {
        const formData = await request.formData();
        const restaurantId = formData.get('restaurantId');
        const membershipId = formData.get('membershipId');
        const role = formData.get('role');

        if (!restaurantId || !membershipId || !role) {
            return fail(400, { 
                action: 'updateRole',
                error: 'Restaurant ID, membership ID, and role are required' 
            });
        }

        try {
            await serverApi.put(
                `/restaurants/${restaurantId}/memberships/${membershipId}`,
                { role: String(role) },
                cookies
            );

            return { 
                action: 'updateRole',
                success: true, 
                message: 'Role updated successfully' 
            };
        } catch (error: any) {
            return fail(error.status || 500, { 
                action: 'updateRole',
                error: error.body?.message || 'Failed to update role' 
            });
        }
    },

    /**
     * Remove a staff member
     */
    remove: async ({ request, cookies }) => {
        const formData = await request.formData();
        const restaurantId = formData.get('restaurantId');
        const membershipId = formData.get('membershipId');

        if (!restaurantId || !membershipId) {
            return fail(400, { 
                action: 'remove',
                error: 'Restaurant ID and membership ID are required' 
            });
        }

        try {
            await serverApi.delete(
                `/restaurants/${restaurantId}/memberships/${membershipId}`,
                cookies
            );

            return { 
                action: 'remove',
                success: true, 
                message: 'Staff member removed successfully' 
            };
        } catch (error: any) {
            return fail(error.status || 500, { 
                action: 'remove',
                error: error.body?.message || 'Failed to remove staff member' 
            });
        }
    }
};
