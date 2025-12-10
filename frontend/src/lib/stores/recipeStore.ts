import { writable, derived } from 'svelte/store';
import type { Recipe, RecipeCreate } from '$lib/types/recipe';
import { recipeApi } from '$lib/api/recipes';
import { handleAsyncStore } from '$lib/utils/storeHelpers';

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


// --- 3. Store Factory ---

function createRecipeStore() {
    const { subscribe, set, update } = writable<RecipeStore>(initialState);
    
    const store = {
        subscribe,
        set,
        update,

        // Get all recipes for a restaurant
        async fetchRecipes(restaurantId: number) {
            return await handleAsyncStore(
                { subscribe, set, update },
                async () => {
                    const recipes = await recipeApi.getRecipes(restaurantId);
                    update(s => ({
                        ...s,
                        recipes: { ...s.recipes, [restaurantId]: recipes }
                    }));
                    return recipes;
                },
                'Failed to fetch recipes'
            );
        },

        // Get a single recipe
        async fetchRecipe(recipeId: number, restaurantId: number) {
            return await handleAsyncStore(
                { subscribe, set, update },
                async () => {
                    const recipe = await recipeApi.getRecipe(recipeId, restaurantId);
                    update(s => ({ ...s, currentRecipe: recipe }));
                    return recipe;
                },
                'Failed to fetch recipe'
            );
        },

        // Create a new recipe
        async createRecipe(restaurantId: number, recipe: RecipeCreate) {
            return await handleAsyncStore(
                { subscribe, set, update },
                async () => {
                    const newRecipe = await recipeApi.createRecipe(restaurantId, recipe);
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

        // Update a recipe
        async updateRecipe(recipeId: number, restaurantId: number, updates: Partial<Recipe>) {
            return await handleAsyncStore(
                { subscribe, set, update },
                async () => {
                    const updatedRecipe = await recipeApi.updateRecipe(recipeId, restaurantId, updates);
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

        // Delete a recipe
        async deleteRecipe(recipeId: number, restaurantId: number) {
            return await handleAsyncStore(
                { subscribe, set, update },
                async () => {
                    await recipeApi.deleteRecipe(recipeId, restaurantId);
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

        // Clear currently selected recipe
        clearCurrentRecipe() {
            update(s => ({ ...s, currentRecipe: null }));
        },

        // Select a recipe from the store
        selectRecipe(restaurantId: number, recipeId: number) {
            update(s => {
                const recipe = s.recipes[restaurantId]?.find(r => r.id === recipeId) || null;
                return { ...s, currentRecipe: recipe };
            });
        },

        // Reset store to initial state
        reset() {
            set(initialState);
        }
    };

    return store;
}

// --- 4. Create and Export Store Instance ---
export const recipeStore = createRecipeStore();

// --- 5. Derived Stores for Convenience ---
export const recipes = derived(recipeStore, $store => $store.recipes);
export const currentRecipe = derived(recipeStore, $store => $store.currentRecipe);
export const isLoading = derived(recipeStore, $store => $store.loading);
export const error = derived(recipeStore, $store => $store.error);