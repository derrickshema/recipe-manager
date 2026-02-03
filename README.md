# Recipe Manager

A multi-tenant restaurant management platform where restaurant owners can manage menus and customers can browse and order food.

## Tech Stack

- **Frontend:** SvelteKit, Tailwind CSS
- **Backend:** FastAPI, SQLModel
- **Database:** PostgreSQL
- **Auth:** JWT + httpOnly cookies
- **Payments:** Stripe
- **File Storage:** S3 (LocalStack for local dev)
- **Email:** Resend
- **Real-time:** WebSockets

---

## Quick Start (Docker)

```bash
# 1. Start all services
docker-compose up -d

# 2. Run database migrations (first time only)
docker-compose exec backend alembic upgrade head

# 3. Create S3 bucket (first time only)
docker-compose exec localstack awslocal s3 mb s3://recipe-images

# 4. Create superadmin account (first time only)
docker-compose exec backend python create_superadmin.py
```

**App URLs:**
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

**Stop the app:**
```bash
docker-compose down        # Keep data
docker-compose down -v     # Delete all data
```

---

## Development Mode

For active development with hot-reload:

### Prerequisites
- Python 3.13+
- Node.js 22+
- pnpm
- PostgreSQL (local or Docker)
- Docker Desktop (for LocalStack)

### Backend

```bash
cd backend

# Create virtual environment (first time)
python -m venv venv
venv\Scripts\Activate.ps1   # Windows
# source venv/bin/activate  # Mac/Linux

# Install dependencies (first time)
pip install -r requirements.txt

# Create .env file (first time)
cp .env.example .env  # Then edit with your values

# Run migrations
alembic upgrade head

# Start server
uvicorn app.main:app --reload
```

### Frontend

```bash
cd frontend

# Install dependencies (first time)
pnpm install

# Start dev server
pnpm dev
```

### LocalStack (S3)

```bash
# Start LocalStack
docker run -d --name localstack -p 4566:4566 localstack/localstack

# Create bucket
docker exec localstack awslocal s3 mb s3://recipe-images
```

### Stripe Webhooks (for payment testing)

```bash
stripe listen --forward-to localhost:8000/payments/webhook
```

---

## Environment Variables

Create `backend/.env`:

```env
DATABASE_URL=postgresql://user:password@localhost:5432/recipe_db
SECRET_KEY=your-secret-key-here

# Stripe
STRIPE_SECRET_KEY=sk_test_...
STRIPE_PUBLISHABLE_KEY=pk_test_...
STRIPE_WEBHOOK_SECRET=whsec_...

# S3 / LocalStack
S3_BUCKET_NAME=recipe-images
S3_ENDPOINT_URL=http://localhost:4566
S3_ACCESS_KEY=test
S3_SECRET_KEY=test
S3_REGION=us-east-1

# Email
RESEND_API_KEY=re_...

# Frontend URL (for email links)
FRONTEND_URL=http://localhost:3000
```

---

## Running Tests

```bash
cd backend
pytest tests/ -v           # All tests
pytest tests/test_auth.py  # Auth tests only
pytest tests/ -k "order"   # Tests matching "order"
```

---

## Project Structure

```
recipe-manager/
├── backend/
│   ├── app/
│   │   ├── main.py          # FastAPI app
│   │   ├── config.py        # Settings
│   │   ├── db/              # Database setup
│   │   ├── models/          # SQLModel models
│   │   ├── routes/          # API endpoints
│   │   └── utilities/       # Auth, email, S3
│   ├── migrations/          # Alembic migrations
│   ├── tests/               # pytest tests
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── lib/             # Components, stores, utils
│   │   └── routes/          # SvelteKit pages
│   ├── Dockerfile
│   └── package.json
├── docker-compose.yml
└── README.md
```

---

## User Roles

| Role | Description |
|------|-------------|
| **Superadmin** | System admin - approves restaurants, manages users |
| **Restaurant Owner** | Creates restaurant, manages menu & orders |
| **Employee** | Restaurant staff - views orders |
| **Customer** | Browses restaurants, places orders |

---

## Key Features

- ✅ User registration & login (email verification)
- ✅ Password reset via email
- ✅ Restaurant registration with approval workflow
- ✅ Menu/recipe management with image uploads
- ✅ Staff management (invite by email)
- ✅ Customer ordering with Stripe payments
- ✅ Real-time order status updates (WebSockets)
- ✅ Admin dashboard for system management
