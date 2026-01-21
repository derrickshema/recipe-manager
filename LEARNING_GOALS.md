# Learning Goals

## Overview

This project is a learning vehicle for building production-ready web applications. Below are the key concepts and technologies to master through building the Recipe Manager.

---

## Progress Legend

- ⬜ Not started
- 🟡 In progress
- ✅ Completed

---

## Core Infrastructure

| Topic | Status | Notes |
|-------|--------|-------|
| **Auth** (JWT, sessions, OAuth, MFA) | 🟡 | JWT + httpOnly cookies implemented |
| **Authorization** (RBAC) | 🟡 | System roles + org roles implemented |
| **Multitenancy** (Data isolation, tenant context) | 🟡 | Restaurant-based isolation via memberships |
| **SSR and CSR patterns** (When to use each, hydration) | 🟡 | SvelteKit form actions, server-side state |
| **Containerization** (Docker + Docker Compose + Networking) | ⬜ | |
| **CI/CD** (Automated testing, deployment, GitHub Actions) | ⬜ | |
| **Testing** (Unit, integration, E2E - pytest + Playwright) | ⬜ | |
| **Monitoring** (Sentry, structured logging) | ⬜ | |
| **Environmental configuration** (Secret management, env validation) | 🟡 | Using .env files |

---

## Universal Feature Modules

| Topic | Status | Notes |
|-------|--------|-------|
| **Status Workflow Engine** (State machine pattern) | ⬜ | Could apply to order status |
| **Payment Processing** (Stripe) | ⬜ | |
| **File Upload + Cloud Storage** (S3) | ⬜ | Recipe images |
| **Email Notifications** (SendGrid/Resend) | ⬜ | |
| **Scheduling/Calendar logic** | ⬜ | |

---

## Advanced Features

| Topic | Status | Notes |
|-------|--------|-------|
| **Real-time** (WebSockets) | ⬜ | Live order updates |
| **Background Jobs** (Celery/Redis) | ⬜ | |
| **Search** (Full-text, filters, Elasticsearch) | ⬜ | Recipe search |
| **Geolocation services** | ⬜ | Restaurant finder |

---

## Project-Specific Skills

| Topic | Status | Notes |
|-------|--------|-------|
| **FastAPI** | 🟡 | Routes, dependencies, validation |
| **SQLModel/SQLAlchemy** | 🟡 | Models, relationships, queries |
| **SvelteKit** | 🟡 | Pages, form actions, stores |
| **PostgreSQL** | 🟡 | Schema design, migrations (Alembic) |
| **Tailwind CSS** | 🟡 | Styling, theming |

---

## Implementation Checklist

### Auth & Authorization
- [x] Password hashing (bcrypt)
- [x] JWT token creation/validation
- [x] httpOnly cookie storage
- [x] System roles (superadmin, restaurant_owner, customer)
- [x] Organization roles (restaurant_admin, employee)
- [x] RBAC middleware/dependencies
- [ ] OAuth (Google, GitHub)
- [ ] MFA (TOTP)
- [ ] Password reset flow
- [ ] Email verification

### Multitenancy
- [x] Restaurant model
- [x] Membership model (user ↔ restaurant)
- [x] Tenant-scoped queries
- [ ] Tenant-aware middleware
- [ ] Data isolation tests

### Frontend Patterns
- [x] SSR form actions (registration)
- [x] Server-side cookie state
- [ ] Client-side state (when appropriate)
- [ ] Optimistic UI updates
- [ ] Error boundaries

### DevOps
- [ ] Dockerfile (backend)
- [ ] Dockerfile (frontend)
- [ ] docker-compose.yml
- [ ] GitHub Actions workflow
- [ ] Automated tests in CI
- [ ] Staging environment
- [ ] Production deployment

---

## Resources

| Topic | Resource |
|-------|----------|
| FastAPI | [fastapi.tiangolo.com](https://fastapi.tiangolo.com) |
| SQLModel | [sqlmodel.tiangolo.com](https://sqlmodel.tiangolo.com) |
| SvelteKit | [kit.svelte.dev](https://kit.svelte.dev) |
| JWT | [jwt.io](https://jwt.io) |
| RBAC | [auth0.com/docs/authorization](https://auth0.com/docs/manage-users/access-control/rbac) |
| Docker | [docs.docker.com](https://docs.docker.com) |
| GitHub Actions | [docs.github.com/actions](https://docs.github.com/en/actions) |

---

## Notes

*Add learnings, gotchas, and insights as you progress:*

- **2026-01-20**: Split auth utilities into `auth.py` (identity) and `rbac.py` (permissions)
- **2026-01-20**: Refactored multi-step registration from client store to server-side encrypted cookies
