# Finance Tracker API

A RESTful API for personal finance management built with Flask, PostgreSQL, and JWT authentication. Supports transaction tracking, category filtering, and income/expense summaries.

---

## Table of Contents

- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Prerequisites](#prerequisites)
- [Environment Setup](#environment-setup)
- [Running the Project](#running-the-project)
- [Database Migrations](#database-migrations)
- [API Reference](#api-reference)
- [Running Tests](#running-tests)
- [Common Issues](#common-issues)

---

## Tech Stack

| Layer | Technology |
|---|---|
| Framework | Flask 3.0 |
| Database | PostgreSQL 15 |
| ORM | Flask-SQLAlchemy 3.1 |
| Migrations | Flask-Migrate (Alembic) |
| Authentication | Flask-JWT-Extended 4.6 |
| Password hashing | Flask-Bcrypt 1.0 |
| Validation | Marshmallow 3.20 |
| Containerisation | Docker + Docker Compose |
| Testing | pytest + pytest-flask |

---

## Project Structure

```
finance-tracker-api/
├── app/
│   ├── __init__.py          # App factory (create_app)
│   ├── models.py            # SQLAlchemy models (User, Transaction)
│   ├── schemas.py           # Marshmallow validation schemas
│   └── routes/
│       ├── auth.py          # /api/auth — register, login
│       └── transactions.py  # /api/transactions — CRUD + summary
├── tests/
│   ├── conftest.py          # Fixtures (app, client, db, auth_headers)
│   ├── test_auth.py         # Auth flow tests
│   ├── test_transactions.py # Transaction endpoint tests
│   ├── test_validation.py   # Marshmallow schema tests
│   └── test_errors.py       # Error handling tests
├── migrations/              # Alembic migration versions
├── config.py                # Config class (reads from .env)
├── docker-compose.yml       # API + PostgreSQL services
├── Dockerfile               # Python 3.10-slim image
└── requirements.txt         # Python dependencies
```

---

## Prerequisites

Before running this project, make sure you have the following installed:

- [Docker Desktop](https://www.docker.com/products/docker-desktop/) (includes Docker Compose)
- Git

> **Windows/WSL2 users:** If you have a local PostgreSQL service running, it will conflict with Docker on port 5432. Stop it before starting the containers:
> ```bash
> sudo systemctl stop postgresql
> ```

---

## Environment Setup

**1. Clone the repository**

```bash
git clone https://github.com/ngocho24/finance-tracker-api.git
cd finance-tracker-api
```

**2. Create a `.env` file** in the project root:

```env
DATABASE_URL=postgresql://dev_user:dev_password@db:5432/finance_tracker
JWT_SECRET_KEY=your-secret-key-change-in-production
```

> The `DATABASE_URL` hostname must be `db` — this matches the service name in `docker-compose.yml` and is resolved automatically inside the Docker network.

---

## Running the Project

**1. Build and start the containers**

```bash
docker-compose up -d --build
```

This starts two containers:
- `finance_db` — PostgreSQL 15 on port 5432
- `finance-tracker-api-api-1` — Flask API on port 5000

**2. Verify both containers are running**

```bash
docker-compose ps
```

Both services should show `Up`.

**3. Run database migrations**

On first run, initialise and apply migrations to create the database tables:

```bash
docker-compose exec api flask db init
docker-compose exec api flask db migrate -m "initial migration"
docker-compose exec api flask db upgrade
```

> On subsequent runs (after `docker-compose down`), only `flask db upgrade` is needed — the `migrations/` folder already exists.

**4. Verify the API is responding**

```bash
curl http://127.0.0.1:5000/api/auth/register
```

---

## Database Migrations

When you add or modify a model, generate and apply a new migration:

```bash
# Generate migration from model changes
docker-compose exec api flask db migrate -m "describe your change"

# Apply to the database
docker-compose exec api flask db upgrade
```

To roll back the last migration:

```bash
docker-compose exec api flask db downgrade
```

---

## API Reference

### Authentication

All transaction endpoints require a JWT token in the `Authorization` header:

```
Authorization: Bearer <your_token>
```

---

### POST `/api/auth/register`

Register a new user.

**Request body:**
```json
{
  "email": "user@example.com",
  "password": "yourpassword"
}
```

**Responses:**

| Status | Body |
|---|---|
| 201 | `{"msg": "User created successfully"}` |
| 400 | `{"msg": "User already exists"}` |

---

### POST `/api/auth/login`

Log in and receive a JWT access token.

**Request body:**
```json
{
  "email": "user@example.com",
  "password": "yourpassword"
}
```

**Responses:**

| Status | Body |
|---|---|
| 200 | `{"access_token": "<jwt>"}` |
| 401 | `{"msg": "Invalid credentials"}` |

---

### POST `/api/transactions/`

Create a new transaction. Requires authentication.

**Request body:**
```json
{
  "amount": 150.00,
  "description": "Grocery shopping",
  "category": "Food",
  "type": "expense"
}
```

**Validation rules:**
- `amount` — required, must be greater than 0
- `description` — required, 3–255 characters
- `category` — required, 2–50 characters
- `type` — required, must be `"income"` or `"expense"`

**Responses:**

| Status | Body |
|---|---|
| 201 | `{"msg": "Transaction recorded", "transaction": {...}}` |
| 400 | `{"field": ["error message"]}` |
| 401 | `{"msg": "Missing Authorization Header"}` |

---

### GET `/api/transactions/`

Get all transactions for the authenticated user. Supports optional query filters.

**Query parameters:**

| Parameter | Example | Description |
|---|---|---|
| `category` | `?category=Food` | Filter by category |
| `type` | `?type=expense` | Filter by `income` or `expense` |

**Response (200):**
```json
[
  {
    "id": 1,
    "amount": "150.00",
    "description": "Grocery shopping",
    "category": "Food",
    "type": "expense",
    "date": "2026-05-20T08:56:35.846856"
  }
]
```

---

### GET `/api/transactions/summary`

Get a financial summary for the authenticated user.

**Response (200):**
```json
{
  "total_income": 2500.0,
  "total_expense": 650.0,
  "net_balance": 1850.0
}
```

---

## Running Tests

The test suite uses an in-memory SQLite database — no running containers needed.

**Run all tests:**

```bash
docker-compose exec api pytest tests/ -v
```

**Run a specific test file:**

```bash
docker-compose exec api pytest tests/test_auth.py -v
```

**Expected output:**

```
tests/test_auth.py::test_register_success PASSED
tests/test_auth.py::test_register_duplicate_email PASSED
tests/test_auth.py::test_login_returns_token PASSED
tests/test_auth.py::test_login_wrong_password PASSED
tests/test_auth.py::test_password_is_hashed PASSED
tests/test_auth.py::test_protected_route_without_token PASSED
tests/test_errors.py::test_404_returns_json PASSED
tests/test_errors.py::test_401_returns_json PASSED
tests/test_errors.py::test_malformed_json PASSED
tests/test_transactions.py::test_create_transaction PASSED
tests/test_transactions.py::test_get_transactions PASSED
tests/test_transactions.py::test_filter_by_category PASSED
tests/test_transactions.py::test_filter_by_type PASSED
tests/test_transactions.py::test_summary PASSED
tests/test_transactions.py::test_user_isolation PASSED
tests/test_validation.py::test_negative_amount PASSED
tests/test_validation.py::test_invalid_type PASSED
tests/test_validation.py::test_missing_required_fields PASSED
tests/test_validation.py::test_description_too_short PASSED
tests/test_validation.py::test_empty_body PASSED

20 passed in X.XXs
```

### What the tests cover

| Area | Tests |
|---|---|
| Auth system | Register, login, duplicate email, bcrypt hashing, JWT protection |
| Transaction engine | POST creates row, GET returns list, filtering, summary totals, user data isolation |
| Marshmallow validation | Invalid amount, bad type, missing fields, short strings, empty body |
| Error handling | 404 returns JSON, 401 returns JSON, malformed JSON body |

---

## Common Issues

**Port 5432 already in use**

A local PostgreSQL service is running and blocking Docker. Stop it:

```bash
sudo systemctl stop postgresql
```

Then retry `docker-compose up -d`.

---

**`service "api" is not running`**

The API container crashed on startup. Check the logs:

```bash
docker-compose logs api --tail=30
```

---

**`could not translate host name "db"`**

The API container started before the database was ready, or the two containers are on different networks. Fix with a full restart:

```bash
docker-compose down
docker-compose up -d
sleep 5
docker-compose exec api flask db upgrade
```

---

**Migrations folder already exists**

If you get `Error: Directory migrations already exists` after a rebuild, the folder was baked into the old image. Rebuild cleanly:

```bash
rm -rf migrations/
docker-compose down
docker-compose build --no-cache
docker-compose up -d
docker-compose exec api flask db init
docker-compose exec api flask db migrate -m "initial migration"
docker-compose exec api flask db upgrade
```

---

**Stopping the project**

```bash
docker-compose down
```

The PostgreSQL data is persisted in a Docker volume (`postgres_data`) and will survive restarts. To wipe the database entirely:

```bash
docker-compose down -v
```