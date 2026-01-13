# Database Schema

## Overview

The Recipe Manager uses PostgreSQL with SQLModel (SQLAlchemy + Pydantic) for ORM.

---

## Entity Relationship Diagram

```
┌─────────────────┐       ┌─────────────────┐       ┌─────────────────┐
│      User       │       │   Membership    │       │   Restaurant    │
├─────────────────┤       ├─────────────────┤       ├─────────────────┤
│ id (PK)         │──────<│ user_id (FK)    │>──────│ id (PK)         │
│ username        │       │ restaurant_id(FK│       │ restaurant_name │
│ email           │       │ role            │       │ created_at      │
│ hashed_password │       │ created_at      │       │ updated_at      │
│ first_name      │       └─────────────────┘       └────────┬────────┘
│ last_name       │                                          │
│ role (system)   │                                          │
│ created_at      │                                          │
│ updated_at      │                                          │
└─────────────────┘                                          │
                                                             │
                           ┌─────────────────┐               │
                           │     Recipe      │               │
                           ├─────────────────┤               │
                           │ id (PK)         │               │
                           │ restaurant_id(FK│───────────────┘
                           │ name            │
                           │ description     │
                           │ ingredients     │
                           │ instructions    │
                           │ prep_time       │
                           │ cook_time       │
                           │ servings        │
                           │ created_at      │
                           │ updated_at      │
                           └─────────────────┘
```

---

## Tables

### User

Stores all user accounts in the system.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | INTEGER | PK, AUTO | Unique identifier |
| `username` | VARCHAR(50) | UNIQUE, NOT NULL | Login username |
| `email` | VARCHAR(255) | UNIQUE, NOT NULL | Email address |
| `hashed_password` | VARCHAR(255) | NOT NULL | Bcrypt hashed password |
| `first_name` | VARCHAR(100) | | User's first name |
| `last_name` | VARCHAR(100) | | User's last name |
| `role` | ENUM | NOT NULL | System role (see below) |
| `created_at` | TIMESTAMP | DEFAULT NOW | Record creation time |
| `updated_at` | TIMESTAMP | ON UPDATE | Last modification time |

**System Roles:**
- `customer` - Regular customer user
- `restaurant_owner` - Owns one or more restaurants
- `superadmin` - System administrator

---

### Restaurant

Stores restaurant information.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | INTEGER | PK, AUTO | Unique identifier |
| `restaurant_name` | VARCHAR(255) | NOT NULL | Restaurant name |
| `cuisine_type` | VARCHAR(100) | | Type of cuisine |
| `address` | TEXT | | Physical address |
| `phone` | VARCHAR(20) | | Contact phone |
| `created_at` | TIMESTAMP | DEFAULT NOW | Record creation time |
| `updated_at` | TIMESTAMP | ON UPDATE | Last modification time |

---

### Membership

Junction table linking users to restaurants with roles.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | INTEGER | PK, AUTO | Unique identifier |
| `user_id` | INTEGER | FK → User.id | User reference |
| `restaurant_id` | INTEGER | FK → Restaurant.id | Restaurant reference |
| `role` | ENUM | NOT NULL | Organization role (see below) |
| `created_at` | TIMESTAMP | DEFAULT NOW | When user joined |

**Organization Roles:**
- `restaurant_admin` - Full restaurant management
- `chef` - Can manage recipes
- `staff` - Can view recipes

**Unique Constraint:** `(user_id, restaurant_id)` - User can only have one role per restaurant

---

### Recipe

Stores recipe information for restaurants.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | INTEGER | PK, AUTO | Unique identifier |
| `restaurant_id` | INTEGER | FK → Restaurant.id | Owner restaurant |
| `name` | VARCHAR(255) | NOT NULL | Recipe name |
| `description` | TEXT | | Recipe description |
| `ingredients` | JSON/TEXT | | List of ingredients |
| `instructions` | TEXT | | Cooking instructions |
| `prep_time` | INTEGER | | Prep time in minutes |
| `cook_time` | INTEGER | | Cook time in minutes |
| `servings` | INTEGER | | Number of servings |
| `created_at` | TIMESTAMP | DEFAULT NOW | Record creation time |
| `updated_at` | TIMESTAMP | ON UPDATE | Last modification time |

---

## Indexes

```sql
-- User lookups
CREATE INDEX idx_user_username ON user(username);
CREATE INDEX idx_user_email ON user(email);

-- Membership lookups
CREATE INDEX idx_membership_user ON membership(user_id);
CREATE INDEX idx_membership_restaurant ON membership(restaurant_id);

-- Recipe lookups
CREATE INDEX idx_recipe_restaurant ON recipe(restaurant_id);
```

---

## Migrations

Migrations are managed with **Alembic**.

### Location
```
backend/migrations/versions/
```

### Commands

```bash
# Create new migration
alembic revision --autogenerate -m "description"

# Apply all migrations
alembic upgrade head

# Rollback one migration
alembic downgrade -1

# Show current version
alembic current

# Show migration history
alembic history
```

### Migration History

| Version | Description | Date |
|---------|-------------|------|
| `9a5748f8e74f` | Initial migration | - |
| `48420f53b820` | DateTime objects in models | - |
| `90eedaf05f0f` | DateTime objects again | - |
| `83cd928ec422` | Changed role name | - |
| `ab712629b06e` | Changed role again | - |
| `0f3ee4a5926f` | Remove restaurant_id from user | - |
| `add_customer_role` | Add customer role | - |

---

## Sample Queries

### Get user with all restaurant memberships
```sql
SELECT u.*, m.role as org_role, r.restaurant_name
FROM user u
LEFT JOIN membership m ON u.id = m.user_id
LEFT JOIN restaurant r ON m.restaurant_id = r.id
WHERE u.id = 1;
```

### Get all recipes for a restaurant
```sql
SELECT * FROM recipe
WHERE restaurant_id = 1
ORDER BY created_at DESC;
```

### Get all staff for a restaurant
```sql
SELECT u.*, m.role as org_role
FROM user u
JOIN membership m ON u.id = m.user_id
WHERE m.restaurant_id = 1;
```

---

## Backup & Restore

### Backup
```bash
pg_dump -U postgres recipe_db > backup_$(date +%Y%m%d).sql
```

### Restore
```bash
psql -U postgres recipe_db < backup_20240115.sql
```

---

## Future Considerations

As the project grows, consider:

- [ ] **Orders table** - Customer orders
- [ ] **OrderItems table** - Items in an order
- [ ] **Categories table** - Recipe categories
- [ ] **Reviews table** - Customer reviews
- [ ] **Media table** - Recipe images
- [ ] **Audit log** - Track changes for compliance
