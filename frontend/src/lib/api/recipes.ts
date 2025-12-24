import type { Recipe, RecipeCreateRequest, RecipeUpdateRequest } from '$lib/types';
import { api } from '$lib/utils/apiHelpers';

/**
 * Recipe API Client
 * Handles all recipe-related HTTP requests
 */
export const recipeApi = {
    /**
     * Get all recipes for a restaurant
     * @param restaurantId - Restaurant ID to fetch recipes for
     * @returns Array of recipes
     */
    getRecipes: async (restaurantId: number): Promise<Recipe[]> => {
        return api.get<Recipe[]>(`/recipes/?restaurant_id=${restaurantId}`);
    },

    /**
     * Get a single recipe by ID
     * @param recipeId - Recipe ID
     * @param restaurantId - Restaurant ID
     * @returns Recipe details
     */
    getRecipe: async (recipeId: number, restaurantId: number): Promise<Recipe> => {
        return api.get<Recipe>(`/recipes/${recipeId}?restaurant_id=${restaurantId}`);
    },

    /**
     * Create a new recipe
     * @param restaurantId - Restaurant ID
     * @param recipe - Recipe data to create
     * @returns Created recipe
     */
    createRecipe: async (restaurantId: number, recipe: RecipeCreateRequest): Promise<Recipe> => {
        return api.post<Recipe>(`/recipes/?restaurant_id=${restaurantId}`, recipe);
    },

    /**
     * Update an existing recipe
     * @param recipeId - Recipe ID to update
     * @param restaurantId - Restaurant ID
     * @param recipe - Recipe data to update
     * @returns Updated recipe
     */
    updateRecipe: async (recipeId: number, restaurantId: number, recipe: RecipeUpdateRequest): Promise<Recipe> => {
        return api.put<Recipe>(`/recipes/${recipeId}?restaurant_id=${restaurantId}`, recipe);
    },

    /**
     * Delete a recipe
     * @param recipeId - Recipe ID to delete
     * @param restaurantId - Restaurant ID
     */
    deleteRecipe: async (recipeId: number, restaurantId: number): Promise<void> => {
        return api.delete(`/recipes/${recipeId}?restaurant_id=${restaurantId}`);
    }
};