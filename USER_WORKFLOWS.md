# User Workflows

## Overview

This document defines the daily actions and workflows for each user type in the Recipe Manager system. Use this to guide feature development and prioritization.

---

## User Types

| Role | Description | Access Level |
|------|-------------|--------------|
| **Superadmin** | System administrator | Full system access |
| **Restaurant Owner** | Owns/manages a restaurant | Full restaurant access |
| **Employee** | Restaurant staff | Limited restaurant access |
| **Customer** | End user ordering food | Public + order access |

---

## 🔴 Superadmin Workflows

### Daily Tasks
- [ ] Review pending restaurant registrations
- [ ] Approve or reject new restaurants
- [ ] Handle support escalations
- [ ] Monitor system health

### Periodic Tasks
- [ ] Audit user accounts
- [ ] Review analytics/reports
- [ ] Manage system settings

### User Stories

```
As a Superadmin, I want to...

□ View all pending restaurant applications
□ Approve a restaurant application
□ Reject a restaurant application with a reason
□ Suspend a restaurant for policy violations
□ View all users in the system
□ Deactivate a user account
□ View system-wide analytics (total restaurants, users, orders)
□ Search for any restaurant or user
```

---

## 🟠 Restaurant Owner/Admin Workflows

### Daily Tasks
- [ ] Check incoming orders
- [ ] Update menu item availability
- [ ] View daily sales summary
- [ ] Respond to customer feedback

### Weekly Tasks
- [ ] Review sales analytics
- [ ] Update menu prices
- [ ] Add/remove menu items
- [ ] Manage staff schedules

### Onboarding (First Time)
- [ ] Complete registration
- [ ] Wait for approval
- [ ] Set up restaurant profile (hours, address, photos)
- [ ] Create initial menu
- [ ] Invite staff members

### User Stories

```
As a Restaurant Owner, I want to...

SETUP & PROFILE
□ Register my restaurant
□ Edit restaurant details (name, address, phone, hours)
□ Upload restaurant logo/photos
□ Set operating hours
□ Configure delivery zones (if applicable)

MENU MANAGEMENT
□ Create menu categories (Appetizers, Mains, Desserts)
□ Add a new recipe/menu item
□ Edit an existing recipe (name, price, description)
□ Upload a photo for a recipe
□ Mark an item as "sold out" temporarily
□ Delete a recipe
□ Reorder menu items
□ Set item availability by day/time

STAFF MANAGEMENT
□ Invite an employee by email
□ View all staff members
□ Change an employee's role
□ Remove an employee from my restaurant

ORDERS (Future)
□ View incoming orders in real-time
□ Accept an order
□ Mark an order as "preparing"
□ Mark an order as "ready for pickup/delivery"
□ Cancel an order with reason
□ View order history

ANALYTICS (Future)
□ View daily/weekly/monthly sales
□ See best-selling items
□ View peak hours
□ Export reports
```

---

## 🟢 Employee Workflows

### Daily Tasks
- [ ] Clock in/out
- [ ] View assigned orders
- [ ] Update order status
- [ ] Mark items as sold out

### User Stories

```
As an Employee, I want to...

□ View the restaurant's menu
□ Mark items as sold out
□ View incoming orders
□ Update order status (preparing → ready)
□ View my shift schedule (Future)
```

---

## 🔵 Customer Workflows

### Browsing (No Account)
- [ ] Browse restaurants
- [ ] View restaurant menus
- [ ] Search for restaurants by cuisine/location

### Ordering (Account Required)
- [ ] Register an account
- [ ] Log in
- [ ] Add items to cart
- [ ] Customize order (notes, modifications)
- [ ] Checkout and pay
- [ ] Track order status
- [ ] View order history
- [ ] Leave a review

### User Stories

```
As a Customer, I want to...

DISCOVERY
□ Browse all restaurants
□ Filter restaurants by cuisine type
□ Search restaurants by name
□ View a restaurant's menu
□ See item photos and descriptions
□ Check restaurant hours
□ See if a restaurant is currently open

ACCOUNT
□ Register with email/password
□ Register with Google (Future)
□ Log in
□ Reset my password
□ Update my profile
□ Save favorite restaurants

ORDERING (Future)
□ Add items to cart
□ Modify item (add notes, remove ingredients)
□ View cart
□ Remove items from cart
□ Apply a promo code
□ Choose pickup or delivery
□ Enter delivery address
□ Pay with card
□ Receive order confirmation
□ Track order status in real-time
□ View estimated ready/delivery time

POST-ORDER (Future)
□ View past orders
□ Reorder a previous order
□ Leave a rating/review
□ Report an issue with order
```

---

## Feature Priority Matrix

### Phase 1: Core (MVP) ✅
| Feature | Owner | Employee | Customer |
|---------|-------|----------|----------|
| Registration | ✅ | - | ⬜ |
| Login/Logout | ✅ | ✅ | ⬜ |
| Restaurant Profile | 🟡 | - | - |
| Menu CRUD | 🟡 | 👁️ | 👁️ |
| Staff Management | ⬜ | - | - |

### Phase 2: Orders
| Feature | Owner | Employee | Customer |
|---------|-------|----------|----------|
| View Orders | ⬜ | ⬜ | ⬜ |
| Create Order | - | - | ⬜ |
| Update Order Status | ⬜ | ⬜ | - |
| Order History | ⬜ | - | ⬜ |

### Phase 3: Payments & Notifications
| Feature | Owner | Employee | Customer |
|---------|-------|----------|----------|
| Stripe Integration | ⬜ | - | ⬜ |
| Email Notifications | ⬜ | ⬜ | ⬜ |
| Real-time Updates | ⬜ | ⬜ | ⬜ |

### Phase 4: Advanced
| Feature | Owner | Employee | Customer |
|---------|-------|----------|----------|
| Analytics Dashboard | ⬜ | - | - |
| Reviews/Ratings | ⬜ | - | ⬜ |
| Search (Elasticsearch) | - | - | ⬜ |
| Geolocation | - | - | ⬜ |

**Legend:** ✅ Done | 🟡 In Progress | ⬜ Not Started | 👁️ View Only | - Not Applicable

---

## Screen Map

```
PUBLIC
├── / (Landing page)
├── /login
├── /register
│   ├── /register/customer
│   └── /register/restaurant
│       └── /register/restaurant/business
└── /restaurants (browse - Future)
    └── /restaurants/[id] (menu view - Future)

CUSTOMER (authenticated)
├── /home (customer dashboard)
├── /cart (Future)
├── /checkout (Future)
├── /orders (Future)
│   └── /orders/[id]
└── /profile

RESTAURANT (authenticated)
├── /dashboard
├── /recipes
│   ├── /recipes/new
│   └── /recipes/[id]/edit
├── /staff
│   └── /staff/invite
├── /orders (Future)
│   └── /orders/[id]
├── /analytics (Future)
└── /settings

SUPERADMIN (authenticated)
├── /overview
├── /restaurants
│   └── /restaurants/[id]
└── /users (Future)
```

---

## Notes

*Add workflow discoveries and changes here:*

- **2026-01-21**: Initial workflow document created
