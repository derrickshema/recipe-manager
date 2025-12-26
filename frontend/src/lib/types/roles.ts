/**
 * System-wide roles that apply across the entire application
 */
export enum SystemRole {
    SUPERADMIN = "superadmin",
    CUSTOMER = "customer",
    RESTAURANT_OWNER = "restaurant_owner",
    SUSPENDED = "suspended"
}

/**
 * Organization-specific roles that apply within a specific restaurant
 */
export enum OrgRole {
    RESTAURANT_ADMIN = "restaurant_admin",
    EMPLOYEE = "employee"
}

// Type guard to check if a string is a valid SystemRole
export function isSystemRole(role: string): role is SystemRole {
    return Object.values(SystemRole).includes(role as SystemRole);
}

// Type guard to check if a string is a valid OrgRole
export function isOrgRole(role: string): role is OrgRole {
    return Object.values(OrgRole).includes(role as OrgRole);
}