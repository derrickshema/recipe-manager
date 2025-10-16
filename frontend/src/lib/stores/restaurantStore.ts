import { writable, derived } from 'svelte/store';
import type { Restaurant, Membership } from '$lib/types/restaurant';
import { restaurantApi } from '$lib/api/restaurants';

interface RestaurantStore {
    restaurants: Restaurant[];
    memberships: Record<number, Membership[]>;  // Keyed by restaurant_id
    loading: boolean;
    error: string | null;
    currentRestaurant: Restaurant | null;
}

function createRestaurantStore() {
    const initialState: RestaurantStore = {
        restaurants: [],
        memberships: {},
        loading: false,
        error: null,
        currentRestaurant: null
    };

    const { subscribe, set, update } = writable<RestaurantStore>(initialState);

    return {
        subscribe,
        
        // Fetch all restaurants
        async fetchRestaurants() {
            update(state => ({ ...state, loading: true, error: null }));
            try {
                const restaurants = await restaurantApi.getRestaurants();
                update(state => ({
                    ...state,
                    restaurants,
                    loading: false
                }));
            } catch (error) {
                update(state => ({
                    ...state,
                    error: error instanceof Error ? error.message : 'Failed to fetch restaurants',
                    loading: false
                }));
            }
        },

        // Fetch a single restaurant
        async fetchRestaurant(id: number) {
            update(state => ({ ...state, loading: true, error: null }));
            try {
                const restaurant = await restaurantApi.getRestaurant(id);
                update(state => ({
                    ...state,
                    currentRestaurant: restaurant,
                    loading: false
                }));
                return restaurant;
            } catch (error) {
                update(state => ({
                    ...state,
                    error: error instanceof Error ? error.message : 'Failed to fetch restaurant',
                    loading: false
                }));
                throw error;
            }
        },

        // Create a new restaurant
        async createRestaurant(name: string) {
            update(state => ({ ...state, loading: true, error: null }));
            try {
                const newRestaurant = await restaurantApi.createRestaurant({ restaurant_name: name });
                update(state => ({
                    ...state,
                    restaurants: [...state.restaurants, newRestaurant],
                    loading: false
                }));
                return newRestaurant;
            } catch (error) {
                update(state => ({
                    ...state,
                    error: error instanceof Error ? error.message : 'Failed to create restaurant',
                    loading: false
                }));
                throw error;
            }
        },

        // Update a restaurant
        async updateRestaurant(id: number, name: string) {
            update(state => ({ ...state, loading: true, error: null }));
            try {
                const updatedRestaurant = await restaurantApi.updateRestaurant(id, { restaurant_name: name });
                update(state => ({
                    ...state,
                    restaurants: state.restaurants.map(restaurant => 
                        restaurant.id === id ? updatedRestaurant : restaurant
                    ),
                    currentRestaurant: updatedRestaurant,
                    loading: false
                }));
                return updatedRestaurant;
            } catch (error) {
                update(state => ({
                    ...state,
                    error: error instanceof Error ? error.message : 'Failed to update restaurant',
                    loading: false
                }));
                throw error;
            }
        },

        // Delete a restaurant
        async deleteRestaurant(id: number) {
            update(state => ({ ...state, loading: true, error: null }));
            try {
                await restaurantApi.deleteRestaurant(id);
                update(state => ({
                    ...state,
                    restaurants: state.restaurants.filter(restaurant => restaurant.id !== id),
                    currentRestaurant: null,
                    loading: false
                }));
            } catch (error) {
                update(state => ({
                    ...state,
                    error: error instanceof Error ? error.message : 'Failed to delete restaurant',
                    loading: false
                }));
                throw error;
            }
        },

        // Fetch memberships for a restaurant
        async fetchMemberships(restaurantId: number) {
            update(state => ({ ...state, loading: true, error: null }));
            try {
                const memberships = await restaurantApi.getMemberships(restaurantId);
                update(state => ({
                    ...state,
                    memberships: { ...state.memberships, [restaurantId]: memberships },
                    loading: false
                }));
            } catch (error) {
                update(state => ({
                    ...state,
                    error: error instanceof Error ? error.message : 'Failed to fetch memberships',
                    loading: false
                }));
            }
        },

        // Reset store
        reset() {
            set(initialState);
        }
    };
}

export const restaurantStore = createRestaurantStore();

// Derived stores for convenience
export const restaurants = derived(restaurantStore, $store => $store.restaurants);
export const currentRestaurant = derived(restaurantStore, $store => $store.currentRestaurant);
export const memberships = derived(restaurantStore, $store => $store.memberships);
export const isLoading = derived(restaurantStore, $store => $store.loading);
export const error = derived(restaurantStore, $store => $store.error);