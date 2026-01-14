import { goto } from '$app/navigation';

/**
 * ============================================================================
 * CLIENT-SIDE API CLIENT
 * ============================================================================
 * 
 * IMPORTANT: This file is for CLIENT-SIDE (browser) API calls ONLY.
 * 
 * ┌─────────────────────────────────────────────────────────────────────────┐
 * │  WHEN TO USE THIS vs SERVER-SIDE FETCH                                  │
 * ├─────────────────────────────────────────────────────────────────────────┤
 * │  USE SERVER-SIDE (src/lib/server/api.ts + form actions):                │
 * │    ✅ Initial page data loading (SSR)                                   │
 * │    ✅ CRUD operations (create, update, delete)                          │
 * │    ✅ Any authenticated API call that can use form actions              │
 * │    ✅ Data that should be SEO-indexed                                   │
 * │                                                                         │
 * │  USE THIS CLIENT-SIDE API (this file):                                  │
 * │    ✅ Real-time search with debouncing                                  │
 * │    ✅ Autocomplete/typeahead features                                   │
 * │    ✅ Interactive filtering without page reload                         │
 * │    ✅ File uploads with progress tracking                               │
 * │    ✅ WebSocket fallback polling                                        │
 * │    ✅ Client-only features (shopping cart sync, etc.)                   │
 * └─────────────────────────────────────────────────────────────────────────┘
 * 
 * The httpOnly cookie is automatically sent with requests (credentials: 'include').
 * This means authenticated requests work here too, but prefer SSR when possible.
 */

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

// ============================================================================
// TYPES
// ============================================================================

export type HttpMethod = 'GET' | 'POST' | 'PUT' | 'PATCH' | 'DELETE';

export interface RequestConfig<TBody = unknown> {
    data?: TBody;
    params?: Record<string, string>;
    headers?: Record<string, string>;
    signal?: AbortSignal; // For cancellable requests (search debouncing)
}

export interface ApiError extends Error {
    status: number;
    data?: unknown;
}

// ============================================================================
// CORE FETCH FUNCTION
// ============================================================================

/**
 * Low-level fetch wrapper for client-side API calls.
 * Prefer using the `api` helper object below for convenience.
 */
export async function apiFetch<T = unknown>(
    path: string,
    method: HttpMethod,
    config: RequestConfig = {}
): Promise<T> {
    const { data, params, headers: customHeaders, signal } = config;

    // Build URL with query parameters
    const url = new URL(`${API_BASE_URL}${path}`);
    if (params) {
        Object.entries(params).forEach(([key, value]) => {
            url.searchParams.append(key, value);
        });
    }

    // Prepare request
    const response = await fetch(url.toString(), {
        method,
        headers: {
            'Content-Type': 'application/json',
            ...customHeaders,
        },
        body: data && method !== 'GET' ? JSON.stringify(data) : undefined,
        credentials: 'include', // Sends httpOnly cookie automatically
        signal,
    });

    // Handle 401 - redirect to login
    if (response.status === 401) {
        goto('/login');
        throw createApiError('Unauthorized - redirecting to login', 401);
    }

    // Handle errors
    if (!response.ok) {
        const errorData = await response.json().catch(() => ({ detail: response.statusText }));
        throw createApiError(
            errorData.detail || `HTTP ${response.status}: ${response.statusText}`,
            response.status,
            errorData
        );
    }

    // Handle empty responses (204 No Content)
    if (response.status === 204) {
        return null as T;
    }

    return response.json() as Promise<T>;
}

function createApiError(message: string, status: number, data?: unknown): ApiError {
    const error = new Error(message) as ApiError;
    error.status = status;
    error.data = data;
    return error;
}

// ============================================================================
// CONVENIENCE API OBJECT
// ============================================================================

/**
 * Convenient API helper with typed methods.
 * 
 * @example
 * // Search with debouncing (client-side only feature)
 * const results = await api.get<SearchResult[]>('/recipes/search', {
 *     params: { q: searchTerm },
 *     signal: abortController.signal
 * });
 * 
 * @example
 * // File upload with progress (not shown here, but you could extend this)
 * const uploaded = await api.post<FileResponse>('/files/upload', formData);
 */
export const api = {
    get: <T>(path: string, config?: RequestConfig) => 
        apiFetch<T>(path, 'GET', config),
    
    post: <T>(path: string, data?: unknown, config?: RequestConfig) => 
        apiFetch<T>(path, 'POST', { ...config, data }),
    
    put: <T>(path: string, data?: unknown, config?: RequestConfig) => 
        apiFetch<T>(path, 'PUT', { ...config, data }),
    
    patch: <T>(path: string, data?: unknown, config?: RequestConfig) => 
        apiFetch<T>(path, 'PATCH', { ...config, data }),
    
    delete: <T>(path: string, config?: RequestConfig) => 
        apiFetch<T>(path, 'DELETE', config),
} as const;
