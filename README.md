# fitnessMaven

A gym courtesy timer application that helps gym-goers be mindful of how long they occupy a machine, ensuring fair access for everyone.

## Purpose

In busy gyms, machines are shared resources. fitnessMaven tracks how long a user has been on a piece of equipment and sends alerts to their device:

- **Yellow alert** - Triggered when usage exceeds **10 minutes**. A gentle reminder that others may be waiting.
- **Red alert** - Triggered when usage exceeds **15 minutes**. A stronger signal to wrap up and free the machine.

## Architecture

```
┌─────────────────────────────────────────────┐
│           Clients (Interface Layer)          │
│   Mobile App  │  Web App  │  IoT Device     │
└──────────────────┬──────────────────────────┘
                   │ HTTPS + JWT
┌──────────────────▼──────────────────────────┐
│            API Gateway / Auth Layer          │
│   OAuth2 / JWT token validation / Rate      │
│   limiting / CORS                           │
└──────────────────┬──────────────────────────┘
                   │
┌──────────────────▼──────────────────────────┐
│          Business Logic Layer (Python)       │
│   Timer service │ Alert service │ Machine   │
│   management    │ Notification engine       │
└──────────────────┬──────────────────────────┘
                   │
┌──────────────────▼──────────────────────────┐
│              Data Layer                      │
│   PostgreSQL                                │
└─────────────────────────────────────────────┘
```

The interface layer is fully decoupled from business logic. Any client (mobile, web, IoT) authenticates via JWT and hits the same REST API.

## Tech Stack

| Layer | Technology | Purpose |
|---|---|---|
| **API Framework** | FastAPI | Async Python framework with built-in OAuth2/JWT support |
| **Auth** | OAuth2 + JWT | Stateless tokens across mobile/web/IoT clients |
| **Password Hashing** | bcrypt (passlib) | Industry-standard password security |
| **Database** | PostgreSQL | Relational data store for users, sessions, machines |
| **ORM** | SQLAlchemy | Database abstraction and query building |
| **Migrations** | Alembic | Schema versioning |
| **Push Notifications** | Firebase Cloud Messaging | Cross-platform alerts (future) |
| **Infrastructure** | Terraform + Ansible | Provisioning and configuration on Azure |
| **Server OS** | Ubuntu 22.04 LTS | Hosting environment |

## Target Devices

- **Smartphone** (initial target) - Push notifications via mobile app
- **IoT devices** (future) - Visual indicators on connected hardware near gym equipment

## Project Structure

```
fitnessMaven/
├── app/
│   ├── main.py             # FastAPI entry point
│   ├── config.py           # Environment-based settings
│   ├── database.py         # SQLAlchemy engine and session
│   ├── api/                # Route handlers
│   │   └── auth.py
│   ├── auth/               # JWT, password hashing
│   │   ├── jwt.py
│   │   └── passwords.py
│   ├── models/             # SQLAlchemy DB models
│   │   └── user.py
│   ├── schemas/            # Pydantic request/response schemas
│   │   └── user.py
│   └── services/           # Business logic
│       └── timer.py
├── tests/
│   └── unit_tests/
├── infra/
│   ├── provision.sh        # Spin up Azure resources
│   ├── destroy.sh          # Tear down Azure resources
│   ├── terraform/          # Infrastructure as code
│   └── ansible/            # Server configuration
├── pyproject.toml          # Dependencies and project config
├── requirements.lock       # Pinned dependency versions
├── run.sh                  # Local development server
└── README.md
```

## Auth Module Roadmap

| Phase | Name | Description | Status |
|---|---|---|---|
| 1 | **Project Structure & Config** | Scaffold app/ directory, FastAPI entry point, env config, DB connection | In Progress |
| 2 | **User Model & Database** | SQLAlchemy User model, Alembic migrations, Pydantic schemas | Pending |
| 3 | **Registration** | bcrypt password hashing, POST /auth/register, input validation | Pending |
| 4 | **JWT Authentication** | Token creation (access + refresh), POST /auth/login, token validation | Pending |
| 5 | **Protected Routes & Middleware** | get_current_user dependency, POST /auth/refresh, POST /auth/logout | Pending |
| 6 | **Auth Testing** | Unit tests for hashing/JWT, integration tests for all auth endpoints | Pending |

## Local Development

```bash
# Activate virtual environment
source FitnessMaven/bin/activate

# Install dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Start the API server (port 8000)
./run.sh
```

## Infrastructure

```bash
# Provision Azure resources
./infra/provision.sh

# Configure the server
ansible-playbook -i infra/ansible/inventory.ini infra/ansible/playbook.yml

# Tear down all resources
./infra/destroy.sh
```

## Status

This project is under active development.
