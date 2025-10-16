import { writable, derived } from 'svelte/store';
import type { Recipe } from '$lib/types/recipe';
import { recipeApi } from '$lib/api/recipes';

interface RecipeStore {
    recipes: Record<number, Recipe[]>;  // Keyed by restaurant_id
    loading: boolean;
    error: string | null;
    currentRecipe: Recipe | null;
}

function createRecipeStore() {
    const initialState: RecipeStore = {
        recipes: {},
        loading: false,
        error: null,
        currentRecipe: null
    };

    const { subscribe, set, update } = writable<RecipeStore>(initialState);

    return {
        subscribe,
        
        // Fetch recipes for a restaurant
        async fetchRecipes(restaurantId: number) {
            update(state => ({ ...state, loading: true, error: null }));
            try {
                const recipes = await recipeApi.getRecipes(restaurantId);
                update(state => ({
                    ...state,
                    recipes: { ...state.recipes, [restaurantId]: recipes },
                    loading: false
                }));
            } catch (error) {
                update(state => ({
                    ...state,
                    error: error instanceof Error ? error.message : 'Failed to fetch recipes',
                    loading: false
                }));
            }
        },

        // Fetch a single recipe
        async fetchRecipe(recipeId: number, restaurantId: number) {
            update(state => ({ ...state, loading: true, error: null }));
            try {
                const recipe = await recipeApi.getRecipe(recipeId, restaurantId);
                update(state => ({
                    ...state,
                    currentRecipe: recipe,
                    loading: false
                }));
                return recipe;
            } catch (error) {
                update(state => ({
                    ...state,
                    error: error instanceof Error ? error.message : 'Failed to fetch recipe',
                    loading: false
                }));
                throw error;
            }
        },

        // Create a new recipe
        async createRecipe(restaurantId: number, recipe: Omit<Recipe, 'id' | 'created_at' | 'updated_at' | 'restaurant_id'>) {
            update(state => ({ ...state, loading: true, error: null }));
            try {
                const newRecipe = await recipeApi.createRecipe(restaurantId, recipe);
                update(state => ({
                    ...state,
                    recipes: {
                        ...state.recipes,
                        [restaurantId]: [...(state.recipes[restaurantId] || []), newRecipe]
                    },
                    loading: false
                }));
                return newRecipe;
            } catch (error) {
                update(state => ({
                    ...state,
                    error: error instanceof Error ? error.message : 'Failed to create recipe',
                    loading: false
                }));
                throw error;
            }
        },

        // Update a recipe
        async updateRecipe(recipeId: number, restaurantId: number, updates: Partial<Recipe>) {
            update(state => ({ ...state, loading: true, error: null }));
            try {
                const updatedRecipe = await recipeApi.updateRecipe(recipeId, restaurantId, updates);
                update(state => ({
                    ...state,
                    recipes: {
                        ...state.recipes,
                        [restaurantId]: state.recipes[restaurantId]?.map(recipe => 
                            recipe.id === recipeId ? updatedRecipe : recipe
                        ) || []
                    },
                    currentRecipe: updatedRecipe,
                    loading: false
                }));
                return updatedRecipe;
            } catch (error) {
                update(state => ({
                    ...state,
                    error: error instanceof Error ? error.message : 'Failed to update recipe',
                    loading: false
                }));
                throw error;
            }
        },

        // Delete a recipe
        async deleteRecipe(recipeId: number, restaurantId: number) {
            update(state => ({ ...state, loading: true, error: null }));
            try {
                await recipeApi.deleteRecipe(recipeId, restaurantId);
                update(state => ({
                    ...state,
                    recipes: {
                        ...state.recipes,
                        [restaurantId]: state.recipes[restaurantId]?.filter(recipe => recipe.id !== recipeId) || []
                    },
                    currentRecipe: null,
                    loading: false
                }));
            } catch (error) {
                update(state => ({
                    ...state,
                    error: error instanceof Error ? error.message : 'Failed to delete recipe',
                    loading: false
                }));
                throw error;
            }
        },

        // Reset store
        reset() {
            set(initialState);
        }
    };
}

export const recipeStore = createRecipeStore();

// Derived stores for convenience
export const recipes = derived(recipeStore, $store => $store.recipes);
export const currentRecipe = derived(recipeStore, $store => $store.currentRecipe);
export const isLoading = derived(recipeStore, $store => $store.loading);
export const error = derived(recipeStore, $store => $store.error);