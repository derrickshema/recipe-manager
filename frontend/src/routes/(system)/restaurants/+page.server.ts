import { fail } from '@sveltejs/kit';
import { serverApi } from '$lib/server/api';
import type { PageServerLoad, Actions } from './$types';
import type { Restaurant } from '$lib/types';

/**
 * Server-side load function for the restaurant management page.
 * Fetches all restaurants and pending restaurants for superadmin users.
 */
export const load: PageServerLoad = async ({ cookies }) => {
    try {
        // Fetch both lists in parallel
        const [restaurants, pendingRestaurants] = await Promise.all([
            serverApi.get<Restaurant[]>('/restaurants/', cookies),
            serverApi.get<Restaurant[]>('/restaurants/admin/pending', cookies)
        ]);

        return {
            restaurants,
            pendingRestaurants
        };
    } catch (error) {
        console.error('Error loading restaurants:', error);
        return {
            restaurants: [],
            pendingRestaurants: [],
            error: 'Failed to load restaurants'
        };
    }
};

/**
 * Form actions for restaurant management operations.
 * All mutations use SSR form actions for better security.
 */
export const actions: Actions = {
    /**
     * Approve a pending restaurant
     */
    approve: async ({ request, cookies }) => {
        const formData = await request.formData();
        const restaurantId = formData.get('restaurantId');

        if (!restaurantId) {
            return fail(400, { 
                action: 'approve',
                error: 'Restaurant ID is required' 
            });
        }

        try {
            await serverApi.post<Restaurant>(
                `/restaurants/${restaurantId}/approve`,
                {},
                cookies
            );

            return { 
                action: 'approve',
                success: true, 
                message: 'Restaurant approved successfully' 
            };
        } catch (error: any) {
            return fail(error.status || 500, { 
                action: 'approve',
                error: error.body?.message || 'Failed to approve restaurant' 
            });
        }
    },

    /**
     * Reject a pending restaurant
     */
    reject: async ({ request, cookies }) => {
        const formData = await request.formData();
        const restaurantId = formData.get('restaurantId');

        if (!restaurantId) {
            return fail(400, { 
                action: 'reject',
                error: 'Restaurant ID is required' 
            });
        }

        try {
            await serverApi.post<Restaurant>(
                `/restaurants/${restaurantId}/reject`,
                {},
                cookies
            );

            return { 
                action: 'reject',
                success: true, 
                message: 'Restaurant rejected successfully' 
            };
        } catch (error: any) {
            return fail(error.status || 500, { 
                action: 'reject',
                error: error.body?.message || 'Failed to reject restaurant' 
            });
        }
    },

    /**
     * Suspend an approved restaurant
     */
    suspend: async ({ request, cookies }) => {
        const formData = await request.formData();
        const restaurantId = formData.get('restaurantId');

        if (!restaurantId) {
            return fail(400, { 
                action: 'suspend',
                error: 'Restaurant ID is required' 
            });
        }

        try {
            await serverApi.post<Restaurant>(
                `/restaurants/${restaurantId}/suspend`,
                {},
                cookies
            );

            return { 
                action: 'suspend',
                success: true, 
                message: 'Restaurant suspended successfully' 
            };
        } catch (error: any) {
            return fail(error.status || 500, { 
                action: 'suspend',
                error: error.body?.message || 'Failed to suspend restaurant' 
            });
        }
    },

    /**
     * Reactivate a suspended restaurant (uses approve endpoint)
     */
    reactivate: async ({ request, cookies }) => {
        const formData = await request.formData();
        const restaurantId = formData.get('restaurantId');

        if (!restaurantId) {
            return fail(400, { 
                action: 'reactivate',
                error: 'Restaurant ID is required' 
            });
        }

        try {
            await serverApi.post<Restaurant>(
                `/restaurants/${restaurantId}/approve`,
                {},
                cookies
            );

            return { 
                action: 'reactivate',
                success: true, 
                message: 'Restaurant reactivated successfully' 
            };
        } catch (error: any) {
            return fail(error.status || 500, { 
                action: 'reactivate',
                error: error.body?.message || 'Failed to reactivate restaurant' 
            });
        }
    }
};
