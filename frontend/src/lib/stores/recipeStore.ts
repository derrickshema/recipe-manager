import { writable, derived } from 'svelte/store';
import type { Recipe, RecipeCreateRequest, RecipeUpdateRequest } from '$lib/types';
import { handleAsyncStore } from '$lib/utils/storeHelpers';
import { recipeService } from '$lib/services/recipeService';

// --- 1. State Definition ---
interface RecipeStore {
    recipes: Record<number, Recipe[]>; // Keyed by restaurant_id for caching
    loading: boolean;
    error: string | null;
    currentRecipe: Recipe | null;
}

const initialState: RecipeStore = {
    recipes: {},
    loading: false,
    error: null,
    currentRecipe: null
};


// --- 2. Store Factory ---

function createRecipeStore() {
    const { subscribe, set, update } = writable<RecipeStore>(initialState);
    
    const store = {
        subscribe,
        set,
        update,

        /**
         * Fetch all recipes for a restaurant
         * Delegates business logic to recipeService, manages state here
         */
        async fetchRecipes(restaurantId: number) {
            return await handleAsyncStore(
                { subscribe, set, update },
                async () => {
                    const recipes = await recipeService.fetchRecipes(restaurantId);
                    update(s => ({
                        ...s,
                        recipes: { ...s.recipes, [restaurantId]: recipes }
                    }));
                    return recipes;
                },
                'Failed to fetch recipes'
            );
        },

        /**
         * Fetch a single recipe
         * Delegates business logic to recipeService, manages state here
         */
        async fetchRecipe(recipeId: number, restaurantId: number) {
            return await handleAsyncStore(
                { subscribe, set, update },
                async () => {
                    const recipe = await recipeService.fetchRecipe(recipeId, restaurantId);
                    update(s => ({ ...s, currentRecipe: recipe }));
                    return recipe;
                },
                'Failed to fetch recipe'
            );
        },

        /**
         * Create a new recipe
         * Delegates business logic to recipeService, manages state here
         * @param restaurantId - Restaurant ID
         * @param recipe - Recipe data to create
         */
        async createRecipe(restaurantId: number, recipe: RecipeCreateRequest) {
            return await handleAsyncStore(
                { subscribe, set, update },
                async () => {
                    const newRecipe = await recipeService.createRecipe(restaurantId, recipe);
                    update(s => ({
                        ...s,
                        recipes: {
                            ...s.recipes,
                            [restaurantId]: [...(s.recipes[restaurantId] || []), newRecipe]
                        }
                    }));
                    return newRecipe;
                },
                'Failed to create recipe'
            );
        },

        /**
         * Update a recipe
         * Delegates business logic to recipeService, manages state here
         * @param recipeId - Recipe ID to update
         * @param restaurantId - Restaurant ID
         * @param updates - Recipe fields to update
         */
        async updateRecipe(recipeId: number, restaurantId: number, updates: RecipeUpdateRequest) {
            return await handleAsyncStore(
                { subscribe, set, update },
                async () => {
                    const updatedRecipe = await recipeService.updateRecipe(recipeId, restaurantId, updates);
                    update(s => {
                        const updatedList = s.recipes[restaurantId]?.map(recipe => 
                            recipe.id === recipeId ? updatedRecipe : recipe
                        ) || [];
                        
                        return {
                            ...s,
                            recipes: { ...s.recipes, [restaurantId]: updatedList },
                            currentRecipe: s.currentRecipe?.id === recipeId ? updatedRecipe : s.currentRecipe
                        };
                    });
                    return updatedRecipe;
                },
                'Failed to update recipe'
            );
        },

        /**
         * Delete a recipe
         * Delegates business logic to recipeService, manages state here
         */
        async deleteRecipe(recipeId: number, restaurantId: number) {
            return await handleAsyncStore(
                { subscribe, set, update },
                async () => {
                    await recipeService.deleteRecipe(recipeId, restaurantId);
                    update(s => ({
                        ...s,
                        recipes: {
                            ...s.recipes,
                            [restaurantId]: s.recipes[restaurantId]?.filter(recipe => recipe.id !== recipeId) || []
                        },
                        currentRecipe: s.currentRecipe?.id === recipeId ? null : s.currentRecipe
                    }));
                },
                'Failed to delete recipe'
            );
        },

        /**
         * Clear currently selected recipe
         */
        clearCurrentRecipe() {
            update(s => ({ ...s, currentRecipe: null }));
        },

        /**
         * Select a recipe from the store (local operation, no API call)
         */
        selectRecipe(restaurantId: number, recipeId: number) {
            update(s => {
                const recipe = s.recipes[restaurantId]?.find(r => r.id === recipeId) || null;
                return { ...s, currentRecipe: recipe };
            });
        },

        /**
         * Reset store to initial state
         */
        reset() {
            set(initialState);
        }
    };

    return store;
}

// --- 3. Create and Export Store Instance ---
export const recipeStore = createRecipeStore();

// --- 4. Derived Stores for Convenience ---
export const recipes = derived(recipeStore, $store => $store.recipes);
export const currentRecipe = derived(recipeStore, $store => $store.currentRecipe);
export const isLoading = derived(recipeStore, $store => $store.loading);
export const error = derived(recipeStore, $store => $store.error);