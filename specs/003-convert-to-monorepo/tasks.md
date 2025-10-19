# Tasks: Monorepo Conversion

**Input**: Design documents from `/specs/003-convert-to-monorepo/`
**Prerequisites**: plan.md (complete), spec.md (complete), research.md (complete)

**Tests**: This is an infrastructure migration - validation uses existing tests (no new test creation required)

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each capability.

## Format: `[ID] [P?] [Story] Description`
- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1, US2, US3)
- All paths are absolute from repository root

## Path Conventions
This project will transition to Nx monorepo structure:
- **Current**: `src/` (API), `grimoire-ui/` (UI), `tests/` (API tests)
- **Target**: `apps/api/`, `apps/ui/`, `libs/` (shared - future)

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Initialize Nx workspace and create directory structure for monorepo

- [x] **T001** [P] [SETUP] Initialize Nx workspace at repository root using `npx create-nx-workspace@latest`
  - Use `--preset=apps` (empty apps preset)
  - Set `--nx-cloud=false` (no Nx Cloud integration)
  - Verify nx.json and package.json created

- [x] **T002** [P] [SETUP] Create monorepo directory structure
  - Create `apps/` directory for applications
  - Create `libs/` directory for shared libraries (placeholder)
  - Create `tools/` directory for custom Nx plugins (placeholder)
  - Add `.gitkeep` files to `libs/` and `tools/`

- [x] **T003** [P] [SETUP] Update root `.gitignore` for Nx artifacts
  - Add `.nx/` (Nx cache directory)
  - Add `dist/` (build outputs)
  - Add `tmp/` (temporary files)
  - Keep existing entries for `.venv/`, `node_modules/`, etc.

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core migration infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [x] **T004** [FOUNDATION] Create migration validation script at `scripts/validate-migration.sh`
  - Checklist from research.md validation section
  - Test: API tests pass (`nx run api:test`)
  - Test: UI tests pass (`nx run ui:test`)
  - Test: API serve <30s (`nx run api:serve`)
  - Test: UI serve <30s (`nx run ui:serve`)
  - Test: Docker builds (`docker-compose up`)
  - Test: Affected detection (`nx affected:test --base=main`)
  - Test: Git history preserved (`git log --follow apps/api/src/main.py`)

- [x] **T005** [P] [FOUNDATION] Create root `tsconfig.base.json` for TypeScript workspace configuration
  - Base paths for workspace-wide imports
  - Compiler options compatible with Next.js and potential shared libs
  - Reference: research.md section 7 (workspace structure)

- [x] **T006** [P] [FOUNDATION] Update root `package.json` with Nx dependencies
  - Add `nx` (latest stable)
  - Add `@nx/workspace`
  - Add workspace-level scripts: `install:api`, `graph`, `affected`
  - Keep existing Prisma dependencies if at root (or move to apps/ui)
  - NOTE: Completed in T001

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Independent Application Development (Priority: P1) 🎯 MVP

**Goal**: Enable developers to run, build, and test API and UI applications independently without cross-dependencies

**Independent Test**:
1. `nx serve api` starts in <30s without UI dependencies (SC-001)
2. `nx serve ui` starts in <30s without API dependencies (SC-002)
3. `nx test api` runs only API tests (SC-005)
4. `nx test ui` runs only UI tests (SC-006)

### Migration for User Story 1

**API Application Migration:**

- [x] **T007** [US1] Create `apps/api/` directory structure
  - Create `apps/api/` directory
  - Prepare for file moves using `git mv`

- [x] **T008** [US1] Move API source code with git history preservation
  - `git mv src apps/api/src`
  - `git mv tests apps/api/tests`
  - `git mv alembic apps/api/alembic`
  - Verify: `git log --follow apps/api/src/main.py` shows full history (A-003)

- [x] **T009** [US1] Move API configuration files
  - `git mv requirements.txt apps/api/requirements.txt`
  - `git mv pyproject.toml apps/api/pyproject.toml`
  - `git mv Dockerfile apps/api/Dockerfile`
  - `git mv alembic.ini apps/api/alembic.ini`
  - Keep `.env` at root (or copy to apps/api and update paths)

- [x] **T010** [US1] Create `apps/api/project.json` for Nx configuration
  - Define `serve` target using nx:run-commands executor
  - Command: `uvicorn src.main:app --reload` with `cwd: apps/api`
  - Define `test` target using nx:run-commands executor
  - Command: `pytest` with `cwd: apps/api`
  - Define `test-coverage` target using nx:run-commands executor
  - Command: `pytest --cov=src --cov-report=term-missing` with `cwd: apps/api`
  - Define `lint` target using nx:run-commands executor
  - Command: `ruff check . && mypy src` with `cwd: apps/api`
  - Define `format` target using nx:run-commands executor
  - Command: `black .` with `cwd: apps/api`
  - Define `migrate` target using nx:run-commands executor
  - Command: `alembic upgrade head` with `cwd: apps/api`
  - Configure `inputs` for affected detection (research.md section 3):
    - `{projectRoot}/src/**/*.py`
    - `{projectRoot}/tests/**/*.py`
    - `{projectRoot}/requirements.txt`
    - `{projectRoot}/pyproject.toml`
  - Set `implicitDependencies: []` (API is independent)
  - Reference: research.md section 1 (Nx with Python)

- [x] **T011** [US1] Update API Dockerfile for monorepo context
  - Verify COPY statements work with new build context `apps/api`
  - Dockerfile should remain largely unchanged (research.md section 4)
  - Test: `docker build -t grimoire-api ./apps/api`
  - NOTE: Dockerfile moved to apps/api/, content unchanged - build context will be updated in docker-compose.yml (T024)

**UI Application Migration:**

- [x] **T012** [P] [US1] Create `apps/ui/` directory structure
  - Create `apps/ui/` directory
  - Prepare for file moves using `git mv`

- [x] **T013** [P] [US1] Move UI source code with git history preservation
  - `git mv grimoire-ui/src apps/ui/src`
  - `git mv grimoire-ui/prisma apps/ui/prisma`
  - `git mv grimoire-ui/public apps/ui/public` (not found - skipped)
  - Verify: `git log --follow apps/ui/src/app/page.tsx` shows full history (A-003)

- [x] **T014** [P] [US1] Move UI configuration files
  - `git mv grimoire-ui/package.json apps/ui/package.json`
  - `git mv grimoire-ui/next.config.js apps/ui/next.config.js`
  - `git mv grimoire-ui/tailwind.config.ts apps/ui/tailwind.config.ts`
  - `git mv grimoire-ui/tsconfig.json apps/ui/tsconfig.json`
  - `git mv grimoire-ui/.eslintrc.json apps/ui/.eslintrc.json`
  - `git mv grimoire-ui/postcss.config.mjs apps/ui/postcss.config.mjs`
  - Update `tsconfig.json` to extend `../../tsconfig.base.json`

- [x] **T015** [P] [US1] Create `apps/ui/project.json` for Nx configuration
  - Define `serve` target using nx:run-commands executor
  - Command: `yarn dev` with `cwd: apps/ui`
  - Define `build` target using nx:run-commands executor
  - Command: `yarn build` with `cwd: apps/ui`
  - Define `start` target using nx:run-commands executor
  - Command: `yarn start` with `cwd: apps/ui` (production mode)
  - Define `test` target using nx:run-commands executor
  - Command: `yarn test` with `cwd: apps/ui`
  - Define `e2e` target using nx:run-commands executor
  - Command: `yarn test:e2e` with `cwd: apps/ui`
  - Define `lint` target using nx:run-commands executor
  - Command: `yarn lint` with `cwd: apps/ui`
  - Define `type-check` target using nx:run-commands executor
  - Command: `yarn type-check` with `cwd: apps/ui`
  - Define `prisma-migrate` target using nx:run-commands executor
  - Command: `yarn prisma migrate dev` with `cwd: apps/ui`
  - Define `prisma-generate` target using nx:run-commands executor
  - Command: `yarn prisma generate` with `cwd: apps/ui`
  - Configure `inputs` for affected detection:
    - `{projectRoot}/src/**/*.{ts,tsx,js,jsx}`
    - `{projectRoot}/prisma/**/*`
    - `{projectRoot}/package.json`
    - `{projectRoot}/next.config.js`
    - `{projectRoot}/tailwind.config.ts`
  - Set `implicitDependencies: []` (UI is independent)
  - Reference: research.md section 1

- [x] **T016** [P] [US1] Remove empty `grimoire-ui/` directory
  - `rmdir grimoire-ui` (should be empty after file moves)

**Workspace Configuration:**

- [x] **T017** [US1] Configure root `nx.json` for workspace settings
  - Set `affected.defaultBase: "main"`
  - Configure `targetDefaults` for test, lint, build targets
  - Set `defaultProject` to `api` or `ui` (optional)
  - Enable task caching for test, lint, build targets
  - Reference: research.md section 3 (affected detection)

**Validation for User Story 1:**

- [x] **T018** [US1] Run validation script - API independence tests
  - Verify: `nx run api:serve` starts in <30 seconds (SC-001, FR-002)
  - Verify: `nx run api:test` runs all API tests successfully (SC-005, FR-006)
  - Verify: No UI code loaded during API operations (FR-010)
  - Verify: Git history preserved for API files (A-003)

- [x] **T019** [US1] Run validation script - UI independence tests
  - Verify: `nx run ui:serve` starts in <30 seconds (SC-002, FR-003)
  - Verify: `nx run ui:test` runs all UI tests successfully (SC-006, FR-007)
  - Verify: No API code loaded during UI operations (FR-011)
  - Verify: Git history preserved for UI files (A-003)

**Checkpoint**: At this point, User Story 1 should be fully functional - both applications run independently with all tests passing

---

## Phase 4: User Story 2 - Unified Dependency and Build Management (Priority: P2)

**Goal**: Enable single-command installation and consistent tooling across both applications

**Independent Test**:
1. New developer runs `npm install` → all Nx dependencies installed
2. Developer runs workspace-level commands like `nx run-many --target=test --all` (FR-004, FR-014)
3. Both applications use consistent configurations

### Implementation for User Story 2

**Unified Installation:**

- [ ] **T020** [US2] Update root README.md with monorepo installation instructions
  - Document: `npm install` (installs Nx + workspace tools)
  - Document: `cd apps/api && pip install -r requirements.txt` (API Python deps)
  - Document: `cd apps/ui && yarn install` (UI JavaScript deps)
  - Or create unified script: `npm run install:all`
  - Target: <15 minute onboarding (SC-008)
  - Reference: quickstart.md (already created in planning phase)

- [ ] **T021** [P] [US2] Create workspace-level installation script in root `package.json`
  - Add script: `"install:all": "npm install && cd apps/api && pip install -r requirements.txt && cd ../ui && yarn install"`
  - Add script: `"install:api": "cd apps/api && pip install -r requirements.txt"`
  - Add script: `"install:ui": "cd apps/ui && yarn install"`
  - Verify: Full setup completes in <5 minutes (SC-003)

**Consistent Tooling:**

- [ ] **T022** [P] [US2] Configure workspace-level linting and formatting
  - Update root `package.json` with scripts:
    - `"lint:all": "nx run-many --target=lint --all"`
    - `"format:all": "nx run api:format && nx run ui:format"`
  - Verify: `npm run lint:all` lints both API and UI (FR-014)

- [ ] **T023** [P] [US2] Configure workspace-level testing commands
  - Update root `package.json` with scripts:
    - `"test:all": "nx run-many --target=test --all"`
    - `"test:all:parallel": "nx run-many --target=test --all --parallel"`
  - Verify: Commands execute successfully

**Docker and Docker Compose Updates:**

- [ ] **T024** [US2] Update `docker-compose.yml` for monorepo paths
  - Update API service `build.context` to `./apps/api`
  - Update API service `dockerfile` to `Dockerfile` (relative to context)
  - Update API service volume mounts: `./apps/api/src:/app/src`
  - Update UI service paths similarly (if UI has Docker service)
  - Keep database service unchanged (FR-012, A-007)
  - Reference: research.md section 4 (Docker integration)

- [ ] **T025** [US2] Verify Docker builds work with new structure
  - Test: `docker-compose build` succeeds for all services (SC-007)
  - Test: `docker-compose up` starts all services successfully
  - Test: Containers can access code at updated paths

**Environment Variables:**

- [ ] **T026** [US2] Standardize environment variable management
  - Decide: Keep `.env` at root or separate per app
  - Update `.env.example` with monorepo context
  - Document environment variable locations in README.md
  - Reference: A-008 (environment variable standardization)

**Validation for User Story 2:**

- [ ] **T027** [US2] Test unified installation workflow
  - Clone repository fresh (or simulate)
  - Run: `npm install` (Nx workspace setup)
  - Run: `npm run install:all` (all dependencies)
  - Verify: Completes in <5 minutes on standard machine (SC-003)
  - Verify: Both apps can start after installation

- [ ] **T028** [US2] Test workspace-level commands
  - Run: `nx run-many --target=lint --all` (FR-014)
  - Run: `nx run-many --target=test --all`
  - Verify: Both applications processed correctly
  - Verify: Clear visibility of all applications (FR-004, acceptance scenario 4)

**Checkpoint**: At this point, User Stories 1 AND 2 should both work - independent apps + unified management

---

## Phase 5: User Story 3 - Efficient CI/CD with Affected Detection (Priority: P3)

**Goal**: Optimize CI pipeline to run only affected tests/builds based on code changes

**Independent Test**:
1. Make API-only change → `nx affected:test --base=main` runs only API tests (SC-004)
2. Make UI-only change → only UI tests run
3. CI pipeline execution time reduces by 30%+ for single-app changes

### Implementation for User Story 3

**Affected Detection Configuration:**

- [ ] **T029** [P] [US3] Verify affected detection inputs in `apps/api/project.json`
  - Confirm `inputs` configured in T010 are correct
  - Test: Change `apps/api/src/models/word.py`
  - Run: `nx affected:graph --base=main`
  - Verify: Only API marked as affected (FR-009)
  - Reference: research.md section 3 (affected detection)

- [ ] **T030** [P] [US3] Verify affected detection inputs in `apps/ui/project.json`
  - Confirm `inputs` configured in T015 are correct
  - Test: Change `apps/ui/src/app/page.tsx`
  - Run: `nx affected:graph --base=main`
  - Verify: Only UI marked as affected (FR-009)

**CI/CD Workflow Updates:**

- [ ] **T031** [US3] Update GitHub Actions workflow at `.github/workflows/ci.yml`
  - Add `fetch-depth: 0` to checkout step (required for affected)
  - Add Node.js setup step (for Nx)
  - Add Python setup step (for API)
  - Update test job to use:
    - `npx nx affected --target=test --base=origin/main` (for PRs)
    - `npx nx run-many --target=test --all` (for main branch)
  - Reference: research.md section 6 (CI/CD integration)

- [ ] **T032** [P] [US3] Update GitHub Actions workflow at `.github/workflows/pr-assistant.yml` (if exists)
  - Update to use Nx affected detection
  - Ensure compatible with monorepo structure

- [ ] **T033** [P] [US3] Update GitHub Actions workflow at `.github/workflows/code-review.yml` (if exists)
  - Update to use Nx affected detection
  - Ensure linting uses `nx affected:lint --base=origin/main`

**Local Affected Commands:**

- [ ] **T034** [US3] Add affected detection scripts to root `package.json`
  - `"affected:test": "nx affected --target=test --base=main"`
  - `"affected:build": "nx affected --target=build --base=main"`
  - `"affected:lint": "nx affected --target=lint --base=main"`
  - `"affected:graph": "nx affected:graph --base=main"` (visualization)

**Validation for User Story 3:**

- [ ] **T035** [US3] Test affected detection with API-only changes
  - Change: `apps/api/src/services/word_service.py`
  - Run: `nx affected:test --base=main --dry-run`
  - Verify: Only API tests in execution plan
  - Run: `nx affected:test --base=main`
  - Verify: UI tests skipped, API tests run
  - Measure: Time saved vs. full test run

- [ ] **T036** [US3] Test affected detection with UI-only changes
  - Change: `apps/ui/src/components/WordDisplay.tsx`
  - Run: `nx affected:test --base=main --dry-run`
  - Verify: Only UI tests in execution plan
  - Run: `nx affected:test --base=main`
  - Verify: API tests skipped, UI tests run
  - Measure: Time saved vs. full test run

- [ ] **T037** [US3] Test affected detection with shared config changes
  - Change: Root `nx.json` or `docker-compose.yml`
  - Run: `nx affected:test --base=main --dry-run`
  - Verify: Both API and UI tests in execution plan (correct behavior)

- [ ] **T038** [US3] Validate CI pipeline efficiency gains
  - Create test PR with API-only changes
  - Verify: CI runs only affected tests
  - Measure: Pipeline time reduction
  - Target: ≥30% reduction for single-app changes (SC-004)
  - Reference: research.md section 6 (expected 30-40% reduction)

**Checkpoint**: All user stories should now be independently functional with optimized CI/CD

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Documentation, cleanup, and final validation across all user stories

- [ ] **T039** [P] [POLISH] Update root README.md with complete monorepo documentation
  - Replace old structure references with new `apps/api` and `apps/ui`
  - Add "Quick Start" section linking to quickstart.md (already exists)
  - Add command reference table (old commands → Nx commands)
  - Add troubleshooting section
  - Reference: research.md section 7 (developer workflow)
  - Target: Enable 15-minute onboarding (SC-008)

- [ ] **T040** [P] [POLISH] Verify quickstart.md is up-to-date
  - Quickstart.md already created in planning phase
  - Verify all commands work as documented
  - Test against validation script from T004
  - Verify migration guide section is accurate

- [ ] **T041** [P] [POLISH] Update CLAUDE.md with monorepo commands
  - Already updated in planning phase
  - Verify Nx commands are documented
  - Verify project structure is accurate

- [ ] **T042** [P] [POLISH] Add migration rollback documentation
  - Document rollback procedure in README.md or MIGRATION.md
  - Reference: research.md section 5 (rollback plan)
  - Explain: How to revert merge commit if critical issues found (A-009)

- [ ] **T043** [P] [POLISH] Clean up old configuration files
  - Remove old root-level files no longer needed:
    - Old `package.json` entries specific to grimoire-ui (if moved)
    - Old scripts that are now Nx tasks
  - Keep: `docker-compose.yml` (updated), `.env`, `.gitignore` (updated)

- [ ] **T044** [P] [POLISH] Verify Nx graph visualization works
  - Run: `nx graph`
  - Verify: Shows both `api` and `ui` applications
  - Verify: Shows no incorrect dependencies between them
  - Verify: Graph opens in browser successfully

- [ ] **T045** [POLISH] Run complete validation script from T004
  - Execute: `./scripts/validate-migration.sh`
  - All checks must pass:
    - ✅ `nx run api:test` - All API tests pass (SC-005)
    - ✅ `nx run ui:test` - All UI tests pass (SC-006)
    - ✅ `nx run api:serve` - API starts <30s (SC-001)
    - ✅ `nx run ui:serve` - UI starts <30s (SC-002)
    - ✅ `docker-compose up` - Services start (SC-007)
    - ✅ `nx affected:test --base=main` - Affected works
    - ✅ Git history preserved (A-003)

- [ ] **T046** [POLISH] Create migration commit and PR
  - Commit all changes with message referencing migration
  - Push to feature branch `003-convert-to-monorepo`
  - Create PR with:
    - Title: "Convert to Nx Monorepo - Independent API and UI Applications"
    - Description linking to spec.md, plan.md, quickstart.md
    - Validation results from T045
    - Before/After command comparison
  - Reference: C-001 (migration on feature branch)

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Story 1 (Phase 3)**: Depends on Foundational - Core independent apps (P1 - highest priority)
- **User Story 2 (Phase 4)**: Depends on User Story 1 - Builds on independent apps
- **User Story 3 (Phase 5)**: Depends on User Stories 1 and 2 - Optimization layer
- **Polish (Phase 6)**: Depends on all user stories being complete

### User Story Dependencies

```
Foundational (Phase 2)
    ↓
User Story 1 (P1) - Independent Apps [MUST complete first - MVP]
    ↓
User Story 2 (P2) - Unified Management [Builds on US1]
    ↓
User Story 3 (P3) - Affected Detection [Builds on US1 + US2]
    ↓
Polish (Phase 6)
```

**Note**: User Stories 2 and 3 technically could start after US1, but sequential is recommended for this migration to ensure stability at each layer.

### Within Each User Story

**User Story 1 (Independent Apps):**
- API migration (T007-T011) can run in parallel with UI migration (T012-T016) ✅
- Workspace configuration (T017) depends on both apps being moved
- Validation (T018-T019) depends on workspace configuration

**User Story 2 (Unified Management):**
- Documentation (T020), installation scripts (T021), tooling config (T022-T023) are parallel ✅
- Docker updates (T024-T025) are sequential
- Environment variables (T026) is independent
- Validation (T027-T028) is last

**User Story 3 (Affected Detection):**
- Affected config verification (T029-T030) are parallel ✅
- CI workflow updates (T031-T033) are parallel ✅
- Local scripts (T034) is independent
- Validation (T035-T038) is sequential (different test scenarios)

### Parallel Opportunities

**Within Setup (Phase 1):**
- T001, T002, T003 can all run in parallel

**Within Foundational (Phase 2):**
- T005, T006 can run in parallel
- T004 should be created early but only executed during validation

**Within User Story 1:**
```bash
# Parallel group 1: Directory setup
Task T007: Create apps/api/ structure
Task T012: Create apps/ui/ structure

# Parallel group 2: File migrations (AFTER directories created)
Task T008-T009: Move API files
Task T013-T014: Move UI files

# Parallel group 3: Nx configurations (AFTER file migrations)
Task T010: Create apps/api/project.json
Task T011: Update API Dockerfile
Task T015: Create apps/ui/project.json
Task T016: Remove old grimoire-ui/

# Sequential: Workspace config + validation
Task T017: Configure nx.json (needs both apps)
Task T018-T019: Validation
```

**Within User Story 2:**
```bash
# Parallel group:
Task T020: Update README
Task T021: Installation scripts
Task T022: Linting config
Task T023: Testing commands
```

**Within User Story 3:**
```bash
# Parallel group 1: Affected detection
Task T029: Verify API affected inputs
Task T030: Verify UI affected inputs

# Parallel group 2: CI workflows
Task T031: Update ci.yml
Task T032: Update pr-assistant.yml
Task T033: Update code-review.yml
```

**Within Polish (Phase 6):**
```bash
# All documentation/cleanup tasks can run in parallel:
Task T039: Update README
Task T040: Verify quickstart.md
Task T041: Update CLAUDE.md
Task T042: Rollback docs
Task T043: Cleanup old files
Task T044: Verify Nx graph

# Final validation is sequential:
Task T045: Run validation script
Task T046: Create PR
```

---

## Parallel Example: User Story 1 - API and UI Migration

```bash
# Step 1: Create both app directories in parallel
Parallel Task Group 1:
  - Task T007: "Create apps/api/ directory structure"
  - Task T012: "Create apps/ui/ directory structure"

# Step 2: Move API and UI files in parallel (after Step 1 completes)
Parallel Task Group 2:
  - Task T008: "Move API source code with git mv"
  - Task T009: "Move API config files"
  - Task T013: "Move UI source code with git mv"
  - Task T014: "Move UI config files"

# Step 3: Configure both apps in parallel (after Step 2 completes)
Parallel Task Group 3:
  - Task T010: "Create apps/api/project.json"
  - Task T011: "Update API Dockerfile"
  - Task T015: "Create apps/ui/project.json"
  - Task T016: "Remove empty grimoire-ui/"

# Step 4: Sequential workspace configuration (after Step 3 completes)
Sequential Task:
  - Task T017: "Configure root nx.json" (needs both apps configured)

# Step 5: Validation (after Step 4 completes)
Sequential Tasks:
  - Task T018: "Validate API independence"
  - Task T019: "Validate UI independence"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only - Independent Apps)

1. Complete **Phase 1: Setup** (T001-T003) - Initialize Nx workspace
2. Complete **Phase 2: Foundational** (T004-T006) - Migration infrastructure
3. Complete **Phase 3: User Story 1** (T007-T019) - Move apps, configure Nx, validate
4. **STOP and VALIDATE**:
   - Run validation script (T018-T019)
   - Verify both apps work independently
   - Verify all existing tests pass
   - Verify git history preserved
5. **Checkpoint**: You now have a working monorepo with independent apps (MVP!)
6. Optionally merge to main if satisfied, or continue to US2

### Incremental Delivery (Recommended)

1. **Foundation** (Phases 1-2): Setup + Scripts → Ready to migrate
2. **US1 Delivery** (Phase 3): Independent apps → Test → Merge → **MVP achieved!**
   - At this point, monorepo works and apps are independent
   - Can pause here and deploy/use before continuing
3. **US2 Delivery** (Phase 4): Unified management → Test → Merge
   - Adds convenience but doesn't change core independence
4. **US3 Delivery** (Phase 5): Affected detection → Test → Merge
   - Optimization that saves CI time
5. **Polish** (Phase 6): Documentation, cleanup, final PR

### Sequential Execution (Single Developer)

Recommended order for solo implementation:

1. Phase 1: Setup (1-2 hours)
2. Phase 2: Foundational (1-2 hours)
3. Phase 3: User Story 1 (4-6 hours) ← **Critical MVP milestone**
   - Validate thoroughly before proceeding
4. Phase 4: User Story 2 (2-3 hours)
5. Phase 5: User Story 3 (2-3 hours)
6. Phase 6: Polish (1-2 hours)

**Total estimated time**: 11-18 hours for complete migration

### Parallel Team Strategy (2-3 Developers)

With multiple developers:

1. **Together**: Complete Phases 1-2 (Setup + Foundational)
2. **Split for User Story 1**:
   - Developer A: API migration (T007-T011, T018)
   - Developer B: UI migration (T012-T016, T019)
   - Developer C: Workspace config + validation (T017, integration)
3. **Together**: Review and validate User Story 1
4. **Split for User Story 2**:
   - Developer A: Docker updates (T024-T026)
   - Developer B: Installation scripts (T020-T023)
   - Developer C: Validation (T027-T028)
5. **Split for User Story 3**:
   - Developer A: CI workflows (T031-T033)
   - Developer B: Affected detection config (T029-T030, T034)
   - Developer C: Validation (T035-T038)
6. **Together**: Polish phase (T039-T046)

---

## Notes

- **[P] tasks**: Different files, can run in parallel if multiple developers/agents
- **[Story] labels**: Map tasks to specific user stories for traceability
- **Git history preservation**: Critical requirement (A-003) - always use `git mv`
- **Validation at each checkpoint**: Don't skip validation steps
- **Reversibility**: Feature branch allows abandonment if critical issues found (A-009)
- **No breaking changes**: All existing tests must pass without modification (C-002, SC-005, SC-006)
- **Performance**: Build/startup times must not increase (C-005, SC-001, SC-002)
- **Infrastructure migration**: No application code changes - only file movements and configuration

---

## Success Metrics

After completing all tasks, verify:

✅ **SC-001**: API dev server starts in <30 seconds
✅ **SC-002**: UI dev server starts in <30 seconds
✅ **SC-003**: Full setup completes in <5 minutes
✅ **SC-004**: CI time reduces by ≥30% for single-app changes
✅ **SC-005**: All API tests pass without modification
✅ **SC-006**: All UI tests pass without modification
✅ **SC-007**: Docker builds complete successfully
✅ **SC-008**: New developers can setup in <15 minutes
✅ **SC-009**: Zero breaking changes to development workflows

✅ **A-003**: Git history preserved for all files
✅ **A-009**: Migration is reversible via git revert

---

**Total Tasks**: 46
**Estimated Effort**: 11-18 hours (single developer), 6-10 hours (team of 3)
**MVP Checkpoint**: After Phase 3 (User Story 1) - Task T019
**Critical Path**: Setup → Foundational → US1 → US2 → US3 → Polish
