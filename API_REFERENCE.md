# API Reference

## Base URL

- **Development**: `http://localhost:8000`
- **Production**: `https://api.your-domain.com`

## Authentication

All authenticated endpoints require an `access_token` cookie (httpOnly) set by the login endpoint.

---

## Auth Endpoints

### POST `/auth/token`
Login and receive authentication cookie.

**Request Body:**
```json
{
  "username": "string",
  "password": "string"
}
```

**Response (200):**
```json
{
  "id": 1,
  "username": "johndoe",
  "email": "john@example.com",
  "first_name": "John",
  "last_name": "Doe",
  "role": "customer",
  "message": "Login successful"
}
```

**Cookie Set:** `access_token` (httpOnly, Secure, SameSite=Lax)

---

### POST `/auth/logout`
Clear authentication cookie.

**Response (200):**
```json
{
  "message": "Logged out successfully"
}
```

---

### POST `/auth/register`
Register a new customer user.

**Request Body:**
```json
{
  "username": "string",
  "email": "string",
  "password": "string",
  "first_name": "string",
  "last_name": "string"
}
```

**Response (201):**
```json
{
  "id": 1,
  "username": "johndoe",
  "email": "john@example.com",
  "first_name": "John",
  "last_name": "Doe",
  "role": "customer"
}
```

---

### POST `/auth/register/restaurant-owner`
Register a new restaurant owner with restaurant.

**Request Body:**
```json
{
  "username": "string",
  "email": "string",
  "password": "string",
  "first_name": "string",
  "last_name": "string",
  "phone_number": "string (optional)",
  "restaurant_name": "string",
  "cuisine_type": "string (optional)",
  "address": "string (optional)",
  "restaurant_phone": "string (optional)"
}
```

**Response (201):** User object with `role: "restaurant_owner"`

---

### GET `/auth/me`
Get current authenticated user profile.

**Auth Required:** Yes

**Response (200):**
```json
{
  "id": 1,
  "username": "johndoe",
  "email": "john@example.com",
  "first_name": "John",
  "last_name": "Doe",
  "role": "customer"
}
```

---

## Restaurant Endpoints

### GET `/restaurants`
List all restaurants.

**Auth Required:** No

**Query Parameters:**
- `skip` (int): Pagination offset (default: 0)
- `limit` (int): Max results (default: 100)

---

### GET `/restaurants/{restaurant_id}`
Get restaurant details.

---

### POST `/restaurants`
Create a new restaurant.

**Auth Required:** Yes (restaurant_owner or superadmin)

---

## Recipe Endpoints

### GET `/restaurants/{restaurant_id}/recipes`
List recipes for a restaurant.

### POST `/restaurants/{restaurant_id}/recipes`
Create a new recipe.

**Auth Required:** Yes (restaurant staff)

### GET `/recipes/{recipe_id}`
Get recipe details.

### PUT `/recipes/{recipe_id}`
Update a recipe.

**Auth Required:** Yes (recipe owner or admin)

### DELETE `/recipes/{recipe_id}`
Delete a recipe.

**Auth Required:** Yes (recipe owner or admin)

---

## Error Responses

### 400 Bad Request
```json
{
  "detail": "Description of validation error"
}
```

### 401 Unauthorized
```json
{
  "detail": "Not authenticated"
}
```

### 403 Forbidden
```json
{
  "detail": "Forbidden"
}
```

### 404 Not Found
```json
{
  "detail": "Resource not found"
}
```

---

## User Roles

| Role | System Access |
|------|---------------|
| `customer` | Browse restaurants, place orders |
| `restaurant_owner` | Manage own restaurants and staff |
| `superadmin` | Full system access |

## Organization Roles (within a restaurant)

| Role | Restaurant Access |
|------|-------------------|
| `restaurant_admin` | Full restaurant management |
| `chef` | Manage recipes |
| `staff` | View recipes |
