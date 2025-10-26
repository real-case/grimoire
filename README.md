# Grimoire

A vocabulary learning application with AI-powered word enrichment, built as an Nx monorepo.

## Project Structure

This is an Nx monorepo containing:

- **apps/api/** - FastAPI backend service (Python 3.12+)
- **apps/ui/** - Next.js 14 frontend application (TypeScript)
- **libs/** - Shared libraries (future)
- **tools/** - Custom Nx plugins (future)

## Quick Start

### Prerequisites

- Node.js 18+ and npm
- Python 3.12+
- PostgreSQL (or Docker Compose)
- Yarn 4.9.1 (for UI)

### Installation

**Option 1: Install All Dependencies (Recommended)**

```bash
# Install Nx workspace dependencies
npm install

# Install all application dependencies (API + UI)
npm run install:all
```

**Option 2: Install Individually**

```bash
# 1. Install Nx workspace
npm install

# 2. Install API dependencies (Python)
npm run install:api

# 3. Install UI dependencies (Yarn)
npm run install:ui
```

Target installation time: < 5 minutes

### Running Applications

**API (FastAPI Backend)**

```bash
# Development server
npx nx run api:serve

# Run tests
npx nx run api:test

# Run with coverage
npx nx run api:test-coverage

# Lint and format
npx nx run api:lint
npx nx run api:format
```

**UI (Next.js Frontend)**

```bash
# Development server
npx nx run ui:serve

# Production build
npx nx run ui:build

# Type checking
npx nx run ui:type-check

# Lint
npx nx run ui:lint
```

**Docker Compose**

```bash
# Start all services (API + Database)
docker-compose up

# Build and start
docker-compose up --build

# Stop all services
docker-compose down
```

### Workspace Commands

Run commands across all applications:

```bash
# Run tests for all apps
npx nx run-many --target=test --all

# Lint all apps
npm run lint:all

# Run tests in parallel
npm run test:all
```

### Database Migrations

**API (Alembic)**

```bash
npx nx run api:migrate
```

**UI (Prisma)**

```bash
npx nx run ui:prisma-migrate
npx nx run ui:prisma-generate
```

## Development Workflow

### Running Affected Commands

Nx can detect which apps are affected by your changes:

```bash
# Test only affected apps
npx nx affected:test --base=main

# Lint only affected apps
npx nx affected:lint --base=main

# See dependency graph
npx nx graph
```

### Project Commands

Each application has its own project.json with defined targets. View available commands:

```bash
npx nx show project api
npx nx show project ui
```

## Environment Variables

- **Root .env**: Shared configuration (if needed)
- **apps/api/.env**: API-specific variables (database, API keys)
- **apps/ui/.env.local**: UI-specific variables (API URL)

See `.env.example` files in each app directory for required variables.

## Architecture

### Backend (API)
- Python 3.12+ with FastAPI
- SQLAlchemy 2.0 (async) + PostgreSQL
- Anthropic Claude API for enrichment
- Redis for caching
- Alembic for migrations

### Frontend (UI)
- TypeScript 5.3+ with Next.js 14 (App Router)
- React 18.3+
- Tailwind CSS for styling
- Prisma as ORM
- Headless UI components

## Testing

```bash
# Test specific app
npx nx run api:test
npx nx run ui:test

# Test all apps
npm run test:all

# Test with coverage (API)
npx nx run api:test-coverage
```

## Validation

Run the migration validation script to ensure everything is working:

```bash
./scripts/validate-migration.sh
```

This checks:
- API and UI tests pass
- Both apps start in < 30 seconds
- Docker builds successfully
- Nx affected detection works
- Git history preserved

## Documentation

- [Development Guidelines](./CLAUDE.md) - Code style and conventions
- [Quick Start Guide](./specs/003-convert-to-monorepo/quickstart.md) - Detailed setup
- [Monorepo Spec](./specs/003-convert-to-monorepo/spec.md) - Architecture decisions

## Contributing

1. Create a feature branch
2. Make changes
3. Run affected tests: `npx nx affected:test --base=main`
4. Run affected lint: `npx nx affected:lint --base=main`
5. Create PR

## License

See LICENSE file for details.
