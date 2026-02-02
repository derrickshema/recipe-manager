import type { PageServerLoad } from './$types';
import type { Restaurant, Recipe } from '$lib/types';

const API_BASE_URL = process.env.API_BASE_URL || 'http://localhost:8000';

/**
 * Server-side load function for the restaurant detail page.
 * Fetches the restaurant details and its menu (recipes).
 */
export const load: PageServerLoad = async ({ params }) => {
    const restaurantId = params.id;
    
    try {
        // Fetch restaurant details (public endpoint)
        const restaurantResponse = await fetch(`${API_BASE_URL}/restaurants/approved/${restaurantId}`);
        
        if (!restaurantResponse.ok) {
            return {
                restaurant: null,
                recipes: [],
                error: 'Restaurant not found'
            };
        }
        
        const restaurant: Restaurant = await restaurantResponse.json();
        
        // Fetch restaurant menu (public endpoint)
        const recipesResponse = await fetch(`${API_BASE_URL}/recipes/public/${restaurantId}`);
        
        let recipes: Recipe[] = [];
        if (recipesResponse.ok) {
            recipes = await recipesResponse.json();
        }
        
        return {
            restaurant,
            recipes
        };
    } catch (error) {
        console.error('Error loading restaurant:', error);
        return {
            restaurant: null,
            recipes: [],
            error: 'Failed to load restaurant'
        };
    }
};
