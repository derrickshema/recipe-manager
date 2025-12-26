import { goto } from '$app/navigation';

// API Configuration: ensures consistent settings for all requests
const API_CONFIG = {
    baseUrl: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000',
    defaultHeaders: {},
} as const;

// HTTP Methods type: used for type safety in requests
export type HttpMethod = 'GET' | 'POST' | 'PUT' | 'PATCH' | 'DELETE';

// Request configuration type: to define options for API requests and serve as request blueprint 
export interface RequestConfig<TBody = unknown> extends Omit<RequestInit, 'body' | 'method' | 'headers'> {
    auth?: boolean;
    data?: TBody;
    params?: Record<string, string>;
    headers?: Record<string, string>; // Custom headers to merge with defaults
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
    const { data, params, headers: customHeaders, ...customOptions } = config;

    // Construct URL with API base: new URL is a standard safe way to build URLs
    const url = new URL(`${API_CONFIG.baseUrl}${path}`);

    // Feature Use: Append URL query parameters from 'params'
    if (params) {
        Object.entries(params).forEach(([key, value]) => {
            url.searchParams.append(key, value);
        });
    }

    // Prepare headers: Start with defaults, then allow them to be overridden by customHeaders
    const headers = {
        ...API_CONFIG.defaultHeaders,
        'Content-Type': 'application/json', 
        ...customHeaders,
    } as Record<string, string>;

    // Add Authorization header if token exists and auth is not explicitly disabled
    const shouldIncludeAuth = config.auth !== false; // Default to true
    if (shouldIncludeAuth && typeof window !== 'undefined' && typeof localStorage !== 'undefined') {
        const token = localStorage.getItem('access_token');
        if (token) {
            headers['Authorization'] = `Bearer ${token}`;
        }
    }

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
        // Clear token and redirect to login
        if (typeof localStorage !== 'undefined') {
            localStorage.removeItem('access_token');
        }
        goto('/login');
        throw new Error('Unauthorized - redirecting to login');
    }

    // Handle other HTTP errors
    if (!response.ok) {
        const errorData = await response.json().catch(() => ({ detail: response.statusText }));
        const error = new Error(errorData.detail || `HTTP ${response.status}: ${response.statusText}`);
        (error as any).status = response.status;
        (error as any).data = errorData;
        throw error;
    }

    return response;
}

