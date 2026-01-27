import type { OrgRole } from './roles';

// ==================== Core Restaurant Types ====================

/**
 * Restaurant approval status enum
 */
export enum ApprovalStatus {
    PENDING = "pending",
    APPROVED = "approved",
    REJECTED = "rejected",
    SUSPENDED = "suspended"
}

/**
 * Complete restaurant entity
 * Returned from GET /restaurants/{id}
 */
export interface Restaurant {
    id: number;
    restaurant_name: string;
    cuisine_type?: string;
    address?: string;
    phone?: string;
    logo_url?: string;
    approval_status: ApprovalStatus;
    created_at: string;
    updated_at: string;
}

// ==================== Restaurant Operations ====================

/**
 * Restaurant creation request payload
 * Sent to POST /restaurants
 */
export interface RestaurantCreateRequest {
    restaurant_name: string;
    cuisine_type?: string;
    address?: string;
    phone?: string;
    logo_url?: string;
}

/**
 * Restaurant update request payload
 * Sent to PUT /restaurants/{id}
 */
export interface RestaurantUpdateRequest {
    restaurant_name?: string;
    cuisine_type?: string;
    address?: string;
    phone?: string;
    logo_url?: string;
    approval_status?: ApprovalStatus;
}

/**
 * Response from restaurant list endpoint
 * GET /restaurants
 */
export interface RestaurantListResponse {
    restaurants: Restaurant[];
    total: number;
}

// ==================== Membership Management ====================

/**
 * Restaurant membership entity
 * Links users to restaurants with specific roles
 */
export interface Membership {
    id: number;
    user_id: number;
    restaurant_id: number;
    role: OrgRole;
    created_at: string;
    updated_at: string;
}

/**
 * Add member request payload
 * Sent to POST /restaurants/{id}/memberships
 */
export interface AddMemberRequest {
    user_id: number;
    role: OrgRole;
}

/**
 * Update membership request payload
 * Sent to PUT /restaurants/{id}/memberships/{membershipId}
 */
export interface UpdateMembershipRequest {
    role: OrgRole;
}

/**
 * Response from membership operations
 */
export interface MembershipResponse {
    membership: Membership;
}

// Type aliases for backward compatibility
export type RestaurantCreate = RestaurantCreateRequest;
export type RestaurantUpdate = RestaurantUpdateRequest;

// Re-export OrgRole for convenience
export type { OrgRole };