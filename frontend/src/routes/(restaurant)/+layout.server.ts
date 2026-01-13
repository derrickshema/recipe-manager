import { redirect } from '@sveltejs/kit';
import type { LayoutServerLoad } from './$types';

/**
 * Server-side layout load for restaurant routes.
 * Validates authentication and role using the parent's user data.
 */
export const load: LayoutServerLoad = async ({ parent }) => {
    const { user } = await parent();
    
    // Redirect to login if not authenticated
    if (!user) {
        throw redirect(303, '/login');
    }
    
    // Check if user is a restaurant owner
    if (user.role !== 'restaurant_owner') {
        throw redirect(303, '/');
    }
    
    return {
        user
    };
};
