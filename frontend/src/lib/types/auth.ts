import type { SystemRole } from './roles';

export interface AuthUser {
    id: string;
    email: string;
    first_name: string;
    last_name: string;
    role: SystemRole;
    restaurant_id?: string;
    isAuthenticated: boolean;
}

/**
 * Data required for user login
 */
export interface UserLogin {
    username: string;
    password: string;
}

/**
 * Data required for user registration
 */
export interface UserRegister {
    username: string;
    email: string;
    password: string;
    first_name: string;
    last_name: string;
    role?: SystemRole;          // Optional: defaults to SystemRole.USER
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