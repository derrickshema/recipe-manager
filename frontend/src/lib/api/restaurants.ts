import type {
    Restaurant,
    RestaurantCreateRequest,
    RestaurantUpdateRequest,
    Membership,
    AddMemberRequest,
    UpdateMembershipRequest,
    OrgRole
} from '$lib/types';
import { api } from '$lib/utils/apiHelpers';

/**
 * Restaurant API Client
 * Handles all restaurant-related HTTP requests
 */
export const restaurantApi = {
    /**
     * Get all restaurants the user has access to
     * @returns Array of restaurants
     */
    getRestaurants: async (): Promise<Restaurant[]> => {
        return api.get<Restaurant[]>('/restaurants/');
    },

    /**
     * Get a single restaurant by ID
     * @param id - Restaurant ID
     * @returns Restaurant details
     */
    getRestaurant: async (id: number): Promise<Restaurant> => {
        return api.get<Restaurant>(`/restaurants/${id}`);
    },

    /**
     * Create a new restaurant
     * @param restaurant - Restaurant data to create
     * @returns Created restaurant
     */
    createRestaurant: async (restaurant: RestaurantCreateRequest): Promise<Restaurant> => {
        return api.post<Restaurant>('/restaurants/', restaurant);
    },

    /**
     * Update an existing restaurant
     * @param id - Restaurant ID to update
     * @param restaurant - Restaurant data to update
     * @returns Updated restaurant
     */
    updateRestaurant: async (id: number, restaurant: RestaurantUpdateRequest): Promise<Restaurant> => {
        return api.put<Restaurant>(`/restaurants/${id}`, restaurant);
    },

    /**
     * Delete a restaurant
     * @param id - Restaurant ID to delete
     */
    deleteRestaurant: async (id: number): Promise<void> => {
        return api.delete(`/restaurants/${id}`);
    },

    /**
     * Get all memberships for a restaurant
     * @param restaurantId - Restaurant ID
     * @returns Array of memberships
     */
    getMemberships: async (restaurantId: number): Promise<Membership[]> => {
        return api.get<Membership[]>(`/restaurants/${restaurantId}/memberships`);
    },

    /**
     * Add a member to a restaurant
     * @param restaurantId - Restaurant ID
     * @param userId - User ID to add
     * @param role - Organization role to assign
     * @returns Created membership
     */
    addMember: async (restaurantId: number, userId: number, role: OrgRole): Promise<Membership> => {
        const request: AddMemberRequest = { user_id: userId, role };
        return api.post<Membership>(`/restaurants/${restaurantId}/memberships`, request);
    },

    /**
     * Update a member's role
     * @param restaurantId - Restaurant ID
     * @param membershipId - Membership ID to update
     * @param role - New organization role
     * @returns Updated membership
     */
    updateMembership: async (restaurantId: number, membershipId: number, role: OrgRole): Promise<Membership> => {
        const request: UpdateMembershipRequest = { role };
        return api.put<Membership>(`/restaurants/${restaurantId}/memberships/${membershipId}`, request);
    },

    /**
     * Remove a member from a restaurant
     * @param restaurantId - Restaurant ID
     * @param membershipId - Membership ID to remove
     */
    removeMember: async (restaurantId: number, membershipId: number): Promise<void> => {
        return api.delete(`/restaurants/${restaurantId}/memberships/${membershipId}`);
    },

    // ==================== Admin Operations ====================

    /**
     * Get all pending restaurant registrations (Admin only)
     * @returns Array of pending restaurants
     */
    getPendingRestaurants: async (): Promise<Restaurant[]> => {
        return api.get<Restaurant[]>('/restaurants/admin/pending');
    },

    /**
     * Approve a restaurant registration (Admin only)
     * @param restaurantId - Restaurant ID to approve
     * @returns Updated restaurant
     */
    approveRestaurant: async (restaurantId: number): Promise<Restaurant> => {
        return api.post<Restaurant>(`/restaurants/${restaurantId}/approve`, {});
    },

    /**
     * Reject a restaurant registration (Admin only)
     * @param restaurantId - Restaurant ID to reject
     * @returns Updated restaurant
     */
    rejectRestaurant: async (restaurantId: number): Promise<Restaurant> => {
        return api.post<Restaurant>(`/restaurants/${restaurantId}/reject`, {});
    },

    /**
     * Suspend a restaurant (Admin only)
     * @param restaurantId - Restaurant ID to suspend
     * @returns Updated restaurant
     */
    suspendRestaurant: async (restaurantId: number): Promise<Restaurant> => {
        return api.post<Restaurant>(`/restaurants/${restaurantId}/suspend`, {});
    }
};