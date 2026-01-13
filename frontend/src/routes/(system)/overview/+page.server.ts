import { serverApi } from '$lib/server/api';
import type { PageServerLoad } from './$types';
import type { Restaurant } from '$lib/types';

/**
 * Server-side load function for the system overview page.
 * Fetches system-wide statistics for superadmins.
 */
export const load: PageServerLoad = async ({ cookies }) => {
    try {
        // Fetch restaurants and pending restaurants for stats
        const [restaurants, pendingRestaurants] = await Promise.all([
            serverApi.get<Restaurant[]>('/restaurants/', cookies),
            serverApi.get<Restaurant[]>('/restaurants/admin/pending', cookies)
        ]);

        return {
            stats: {
                totalRestaurants: restaurants.length,
                pendingApprovals: pendingRestaurants.length,
                approvedRestaurants: restaurants.filter(r => r.approval_status === 'approved').length,
                suspendedRestaurants: restaurants.filter(r => r.approval_status === 'suspended').length
            }
        };
    } catch (error) {
        console.error('Error loading overview:', error);
        return {
            stats: {
                totalRestaurants: 0,
                pendingApprovals: 0,
                approvedRestaurants: 0,
                suspendedRestaurants: 0
            },
            error: 'Failed to load overview data'
        };
    }
};
