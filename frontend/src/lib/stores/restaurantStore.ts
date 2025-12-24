import { writable, derived } from 'svelte/store';
import type {
    Restaurant,
    RestaurantCreateRequest,
    RestaurantUpdateRequest,
    Membership
} from '$lib/types';
import { handleAsyncStore } from '$lib/utils/storeHelpers';
import { restaurantService } from '$lib/services/restaurantService';

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
        
        /**
         * Fetch all restaurants
         * Delegates business logic to restaurantService, manages state here
         */
        async fetchRestaurants() {
            return handleAsyncStore(
                { subscribe, set, update },
                async () => {
                    const restaurants = await restaurantService.fetchRestaurants();
                    update(state => ({
                        ...state,
                        restaurants
                    }));
                    return restaurants;
                },
                'Failed to fetch restaurants'
            );
        },

        /**
         * Fetch a single restaurant
         * Delegates business logic to restaurantService, manages state here
         */
        async fetchRestaurant(id: number) {
            return handleAsyncStore(
                { subscribe, set, update },
                async () => {
                    const restaurant = await restaurantService.fetchRestaurant(id);
                    update(state => ({
                        ...state,
                        currentRestaurant: restaurant
                    }));
                    return restaurant;
                },
                'Failed to fetch restaurant'
            );
        },

        /**
         * Create a new restaurant
         * Delegates business logic to restaurantService, manages state here
         * @param data - Restaurant data to create
         */
        async createRestaurant(data: RestaurantCreateRequest) {
            return handleAsyncStore(
                { subscribe, set, update },
                async () => {
                    const newRestaurant = await restaurantService.createRestaurant(data);
                    update(state => ({
                        ...state,
                        restaurants: [...state.restaurants, newRestaurant]
                    }));
                    return newRestaurant;
                },
                'Failed to create restaurant'
            );
        },

        /**
         * Update a restaurant
         * Delegates business logic to restaurantService, manages state here
         * @param id - Restaurant ID to update
         * @param data - Restaurant fields to update
         */
        async updateRestaurant(id: number, data: RestaurantUpdateRequest) {
            return handleAsyncStore(
                { subscribe, set, update },
                async () => {
                    const updatedRestaurant = await restaurantService.updateRestaurant(id, data);
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

        /**
         * Delete a restaurant
         * Delegates business logic to restaurantService, manages state here
         */
        async deleteRestaurant(id: number) {
            return handleAsyncStore(
                { subscribe, set, update },
                async () => {
                    await restaurantService.deleteRestaurant(id);
                    update(state => ({
                        ...state,
                        restaurants: state.restaurants.filter(restaurant => restaurant.id !== id),
                        currentRestaurant: null
                    }));
                },
                'Failed to delete restaurant'
            );
        },

        /**
         * Fetch memberships for a restaurant
         * Delegates business logic to restaurantService, manages state here
         */
        async fetchMemberships(restaurantId: number) {
            return handleAsyncStore(
                { subscribe, set, update },
                async () => {
                    const memberships = await restaurantService.fetchMemberships(restaurantId);
                    update(state => ({
                        ...state,
                        memberships: { ...state.memberships, [restaurantId]: memberships }
                    }));
                    return memberships;
                },
                'Failed to fetch memberships'
            );
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
export const restaurantStore = createRestaurantStore();

// --- 4. Derived Stores for Convenience ---
export const restaurants = derived(restaurantStore, $store => $store.restaurants);
export const currentRestaurant = derived(restaurantStore, $store => $store.currentRestaurant);
export const memberships = derived(restaurantStore, $store => $store.memberships);
export const isLoading = derived(restaurantStore, $store => $store.loading);
export const error = derived(restaurantStore, $store => $store.error);