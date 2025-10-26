# Research: Monorepo Conversion with Nx

**Feature**: 003-convert-to-monorepo
**Date**: 2025-10-19
**Purpose**: Investigate best practices and implementation patterns for converting Grimoire to an Nx-managed monorepo

## Research Areas

### 1. Nx with Python Applications

**Question**: How to integrate Python applications into an Nx monorepo alongside TypeScript/Next.js applications?

**Investigation**:
- Nx was originally designed for JavaScript/TypeScript monorepos
- Python support is available through community plugins or custom executors
- Options evaluated:
  1. `@nxlv/python` - Community plugin for Python support
  2. Custom executors using Nx's plugin system
  3. Nx's run-commands executor for wrapping Python tooling

**Decision**: Use Nx run-commands executor for Python tasks

**Rationale**:
- **Simplicity**: Wraps existing Python commands (pytest, uvicorn, pip) without requiring custom executors
- **Flexibility**: Allows calling any shell command, preserving existing workflows
- **No additional dependencies**: Avoids third-party plugins that may lag behind Nx updates
- **Proven pattern**: Widely used for non-JS languages in Nx workspaces
- **Example configuration**:
  ```json
  {
    "targets": {
      "serve": {
        "executor": "nx:run-commands",
        "options": {
          "command": "cd apps/api && uvicorn src.main:app --reload",
          "cwd": "apps/api"
        }
      },
      "test": {
        "executor": "nx:run-commands",
        "options": {
          "command": "pytest",
          "cwd": "apps/api"
        }
      }
    }
  }
  ```

**Alternatives Considered**:
- `@nxlv/python`: Provides native Python support but adds external dependency; overkill for our simple use case
- Custom plugin: Unnecessary complexity for wrapping existing commands; would require maintenance

**References**:
- Nx run-commands documentation: https://nx.dev/nx-api/nx/executors/run-commands
- Nx plugin architecture: https://nx.dev/extending-nx/intro/getting-started

---

### 2. Managing Python Dependencies in Nx Monorepo

**Question**: How should Python dependencies (requirements.txt, pyproject.toml) be managed within the Nx workspace structure?

**Investigation**:
- Nx typically manages dependencies through root package.json for JS/TS
- Python uses pip + requirements.txt or pyproject.toml
- Need to support virtual environments for isolation

**Decision**: Keep Python dependencies local to apps/api

**Rationale**:
- **Isolation**: Python virtual environments (.venv) should remain app-specific
- **Tooling compatibility**: Existing Python tooling (pip, pipenv, poetry) expects local dependency files
- **No cross-language sharing**: API and UI don't share Python dependencies
- **Structure**:
  ```
  apps/api/
  ├── requirements.txt       # Python dependencies (unchanged)
  ├── pyproject.toml        # Python project config (unchanged)
  └── .venv/                # Virtual environment (gitignored)
  ```

**Installation approach**:
- Root `package.json` includes Nx script: `"install:api": "cd apps/api && pip install -r requirements.txt"`
- Nx target in `apps/api/project.json`:
  ```json
  {
    "targets": {
      "install": {
        "executor": "nx:run-commands",
        "options": {
          "command": "pip install -r requirements.txt",
          "cwd": "apps/api"
        }
      }
    }
  }
  ```

**Alternatives Considered**:
- Centralized Python deps: Would break virtual environment isolation and complicate dependency resolution
- Poetry/Pipenv: Unnecessary migration; requirements.txt + pip already works

**References**:
- Python packaging best practices: https://packaging.python.org/en/latest/guides/
- Nx monorepo patterns: https://nx.dev/concepts/more-concepts/applications-and-libraries

---

### 3. Nx Affected Detection for Python

**Question**: How to configure Nx's affected command to detect changes in Python files and trigger appropriate tasks?

**Investigation**:
- Nx uses dependency graph to determine affected projects
- Graph built from import statements and configuration files
- Python imports need to be tracked

**Decision**: Configure implicitDependencies and inputs in project.json

**Rationale**:
- **Implicit dependencies**: Define cross-project dependencies (e.g., API depends on shared config)
- **Input patterns**: Specify which files trigger rebuilds/retests
- **Example configuration** for `apps/api/project.json`:
  ```json
  {
    "name": "api",
    "implicitDependencies": [],
    "targets": {
      "test": {
        "executor": "nx:run-commands",
        "options": {
          "command": "pytest"
        },
        "inputs": [
          "{projectRoot}/src/**/*.py",
          "{projectRoot}/tests/**/*.py",
          "{projectRoot}/requirements.txt",
          "{projectRoot}/pyproject.toml"
        ]
      }
    }
  }
  ```
- **Root nx.json** configuration:
  ```json
  {
    "affected": {
      "defaultBase": "main"
    },
    "targetDefaults": {
      "test": {
        "dependsOn": ["^test"]
      }
    }
  }
  ```

**How affected detection works**:
1. Developer changes `apps/api/src/models/word.py`
2. Nx detects change matches input pattern `{projectRoot}/src/**/*.py`
3. `nx affected:test` runs only API tests, skips UI tests
4. CI pipeline saves ~50% execution time for API-only changes

**Alternatives Considered**:
- No affected detection: Would always run all tests; defeats purpose of monorepo (SC-004 requirement)
- Custom affected logic: Nx built-in is sufficient and well-tested

**References**:
- Nx affected commands: https://nx.dev/ci/features/affected
- Project configuration: https://nx.dev/reference/project-configuration

---

### 4. Docker Integration with Nx Monorepo

**Question**: How to update Docker and docker-compose configurations to work with the new monorepo structure?

**Investigation**:
- Existing Dockerfile builds from root with `src/` as context
- docker-compose.yml references root-level directories
- Need to preserve multi-stage builds and layer caching

**Decision**: Update docker-compose paths and Dockerfile COPY statements

**Rationale**:
- **Minimal changes**: Update paths rather than restructuring Dockerfiles
- **Preserve optimization**: Keep existing multi-stage builds and caching layers
- **Example docker-compose.yml update**:
  ```yaml
  # Before
  services:
    api:
      build:
        context: .
        dockerfile: Dockerfile
      volumes:
        - ./src:/app/src

  # After
  services:
    api:
      build:
        context: ./apps/api
        dockerfile: Dockerfile
      volumes:
        - ./apps/api/src:/app/src
  ```
- **Example Dockerfile update** (apps/api/Dockerfile):
  ```dockerfile
  # Before
  COPY requirements.txt .
  COPY src/ ./src/

  # After (no change needed if context is apps/api)
  COPY requirements.txt .
  COPY src/ ./src/
  ```
- **Build context**: Set to `apps/api` or `apps/ui` for each service
- **Compose project**: Root docker-compose.yml remains at repository root for convenience

**Alternatives Considered**:
- Single Dockerfile for all apps: Would complicate builds and break isolation
- Nested docker-compose files: Unnecessary; single root file with updated paths is simpler

**References**:
- Docker Compose build context: https://docs.docker.com/compose/compose-file/build/
- Multi-stage builds: https://docs.docker.com/build/building/multi-stage/

---

### 5. Migration Strategy and Rollback Plan

**Question**: How to safely migrate existing code to monorepo structure with ability to rollback?

**Investigation**:
- Git history preservation is critical (A-003)
- Need to test migration without breaking main branch
- Rollback plan required (A-009)

**Decision**: Git mv for directory moves + comprehensive validation

**Rationale**:
- **Git history preservation**: Use `git mv` to preserve file history
- **Migration script**:
  ```bash
  #!/bin/bash
  # Migration script (run from feature branch)

  # 1. Initialize Nx workspace
  npx create-nx-workspace@latest --preset=apps --nx-cloud=false

  # 2. Move API files
  mkdir -p apps/api
  git mv src apps/api/src
  git mv tests apps/api/tests
  git mv alembic apps/api/alembic
  git mv requirements.txt apps/api/requirements.txt
  git mv pyproject.toml apps/api/pyproject.toml
  git mv Dockerfile apps/api/Dockerfile

  # 3. Move UI files
  mkdir -p apps/ui
  git mv grimoire-ui/* apps/ui/
  rmdir grimoire-ui

  # 4. Create Nx configs
  # (Generate project.json files for each app)

  # 5. Update docker-compose.yml paths
  # 6. Update root package.json
  # 7. Create README.md with new instructions
  ```

**Validation checklist** (all must pass before merge):
- ✅ `nx run api:test` - All API tests pass
- ✅ `nx run ui:test` - All UI tests pass
- ✅ `nx run api:serve` - API starts in <30s
- ✅ `nx run ui:serve` - UI starts in <30s
- ✅ `docker-compose up` - All services start correctly
- ✅ `nx affected:test --base=main` - Affected detection works
- ✅ Git history preserved: `git log --follow apps/api/src/main.py` shows full history

**Rollback plan**:
1. **Before merge**: Feature branch 003-convert-to-monorepo can be abandoned
2. **After merge**: Revert merge commit, then:
   ```bash
   git revert <merge-commit-sha>
   # OR if catastrophic:
   git revert -m 1 <merge-commit-sha>
   ```
3. **Validation**: All original tests still pass in pre-migration structure

**Alternatives Considered**:
- Copy instead of move: Loses git history (violates A-003)
- Manual file moves: Error-prone; scripted approach is repeatable and testable
- No rollback plan: Violates A-009 constraint

**References**:
- Git mv documentation: https://git-scm.com/docs/git-mv
- Nx workspace setup: https://nx.dev/getting-started/intro

---

### 6. CI/CD Integration

**Question**: How to update GitHub Actions workflows to leverage Nx affected detection?

**Investigation**:
- Current workflows likely run all tests on every commit
- Nx affected can optimize CI execution time (SC-004: 30% reduction target)
- Need to handle main branch (all tests) vs PR branches (affected only)

**Decision**: Update GitHub Actions to use nx affected commands

**Rationale**:
- **Selective execution**: Run only affected tests/builds on PRs
- **Full execution on main**: Ensure comprehensive validation before merge
- **Example workflow update**:
  ```yaml
  # .github/workflows/ci.yml (updated)
  name: CI

  on:
    pull_request:
    push:
      branches: [main]

  jobs:
    test:
      runs-on: ubuntu-latest
      steps:
        - uses: actions/checkout@v3
          with:
            fetch-depth: 0  # Required for Nx affected

        - uses: actions/setup-node@v3
        - uses: actions/setup-python@v4

        - name: Install dependencies
          run: |
            npm install
            cd apps/api && pip install -r requirements.txt

        - name: Run affected tests (PR)
          if: github.event_name == 'pull_request'
          run: npx nx affected --target=test --base=origin/main

        - name: Run all tests (main)
          if: github.event_name == 'push' && github.ref == 'refs/heads/main'
          run: npx nx run-many --target=test --all
  ```

**Expected CI improvements**:
- API-only changes: Run only API tests (~2 min instead of ~4 min) = 50% reduction
- UI-only changes: Run only UI tests (~1 min instead of ~4 min) = 75% reduction
- Shared config changes: Run all tests (~4 min) = no change
- **Average**: 30-40% reduction in CI time (exceeds SC-004 target of 30%)

**Alternatives Considered**:
- Manual path filters in GitHub Actions: Less flexible than Nx affected; duplicates logic
- No CI optimization: Wastes resources; defeats monorepo benefit

**References**:
- Nx CI setup: https://nx.dev/ci/intro/ci-with-nx
- GitHub Actions with Nx: https://nx.dev/ci/recipes/set-up/monorepo-ci-github-actions

---

### 7. Developer Workflow and Documentation

**Question**: What documentation and tooling changes are needed to support the new monorepo workflow?

**Investigation**:
- Developers need clear commands for common tasks
- Onboarding should be fast (SC-008: <15 minutes)
- Must maintain workflow familiarity (C-004)

**Decision**: Create comprehensive quickstart.md + update root README.md

**Rationale**:
- **Command clarity**: Document Nx equivalents for existing workflows
- **Quick reference table**:

  | Old Command | New Command | Notes |
  |-------------|-------------|-------|
  | `cd src && uvicorn main:app --reload` | `nx serve api` | API dev server |
  | `cd grimoire-ui && yarn dev` | `nx serve ui` | UI dev server |
  | `pytest` | `nx test api` | API tests |
  | `cd grimoire-ui && yarn test` | `nx test ui` | UI tests |
  | `pip install -r requirements.txt` | `nx install api` | API dependencies |
  | `docker-compose up` | `docker-compose up` | Unchanged |

- **Root README.md** includes:
  - One-command setup: `npm install && nx install api`
  - Quick start: `nx serve api` and `nx serve ui`
  - Link to `specs/003-convert-to-monorepo/quickstart.md` for details

- **quickstart.md** includes:
  - Repository structure overview
  - Installation instructions
  - Common development tasks
  - Troubleshooting guide
  - CI/CD changes
  - Migration from old structure

**Developer experience improvements**:
- **Parallel execution**: `nx run-many --target=test --all --parallel` runs both test suites concurrently
- **Affected commands**: `nx affected:test` runs only changed apps during development
- **Caching**: Nx caches test results; unchanged tests skip re-execution
- **Graph visualization**: `nx graph` shows application dependencies

**Alternatives Considered**:
- Minimal documentation: Would hurt onboarding (violates SC-008)
- Keep old scripts: Confusing to maintain dual workflows; better to fully migrate

**References**:
- Nx run-many: https://nx.dev/nx-api/nx/documents/run-many
- Developer workflow guide: https://nx.dev/getting-started/tutorials/react-monorepo-tutorial

---

## Summary of Key Decisions

| Area | Decision | Primary Benefit |
|------|----------|----------------|
| **Python Integration** | Use nx:run-commands executor | Simplicity, no plugins needed |
| **Python Dependencies** | Keep local to apps/api | Isolation, tooling compatibility |
| **Affected Detection** | Configure inputs in project.json | 30-50% CI time reduction |
| **Docker** | Update paths, keep structure | Minimal changes, preserve optimization |
| **Migration** | Git mv + validation script | History preservation, rollback support |
| **CI/CD** | Nx affected in GitHub Actions | Selective test execution |
| **Documentation** | Comprehensive quickstart.md | <15 min onboarding (SC-008) |

## Open Questions / Risks

### Risk 1: Python Import Analysis
**Issue**: Nx may not fully analyze Python imports for dependency graph
**Mitigation**: Use explicit `implicitDependencies` in project.json; manual testing of affected detection
**Impact**: Low - API is currently isolated from UI, no shared Python code

### Risk 2: CI Pipeline Configuration
**Issue**: GitHub Actions may need significant updates
**Mitigation**: Test workflows in feature branch before merge
**Impact**: Medium - Could delay PR feedback if misconfigured

### Risk 3: Developer Adoption
**Issue**: Team must learn Nx commands
**Mitigation**: Comprehensive documentation + command reference table
**Impact**: Low - Commands are straightforward aliases

## Next Steps (Phase 1)

1. ✅ **Research complete** - All key areas investigated
2. ⏳ **data-model.md** - N/A for this feature (no data model changes)
3. ⏳ **contracts/** - N/A for this feature (no new APIs)
4. ⏳ **quickstart.md** - Create comprehensive developer guide
5. ⏳ **Update CLAUDE.md** - Add Nx to Active Technologies

---

**Research completed**: 2025-10-19
**Ready for Phase 1**: ✅ Yes
