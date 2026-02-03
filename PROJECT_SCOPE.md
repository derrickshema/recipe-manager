# Project Scope

## Overview

**Recipe Manager** is a multi-tenant restaurant management platform where restaurant owners can manage their menus and customers can browse and order food.

**Purpose:** Learning project to master production-ready web app development patterns.

---

## Core Features (MVP)

### ✅ Authentication & Authorization
- [x] User registration (customer, restaurant owner)
- [x] Login/logout with JWT + httpOnly cookies
- [x] Password hashing (bcrypt)
- [x] System roles (superadmin, restaurant_owner, customer)
- [x] Organization roles (restaurant_admin, employee)
- [x] RBAC middleware
- [x] Password reset via email (Resend)
- [x] Email verification on signup

### ✅ Multi-tenancy
- [x] Restaurant model with approval workflow
- [x] Membership model (user ↔ restaurant association)
- [x] Tenant-scoped data access
- [x] Restaurant owner registration flow

### ✅ Restaurant Management
- [x] Restaurant profile (name, address, phone, cuisine)
- [x] Approval status workflow (pending → approved/rejected)
- [x] Restaurant logo/photos (S3 upload)

### ✅ Admin Dashboard
- [x] System overview (stats)
- [x] Restaurant management (approve/reject/suspend)
- [x] User management (view, suspend, delete)
- [x] User deletion cascade (restaurants, memberships)

### ✅ Menu/Recipe Management
- [x] Recipe CRUD (create, read, update, delete)
- [x] Recipe fields (title, description, ingredients, instructions)
- [x] Recipe images (S3 upload with LocalStack)

### ✅ Staff Management
- [x] Invite employee by email
- [x] View staff members
- [x] Change employee role
- [x] Remove employee

### ✅ Customer Experience
- [x] Browse approved restaurants
- [x] View restaurant menu
- [x] Search restaurants (name, cuisine)
- [x] Filter restaurants

---

## Phase 2: Orders & Payments

### ✅ Order System
- [x] Create order (customer)
- [x] Order status workflow (pending → preparing → ready → completed)
- [x] View incoming orders (restaurant)
- [x] Update order status (restaurant)
- [x] Order history (customer & restaurant)
- [x] Real-time order updates (WebSockets)

### ✅ Payment Processing
- [x] Stripe Checkout integration
- [x] Payment confirmation webhook
- [x] Order marked as paid

---

## Phase 3: Notifications & Communication

### ✅ Email Notifications
- [x] Password reset email
- [x] Email verification on signup
- [x] Staff invitation email

---

## Phase 4: DevOps & Production

### ✅ Production Readiness
- [x] Health check endpoint
- [x] Environment variable validation (Pydantic Settings)

### ✅ Testing
- [x] Backend integration tests (pytest) - auth & order flows (19 tests)
- [~] E2E test (Playwright) - skipped (integration tests sufficient for learning)

### ✅ Containerization
- [x] Backend Dockerfile (multi-stage, Python 3.13-slim)
- [x] Frontend Dockerfile (multi-stage, Node 22)
- [x] docker-compose.yml (backend, frontend, postgres, localstack)
- [x] Docker Desktop installed
- [x] LocalStack container for S3 emulation

### ✅ Deployment (Skipped)
- [~] Deploy to Railway/Render - skipped (focus on building more apps)
- [x] App runs fully in Docker containers locally
- [x] Production-ready configuration (env validation, health checks)

---

## Out of Scope

These features are explicitly **not** planned:

- OAuth (Google/GitHub login)
- MFA/2FA
- Subscription billing
- Delivery logistics/tracking
- Reviews and ratings
- Loyalty programs
- Mobile apps (native)
- Multiple languages/i18n
- Advanced inventory management
- Reservation system
- Table management

---

## Tech Stack

| Layer | Technology |
|-------|------------|
| Frontend | SvelteKit, Tailwind CSS |
| Backend | FastAPI, SQLModel |
| Database | PostgreSQL |
| Auth | JWT, bcrypt, httpOnly cookies |
| File Storage | AWS S3 (LocalStack for dev) |
| Payments | Stripe |
| Email | Resend |
| Real-time | WebSockets |
| Containerization | Docker, Docker Compose |
| Hosting | Railway or Render |

---

## User Roles Summary

| Role | Description | Capabilities |
|------|-------------|--------------|
| **Superadmin** | System administrator | Approve restaurants, manage all users |
| **Restaurant Owner** | Owns a restaurant | Full restaurant management |
| **Employee** | Restaurant staff | View menu, manage orders |
| **Customer** | End user | Browse, order, track orders |

---

## Timeline Estimate

| Phase | Features | Duration |
|-------|----------|----------|
| MVP (Core) | Auth, Restaurants, Recipes | ✅ Done |
| Phase 2 | Orders, Payments, Real-time | ✅ Done |
| Phase 3 | Email Notifications | ✅ Done |
| Phase 4 | Docker, Testing | ✅ Done |

**Status:** ✅ Complete (local development)

---

## Success Criteria

The project is "complete" when:

1. ✅ A restaurant owner can register and manage their menu
2. ✅ A customer can browse restaurants and place an order
3. ✅ Payments are processed via Stripe
4. ✅ Order status updates in real-time
5. ✅ App runs in Docker containers
6. ✅ Integration tests pass (19 tests)
7. [~] Cloud deployment - skipped (learning goal achieved)

---

## Notes

*Add scope changes and decisions here:*

- **2026-01-26**: Initial scope document created
- **2026-01-26**: Implemented S3 image upload for recipes using LocalStack
- **2026-01-26**: Set up Docker Desktop and LocalStack container
- **2026-01-26**: Implemented password reset via email using Resend
- **2026-01-27**: Implemented email verification on signup
- **2026-01-27**: Added user management page (view, suspend, delete users)
- **2026-01-27**: Login now requires verified email (except superadmin)
- **2026-01-27**: Added restaurant logo upload feature (S3)
- **2026-02-02**: Moved enums (SystemRole, OrgRole, ApprovalStatus) to shared enums.py
- **2026-02-02**: Added unique constraint on Membership (user_id, restaurant_id)
- **2026-02-02**: Implemented staff management (invite by email, view, change role, remove)
- **2026-02-02**: Added staff invitation email with JWT tokens (7-day expiry)
- **2026-02-02**: Created accept-invitation page for invited users
- **2026-02-03**: Added health check endpoints (/health, /health/ready)
- **2026-02-03**: Centralized config with Pydantic Settings (environment validation)
- **2026-02-03**: Set up pytest with 19 integration tests (auth + orders)
- **2026-02-03**: Created Docker setup (backend + frontend Dockerfiles, docker-compose.yml)
- **2026-02-03**: 🎉 PROJECT COMPLETE - All core patterns learned, ready to build next app
