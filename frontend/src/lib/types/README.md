# Type System Documentation

This directory contains all TypeScript type definitions for the Recipe Manager application. These types follow the **Data Transfer Object (DTO)** pattern to ensure type safety across the entire application.

## Architecture

```
Components/Pages
      ↓
   Stores (State Management)
      ↓
   Services (Business Logic)
      ↓
   API Clients (HTTP)
      ↓
   Types (Shared Contracts)
```

## File Structure

### `auth.ts`
Authentication-related types for user management and registration flows.

**Key Types:**
- `AuthUser` - Authenticated user profile
- `LoginRequest` / `LoginResponse` - Login flow
- `RegisterCustomerRequest` - Customer registration
- `RegisterRestaurantOwnerRequest` - Restaurant owner registration (multi-step)
- `UpdateProfileRequest` - Profile updates
- `ChangePasswordRequest` - Password changes

### `recipe.ts`
Recipe entity and CRUD operation types.

**Key Types:**
- `Recipe` - Complete recipe entity
- `RecipeCreateRequest` - Recipe creation payload
- `RecipeUpdateRequest` - Recipe update payload (all fields optional)
- `RecipeListResponse` - List endpoint response

### `restaurant.ts`
Restaurant entity and membership management types.

**Key Types:**
- `Restaurant` - Complete restaurant entity
- `RestaurantCreateRequest` - Restaurant creation payload
- `RestaurantUpdateRequest` - Restaurant update payload
- `Membership` - User-restaurant relationship
- `AddMemberRequest` - Add member to restaurant
- `UpdateMembershipRequest` - Change member role
- `OrgRole` - Organization roles (RESTAURANT_ADMIN, EMPLOYEE, VIEWER)

### `roles.ts`
System-wide and organization-specific role definitions.

**Key Enums:**
- `SystemRole` - SUPERADMIN, CUSTOMER, USER, SUSPENDED
- `OrgRole` - RESTAURANT_ADMIN, EMPLOYEE, VIEWER

### `index.ts`
Central export file for convenient imports.

## Usage Examples

### Import from index (recommended)
```typescript
import type { LoginRequest, Recipe, Restaurant } from '$lib/types';
```

### Using in API clients
```typescript
import type { LoginRequest, LoginResponse } from '$lib/types';

export const authApi = {
    login: async (credentials: LoginRequest): Promise<LoginResponse> => {
        return api.post<LoginResponse>('/auth/token', credentials);
    }
};
```

### Using in services
```typescript
import type { RegisterCustomerRequest, AuthUser } from '$lib/types';

export const authService = {
    async register(data: RegisterCustomerRequest): Promise<AuthUser> {
        await authApi.register(data);
        return this.login({ username: data.username, password: data.password });
    }
};
```

### Using in stores
```typescript
import type { LoginRequest } from '$lib/types';

async login(credentials: LoginRequest) {
    return handleAsyncStore(
        { subscribe, set, update },
        async () => {
            const userProfile = await authService.login(credentials);
            update(state => ({ ...state, user: userProfile }));
            return userProfile;
        }
    );
}
```

### Using in components
```typescript
<script lang="ts">
    import type { LoginRequest } from '$lib/types';
    import { authStore } from '$lib/stores/authStore';

    let credentials: LoginRequest = {
        username: '',
        password: ''
    };

    async function handleLogin() {
        await authStore.login(credentials);
    }
</script>
```

## Benefits

✅ **Type Safety** - Catch errors at compile time, not runtime  
✅ **Self-Documenting** - Clear API contracts with JSDoc annotations  
✅ **Maintainability** - Change once, update everywhere via TypeScript errors  
✅ **IDE Intelligence** - Better autocomplete and inline documentation  
✅ **Validation Ready** - Easy to pair with runtime validators (Zod, Yup, etc.)  
✅ **Refactoring Confidence** - TypeScript shows all affected code

## Naming Conventions

- **Entities**: `Recipe`, `Restaurant`, `AuthUser`
- **Request DTOs**: `*Request` (e.g., `LoginRequest`, `RecipeCreateRequest`)
- **Response DTOs**: `*Response` (e.g., `LoginResponse`, `RecipeListResponse`)
- **Enums**: PascalCase (e.g., `SystemRole`, `OrgRole`)

## Best Practices

1. **Always use explicit types** - Don't rely on `any` or implicit types
2. **Import from index.ts** - Cleaner imports, easier refactoring
3. **Add JSDoc comments** - Helps other developers understand the types
4. **Use optional fields sparingly** - Only when truly optional in the API
5. **Keep Request/Response separate** - Even if similar, maintain clarity
6. **Follow DRY with type aliases** - `RecipeCreate` = `RecipeCreateRequest` for backward compatibility

## Migration Notes

**Backward Compatibility:**
Type aliases maintain compatibility with older code:
- `RecipeCreate` → `RecipeCreateRequest`
- `RecipeUpdate` → `RecipeUpdateRequest`
- `RestaurantCreate` → `RestaurantCreateRequest`
- `RestaurantUpdate` → `RestaurantUpdateRequest`

Gradually migrate to the `*Request` naming for consistency.
