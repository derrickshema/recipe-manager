import { serverApi } from '$lib/server/api';
import type { PageServerLoad } from './$types';
import type { Restaurant } from '$lib/types';

const API_BASE_URL = process.env.API_BASE_URL || 'http://localhost:8000';

/**
 * Server-side load function for the customer home page.
 * Fetches approved restaurants for customers to browse.
 */
export const load: PageServerLoad = async ({ cookies }) => {
    try {
        // Fetch approved restaurants (public endpoint - no auth required)
        const response = await fetch(`${API_BASE_URL}/restaurants/approved`);
        
        if (!response.ok) {
            console.error('Failed to fetch restaurants:', response.status);
            return {
                restaurants: [],
                error: 'Failed to load restaurants'
            };
        }

        const restaurants: Restaurant[] = await response.json();

        return {
            restaurants
        };
    } catch (error) {
        console.error('Error loading restaurants:', error);
        return {
            restaurants: [],
            error: 'Failed to load restaurants'
        };
    }
};
