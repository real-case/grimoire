# grimoire Development Guidelines

Auto-generated from all feature plans. Last updated: 2025-10-19

## Active Technologies

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
- Backend: pip (requirements.txt + pyproject.toml)
- Frontend: Yarn 4.9.1

## Project Structure
```
grimoire/
├── src/                    # Python backend source
├── tests/                  # Python backend tests
├── grimoire-ui/           # Next.js frontend
│   ├── src/               # Frontend source
│   └── package.json       # Frontend dependencies
├── pyproject.toml         # Python project config
├── requirements.txt       # Python dependencies
└── package.json          # Root package config (Prisma)
```

## Commands

### Backend (Python)
```bash
# Run tests
pytest

# Run tests with coverage
pytest --cov=src --cov-report=term-missing

# Lint and format
ruff check .
black .
mypy src

# Run development server
cd src && uvicorn main:app --reload
```

### Frontend (Next.js)
```bash
# Development
cd grimoire-ui && yarn dev

# Build
cd grimoire-ui && yarn build

# Type checking
cd grimoire-ui && yarn type-check

# Linting
cd grimoire-ui && yarn lint

# Testing
cd grimoire-ui && yarn test
cd grimoire-ui && yarn test:e2e
```

### Database
```bash
# Prisma migrations
yarn prisma migrate dev
yarn prisma generate

# Alembic migrations (Python)
cd src && alembic upgrade head
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
- 002-grimoire-ui-implement: Added TypeScript 5.x with Next.js 14+ (App Router)
- 001-an-ai-agent: Added Python 3.12 + FastAPI 0.109.0, Anthropic SDK 0.18.0, SQLAlchemy 2.0 (async), Redis 5.0.1, httpx 0.26.0

<!-- MANUAL ADDITIONS START -->
<!-- MANUAL ADDITIONS END -->
