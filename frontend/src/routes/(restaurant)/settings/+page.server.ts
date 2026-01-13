import { fail } from '@sveltejs/kit';
import { serverApi } from '$lib/server/api';
import type { PageServerLoad, Actions } from './$types';
import type { Restaurant } from '$lib/types';

/**
 * Server-side load function for the restaurant settings page.
 * Fetches the user's restaurant details.
 */
export const load: PageServerLoad = async ({ cookies }) => {
    try {
        // Get the user's restaurants
        const restaurants = await serverApi.get<Restaurant[]>('/restaurants/my', cookies);
        const restaurant = restaurants.length > 0 ? restaurants[0] : null;
        
        return {
            restaurant
        };
    } catch (error) {
        console.error('Error loading settings:', error);
        return {
            restaurant: null,
            error: 'Failed to load restaurant settings'
        };
    }
};

/**
 * Form actions for restaurant settings.
 */
export const actions: Actions = {
    /**
     * Update restaurant details
     */
    update: async ({ request, cookies }) => {
        const formData = await request.formData();
        const restaurantId = formData.get('restaurantId');
        const restaurantName = formData.get('restaurantName');
        const cuisineType = formData.get('cuisineType');
        const address = formData.get('address');
        const phone = formData.get('phone');

        if (!restaurantId) {
            return fail(400, { 
                action: 'update',
                error: 'Restaurant ID is required' 
            });
        }

        if (!restaurantName) {
            return fail(400, { 
                action: 'update',
                error: 'Restaurant name is required',
                values: { restaurantName, cuisineType, address, phone }
            });
        }

        try {
            await serverApi.put<Restaurant>(
                `/restaurants/${restaurantId}`,
                {
                    restaurant_name: String(restaurantName),
                    cuisine_type: cuisineType ? String(cuisineType) : undefined,
                    address: address ? String(address) : undefined,
                    phone: phone ? String(phone) : undefined,
                },
                cookies
            );

            return { 
                action: 'update',
                success: true, 
                message: 'Settings updated successfully' 
            };
        } catch (error: any) {
            return fail(error.status || 500, { 
                action: 'update',
                error: error.body?.message || 'Failed to update settings',
                values: { restaurantName, cuisineType, address, phone }
            });
        }
    }
};
