/**
 * Server-side API utilities for making authenticated requests to the backend.
 * These functions run ONLY on the server and can access httpOnly cookies.
 */

const API_BASE_URL = process.env.API_BASE_URL || 'http://localhost:8000';
import { error } from '@sveltejs/kit';
import type { Cookies } from '@sveltejs/kit';

export interface ServerFetchOptions {
    method?: 'GET' | 'POST' | 'PUT' | 'PATCH' | 'DELETE';
    body?: unknown;
    cookies: Cookies;
}

/**
 * Make an authenticated request to the backend API from the server.
 * Automatically includes the httpOnly cookie for authentication.
 */
export async function serverFetch<T>(
    path: string,
    options: ServerFetchOptions
): Promise<T> {
    const { method = 'GET', body, cookies } = options;
    
    const token = cookies.get('access_token');
    
    const headers: Record<string, string> = {
        'Content-Type': 'application/json',
    };
    
    // Forward the token in the cookie to the backend
    if (token) {
        headers['Cookie'] = `access_token=${token}`;
    }
    
    const response = await fetch(`${API_BASE_URL}${path}`, {
        method,
        headers,
        body: body ? JSON.stringify(body) : undefined,
    });
    
    if (!response.ok) {
        if (response.status === 401) {
            // Token is invalid or expired - clear the cookie
            cookies.delete('access_token', { path: '/' });
            throw error(401, 'Session expired. Please log in again.');
        }
        
        const errorData = await response.json().catch(() => ({ detail: response.statusText }));
        throw error(response.status, errorData.detail || `API Error: ${response.status}`);
    }
    
    // Handle empty responses
    const text = await response.text();
    if (!text) {
        return {} as T;
    }
    
    return JSON.parse(text) as T;
}

/**
 * Server-side API helper object for common HTTP methods
 */
export const serverApi = {
    get: <T>(path: string, cookies: Cookies) => 
        serverFetch<T>(path, { cookies }),
    
    post: <T>(path: string, body: unknown, cookies: Cookies) => 
        serverFetch<T>(path, { method: 'POST', body, cookies }),
    
    put: <T>(path: string, body: unknown, cookies: Cookies) => 
        serverFetch<T>(path, { method: 'PUT', body, cookies }),
    
    patch: <T>(path: string, body: unknown, cookies: Cookies) => 
        serverFetch<T>(path, { method: 'PATCH', body, cookies }),
    
    delete: <T>(path: string, cookies: Cookies) => 
        serverFetch<T>(path, { method: 'DELETE', cookies }),
};
