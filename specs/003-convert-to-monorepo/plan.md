# Implementation Plan: Monorepo Conversion

**Branch**: `003-convert-to-monorepo` | **Date**: 2025-10-19 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/003-convert-to-monorepo/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Convert the Grimoire project from a dual-directory structure (src/ for API, grimoire-ui/ for frontend) to an Nx-managed monorepo with independent workspace applications. Each application (API and UI) will maintain full independence in terms of running, building, and testing while benefiting from unified dependency management, consistent tooling, and intelligent affected detection for CI/CD optimization.

## Technical Context

**Language/Version**: Python 3.12+ (API), TypeScript 5.3+ (UI), Node.js (Nx orchestration)
**Primary Dependencies**:
- Monorepo: Nx (latest stable), @nx/workspace
- API: FastAPI 0.109.0, SQLAlchemy 2.0.25, Alembic 1.13.1, Anthropic SDK 0.18.0
- UI: Next.js 14.2+, React 18.3+, Prisma 6.17.1, Tailwind CSS 3.4+
- Python plugin: @nx/python or @nrwl/nx-plugin for custom executors

**Storage**: PostgreSQL (existing, managed via Docker Compose - unchanged)
**Testing**:
- API: pytest + pytest-cov
- UI: Jest + React Testing Library + Playwright (e2e)
- Nx: affected command for test orchestration

**Target Platform**:
- API: Linux server (Docker containers)
- UI: Web (Next.js SSR/SSG)
- Development: macOS/Linux workstations

**Project Type**: Monorepo with dual applications (web frontend + API backend)

**Performance Goals**:
- API dev server startup: <30 seconds (isolated)
- UI dev server startup: <30 seconds (isolated)
- Full install (npm install or equivalent): <5 minutes
- CI pipeline reduction: 30% for single-app changes

**Constraints**:
- Zero breaking changes to existing functionality (FR-010, FR-011)
- All existing tests must pass without modification (SC-005, SC-006)
- Docker builds must remain compatible (SC-007)
- Migration must be reversible (A-009)
- Build times must not increase for individual apps (C-005)

**Scale/Scope**:
- 2 applications (API, UI)
- Structure supports future shared libraries
- ~1000 LOC migration scripts/configs
- Existing codebase: ~5000 LOC (estimate based on structure)

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Initial Assessment (Pre-Research)

This feature is primarily an **infrastructure/tooling change** rather than a user-facing feature that adds new capabilities. The Grimoire Constitution focuses on API-first design, data quality, response completeness, performance, and extensibility for word lookup features. This monorepo conversion is a development workflow improvement.

**Evaluation against Core Principles:**

| Principle | Applicable? | Compliance Status | Notes |
|-----------|-------------|-------------------|-------|
| **I. API-First Design** | ❌ Not Applicable | N/A | No new APIs or endpoints being created. Existing APIs remain unchanged (FR-010, FR-011). |
| **II. Data Quality & Accuracy** | ❌ Not Applicable | N/A | No linguistic data changes. Database schemas and data sources unchanged (A-007). |
| **III. Response Completeness** | ❌ Not Applicable | N/A | No changes to word query responses or data structures. |
| **IV. Performance & Efficiency** | ✅ Applicable | ✅ **PASS** | - FR-002/FR-003 ensure independent startup (addresses SC-001/SC-002: <30s startup)<br>- FR-009 provides affected detection (addresses SC-004: 30% CI reduction)<br>- C-005 explicitly constrains: "Build times must not increase"<br>- Performance goals align with constitution's efficiency principle |
| **V. Extensibility** | ✅ Applicable | ✅ **PASS** | - FR-015 ensures support for shared libraries (future extensibility)<br>- Monorepo structure enables easier addition of new applications/services<br>- Workspace configuration provides clear extension points (Key Entities: Workspace, Shared Libraries) |

**Quality Standards Compliance:**

| Standard | Compliance Status | Notes |
|----------|-------------------|-------|
| **Testing Requirements** | ✅ **PASS** | - C-002: "All existing tests must pass without modification"<br>- SC-005/SC-006: 100% test pass rate required<br>- No changes to test content, only execution mechanism (Nx orchestration) |
| **Documentation Requirements** | ✅ **PASS** | - FR-013: "Must provide clear documentation showing how to run each application"<br>- Phase 1 will generate quickstart.md<br>- SC-008: New developers can setup within 15 minutes using docs |
| **Code Quality** | ✅ **PASS** | - FR-014: Linting/formatting preserved across all apps<br>- Existing code quality standards maintained<br>- No code changes to application logic |

**Development Workflow Compliance:**

This feature follows the prescribed workflow:
1. ✅ **Specification**: Complete in `/specs/003-convert-to-monorepo/spec.md`
2. ✅ **API Design**: N/A (no new APIs) - Existing APIs documented in contracts/README.md
3. ⏳ **Test-First**: Existing tests will validate correctness post-migration
4. ⏳ **Implementation**: Pending (next phase: `/speckit.tasks`)
5. ✅ **Documentation**: Complete (quickstart.md generated in Phase 1)
6. ⏳ **Review**: Pending

**GATE RESULT: ✅ PASS**

This infrastructure change does not introduce violations of constitution principles. The feature enhances extensibility (Principle V) and maintains performance standards (Principle IV) while preserving all existing functionality. No exceptions or justifications needed in Complexity Tracking.

---

### Post-Design Assessment (After Phase 1)

**Re-evaluation after completing research and design phases:**

| Principle | Status | Post-Design Notes |
|-----------|--------|------------------|
| **IV. Performance & Efficiency** | ✅ **PASS** | - Research confirmed Nx run-commands approach maintains startup times<br>- Affected detection research validated 30-50% CI time reduction (exceeds SC-004)<br>- Docker integration research confirmed no performance degradation<br>- Caching strategy maintains build performance (C-005) |
| **V. Extensibility** | ✅ **PASS** | - Nx workspace provides clear extension points for future apps/libs<br>- Research validated shared libraries support (libs/ directory)<br>- Custom executors possible if needed in future<br>- Migration strategy preserves reversibility (A-009) |

**Quality Standards Re-evaluation:**

| Standard | Status | Post-Design Notes |
|----------|--------|------------------|
| **Testing Requirements** | ✅ **PASS** | - Validation checklist defined in research.md ensures test compatibility<br>- No test code changes required, only execution wrapper (Nx tasks)<br>- Contract tests, integration tests remain unchanged |
| **Documentation Requirements** | ✅ **PASS** | - quickstart.md provides <15 min onboarding (SC-008)<br>- CLAUDE.md updated with Nx commands and structure<br>- Migration guide included for existing developers<br>- Troubleshooting section addresses common issues |
| **Code Quality** | ✅ **PASS** | - Linting/formatting configs preserved in each app<br>- Nx orchestrates existing tools (ruff, black, mypy, eslint)<br>- No code logic changes required |

**Final Design Validation:**

✅ **All design artifacts complete:**
- research.md: 7 key areas investigated with decisions documented
- data-model.md: N/A confirmed (infrastructure change only)
- contracts/README.md: N/A confirmed (no API changes)
- quickstart.md: Comprehensive developer guide created
- CLAUDE.md: Updated with Nx workspace structure and commands

✅ **No new violations introduced during design phase**

✅ **Constitution compliance maintained**

**FINAL GATE RESULT: ✅ PASS - Ready for implementation planning (`/speckit.tasks`)**

## Project Structure

### Documentation (this feature)

```
specs/003-convert-to-monorepo/
├── plan.md              # This file (/speckit.plan command output)
├── research.md          # Phase 0 output (/speckit.plan command)
├── data-model.md        # Phase 1 output (/speckit.plan command) - N/A for this feature
├── quickstart.md        # Phase 1 output (/speckit.plan command)
├── contracts/           # Phase 1 output (/speckit.plan command) - N/A for this feature
├── checklists/          # Quality validation checklists
│   └── requirements.md  # Spec quality checklist (already created)
└── tasks.md             # Phase 2 output (/speckit.tasks command - NOT created by /speckit.plan)
```

### Current Structure (Pre-Migration)

```
grimoire/
├── src/                    # Python API source
│   ├── main.py
│   ├── models/
│   ├── services/
│   └── api/
├── tests/                  # Python API tests
├── grimoire-ui/           # Next.js UI application
│   ├── src/
│   │   ├── app/
│   │   ├── components/
│   │   └── hooks/
│   ├── prisma/
│   └── package.json
├── alembic/               # Python DB migrations
├── scripts/
├── pyproject.toml         # Python project config
├── requirements.txt       # Python dependencies
├── package.json          # Root package config (Prisma only)
├── docker-compose.yml
└── Dockerfile
```

### Target Structure (Post-Migration)

```
grimoire/                  # Monorepo root
├── apps/
│   ├── api/              # Python FastAPI application
│   │   ├── src/          # Moved from /src
│   │   │   ├── main.py
│   │   │   ├── models/
│   │   │   ├── services/
│   │   │   └── api/
│   │   ├── tests/        # Moved from /tests
│   │   ├── alembic/      # Moved from /alembic
│   │   ├── pyproject.toml
│   │   ├── requirements.txt
│   │   ├── project.json  # Nx project configuration
│   │   └── Dockerfile    # Updated Dockerfile for monorepo context
│   │
│   └── ui/               # Next.js UI application
│       ├── src/          # Moved from /grimoire-ui/src
│       ├── prisma/       # Moved from /grimoire-ui/prisma
│       ├── public/       # Moved from /grimoire-ui/public
│       ├── package.json  # Moved from /grimoire-ui/package.json
│       ├── next.config.js
│       ├── tailwind.config.ts
│       ├── tsconfig.json
│       └── project.json  # Nx project configuration
│
├── libs/                 # Shared libraries (future - structure only)
│   └── .gitkeep
│
├── tools/                # Custom Nx plugins and scripts (if needed)
│   └── .gitkeep
│
├── nx.json               # Nx workspace configuration
├── package.json          # Root package.json with Nx dependencies
├── tsconfig.base.json    # Base TypeScript config for workspace
├── docker-compose.yml    # Updated paths to apps/api and apps/ui
├── .gitignore            # Updated for Nx artifacts
└── README.md             # Updated with monorepo instructions
```

**Structure Decision**: Nx monorepo with applications organized under `apps/` directory. This follows Nx conventions and provides:
- Clear separation between API (Python) and UI (TypeScript/Next.js)
- Future support for shared libraries under `libs/`
- Isolated project configurations via `project.json` files
- Preserved existing directory structures within each app (minimal code movement)
- Docker compatibility via path updates in docker-compose.yml and Dockerfiles

## Complexity Tracking

*Fill ONLY if Constitution Check has violations that must be justified*

**No violations found.** Constitution Check passed for all applicable principles. This section is intentionally empty.
