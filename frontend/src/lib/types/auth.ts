import type { SystemRole, OrgRole } from './roles';

// ==================== Core User Types ====================

/**
 * User profile from backend
 * Raw response from /auth/me endpoint
 */
export interface UserProfile {
    id: number;
    email: string;
    username: string;
    first_name: string;
    last_name: string;
    role: SystemRole;
}

/**
 * Authenticated user profile
 * Returned from authService and stored in authStore
 * Extends UserProfile with frontend-specific fields
 */
export interface AuthUser extends UserProfile {
    org_role?: OrgRole;  // Optional: only for users with restaurant membership
    restaurant_id?: number;  // Optional: derived from membership
    isAuthenticated: boolean;  // Frontend-only field for state management
}

// ==================== Login Flow ====================

/**
 * Login request payload
 * Sent to /auth/token
 */
export interface LoginRequest {
    username: string;
    password: string;
}

/**
 * Login response from /auth/token
 * Contains JWT access token
 */
export interface LoginResponse {
    access_token: string;
    token_type: string;
}

// ==================== Customer Registration Flow ====================

/**
 * Customer registration request payload
 * Sent to /auth/register
 */
export interface RegisterCustomerRequest {
    email: string;
    username: string;
    password: string;
    first_name: string;
    last_name: string;
}

/**
 * Registration response from /auth/register
 * Returns created user profile
 */
export interface RegisterResponse {
    id: string;
    email: string;
    username: string;
    first_name: string;
    last_name: string;
    role: SystemRole;
}

// ==================== Restaurant Owner Registration Flow ====================

/**
 * Restaurant owner registration request payload
 * Sent to /auth/register/restaurant-owner
 * Creates user + restaurant + membership atomically
 */
export interface RegisterRestaurantOwnerRequest {
    // Owner information
    first_name: string;
    last_name: string;
    username: string;
    email: string;
    password: string;
    phone_number?: string;
    
    // Restaurant information
    restaurant_name: string;
    cuisine_type?: string;
    address?: string;
    restaurant_phone?: string;
}

// ==================== Profile Management ====================

/**
 * Profile update request payload
 * Sent to /auth/me (PUT)
 */
export interface UpdateProfileRequest {
    email?: string;
    username?: string;
    first_name?: string;
    last_name?: string;
}

/**
 * Password change request payload
 * Sent to /auth/change-password
 */
export interface ChangePasswordRequest {
    old_password: string;
    new_password: string;
}

/**
 * Generic success response for operations that don't return data
 */
export interface SuccessResponse {
    message: string;
}