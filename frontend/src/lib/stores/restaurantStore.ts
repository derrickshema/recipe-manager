import { writable, derived } from 'svelte/store';
import type { Restaurant, Membership } from '$lib/types/restaurant';
import { restaurantApi } from '$lib/api/restaurants';
import { handleAsyncStore } from '$lib/utils/storeHelpers';

// --- 1. State Definition ---
interface RestaurantStore {
    restaurants: Restaurant[];
    memberships: Record<number, Membership[]>;  // Keyed by restaurant_id
    loading: boolean;
    error: string | null;
    currentRestaurant: Restaurant | null;
}

const initialState: RestaurantStore = {
    restaurants: [],
    memberships: {},
    loading: false,
    error: null,
    currentRestaurant: null
};

// --- 2. Store Creation ---
function createRestaurantStore() {
    const { subscribe, set, update } = writable<RestaurantStore>(initialState);

    const store = {
        subscribe,
        set,
        update,
        
        // Fetch all restaurants
        async fetchRestaurants() {
            return handleAsyncStore(
                { subscribe, set, update },
                async () => {
                    const restaurants = await restaurantApi.getRestaurants();
                    update(state => ({
                        ...state,
                        restaurants
                    }));
                    return restaurants;
                },
                'Failed to fetch restaurants'
            );
        },

        // Fetch a single restaurant
        async fetchRestaurant(id: number) {
            return handleAsyncStore(
                { subscribe, set, update },
                async () => {
                    const restaurant = await restaurantApi.getRestaurant(id);
                    update(state => ({
                        ...state,
                        currentRestaurant: restaurant
                    }));
                    return restaurant;
                },
                'Failed to fetch restaurant'
            );
        },

        // Create a new restaurant
        async createRestaurant(name: string) {
            return handleAsyncStore(
                { subscribe, set, update },
                async () => {
                    const newRestaurant = await restaurantApi.createRestaurant({ restaurant_name: name });
                    update(state => ({
                        ...state,
                        restaurants: [...state.restaurants, newRestaurant]
                    }));
                    return newRestaurant;
                },
                'Failed to create restaurant'
            );
        },

        // Update a restaurant
        async updateRestaurant(id: number, name: string) {
            return handleAsyncStore(
                { subscribe, set, update },
                async () => {
                    const updatedRestaurant = await restaurantApi.updateRestaurant(id, { restaurant_name: name });
                    update(state => ({
                        ...state,
                        restaurants: state.restaurants.map(restaurant => 
                            restaurant.id === id ? updatedRestaurant : restaurant
                        ),
                        currentRestaurant: updatedRestaurant
                    }));
                    return updatedRestaurant;
                },
                'Failed to update restaurant'
            );
        },

        // Delete a restaurant
        async deleteRestaurant(id: number) {
            return handleAsyncStore(
                { subscribe, set, update },
                async () => {
                    await restaurantApi.deleteRestaurant(id);
                    update(state => ({
                        ...state,
                        restaurants: state.restaurants.filter(restaurant => restaurant.id !== id),
                        currentRestaurant: null
                    }));
                },
                'Failed to delete restaurant'
            );
        },

        // Fetch memberships for a restaurant
        async fetchMemberships(restaurantId: number) {
            return handleAsyncStore(
                { subscribe, set, update },
                async () => {
                    const memberships = await restaurantApi.getMemberships(restaurantId);
                    update(state => ({
                        ...state,
                        memberships: { ...state.memberships, [restaurantId]: memberships }
                    }));
                    return memberships;
                },
                'Failed to fetch memberships'
            );
        },

        // Reset store
        reset() {
            set(initialState);
        }
    };

    return store;
}

export const restaurantStore = createRestaurantStore();

// Derived stores for convenience
export const restaurants = derived(restaurantStore, $store => $store.restaurants);
export const currentRestaurant = derived(restaurantStore, $store => $store.currentRestaurant);
export const memberships = derived(restaurantStore, $store => $store.memberships);
export const isLoading = derived(restaurantStore, $store => $store.loading);
export const error = derived(restaurantStore, $store => $store.error);