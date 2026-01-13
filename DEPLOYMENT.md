# Deployment Guide

## Overview

This guide covers deploying the Recipe Manager application to production.

---

## Architecture

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   CDN/Proxy     │────▶│   Frontend      │────▶│   Backend API   │
│   (Cloudflare)  │     │   (Vercel/Node) │     │   (Railway/AWS) │
└─────────────────┘     └─────────────────┘     └─────────────────┘
                                                        │
                                                        ▼
                                                ┌─────────────────┐
                                                │   PostgreSQL    │
                                                │   (Supabase)    │
                                                └─────────────────┘
```

---

## Backend Deployment

### Option 1: Railway

1. Connect GitHub repository
2. Set environment variables:
   ```
   DATABASE_URL=postgresql://...
   SECRET_KEY=<generate-secure-key>
   ALGORITHM=HS256
   ACCESS_TOKEN_EXPIRE_MINUTES=30
   ENVIRONMENT=production
   ```
3. Deploy with Procfile:
   ```
   web: uvicorn app.main:app --host 0.0.0.0 --port $PORT
   ```

### Option 2: AWS (EC2 + RDS)

1. Launch EC2 instance (Ubuntu 22.04)
2. Install Python 3.11, Nginx
3. Set up RDS PostgreSQL
4. Configure Nginx reverse proxy
5. Use systemd for process management

### Option 3: Docker

```dockerfile
# backend/Dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

---

## Frontend Deployment

### Option 1: Vercel (Recommended for SvelteKit)

1. Connect GitHub repository
2. Set build command: `pnpm build`
3. Set environment variables:
   ```
   API_BASE_URL=https://api.your-domain.com
   ```
4. Deploy

### Option 2: Node.js Server

```bash
# Build
pnpm build

# Run with Node adapter
node build/index.js
```

### Option 3: Docker

```dockerfile
# frontend/Dockerfile
FROM node:18-alpine

WORKDIR /app
RUN npm install -g pnpm

COPY package.json pnpm-lock.yaml ./
RUN pnpm install --frozen-lockfile

COPY . .
RUN pnpm build

ENV NODE_ENV=production
CMD ["node", "build"]
```

---

## Environment Variables (Production)

### Backend

| Variable | Description | Example |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection string | `postgresql://user:pass@host:5432/db` |
| `SECRET_KEY` | JWT signing key (256-bit) | Generate with `openssl rand -hex 32` |
| `ALGORITHM` | JWT algorithm | `HS256` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Token lifetime | `30` |
| `ENVIRONMENT` | Environment flag | `production` |

### Frontend

| Variable | Description | Example |
|----------|-------------|---------|
| `API_BASE_URL` | Backend API URL (server-side) | `https://api.your-domain.com` |

---

## Security Checklist

### Before Going Live

- [ ] Generate new `SECRET_KEY` (don't reuse development key)
- [ ] Set `ENVIRONMENT=production` (enables secure cookies)
- [ ] Use HTTPS everywhere
- [ ] Set strong database password
- [ ] Remove/disable DEBUG mode
- [ ] Configure CORS for production domain only
- [ ] Set up rate limiting
- [ ] Enable logging and monitoring

### CORS Configuration

Update `backend/app/main.py`:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://your-domain.com"],  # Production domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Cookie Settings

In production, cookies are automatically set with:
- `Secure=True` (HTTPS only)
- `HttpOnly=True` (no JS access)
- `SameSite=Lax` (CSRF protection)

---

## Database Migrations (Production)

```bash
# SSH into server or use Railway CLI
cd backend

# Run migrations
alembic upgrade head

# Create superadmin (first time only)
python create_superadmin.py
```

---

## Monitoring

### Recommended Tools

- **Logs**: Railway logs, CloudWatch, or Papertrail
- **Errors**: Sentry
- **Performance**: New Relic or Datadog
- **Uptime**: UptimeRobot or Better Uptime

### Health Check Endpoint

Add to backend:
```python
@app.get("/health")
async def health_check():
    return {"status": "healthy"}
```

---

## SSL/TLS

### Using Cloudflare (Recommended)

1. Add domain to Cloudflare
2. Set SSL mode to "Full (strict)"
3. Enable "Always Use HTTPS"

### Using Let's Encrypt (Self-hosted)

```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d api.your-domain.com
```

---

## Scaling

### Horizontal Scaling

- Use load balancer (AWS ALB, Cloudflare)
- Run multiple backend instances
- Use Redis for session storage (if needed)

### Database Scaling

- Enable connection pooling (PgBouncer)
- Set up read replicas
- Regular backups

---

## Rollback Procedure

1. Revert to previous Git commit
2. Redeploy
3. If database migration issue:
   ```bash
   alembic downgrade -1
   ```
