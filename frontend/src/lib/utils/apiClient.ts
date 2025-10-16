import { goto } from '$app/navigation';
import { user, isAuthenticated } from '$lib/stores/authStore';

// API Configuration: ensures consistent settings for all requests
const API_CONFIG = {
    baseUrl: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000',
    defaultHeaders: {},
} as const;

// HTTP Methods type: used for type safety in requests
export type HttpMethod = 'GET' | 'POST' | 'PUT' | 'PATCH' | 'DELETE';

// Request configuration type: to define options for API requests and serve as request blueprint 
export interface RequestConfig<TBody = unknown> extends Omit<RequestInit, 'body' | 'method'> {
    auth?: boolean;
    data?: TBody;
    params?: Record<string, string>;
}

/**
 * Main API fetch function with improved type safety and error handling
 * @param path - The API endpoint path
 * @param method - HTTP method
 * @param config - Request configuration
 * @returns Promise with the Response object
 */
export async function apiFetch(
    path: string,
    method: HttpMethod,
    config: RequestConfig = {}
): Promise<Response> {
    const { data, params, ...customOptions } = config;

    // Construct URL with API base
    const url = new URL(`${API_CONFIG.baseUrl}${path}`);

    // Feature Use: Append URL query parameters from 'params'
    if (params) {
        Object.entries(params).forEach(([key, value]) => {
            url.searchParams.append(key, value);
        });
    }

    // Prepare headers: Start with defaults, then allow them to be overridden by customOptions.headers
    const headers = {
        ...API_CONFIG.defaultHeaders,
        // CRITICAL FIX: Add Content-Type here, allowing it to be overridden if needed
        'Content-Type': 'application/json', 
        ...customOptions.headers,
    };

    // Prepare body: stringify the data if it exists
    const body = (data && method !== 'GET') ? JSON.stringify(data) : undefined;
    
    // Final fetch configuration
    const fetchConfig: RequestInit = {
        method,
        headers,
        body,
        // Feature Use: Spread the rest of the RequestInit properties (cache, mode, etc.)
        ...customOptions,
    };

    // Make the request
    const response = await fetch(url.toString(), fetchConfig);

    // Handle authentication errors
    if (response.status === 401) {
        user.signOut();
        isAuthenticated.setFalse();
        goto('/login');
    }

    return response;
}

