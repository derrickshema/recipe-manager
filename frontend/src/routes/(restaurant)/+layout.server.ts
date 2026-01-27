import { redirect } from '@sveltejs/kit';
import { serverApi } from '$lib/server/api';
import type { LayoutServerLoad } from './$types';
import type { Restaurant } from '$lib/types';

/**
 * Server-side layout load for restaurant routes.
 * Validates authentication and role using the parent's user data.
 * Also fetches the user's restaurant for display in the header.
 */
export const load: LayoutServerLoad = async ({ parent, cookies }) => {
    const { user } = await parent();
    
    // Redirect to login if not authenticated
    if (!user) {
        throw redirect(303, '/login');
    }
    
    // Check if user is a restaurant owner
    if (user.role !== 'restaurant_owner') {
        throw redirect(303, '/');
    }
    
    // Fetch the user's restaurant
    let restaurant: Restaurant | null = null;
    try {
        const restaurants = await serverApi.get<Restaurant[]>('/restaurants/my', cookies);
        restaurant = restaurants.length > 0 ? restaurants[0] : null;
    } catch (error) {
        console.error('Error fetching restaurant:', error);
    }
    
    return {
        user,
        restaurant
    };
};
