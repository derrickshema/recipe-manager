import { writable, derived, type Writable } from 'svelte/store';
import type { Recipe, RecipeCreate } from '$lib/types/recipe';
import { recipeApi } from '$lib/api/recipes'; // Assuming this API layer is defined

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

// --- 2. Internal Helper Function for Error Handling ---

/**
 * Executes an async function, setting loading/error states around the execution.
 * @param store The writable store instance.
 * @param fn The asynchronous action to execute (which updates the state).
 * @param errorMsg The default error message.
 */
async function handleAsyncUpdate<T>(
    store: Writable<RecipeStore>,
    fn: () => Promise<T>,
    errorMsg: string
): Promise<T | null> {
    store.update(state => ({ ...state, loading: true, error: null }));
    try {
        const result = await fn();
        store.update(state => ({ ...state, loading: false }));
        return result;
    } catch (error) {
        store.update(state => ({
            ...state,
            error: error instanceof Error ? error.message : errorMsg,
            loading: false
        }));
        // Re-throw the error so component logic can handle it if needed (e.g., toast notification)
        throw error;
    }
}


// --- 3. Store Factory ---

function createRecipeStore() {
    const { subscribe, set, update } = writable<RecipeStore>(initialState);

    // Function to simplify common state updates
    const state = { subscribe, set, update };

    return {
        ...state,
        
        // --- CUD (Create, Update, Delete) Operations ---

        // Fetch recipes for a restaurant
        async fetchRecipes(restaurantId: number) {
            await handleAsyncUpdate(state, async () => {
                const recipes = await recipeApi.getRecipes(restaurantId);
                update(s => ({
                    ...s,
                    recipes: { ...s.recipes, [restaurantId]: recipes }
                }));
            }, 'Failed to fetch recipes.');
        },

        // Fetch a single recipe
        async fetchRecipe(recipeId: number, restaurantId: number) {
            return await handleAsyncUpdate(state, async () => {
                const recipe = await recipeApi.getRecipe(recipeId, restaurantId);
                update(s => ({ ...s, currentRecipe: recipe }));
                return recipe;
            }, 'Failed to fetch recipe.');
        },

        // Create a new recipe
        async createRecipe(restaurantId: number, recipe: RecipeCreate) {
            return await handleAsyncUpdate(state, async () => {
                const newRecipe = await recipeApi.createRecipe(restaurantId, recipe);
                update(s => ({
                    ...s,
                    recipes: {
                        ...s.recipes,
                        [restaurantId]: [...(s.recipes[restaurantId] || []), newRecipe]
                    }
                }));
                return newRecipe;
            }, 'Failed to create recipe.');
        },

        // Update a recipe
        async updateRecipe(recipeId: number, restaurantId: number, updates: Partial<Recipe>) {
            return await handleAsyncUpdate(state, async () => {
                const updatedRecipe = await recipeApi.updateRecipe(recipeId, restaurantId, updates);
                update(s => {
                    const updatedList = s.recipes[restaurantId]?.map(recipe => 
                        recipe.id === recipeId ? updatedRecipe : recipe
                    ) || [];
                    
                    return {
                        ...s,
                        recipes: { ...s.recipes, [restaurantId]: updatedList },
                        currentRecipe: s.currentRecipe?.id === recipeId ? updatedRecipe : s.currentRecipe,
                    };
                });
                return updatedRecipe;
            }, 'Failed to update recipe.');
        },

        // Delete a recipe
        async deleteRecipe(recipeId: number, restaurantId: number) {
            await handleAsyncUpdate(state, async () => {
                await recipeApi.deleteRecipe(recipeId, restaurantId);
                update(s => ({
                    ...s,
                    recipes: {
                        ...s.recipes,
                        [restaurantId]: s.recipes[restaurantId]?.filter(recipe => recipe.id !== recipeId) || []
                    },
                    currentRecipe: s.currentRecipe?.id === recipeId ? null : s.currentRecipe,
                }));
            }, 'Failed to delete recipe.');
        },

        // --- Utility Methods ---

        // NEW: Allows setting the current recipe state directly (or clearing it)
        setCurrentRecipe(recipe: Recipe | null) {
            update(s => ({ ...s, currentRecipe: recipe }));
        },

        // Reset store
        reset() {
            set(initialState);
        }
    };
}

export const recipeStore = createRecipeStore();

// --- 4. Derived Stores for Convenience ---

export const recipes = derived(recipeStore, $store => $store.recipes);
export const currentRecipe = derived(recipeStore, $store => $store.currentRecipe);
export const isLoading = derived(recipeStore, $store => $store.loading);
export const error = derived(recipeStore, $store => $store.error);