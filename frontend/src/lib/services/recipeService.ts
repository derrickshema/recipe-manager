import type { Recipe, RecipeCreateRequest, RecipeUpdateRequest } from '$lib/types';
import { recipeApi } from '$lib/api/recipes';

/**
 * Recipe Service
 * Handles business logic for recipe operations
 * Separated from state management for better testability and reusability
 */
export const recipeService = {
    /**
     * Fetch all recipes for a restaurant
     * @param restaurantId - Restaurant ID to fetch recipes for
     * @returns Array of recipes
     */
    async fetchRecipes(restaurantId: number): Promise<Recipe[]> {
        return await recipeApi.getRecipes(restaurantId);
    },

    /**
     * Fetch a single recipe
     * @param recipeId - Recipe ID
     * @param restaurantId - Restaurant ID
     * @returns Recipe details
     */
    async fetchRecipe(recipeId: number, restaurantId: number): Promise<Recipe> {
        return await recipeApi.getRecipe(recipeId, restaurantId);
    },

    /**
     * Create a new recipe
     * @param restaurantId - Restaurant ID
     * @param recipe - Recipe data to create
     * @returns Created recipe
     */
    async createRecipe(restaurantId: number, recipe: RecipeCreateRequest): Promise<Recipe> {
        return await recipeApi.createRecipe(restaurantId, recipe);
    },

    /**
     * Update an existing recipe
     * @param recipeId - Recipe ID to update
     * @param restaurantId - Restaurant ID
     * @param updates - Recipe fields to update
     * @returns Updated recipe
     */
    async updateRecipe(
        recipeId: number, 
        restaurantId: number, 
        updates: RecipeUpdateRequest
    ): Promise<Recipe> {
        return await recipeApi.updateRecipe(recipeId, restaurantId, updates);
    },

    /**
     * Delete a recipe
     * @param recipeId - Recipe ID to delete
     * @param restaurantId - Restaurant ID
     */
    async deleteRecipe(recipeId: number, restaurantId: number): Promise<void> {
        await recipeApi.deleteRecipe(recipeId, restaurantId);
    }
};