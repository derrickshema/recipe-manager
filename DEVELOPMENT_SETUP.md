# Development Setup

## Prerequisites

- **Python** 3.11+
- **Node.js** 18+
- **pnpm** (recommended) or npm
- **PostgreSQL** 14+
- **Git**

---

## Quick Start

### 1. Clone the Repository

```bash
git clone https://github.com/your-org/recipe-manager.git
cd recipe-manager
```

### 2. Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate (Windows)
venv\Scripts\activate

# Activate (macOS/Linux)
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Copy environment file
cp .env.example .env
# Edit .env with your database credentials

# Run database migrations
alembic upgrade head

# Create superadmin user
python create_superadmin.py

# Start development server
uvicorn app.main:app --reload
```

Backend runs at: `http://localhost:8000`
API docs at: `http://localhost:8000/docs`

### 3. Frontend Setup

```bash
cd frontend

# Install dependencies
pnpm install

# Copy environment file
cp .env.example .env
# Edit if needed (default API URL is localhost:8000)

# Start development server
pnpm dev
```

Frontend runs at: `http://localhost:5173`

---

## Environment Variables

### Backend (.env)

```bash
# Database
DATABASE_URL=postgresql+psycopg2://user:password@localhost:5432/recipe_db

# Security
SECRET_KEY=your-secret-key-generate-a-random-one
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Environment
DEBUG=True
ENVIRONMENT=development

# Superadmin (for initial setup)
SUPERADMIN_USERNAME=admin
SUPERADMIN_PASSWORD=your-secure-password
SUPERADMIN_EMAIL=admin@yourcompany.com
```

### Frontend (.env)

```bash
# API URL for server-side requests
API_BASE_URL=http://localhost:8000

# API URL for client-side (public endpoints only)
VITE_API_BASE_URL=http://localhost:8000
```

---

## Database Setup

### Create PostgreSQL Database

```sql
CREATE DATABASE recipe_db;
CREATE USER recipe_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE recipe_db TO recipe_user;
```

### Run Migrations

```bash
cd backend
alembic upgrade head
```

### Create New Migration

```bash
alembic revision --autogenerate -m "description of changes"
```

---

## Project Structure

```
recipe-manager/
├── backend/
│   ├── app/
│   │   ├── main.py          # FastAPI app entry
│   │   ├── db/               # Database config
│   │   ├── models/           # SQLModel models
│   │   ├── routes/           # API endpoints
│   │   └── utilities/        # Helpers (auth, etc.)
│   ├── migrations/           # Alembic migrations
│   ├── requirements.txt
│   └── .env
│
├── frontend/
│   ├── src/
│   │   ├── lib/
│   │   │   ├── api/          # API clients
│   │   │   ├── components/   # Svelte components
│   │   │   ├── server/       # Server-side utilities
│   │   │   ├── services/     # Business logic
│   │   │   ├── stores/       # Svelte stores
│   │   │   ├── types/        # TypeScript types
│   │   │   └── utils/        # Helpers
│   │   ├── routes/           # SvelteKit routes
│   │   └── hooks.server.ts   # Server hooks
│   ├── package.json
│   └── .env
│
└── docs/                     # Documentation
```

---

## Common Commands

### Backend

```bash
# Start server
uvicorn app.main:app --reload

# Run with specific port
uvicorn app.main:app --reload --port 8080

# Check for Python errors
python -m py_compile app/main.py
```

### Frontend

```bash
# Start dev server
pnpm dev

# Build for production
pnpm build

# Preview production build
pnpm preview

# Type check
pnpm check

# Lint
pnpm lint
```

---

## IDE Setup

### VS Code Extensions (Recommended)

- **Python** - Microsoft
- **Pylance** - Microsoft
- **Svelte for VS Code** - Svelte
- **Tailwind CSS IntelliSense** - Tailwind Labs
- **ESLint** - Microsoft
- **Prettier** - Prettier

### Settings

`.vscode/settings.json`:
```json
{
  "python.defaultInterpreterPath": "./backend/venv/Scripts/python.exe",
  "svelte.enable-ts-plugin": true,
  "editor.formatOnSave": true
}
```

---

## Troubleshooting

### Backend won't start

1. Check PostgreSQL is running
2. Verify DATABASE_URL in .env
3. Run `alembic upgrade head` for migrations

### Frontend type errors

1. Run `pnpm exec svelte-kit sync`
2. Restart VS Code TypeScript server

### Authentication not working

1. Check both servers are running
2. Verify CORS origins in `backend/app/main.py`
3. Clear browser cookies and retry
