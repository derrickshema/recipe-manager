# SSR + CSR Hybrid Authentication Architecture

## Overview

This document describes the secure authentication architecture implemented for the Recipe Manager application, combining the benefits of Server-Side Rendering (SSR) and Client-Side Rendering (CSR) while minimizing security vulnerabilities.

## Security Model

### Authentication Token Storage

| Storage Method | What Goes Here | Why |
|----------------|----------------|-----|
| **httpOnly Cookie** | JWT access token | XSS attacks cannot read it; CSRF mitigated by SameSite |
| **Svelte Stores** | User profile data (no secrets) | Fast UI reactivity |
| **localStorage** | Shopping cart, preferences | Non-sensitive convenience data |

### Cookie Configuration

```python
# Backend (FastAPI)
COOKIE_NAME = "access_token"
COOKIE_MAX_AGE = 60 * 60 * 24 * 7  # 7 days
COOKIE_HTTPONLY = True            # Prevents JavaScript access
COOKIE_SECURE = True              # HTTPS only in production
COOKIE_SAMESITE = "lax"           # Prevents CSRF on cross-site requests
```

## Request Flows

### Login Flow

```
1. User submits login form
2. SvelteKit form action (server-side) receives credentials
3. Server makes request to backend /auth/token
4. Backend validates, returns user data + sets httpOnly cookie
5. SvelteKit forwards cookie to browser
6. Client hydrates authStore with user data (NOT the token)
7. Redirect to appropriate dashboard
```

### Authenticated Request Flow

```
1. User navigates to protected route
2. hooks.server.ts checks for cookie presence
3. +layout.server.ts fetches user profile via cookie
4. Page receives user data via SSR
5. Fast CSR navigation uses cached data
```

### Logout Flow

```
1. User clicks logout (form action)
2. SvelteKit server clears httpOnly cookie
3. Backend /auth/logout called (optional)
4. Client authStore reset
5. Redirect to login
```

## File Structure

### Backend Changes

- `app/routes/auth_routes.py` - Sets httpOnly cookie on login, logout endpoint
- `app/utilities/users_utils.py` - Reads token from cookie OR header

### Frontend Changes

#### Server-Side Files

- `src/routes/+layout.server.ts` - Root layout fetches user on every request
- `src/routes/(auth)/login/+page.server.ts` - Login form action
- `src/routes/(auth)/logout/+page.server.ts` - Logout form action
- `src/routes/(auth)/register/customer/+page.server.ts` - Registration action
- `src/routes/(auth)/register/restaurant/business/+page.server.ts` - Restaurant registration
- `src/routes/(restaurant)/+layout.server.ts` - Role-based access
- `src/routes/(customer)/+layout.server.ts` - Role-based access
- `src/routes/(system)/+layout.server.ts` - Admin access
- `src/lib/server/api.ts` - Server-side API helper

#### Client-Side Files

- `src/lib/stores/authStore.ts` - Simplified store (no localStorage)
- `src/lib/services/authService.ts` - Minimal client utilities
- `src/lib/utils/apiClient.ts` - Updated for cookie-based auth
- `src/hooks.server.ts` - Auth guard middleware

## Security Benefits

### Protected Against

1. **XSS Token Theft** - Token in httpOnly cookie, inaccessible to JavaScript
2. **CSRF Attacks** - SameSite=Lax cookie + form actions
3. **Token Exposure** - Token never in browser JS, localStorage, or URLs

### Best Practices Implemented

- Server-side authentication validation
- Progressive enhancement with form actions
- Role-based route protection
- Automatic token refresh capability (can be added)
- Secure cookie attributes

## Development Notes

### Environment Variables

```bash
# .env (frontend)
API_BASE_URL=http://localhost:8000  # Server-side only
VITE_API_BASE_URL=http://localhost:8000  # Client-side (public endpoints only)

# .env (backend)
SECRET_KEY=your-secret-key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
ENVIRONMENT=development  # or "production" for secure cookies
```

### Testing Authentication

1. Start backend: `cd backend && uvicorn app.main:app --reload`
2. Start frontend: `cd frontend && pnpm dev`
3. Register a new user or login
4. Check browser DevTools → Application → Cookies for `access_token` (httpOnly)
5. Note: You cannot read this cookie via JavaScript (intentional!)

## Migration Notes

If migrating from localStorage-based auth:

1. Clear any existing `access_token` from localStorage
2. The new cookie-based auth will take over
3. Users will need to log in again (one-time)
