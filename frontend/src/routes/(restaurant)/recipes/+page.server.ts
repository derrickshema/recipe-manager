import { fail, redirect } from '@sveltejs/kit';
import { serverApi } from '$lib/server/api';
import type { PageServerLoad, Actions } from './$types';
import type { Restaurant, Recipe } from '$lib/types';

/**
 * Server-side load function for the recipes page.
 * Fetches the user's restaurant and its recipes.
 */
export const load: PageServerLoad = async ({ cookies }) => {
    try {
        // Get the user's restaurants
        const restaurants = await serverApi.get<Restaurant[]>('/restaurants/my', cookies);
        const restaurant = restaurants.length > 0 ? restaurants[0] : null;
        
        if (!restaurant) {
            return {
                restaurant: null,
                recipes: [],
                error: 'No restaurant found'
            };
        }
        
        // Get recipes for the restaurant
        const recipes = await serverApi.get<Recipe[]>(
            `/recipes/?restaurant_id=${restaurant.id}`,
            cookies
        );

        return {
            restaurant,
            recipes
        };
    } catch (error) {
        console.error('Error loading recipes:', error);
        return {
            restaurant: null,
            recipes: [],
            error: 'Failed to load recipes'
        };
    }
};

/**
 * Form actions for recipe CRUD operations.
 * All mutations use SSR form actions for better security.
 */
export const actions: Actions = {
    /**
     * Create a new recipe
     */
    create: async ({ request, cookies }) => {
        const formData = await request.formData();
        const restaurantId = formData.get('restaurantId');
        const title = formData.get('title');
        const description = formData.get('description');
        const ingredientsRaw = formData.get('ingredients');
        const instructionsRaw = formData.get('instructions');
        const prepTime = formData.get('prepTime');
        const cookTime = formData.get('cookTime');
        const servings = formData.get('servings');

        // Validation
        if (!restaurantId || !title) {
            return fail(400, { 
                action: 'create',
                error: 'Restaurant ID and title are required',
                values: { title, description, ingredientsRaw, instructionsRaw, prepTime, cookTime, servings }
            });
        }

        // Parse ingredients and instructions (newline-separated)
        const ingredients = ingredientsRaw 
            ? String(ingredientsRaw).split('\n').filter(i => i.trim())
            : [];
        const instructions = instructionsRaw 
            ? String(instructionsRaw).split('\n').filter(i => i.trim())
            : [];

        try {
            await serverApi.post<Recipe>(
                `/recipes/?restaurant_id=${restaurantId}`,
                {
                    title: String(title),
                    description: description ? String(description) : undefined,
                    ingredients,
                    instructions,
                    prep_time: prepTime ? parseInt(String(prepTime)) : undefined,
                    cook_time: cookTime ? parseInt(String(cookTime)) : undefined,
                    servings: servings ? parseInt(String(servings)) : undefined,
                },
                cookies
            );

            return { 
                action: 'create',
                success: true, 
                message: 'Recipe created successfully' 
            };
        } catch (error: any) {
            return fail(error.status || 500, { 
                action: 'create',
                error: error.body?.message || 'Failed to create recipe',
                values: { title, description, ingredientsRaw, instructionsRaw, prepTime, cookTime, servings }
            });
        }
    },

    /**
     * Update an existing recipe
     */
    update: async ({ request, cookies }) => {
        const formData = await request.formData();
        const recipeId = formData.get('recipeId');
        const restaurantId = formData.get('restaurantId');
        const title = formData.get('title');
        const description = formData.get('description');
        const ingredientsRaw = formData.get('ingredients');
        const instructionsRaw = formData.get('instructions');
        const prepTime = formData.get('prepTime');
        const cookTime = formData.get('cookTime');
        const servings = formData.get('servings');

        if (!recipeId || !restaurantId) {
            return fail(400, { 
                action: 'update',
                error: 'Recipe ID and Restaurant ID are required' 
            });
        }

        // Parse ingredients and instructions (newline-separated)
        const ingredients = ingredientsRaw 
            ? String(ingredientsRaw).split('\n').filter(i => i.trim())
            : undefined;
        const instructions = instructionsRaw 
            ? String(instructionsRaw).split('\n').filter(i => i.trim())
            : undefined;

        try {
            await serverApi.put<Recipe>(
                `/recipes/${recipeId}?restaurant_id=${restaurantId}`,
                {
                    title: title ? String(title) : undefined,
                    description: description ? String(description) : undefined,
                    ingredients,
                    instructions,
                    prep_time: prepTime ? parseInt(String(prepTime)) : undefined,
                    cook_time: cookTime ? parseInt(String(cookTime)) : undefined,
                    servings: servings ? parseInt(String(servings)) : undefined,
                },
                cookies
            );

            return { 
                action: 'update',
                success: true, 
                message: 'Recipe updated successfully' 
            };
        } catch (error: any) {
            return fail(error.status || 500, { 
                action: 'update',
                error: error.body?.message || 'Failed to update recipe' 
            });
        }
    },

    /**
     * Delete a recipe
     */
    delete: async ({ request, cookies }) => {
        const formData = await request.formData();
        const recipeId = formData.get('recipeId');
        const restaurantId = formData.get('restaurantId');

        if (!recipeId || !restaurantId) {
            return fail(400, { 
                action: 'delete',
                error: 'Recipe ID and Restaurant ID are required' 
            });
        }

        try {
            await serverApi.delete(
                `/recipes/${recipeId}?restaurant_id=${restaurantId}`,
                cookies
            );

            return { 
                action: 'delete',
                success: true, 
                message: 'Recipe deleted successfully' 
            };
        } catch (error: any) {
            return fail(error.status || 500, { 
                action: 'delete',
                error: error.body?.message || 'Failed to delete recipe' 
            });
        }
    }
};
