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

### 🟡 Restaurant Management
- [x] Restaurant profile (name, address, phone, cuisine)
- [x] Approval status workflow (pending → approved/rejected)
- [ ] Restaurant logo/photos (S3 - infrastructure ready)

### 🟡 Admin Dashboard
- [x] System overview (stats)
- [x] Restaurant management (approve/reject/suspend)
- [x] User management (view, suspend, delete)
- [ ] User deletion cascade (restaurants, memberships)

### 🟡 Menu/Recipe Management
- [x] Recipe CRUD (create, read, update, delete)
- [x] Recipe fields (title, description, ingredients, instructions)
- [x] Recipe images (S3 upload with LocalStack)
- [ ] Menu categories
- [ ] Item availability toggle (sold out)

### ⬜ Staff Management
- [ ] Invite employee by email
- [ ] View staff members
- [ ] Change employee role
- [ ] Remove employee

### ⬜ Customer Experience
- [x] Browse approved restaurants
- [ ] View restaurant menu
- [ ] Search restaurants (name, cuisine)
- [ ] Filter restaurants

---

## Phase 2: Orders & Payments

### ⬜ Order System
- [ ] Create order (customer)
- [ ] Order status workflow (pending → preparing → ready → completed)
- [ ] View incoming orders (restaurant)
- [ ] Update order status (restaurant)
- [ ] Order history (customer & restaurant)
- [ ] Real-time order updates (WebSockets)

### ⬜ Payment Processing
- [ ] Stripe Checkout integration
- [ ] Payment confirmation webhook
- [ ] Order marked as paid

---

## Phase 3: Notifications & Communication

### 🟡 Email Notifications
- [ ] Welcome email on registration
- [x] Password reset email
- [x] Email verification on signup
- [ ] Order confirmation email
- [ ] Order status update emails
- [ ] Restaurant approval/rejection email

---

## Phase 4: DevOps & Production

### 🟡 Containerization
- [ ] Backend Dockerfile
- [ ] Frontend Dockerfile
- [ ] docker-compose.yml for local dev
- [x] Docker Desktop installed
- [x] LocalStack container for S3 emulation

### ⬜ CI/CD
- [ ] GitHub Actions workflow
- [ ] Automated tests on PR
- [ ] Automated deployment on merge

### ⬜ Testing
- [ ] Backend unit tests (pytest)
- [ ] API integration tests
- [ ] Frontend E2E tests (Playwright)
- [ ] Auth flow tests
- [ ] Order flow tests

### ⬜ Monitoring & Logging
- [ ] Sentry error tracking
- [ ] Structured logging
- [ ] Health check endpoint

### ⬜ Environment Configuration
- [ ] Environment variable validation
- [ ] Secrets management
- [ ] Production config

---

## Advanced Features (Future)

### ⬜ Search
- [ ] Full-text search (PostgreSQL)
- [ ] Search by restaurant name
- [ ] Filter by cuisine type
- [ ] Elasticsearch (if needed)

### ⬜ Geolocation
- [ ] Restaurant location (lat/lng)
- [ ] Distance-based filtering
- [ ] "Near me" search

### ⬜ Background Jobs
- [ ] Celery + Redis setup
- [ ] Email sending queue
- [ ] Order processing queue

### ⬜ Analytics (Nice-to-have)
- [ ] Daily/weekly sales
- [ ] Popular items
- [ ] Peak hours

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
| File Storage | AWS S3 |
| Payments | Stripe |
| Email | SendGrid/Resend |
| Real-time | WebSockets |
| Background Jobs | Celery + Redis |
| Containerization | Docker, Docker Compose |
| CI/CD | GitHub Actions |
| Monitoring | Sentry |
| Hosting | TBD (Railway, Render, or AWS) |

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
| Phase 2 | Orders, Payments, Real-time | ~2 weeks |
| Phase 3 | Email Notifications | ~1 week |
| Phase 4 | Docker, CI/CD, Testing | ~2 weeks |
| Advanced | Search, Background Jobs | ~1 week |

**Total:** ~6-8 weeks from current state

---

## Success Criteria

The project is "complete" when:

1. ✅ A restaurant owner can register and manage their menu
2. ⬜ A customer can browse restaurants and place an order
3. ⬜ Payments are processed via Stripe
4. ⬜ Order status updates in real-time
5. ⬜ Email notifications are sent
6. ⬜ App is containerized and deployed
7. ⬜ CI/CD pipeline runs tests automatically
8. ⬜ Errors are tracked in Sentry

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
