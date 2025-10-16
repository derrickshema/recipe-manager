import type { Restaurant, RestaurantCreate, RestaurantUpdate, Membership } from '$lib/types/restaurant';
import { api } from '$lib/utils/apiHelpers';

export const restaurantApi = {
    // Get all restaurants the user has access to
    getRestaurants: async () => {
        return api.get<Restaurant[]>('/restaurants/');
    },

    // Get a single restaurant
    getRestaurant: async (id: number) => {
        return api.get<Restaurant>(`/restaurants/${id}`);
    },

    // Create a new restaurant
    createRestaurant: async (restaurant: RestaurantCreate) => {
        return api.post<RestaurantCreate>('/restaurants/', restaurant);
    },

    // Update a restaurant
    updateRestaurant: async (id: number, restaurant: RestaurantUpdate) => {
        return api.put<RestaurantUpdate>(`/restaurants/${id}`, restaurant);
    },

    // Delete a restaurant
    deleteRestaurant: async (id: number) => {
        return api.delete(`/restaurants/${id}`);
    },

    // Get restaurant memberships
    getMemberships: async (restaurantId: number) => {
        return api.get<Membership[]>(`/restaurants/${restaurantId}/memberships`);
    },

    // Add a member to restaurant
    addMember: async (restaurantId: number, userId: number, role: string) => {
        return api.post<{ user_id: number; role: string }>(
            `/restaurants/${restaurantId}/memberships`,
            { user_id: userId, role }
        );
    },

    // Update member role
    updateMembership: async (restaurantId: number, membershipId: number, role: string) => {
        return api.put<{ role: string }>(
            `/restaurants/${restaurantId}/memberships/${membershipId}`,
            { role }
        );
    },

    // Remove a member from restaurant
    removeMember: async (restaurantId: number, membershipId: number) => {
        return api.delete(`/restaurants/${restaurantId}/memberships/${membershipId}`);
    }
};