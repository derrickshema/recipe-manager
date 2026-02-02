import { serverApi } from '$lib/server/api';
import type { PageServerLoad } from './$types';
import type { Restaurant } from '$lib/types';

const API_BASE_URL = process.env.API_BASE_URL || 'http://localhost:8000';

/**
 * Server-side load function for the customer home page.
 * Fetches approved restaurants for customers to browse.
 * Supports search and cuisine filter via query parameters.
 */
export const load: PageServerLoad = async ({ url }) => {
    try {
        // Get search and filter parameters from URL
        const search = url.searchParams.get('search') || '';
        const cuisine = url.searchParams.get('cuisine') || '';
        
        // Build query string for the API
        const params = new URLSearchParams();
        if (search) params.append('search', search);
        if (cuisine) params.append('cuisine', cuisine);
        
        const queryString = params.toString() ? `?${params.toString()}` : '';
        
        // Fetch approved restaurants with optional search/filter
        const response = await fetch(`${API_BASE_URL}/restaurants/approved${queryString}`);
        
        if (!response.ok) {
            console.error('Failed to fetch restaurants:', response.status);
            return {
                restaurants: [],
                search,
                cuisine,
                error: 'Failed to load restaurants'
            };
        }

        const restaurants: Restaurant[] = await response.json();

        return {
            restaurants,
            search,
            cuisine
        };
    } catch (error) {
        console.error('Error loading restaurants:', error);
        return {
            restaurants: [],
            search: '',
            cuisine: '',
            error: 'Failed to load restaurants'
        };
    }
};
