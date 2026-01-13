import { serverApi } from '$lib/server/api';
import type { PageServerLoad } from './$types';
import type { Restaurant, Recipe } from '$lib/types';

/**
 * Server-side load function for the restaurant dashboard.
 * Fetches the user's restaurant and related data.
 */
export const load: PageServerLoad = async ({ cookies }) => {
    try {
        // Get the user's restaurants
        const restaurants = await serverApi.get<Restaurant[]>('/restaurants/my', cookies);
        
        // For now, we'll use the first restaurant
        // In the future, we could support multiple restaurants
        const restaurant = restaurants.length > 0 ? restaurants[0] : null;
        
        let recipes: Recipe[] = [];
        let recipeCount = 0;
        
        if (restaurant) {
            // Get recipes for the restaurant
            recipes = await serverApi.get<Recipe[]>(
                `/recipes/?restaurant_id=${restaurant.id}`,
                cookies
            );
            recipeCount = recipes.length;
        }

        return {
            restaurant,
            restaurants,
            recipeCount,
            // Could add more dashboard stats here
            stats: {
                totalRecipes: recipeCount,
                staffCount: 0, // TODO: implement staff count
                pendingOrders: 0 // Future feature
            }
        };
    } catch (error) {
        console.error('Error loading dashboard:', error);
        return {
            restaurant: null,
            restaurants: [],
            recipeCount: 0,
            stats: {
                totalRecipes: 0,
                staffCount: 0,
                pendingOrders: 0
            },
            error: 'Failed to load dashboard data'
        };
    }
};
