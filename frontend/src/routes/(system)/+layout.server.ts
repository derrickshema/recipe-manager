import { redirect } from '@sveltejs/kit';
import type { LayoutServerLoad } from './$types';

/**
 * Server-side layout load for system admin routes.
 * Validates authentication and superadmin role using the parent's user data.
 */
export const load: LayoutServerLoad = async ({ parent }) => {
    const { user } = await parent();
    
    // Redirect to login if not authenticated
    if (!user) {
        throw redirect(303, '/login');
    }
    
    // Check if user is a superadmin
    if (user.role !== 'superadmin') {
        throw redirect(303, '/');
    }
    
    return {
        user
    };
};
