# Task Manager — REST API with Auth & RBAC

A scalable REST API built with **FastAPI (Python)** featuring JWT authentication, role-based access control, and a React.js frontend.

---

## Project Structure

```
crud-app/
├── backend-python/          # FastAPI backend
│   ├── app/
│   │   ├── config/          # Database, logger, settings
│   │   ├── models/          # SQLAlchemy models (User, Task)
│   │   ├── routers/         # API route handlers (auth, tasks, users)
│   │   ├── schemas/         # Pydantic validation schemas
│   │   ├── utils/           # JWT, password, sanitize, response, dependencies
│   │   └── main.py          # FastAPI app entry point
│   ├── seed.py              # Seed demo users and tasks
│   ├── pyproject.toml       # Poetry dependencies
│   ├── Dockerfile
│   └── .env.example
├── frontend/                # React.js frontend (Vite)
│   ├── src/
│   │   ├── api/             # Axios client
│   │   ├── components/      # Navbar, TaskModal, ProtectedRoute
│   │   ├── context/         # AuthContext (JWT state)
│   │   ├── pages/           # Login, Register, Dashboard, Profile, Admin
│   │   └── main.jsx
│   ├── Dockerfile
│   └── .env.example
├── docker-compose.yml
└── README.md
```

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | FastAPI (Python 3.11) |
| Database | PostgreSQL (Neon serverless) |
| ORM | SQLAlchemy 2.0 |
| Auth | JWT (python-jose) + bcrypt |
| Validation | Pydantic v2 |
| Sanitization | bleach (XSS protection) |
| Rate Limiting | slowapi |
| Logging | loguru (rotating files) |
| API Docs | Swagger UI (auto-generated) |
| Frontend | React.js + Vite |
| HTTP Client | Axios |

---

## Getting Started

### Prerequisites
- Python 3.11+
- Poetry
- Node.js 18+
- PostgreSQL (or Neon account)

### 1. Clone the repo
```bash
git clone <your-repo-url>
cd crud-app
```

### 2. Setup Backend
```bash
cd backend-python

# Install dependencies
poetry install

# Copy and fill in your credentials
cp .env.example .env
```

Edit `.env`:
```
DATABASE_URL=postgresql+psycopg2://user:password@host/dbname?sslmode=require
JWT_SECRET=your_super_secret_key_here
JWT_EXPIRES_DAYS=7
PORT=8000
ENV=development
```

### 3. Seed the database
```bash
poetry run python seed.py
```

Seeded accounts:

| Email | Password | Role |
|-------|----------|------|
| admin@example.com | Admin@123 | ADMIN |
| user@example.com | User@123 | USER |

### 4. Start the backend
```bash
poetry run uvicorn app.main:app --reload --port 8000
```

- API: `http://localhost:8000`
- Swagger docs: `http://localhost:8000/api/docs`
- ReDoc: `http://localhost:8000/api/redoc`

### 5. Setup & start the frontend
```bash
cd frontend
npm install
npm run dev
```

Frontend: `http://localhost:5173`

---

## API Endpoints

### Auth — `/api/v1/auth`
| Method | Route | Auth | Description |
|--------|-------|------|-------------|
| POST | `/register` | Public | Register new user, returns JWT |
| POST | `/login` | Public | Login, returns JWT |
| GET | `/me` | Bearer | Get own profile |

### Tasks — `/api/v1/tasks`
| Method | Route | Auth | Description |
|--------|-------|------|-------------|
| GET | `/` | Bearer | List tasks (own for user, all for admin) |
| GET | `/stats` | Bearer | Task counts by status & priority |
| GET | `/{id}` | Bearer | Get single task |
| POST | `/` | Bearer | Create task |
| PATCH | `/{id}` | Bearer | Update task |
| DELETE | `/{id}` | Bearer | Delete task |

**Query params on `GET /tasks`:** `page`, `limit`, `status`, `priority`, `search`, `sortBy`, `order`

### Users — `/api/v1/users`
| Method | Route | Auth | Description |
|--------|-------|------|-------------|
| GET | `/` | Admin | List all users (paginated) |
| GET | `/{id}` | Admin or Own | Get user by ID |
| PATCH | `/{id}` | Own or Admin | Update name / password |
| PATCH | `/{id}/role` | Admin | Change user role |
| DELETE | `/{id}` | Admin | Delete user |

---

## Roles & Permissions

| Action | USER | ADMIN |
|--------|------|-------|
| Register / Login | ✅ | ✅ |
| View & manage own tasks | ✅ | ✅ |
| View all users' tasks | ❌ | ✅ |
| Edit / delete any task | ❌ | ✅ |
| List all users | ❌ | ✅ |
| Change user roles | ❌ | ✅ |
| Delete users | ❌ | ✅ |

---

## Security

| Feature | Implementation |
|---------|---------------|
| Password hashing | bcrypt with salt rounds |
| JWT | HS256, configurable expiry |
| Input validation | Pydantic schemas on all endpoints |
| XSS sanitization | bleach strips HTML from all inputs |
| Rate limiting | 100 req/min (global via slowapi) |
| CORS | Explicit origin whitelist |
| Body size limit | Enforced by FastAPI/uvicorn |

---

## Docker Deployment

```bash
# Copy and fill root .env
cp .env.example .env

# Build and run everything
docker compose up --build
```

Services:
- `backend` → `http://localhost:8000`
- `frontend` → `http://localhost:80`

---

## Scalability Notes

- **Stateless API** — JWT auth means any number of backend instances can run behind a load balancer
- **DB indexes** — composite indexes on `userId`, `status`, `priority`, `createdAt` for fast filtering
- **Connection pooling** — SQLAlchemy pool (size 5, overflow 10) handles concurrent requests
- **Rotating logs** — Daily log rotation with 14-day retention keeps disk usage bounded
- **Neon serverless** — Auto-scales PostgreSQL compute, no manual provisioning
- **Microservices path** — Routers are fully decoupled; `auth`, `tasks`, `users` can be extracted into separate services
- **Caching** — Add Redis in front of `GET /tasks` and stats endpoints to eliminate repeat DB reads
- **Rate limiting** — Already in place via slowapi; tighten per-route for production
