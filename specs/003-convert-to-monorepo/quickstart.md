# Quickstart: Grimoire Nx Monorepo

**Feature**: 003-convert-to-monorepo
**Last Updated**: 2025-10-19

## Overview

Grimoire is now an Nx-managed monorepo containing two independent applications:
- **API** (`apps/api`): Python FastAPI backend for word lookups and vocabulary management
- **UI** (`apps/ui`): Next.js TypeScript frontend for word lookup interface

This guide will help you get started with development in under 15 minutes.

---

## Prerequisites

Before you begin, ensure you have:
- **Node.js** 18+ and npm/yarn
- **Python** 3.12+
- **Docker** and Docker Compose (for database)
- **Git** for version control

---

## Quick Start (5 minutes)

### 1. Clone and Install

```bash
# Clone the repository
git clone <repository-url>
cd grimoire

# Install all dependencies (root + both apps)
npm install

# Install Python dependencies for API
cd apps/api
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
cd ../..
```

### 2. Start Database

```bash
# Start PostgreSQL via Docker Compose
docker-compose up -d postgres

# Wait for database to be ready (about 10 seconds)
docker-compose logs -f postgres
# Press Ctrl+C when you see "database system is ready to accept connections"
```

### 3. Run Database Migrations

```bash
# API migrations (Alembic)
nx run api:migrate
# OR manually: cd apps/api && alembic upgrade head

# UI migrations (Prisma)
nx run ui:prisma-migrate
# OR manually: cd apps/ui && yarn prisma migrate dev
```

### 4. Start Development Servers

```bash
# Terminal 1: Start API
nx serve api
# API runs on http://localhost:8000

# Terminal 2: Start UI
nx serve ui
# UI runs on http://localhost:3000
```

**Done!** Visit http://localhost:3000 to use Grimoire.

---

## Repository Structure

```
grimoire/                      # Monorepo root
├── apps/
│   ├── api/                  # Python FastAPI backend
│   │   ├── src/              # Python source code
│   │   │   ├── main.py       # FastAPI application entry
│   │   │   ├── api/          # API routes
│   │   │   ├── models/       # SQLAlchemy models
│   │   │   └── services/     # Business logic
│   │   ├── tests/            # Pytest tests
│   │   ├── alembic/          # Database migrations
│   │   ├── requirements.txt  # Python dependencies
│   │   ├── pyproject.toml    # Python config
│   │   └── project.json      # Nx configuration
│   │
│   └── ui/                   # Next.js TypeScript frontend
│       ├── src/              # TypeScript source
│       │   ├── app/          # Next.js App Router pages
│       │   ├── components/   # React components
│       │   └── hooks/        # Custom React hooks
│       ├── prisma/           # Prisma schema & migrations
│       ├── package.json      # UI dependencies
│       └── project.json      # Nx configuration
│
├── libs/                     # Shared libraries (future)
├── tools/                    # Custom Nx plugins (future)
├── nx.json                   # Nx workspace configuration
├── package.json              # Root dependencies (Nx)
├── docker-compose.yml        # Database & services
└── README.md                 # This file will link here
```

---

## Common Development Tasks

### Running Applications

| Task | Command | Description |
|------|---------|-------------|
| **API dev server** | `nx serve api` | Start FastAPI with hot reload on port 8000 |
| **UI dev server** | `nx serve ui` | Start Next.js dev server on port 3000 |
| **Both servers** | `nx run-many --target=serve --all --parallel` | Start both in parallel |
| **Production API** | `nx run api:serve-prod` | Run API without reload (production mode) |
| **Production UI** | `nx build ui && nx run ui:start` | Build and run production UI |

### Testing

| Task | Command | Description |
|------|---------|-------------|
| **API tests** | `nx test api` | Run pytest for API |
| **UI tests** | `nx test ui` | Run Jest tests for UI |
| **All tests** | `nx run-many --target=test --all` | Run all tests sequentially |
| **Affected tests** | `nx affected:test` | Run only tests for changed apps |
| **API coverage** | `nx run api:test-coverage` | Run API tests with coverage report |
| **UI E2E** | `nx run ui:e2e` | Run Playwright end-to-end tests |

### Building

| Task | Command | Description |
|------|---------|-------------|
| **Build API** | `nx build api` | Build API (if applicable) |
| **Build UI** | `nx build ui` | Build Next.js production bundle |
| **Build all** | `nx run-many --target=build --all` | Build all applications |
| **Affected build** | `nx affected:build` | Build only changed apps |

### Linting & Formatting

| Task | Command | Description |
|------|---------|-------------|
| **Lint API** | `nx lint api` | Run ruff + mypy on Python code |
| **Lint UI** | `nx lint ui` | Run ESLint on TypeScript code |
| **Lint all** | `nx run-many --target=lint --all` | Lint all applications |
| **Format API** | `nx run api:format` | Format Python with Black |
| **Format UI** | `nx run ui:format` | Format TypeScript with Prettier |

### Database Operations

| Task | Command | Description |
|------|---------|-------------|
| **Start database** | `docker-compose up -d postgres` | Start PostgreSQL container |
| **Stop database** | `docker-compose stop postgres` | Stop PostgreSQL |
| **API migration** | `nx run api:migrate` | Run Alembic migrations |
| **Create API migration** | `cd apps/api && alembic revision --autogenerate -m "description"` | Generate new Alembic migration |
| **UI migration** | `nx run ui:prisma-migrate` | Run Prisma migrations |
| **Prisma generate** | `nx run ui:prisma-generate` | Regenerate Prisma client |
| **Database shell** | `docker exec -it grimoire-postgres psql -U grimoire_user -d grimoire` | Connect to database |

### Dependency Management

| Task | Command | Description |
|------|---------|-------------|
| **Install Nx deps** | `npm install` | Install/update Nx and workspace tools |
| **Install API deps** | `cd apps/api && pip install -r requirements.txt` | Install Python packages |
| **Add API dep** | `cd apps/api && pip install <package> && pip freeze > requirements.txt` | Add Python dependency |
| **Install UI deps** | `cd apps/ui && yarn install` | Install UI JavaScript packages |
| **Add UI dep** | `cd apps/ui && yarn add <package>` | Add UI dependency |

---

## Nx Affected Commands

Nx's affected detection runs only the tasks for applications that have changed. This is especially useful in CI/CD.

### How It Works

1. Nx compares your current branch against a base branch (usually `main`)
2. It identifies which files have changed
3. It determines which applications are affected by those changes
4. It runs tasks only for affected applications

### Examples

```bash
# Test only changed applications
nx affected:test --base=main

# Build only changed applications
nx affected:build --base=main

# Lint only changed applications
nx affected:lint --base=main

# See what will be affected (dry run)
nx affected:test --base=main --dry-run

# See the dependency graph
nx graph
```

### CI/CD Integration

In GitHub Actions, use affected commands for PRs:

```yaml
# Only run tests for changed apps on pull requests
- name: Run affected tests
  if: github.event_name == 'pull_request'
  run: npx nx affected --target=test --base=origin/main

# Run all tests on main branch
- name: Run all tests
  if: github.ref == 'refs/heads/main'
  run: npx nx run-many --target=test --all
```

**Expected CI improvements**:
- API-only changes: ~50% faster (skip UI tests)
- UI-only changes: ~75% faster (skip API tests)
- Average: 30-40% CI time reduction

---

## Migration from Old Structure

If you're familiar with the pre-monorepo structure, here's how commands have changed:

| Old Command | New Command | Notes |
|-------------|-------------|-------|
| `cd src && uvicorn main:app --reload` | `nx serve api` | API dev server |
| `cd grimoire-ui && yarn dev` | `nx serve ui` | UI dev server |
| `pytest` (from root) | `nx test api` | API tests |
| `cd grimoire-ui && yarn test` | `nx test ui` | UI tests |
| `pip install -r requirements.txt` | (same, from apps/api) | Python deps |
| `cd grimoire-ui && yarn install` | `cd apps/ui && yarn install` | UI deps |
| `docker-compose up` | `docker-compose up` | Unchanged |
| `alembic upgrade head` | `nx run api:migrate` | DB migrations |

**Key differences**:
- ✅ **Nx commands** from any directory (no more `cd` into app folders for running)
- ✅ **Parallel execution** with `run-many --parallel`
- ✅ **Affected detection** with `affected:*` commands
- ✅ **Unified workspace** with all apps visible in `nx graph`

---

## Troubleshooting

### "Nx command not found"

**Solution**: Run `npm install` from the repository root.

```bash
cd <repo-root>
npm install
npx nx --version  # Should show Nx version
```

### API server won't start

**Symptoms**: `ModuleNotFoundError` or import errors

**Solution**: Activate virtual environment and install dependencies

```bash
cd apps/api
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
cd ../..
nx serve api
```

### UI server won't start

**Symptoms**: Package errors or missing dependencies

**Solution**: Install UI dependencies

```bash
cd apps/ui
yarn install
cd ../..
nx serve ui
```

### Database connection errors

**Symptoms**: "Could not connect to database" or "Connection refused"

**Solution**: Start PostgreSQL container

```bash
docker-compose up -d postgres
docker-compose logs postgres  # Check if running

# If still failing, check environment variables
cat apps/api/.env              # Should have DATABASE_URL
cat apps/ui/.env.local         # Should have DATABASE_URL for Prisma
```

### Affected detection not working

**Symptoms**: `nx affected:test` runs all tests or none

**Solution**: Ensure you have a base branch to compare against

```bash
# Fetch latest main branch
git fetch origin main

# Run affected against origin/main
nx affected:test --base=origin/main

# Check what Nx thinks is affected
nx affected:graph --base=origin/main
```

### Docker build failures

**Symptoms**: Docker can't find files after monorepo migration

**Solution**: Check docker-compose.yml paths are updated

```yaml
# Ensure build context points to app directory
services:
  api:
    build:
      context: ./apps/api  # Not "."
      dockerfile: Dockerfile
```

### Tests pass locally but fail in CI

**Symptoms**: CI fails with "no tests found" or "command not found"

**Solution**: Ensure CI workflow installs all dependencies

```yaml
# GitHub Actions example
steps:
  - name: Install root dependencies
    run: npm install

  - name: Install API dependencies
    run: cd apps/api && pip install -r requirements.txt

  - name: Install UI dependencies
    run: cd apps/ui && yarn install

  - name: Run tests
    run: nx affected:test --base=origin/main
```

---

## Best Practices

### 1. Use Nx Commands

✅ **Do**: `nx serve api`
❌ **Don't**: `cd apps/api && uvicorn src.main:app`

**Why**: Nx commands are cached, tracked in the dependency graph, and work from any directory.

### 2. Leverage Affected Commands Locally

Before pushing, run only affected tests:

```bash
git add .
nx affected:test --base=main
nx affected:lint --base=main
```

This saves time by skipping unchanged applications.

### 3. Keep Dependencies Isolated

- **API** (Python): Keep `requirements.txt` in `apps/api`
- **UI** (JavaScript): Keep `package.json` in `apps/ui`
- **Root**: Only Nx and workspace-level tools

**Why**: Prevents dependency conflicts and maintains isolation.

### 4. Use Parallel Execution

For independent tasks, run in parallel:

```bash
# Run all tests in parallel
nx run-many --target=test --all --parallel

# Run all lints in parallel
nx run-many --target=lint --all --parallel
```

**Why**: Reduces total execution time (e.g., 4 minutes sequential → 2 minutes parallel).

### 5. Visualize the Graph

When in doubt, visualize dependencies:

```bash
nx graph
```

Opens interactive graph showing applications and their relationships.

### 6. Keep Virtual Environments Local

Each developer should have their own Python virtual environment in `apps/api/.venv`.

```bash
cd apps/api
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

**Why**: Prevents environment conflicts between developers and with system Python.

---

## Next Steps

1. **Read the spec**: [`specs/003-convert-to-monorepo/spec.md`](./spec.md)
2. **Review research**: [`specs/003-convert-to-monorepo/research.md`](./research.md)
3. **Check implementation plan**: [`specs/003-convert-to-monorepo/plan.md`](./plan.md)
4. **Explore the workspace**:
   ```bash
   nx graph                    # Visual dependency graph
   nx list                     # List all projects
   nx show project api         # Show API project details
   nx show project ui          # Show UI project details
   ```

---

## Additional Resources

- **Nx Documentation**: https://nx.dev
- **Nx Affected Commands**: https://nx.dev/ci/features/affected
- **Nx with Python**: https://nx.dev/recipes/other/misc-non-js
- **Docker Compose**: https://docs.docker.com/compose/
- **FastAPI**: https://fastapi.tiangolo.com/
- **Next.js**: https://nextjs.org/docs

---

**Questions or issues?** Check the [troubleshooting section](#troubleshooting) or open an issue in the repository.

**Estimated setup time**: <15 minutes (as per SC-008)
**Last verified**: 2025-10-19
