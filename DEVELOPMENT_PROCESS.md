# Web App Development Process

A repeatable workflow for building web applications from scratch.

---

## Overview

```
Phase 0: Discovery     →  Understand the problem (1-2 days)
Phase 1: Design        →  Plan on paper, not code (1-3 days)
Phase 2: Foundation    →  Build the skeleton (3-5 days)
Phase 3: Core Features →  Build MVP features (1-2 weeks)
Phase 4: Polish        →  Make it production-ready (3-5 days)
Phase 5: Testing       →  Verify it works (ongoing)
Phase 6: Deployment    →  Ship it (1-2 days)
```

---

## Phase 0: Discovery (1-2 days)

**Goal:** Understand what you're building before writing code.

### Steps

| Step | Output |
|------|--------|
| Define the problem | One sentence: "This app helps [who] do [what]" |
| List user types | Who uses this? (e.g., admin, owner, customer) |
| Write user stories | "As a [role], I want to [action] so that [benefit]" |
| Identify MVP | What's the minimum to be useful? |

### Example
> "This app helps restaurant owners manage their menus and customers order food."

### Deliverables
- [ ] Problem statement
- [ ] User types list
- [ ] User stories document
- [ ] MVP feature list

---

## Phase 1: Design (1-3 days)

**Goal:** Make decisions on paper, not in code.

### 1.1 Data Modeling

```
1. List all "nouns" (User, Restaurant, Recipe, Order)
2. Define relationships (User has many Restaurants through Membership)
3. Draw an ERD diagram
4. Define fields for each model
```

**Questions to answer:**
- What are the main entities?
- How do they relate to each other?
- What fields does each need?
- What are the constraints (unique, required, etc.)?

### 1.2 Screen Mapping

```
1. List all screens needed
2. Group by user type
3. Define URL structure
4. Sketch wireframes (even rough boxes)
```

**Example structure:**
```
PUBLIC
├── / (Landing)
├── /login
└── /register

AUTHENTICATED
├── /dashboard
├── /[resource]
│   ├── /[resource]/new
│   └── /[resource]/[id]/edit
└── /settings
```

### 1.3 Tech Stack Decision

| Layer | Options | Considerations |
|-------|---------|----------------|
| Frontend | SvelteKit, Next.js, Nuxt | SSR needs? Team familiarity? |
| Backend | FastAPI, Django, Express | Python vs JS? ORM preference? |
| Database | PostgreSQL, MySQL, MongoDB | Relational vs document? |
| Auth | JWT, Sessions, OAuth | Stateless vs stateful? |
| Hosting | Vercel, Railway, AWS | Budget? Complexity tolerance? |

### Deliverables
- [ ] DATABASE_SCHEMA.md (ERD + field definitions)
- [ ] USER_WORKFLOWS.md (screens + user stories)
- [ ] Tech stack documented

---

## Phase 2: Foundation (3-5 days)

**Goal:** Build the skeleton before features.

### 2.1 Project Setup

```bash
# Backend checklist
□ Create project structure
□ Configure database connection
□ Set up migrations (Alembic)
□ Create base models
□ Test: Can I connect to DB?

# Frontend checklist
□ Create project structure
□ Configure CSS (Tailwind)
□ Create base layout components
□ Set up API client utility
□ Test: Can I render a page?
```

### 2.2 Authentication (Critical - Do Early!)

Auth touches everything. Build it before features.

```
1. User model + registration endpoint
2. Password hashing (bcrypt)
3. Login endpoint + JWT creation
4. Protected route middleware (backend)
5. Frontend login/register pages
6. Cookie/token handling
7. Logout functionality
```

**Test checkpoint:** Can I register, login, and access a protected page?

### 2.3 Authorization (RBAC)

```
1. Define roles (system-level + org-level if multi-tenant)
2. Create role-checking utilities
3. Protect routes by role
4. Test permission boundaries
```

**Test checkpoint:** Can admin access admin pages? Can regular user NOT access them?

### 2.4 Multi-tenancy (if applicable)

```
1. Define tenant model (Organization, Restaurant, etc.)
2. Create membership/association model
3. Scope queries to tenant
4. Test data isolation
```

### Deliverables
- [ ] Working backend with DB connection
- [ ] Working frontend with routing
- [ ] Auth flow complete (register → login → protected page)
- [ ] RBAC utilities created

---

## Phase 3: Core Features (1-2 weeks)

**Goal:** Build MVP features using vertical slices.

### The "Vertical Slice" Approach

Instead of: Build all backend → Build all frontend

Do: Build one complete feature at a time

```
Feature: Recipe Management (3 days)
├── Day 1 AM: Recipe model + migration
├── Day 1 PM: CRUD API endpoints
├── Day 2 AM: Recipe list page (frontend)
├── Day 2 PM: Create recipe form
├── Day 3 AM: Edit/delete functionality
└── Day 3 PM: Test entire flow end-to-end
```

### Feature Development Checklist

For each feature:
```
□ Model
  □ Define fields
  □ Create migration
  □ Run migration
  □ Test in DB

□ API
  □ Create endpoint
  □ List (GET /resources)
  □ Detail (GET /resources/:id)
  □ Create (POST /resources)
  □ Update (PUT /resources/:id)
  □ Delete (DELETE /resources/:id)
  □ Test with curl/Postman

□ Frontend
  □ List page
  □ Detail page (if needed)
  □ Create form
  □ Edit form
  □ Delete confirmation
  □ Loading states
  □ Error handling

□ Integration
  □ Test full flow in browser
  □ Test edge cases
  □ Test permissions
```

### Priority Order

```
1. Auth ✓ (Phase 2)
2. Primary entity CRUD (the main "thing" users manage)
3. Relationships (connecting entities)
4. Secondary features
5. Nice-to-haves (analytics, exports, etc.)
```

---

## Phase 4: Polish (3-5 days)

**Goal:** Make it feel production-ready.

### Checklist

```
□ Error Handling
  □ Global error boundary (frontend)
  □ API error responses standardized
  □ User-friendly error messages
  □ 404 pages

□ Loading States
  □ Page loading indicators
  □ Button loading states
  □ Skeleton loaders for lists
  □ Optimistic updates (optional)

□ Form UX
  □ Client-side validation
  □ Server-side validation
  □ Inline error messages
  □ Success feedback

□ Empty States
  □ "No items yet" messages
  □ Call-to-action in empty states
  □ First-time user guidance

□ Responsive Design
  □ Mobile layouts
  □ Touch-friendly buttons
  □ Readable text sizes

□ Accessibility Basics
  □ Form labels
  □ Alt text for images
  □ Color contrast
  □ Keyboard navigation
```

---

## Phase 5: Testing (Ongoing)

### Testing Pyramid

```
        /\
       /  \      E2E (few)
      /----\     Critical user flows
     /      \
    /--------\   Integration (some)
   /          \  API endpoints
  /------------\ 
 /              \ Unit (many)
/________________\ Pure functions, utilities
```

### Minimum Viable Testing

```
□ Auth flow works (register → login → protected page)
□ CRUD operations work (create → read → update → delete)
□ Role permissions enforced (admin vs user)
□ Forms validate properly (required fields, formats)
□ Error states handled (network failure, invalid data)
```

### Tools

| Type | Tools | When |
|------|-------|------|
| Manual | Browser | Every feature |
| Unit | pytest, vitest | Critical logic |
| Integration | pytest + httpx | API endpoints |
| E2E | Playwright | Key user flows |

---

## Phase 6: Deployment (1-2 days)

### 6.1 Containerization

```dockerfile
# Backend Dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0"]
```

```dockerfile
# Frontend Dockerfile
FROM node:20-slim
WORKDIR /app
COPY package.json pnpm-lock.yaml ./
RUN npm install -g pnpm && pnpm install
COPY . .
RUN pnpm build
CMD ["node", "build"]
```

### 6.2 Docker Compose (Local Dev)

```yaml
version: '3.8'
services:
  db:
    image: postgres:15
    environment:
      POSTGRES_PASSWORD: localdev
    volumes:
      - pgdata:/var/lib/postgresql/data
  
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    depends_on:
      - db
  
  frontend:
    build: ./frontend
    ports:
      - "3000:3000"

volumes:
  pgdata:
```

### 6.3 CI/CD (GitHub Actions)

```yaml
name: CI/CD
on: [push]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Run tests
        run: |
          pip install -r requirements.txt
          pytest
  
  deploy:
    needs: test
    if: github.ref == 'refs/heads/main'
    runs-on: ubuntu-latest
    steps:
      - name: Deploy to production
        run: echo "Deploy here"
```

### 6.4 Deployment Checklist

```
□ Environment variables configured
□ Database migrated
□ SSL/HTTPS enabled
□ Domain configured
□ Monitoring set up (optional)
□ Backups configured (optional)
□ Smoke test in production
```

---

## Quick Reference Checklist

```
□ DISCOVERY
  □ Problem statement written
  □ User types defined
  □ User stories written
  □ MVP scope defined

□ DESIGN
  □ Data models sketched
  □ ERD diagram created
  □ Screen map created
  □ Tech stack chosen

□ FOUNDATION
  □ Backend project setup
  □ Database connected
  □ Frontend project setup
  □ Basic styling configured
  □ Auth implemented
  □ RBAC implemented

□ FEATURES (repeat per feature)
  □ Model + migration
  □ API endpoints
  □ Frontend pages
  □ Forms working
  □ Manual testing passed

□ POLISH
  □ Error handling
  □ Loading states
  □ Form validation
  □ Empty states
  □ Mobile responsive

□ TESTING
  □ Auth flow tested
  □ CRUD operations tested
  □ Permissions tested

□ DEPLOY
  □ Dockerized
  □ CI/CD configured
  □ Staging deployed
  □ Production deployed
```

---

## Common Mistakes to Avoid

| Mistake | Better Approach |
|---------|-----------------|
| Building all backend, then all frontend | Vertical slices (full feature at a time) |
| Skipping auth until later | Do auth in Phase 2 - it touches everything |
| No documentation | Write docs as you build |
| Perfectionism early | Make it work → Make it right → Make it fast |
| Building unused features | Stick to MVP, add based on actual need |
| No version control commits | Commit early, commit often |
| Ignoring mobile | Design mobile-first or test mobile early |
| Hardcoding config | Use environment variables from the start |

---

## Time Estimates

| Phase | Solo Dev | Notes |
|-------|----------|-------|
| Discovery | 1-2 days | Don't skip this |
| Design | 1-3 days | Saves time later |
| Foundation | 3-5 days | Auth takes time |
| Features | 1-2 weeks | Depends on scope |
| Polish | 3-5 days | Often underestimated |
| Testing | Ongoing | Build as you go |
| Deployment | 1-2 days | First time takes longer |

**Total MVP:** 3-5 weeks for a solo developer

---

## Notes

*Add learnings from each project:*

- **2026-01-23**: Created process document based on Recipe Manager project
