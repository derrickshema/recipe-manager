/**
 * Central export for all type definitions
 * Import from here instead of individual files for convenience
 * 
 * @example
 * import type { LoginRequest, Recipe, Restaurant } from '$lib/types';
 */

// ==================== Authentication Types ====================
export type {
    UserProfile,
    AuthUser,
    LoginRequest,
    LoginResponse,
    RegisterCustomerRequest,
    RegisterRestaurantOwnerRequest,
    RegisterResponse,
    UpdateProfileRequest,
    ChangePasswordRequest,
    SuccessResponse
} from './auth';

// ==================== Recipe Types ====================
export type {
    Recipe,
    RecipeCreateRequest,
    RecipeUpdateRequest,
    RecipeListResponse,
    RecipeCreate,
    RecipeUpdate
} from './recipe';

// ==================== Restaurant Types ====================
export type {
    Restaurant,
    RestaurantCreateRequest,
    RestaurantUpdateRequest,
    RestaurantListResponse,
    Membership,
    AddMemberRequest,
    UpdateMembershipRequest,
    MembershipResponse,
    RestaurantCreate,
    RestaurantUpdate,
} from './restaurant';
export { ApprovalStatus } from './restaurant';

// ==================== Role Types ====================
export { SystemRole, OrgRole } from './roles';

// ==================== Order Types ====================
export type {
    Order,
    OrderItem,
    OrderItemCreate,
    OrderCreateRequest,
    OrderUpdateRequest
} from './order';
export { OrderStatus } from './order';
