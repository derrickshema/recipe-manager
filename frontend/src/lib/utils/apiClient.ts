import { goto } from '$app/navigation';

/**
 * API Configuration
 * 
 * NOTE: With httpOnly cookie auth, authenticated API calls should go through
 * SvelteKit server load functions which can access the cookie.
 * 
 * This client is now primarily for:
 * - Public API endpoints (no auth required)
 * - Server-side usage where cookies are forwarded
 */
const API_CONFIG = {
    baseUrl: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000',
    defaultHeaders: {},
} as const;

// HTTP Methods type: used for type safety in requests
export type HttpMethod = 'GET' | 'POST' | 'PUT' | 'PATCH' | 'DELETE';

// Request configuration type
export interface RequestConfig<TBody = unknown> extends Omit<RequestInit, 'body' | 'method' | 'headers'> {
    auth?: boolean;
    data?: TBody;
    params?: Record<string, string>;
    headers?: Record<string, string>;
}

/**
 * Main API fetch function
 * 
 * For authenticated requests, use server load functions instead.
 * This function is for public endpoints or when you explicitly pass credentials.
 */
export async function apiFetch(
    path: string,
    method: HttpMethod,
    config: RequestConfig = {}
): Promise<Response> {
    const { data, params, headers: customHeaders, ...customOptions } = config;

    // Construct URL with API base
    const url = new URL(`${API_CONFIG.baseUrl}${path}`);

    // Append URL query parameters
    if (params) {
        Object.entries(params).forEach(([key, value]) => {
            url.searchParams.append(key, value);
        });
    }

    // Prepare headers
    const headers = {
        ...API_CONFIG.defaultHeaders,
        'Content-Type': 'application/json', 
        ...customHeaders,
    } as Record<string, string>;

    // Note: We no longer add Authorization header from localStorage
    // Authenticated requests should use server-side API proxy with httpOnly cookies

    // Prepare body
    const body = (data && method !== 'GET') ? JSON.stringify(data) : undefined;
    
    // Include credentials for cookie-based auth
    const fetchConfig: RequestInit = {
        method,
        headers,
        body,
        credentials: 'include', // Important: sends cookies with cross-origin requests
        ...customOptions,
    };

    const response = await fetch(url.toString(), fetchConfig);

    // Handle authentication errors
    if (response.status === 401) {
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

