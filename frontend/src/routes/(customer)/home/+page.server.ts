import { serverApi } from '$lib/server/api';
import type { PageServerLoad } from './$types';
import type { Restaurant } from '$lib/types';

/**
 * Server-side load function for the customer home page.
 * Fetches approved restaurants for customers to browse.
 */
export const load: PageServerLoad = async ({ cookies }) => {
    try {
        // For customers, we would typically fetch only approved restaurants
        // For now, we'll return an empty array until we have a public restaurants endpoint
        // TODO: Create a public-facing endpoint for approved restaurants
        const restaurants: Restaurant[] = [];

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
