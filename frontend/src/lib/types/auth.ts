import type { SystemRole, OrgRole } from './roles';

export interface AuthUser {
    id: string;
    email: string;
    username: string;
    first_name: string;
    last_name: string;
    role?: SystemRole; // Optional: defaults to SystemRole.USER
    org_role?: OrgRole;
    restaurant_id?: string;
    isAuthenticated: boolean;
}

export interface LoginCredentials {
    email: string;
    password: string;
}

export interface RegisterData {
    email: string;
    username: string;
    password: string;
    first_name: string;
    last_name: string;
}

/**
 * Response from the login endpoint
 */
export interface LoginResponse {
    access_token: string;
    token_type: string;
    user: AuthUser;
}

/**
 * Response from the registration endpoint
 */
export interface RegisterResponse {
    user: AuthUser;
}