import type { Recipe, RecipeCreate, RecipeUpdate } from '$lib/types/recipe';
import { api } from '$lib/utils/apiHelpers';

export const recipeApi = {
    // Get all recipes for a restaurant
    getRecipes: async (restaurantId: number) => {
        return api.get<Recipe[]>(`/recipes/?restaurant_id=${restaurantId}`);
    },

    // Get a single recipe
    getRecipe: async (recipeId: number, restaurantId: number) => {
        return api.get<Recipe>(`/recipes/${recipeId}?restaurant_id=${restaurantId}`);
    },

    // Create a new recipe
    createRecipe: async (restaurantId: number, recipe: RecipeCreate) => {
        return api.post<Recipe>(`/recipes/?restaurant_id=${restaurantId}`, recipe);
    },

    // Update a recipe
    updateRecipe: async (recipeId: number, restaurantId: number, recipe: RecipeUpdate) => {
        return api.put<Recipe>(`/recipes/${recipeId}?restaurant_id=${restaurantId}`, recipe);
    },

    // Delete a recipe
    deleteRecipe: async (recipeId: number, restaurantId: number) => {
        return api.delete(`/recipes/${recipeId}?restaurant_id=${restaurantId}`);
    }
};