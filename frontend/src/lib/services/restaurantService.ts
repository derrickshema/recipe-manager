import type {
    Restaurant,
    RestaurantCreateRequest,
    RestaurantUpdateRequest,
    Membership,
    OrgRole
} from '$lib/types';
import { restaurantApi } from '$lib/api/restaurants';

/**
 * Restaurant Service
 * Handles business logic for restaurant operations
 * Separated from state management for better testability and reusability
 */
export const restaurantService = {
    /**
     * Fetch all restaurants the user has access to
     * @returns Array of restaurants
     */
    async fetchRestaurants(): Promise<Restaurant[]> {
        return await restaurantApi.getRestaurants();
    },

    /**
     * Fetch a single restaurant by ID
     * @param id - Restaurant ID
     * @returns Restaurant details
     */
    async fetchRestaurant(id: number): Promise<Restaurant> {
        return await restaurantApi.getRestaurant(id);
    },

    /**
     * Create a new restaurant
     * @param data - Restaurant data to create
     * @returns Created restaurant
     */
    async createRestaurant(data: RestaurantCreateRequest): Promise<Restaurant> {
        return await restaurantApi.createRestaurant(data);
    },

    /**
     * Update an existing restaurant
     * @param id - Restaurant ID to update
     * @param data - Restaurant fields to update
     * @returns Updated restaurant
     */
    async updateRestaurant(id: number, data: RestaurantUpdateRequest): Promise<Restaurant> {
        return await restaurantApi.updateRestaurant(id, data);
    },

    /**
     * Delete a restaurant
     * @param id - Restaurant ID to delete
     */
    async deleteRestaurant(id: number): Promise<void> {
        await restaurantApi.deleteRestaurant(id);
    },

    /**
     * Fetch all memberships for a restaurant
     * @param restaurantId - Restaurant ID
     * @returns Array of memberships
     */
    async fetchMemberships(restaurantId: number): Promise<Membership[]> {
        return await restaurantApi.getMemberships(restaurantId);
    },

    /**
     * Add a member to a restaurant
     * @param restaurantId - Restaurant ID
     * @param userId - User ID to add
     * @param role - Organization role to assign
     * @returns Created membership
     */
    async addMember(restaurantId: number, userId: number, role: OrgRole): Promise<Membership> {
        return await restaurantApi.addMember(restaurantId, userId, role);
    },

    /**
     * Update a member's role
     * @param restaurantId - Restaurant ID
     * @param membershipId - Membership ID to update
     * @param role - New organization role
     * @returns Updated membership
     */
    async updateMembership(restaurantId: number, membershipId: number, role: OrgRole): Promise<Membership> {
        return await restaurantApi.updateMembership(restaurantId, membershipId, role);
    },

    /**
     * Remove a member from a restaurant
     * @param restaurantId - Restaurant ID
     * @param membershipId - Membership ID to remove
     */
    async removeMember(restaurantId: number, membershipId: number): Promise<void> {
        await restaurantApi.removeMember(restaurantId, membershipId);
    }
};