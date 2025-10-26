# grimoire Development Guidelines

Auto-generated from all feature plans. Last updated: 2025-10-19

## Active Technologies

### Monorepo Management
- **Nx** (latest stable) - Monorepo orchestration and task execution
- **Node.js** - Required for Nx workspace management
- **Workspace structure**: Apps-based monorepo with independent API and UI applications

### Backend (Python)
- Python 3.12+
- FastAPI 0.109.0 + Uvicorn 0.27.0
- Anthropic SDK 0.18.0
- SQLAlchemy 2.0.25 (async) + asyncpg 0.29.0
- Redis 5.0.1 (with hiredis)
- Alembic 1.13.1 (migrations)
- httpx 0.26.0
- Pydantic 2.5.3
- Loguru 0.7.2
- Sentry SDK 1.40.0

### Frontend (TypeScript/React)
- TypeScript 5.3+
- Next.js 14.2+ (App Router)
- React 18.3+
- Tailwind CSS 3.4+
- Prisma 6.17.1 (ORM)
- Headless UI 2.0
- Heroicons 2.1
- React Hook Form 7.51
- Zod 3.22 (validation)

### Package Management
- **Workspace**: npm (root level, Nx dependencies)
- **Backend**: pip (requirements.txt + pyproject.toml in apps/api)
- **Frontend**: Yarn 4.9.1 (in apps/ui)

## Project Structure

**Note**: This project uses an Nx monorepo structure (as of feature 003-convert-to-monorepo)

```
grimoire/                      # Nx monorepo root
├── apps/
│   ├── api/                  # Python FastAPI backend
│   │   ├── src/              # Python source
│   │   ├── tests/            # Pytest tests
│   │   ├── alembic/          # Database migrations
│   │   ├── requirements.txt  # Python dependencies
│   │   ├── pyproject.toml    # Python config
│   │   └── project.json      # Nx project config
│   │
│   └── ui/                   # Next.js frontend
│       ├── src/              # TypeScript source
│       ├── prisma/           # Prisma schema & migrations
│       ├── package.json      # UI dependencies
│       └── project.json      # Nx project config
│
├── libs/                     # Shared libraries (future)
├── nx.json                   # Nx workspace config
├── package.json              # Root dependencies (Nx)
└── docker-compose.yml        # Database & services
```

## Commands

**Important**: All commands below use Nx task execution. Run from repository root unless otherwise noted.

### Backend (Python API)
```bash
# Run development server
nx serve api

# Run tests
nx test api

# Run tests with coverage
nx run api:test-coverage

# Lint and format
nx lint api
nx run api:format

# Database migrations
nx run api:migrate

# Install Python dependencies
cd apps/api && pip install -r requirements.txt
```

### Frontend (Next.js UI)
```bash
# Development server
nx serve ui

# Build for production
nx build ui

# Type checking
nx run ui:type-check

# Linting
nx lint ui

# Testing
nx test ui
nx run ui:e2e

# Prisma operations
nx run ui:prisma-migrate
nx run ui:prisma-generate
```

### Workspace-wide (All Applications)
```bash
# Run all tests
nx run-many --target=test --all

# Run all tests in parallel
nx run-many --target=test --all --parallel

# Run only affected tests (based on git changes)
nx affected:test --base=main

# Run only affected builds
nx affected:build --base=main

# Lint all applications
nx run-many --target=lint --all

# Visualize dependency graph
nx graph

# List all projects
nx list
```

### Database
```bash
# Start PostgreSQL
docker-compose up -d postgres

# API migrations (Alembic)
nx run api:migrate

# UI migrations (Prisma)
nx run ui:prisma-migrate
nx run ui:prisma-generate
```

### Docker
```bash
# Start all services
docker-compose up -d

# Stop all services
docker-compose down

# View logs
docker-compose logs -f api
docker-compose logs -f postgres
```

## Code Style

### Python
- Line length: 100 characters
- Formatter: Black
- Linter: Ruff
- Type checker: mypy
- Follow PEP 8 and modern Python 3.12 conventions
- Use async/await for I/O operations

### TypeScript/React
- Use TypeScript strict mode
- Follow Next.js 14+ App Router conventions
- Use Tailwind CSS for styling
- Validate forms with React Hook Form + Zod
- Use Prettier for formatting

## Recent Changes
- 003-convert-to-monorepo: Added Python 3.12+ (API), TypeScript 5.3+ (UI), Node.js (Nx orchestration)
- 002-grimoire-ui-implement: Added TypeScript 5.x with Next.js 14+ (App Router)
- 001-an-ai-agent: Added Python 3.12 + FastAPI 0.109.0, Anthropic SDK 0.18.0, SQLAlchemy 2.0 (async), Redis 5.0.1, httpx 0.26.0

<!-- MANUAL ADDITIONS START -->
<!-- MANUAL ADDITIONS END -->
