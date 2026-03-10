# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Galadriel is a Test Management System built with **Reflex** (Python web framework, v0.8.7). It manages test suites, scenarios, cases, and cycles, with Jira integration for bug tracking. Uses SQLite for storage and Radix UI/React on the frontend (managed by Reflex).

## Common Commands

```bash
# Setup
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# Database
reflex db init          # First-time database setup
reflex db migrate       # Apply migrations

# Run
reflex run              # Start dev server

# Tests (pytest)
pytest                                          # All tests
pytest tests/test_yaml_utils.py                 # Specific file
pytest tests/test_yaml_utils.py::test_name      # Single test
```

## Architecture

### Module Structure

Each domain module (`suite/`, `scenario/`, `case/`, `cycle/`, `iteration/`, `user/`, `auth/`) follows a consistent pattern:
- `model.py` — SQLModel classes extending `rx.Model` with `table=True`
- `state.py` — Reflex state classes with event handlers and database operations
- Optional UI files (`add_edit_list.py`, `detail.py`, `pages.py`)

### Key Entry Points

- `rxconfig.py` — Reflex configuration (app name, DB URL, Jira settings)
- `galadriel/galadriel.py` — App definition, page routing via `app.add_page()`
- `galadriel/navigation/routes.py` — All route constants and dynamic routes (e.g., `/suites/[id]`)

### Data Model Relationships

```
Suite → SuiteChild → [Scenario, Case]
Scenario → ScenarioCase → Case
Case → Step (ordered), Case → Prerequisite
Cycle → Iteration → IterationSnapshot → IterationSnapshotLinkedIssues
LocalUser → GaladrielUser → GaladrielUserRole
```

### State Management Patterns

- State classes extend `rx.State`; child states extend parent states (e.g., `AddSuiteState(SuiteState)`)
- Database access always via `with rx.session()` context manager
- `@rx.var` decorators for computed properties
- Event handlers return `rx.redirect()` or `rx.toast()` for user feedback
- Soft delete pattern: records use a `deleted` field rather than being removed

### UI Patterns

- Reusable components in `galadriel/ui/components.py` (TopNavBar, Button, SideBar)
- Responsive design via `rx.desktop_only()` / `rx.mobile_and_tablet()`
- Radix UI components wrapped by Reflex

### Utilities

- `utils/yaml.py` — YAML config read/write helpers
- `utils/jira.py` — Jira REST API integration (issue creation/tracking)
- `utils/timing.py` — UTC-aware datetime handling; all timestamps stored in UTC
- `utils/consts.py` — Status constants and shared definitions

### Configuration

- `galadriel.yaml` — Runtime config (Jira credentials). Copy from `galadriel.yaml.template` for first setup.
- Database: SQLite at `galadriel.db`
- Authentication: `reflex-local-auth` with role-based access (admin, editor, viewer)

### Code Quality

- SonarQube/SonarCloud integration for static analysis
- Alembic for database migrations (`alembic/` directory)
- Docstrings on all modules, classes, and public functions/methods (one-liner style)

### After Every Change

- **Tests**: Always run `pytest` after each change, even if no tests were modified. Update or add tests when new logic, helpers, or state vars are introduced.
- **README**: Evaluate whether `README.md` needs updating (e.g., new features, changed behavior).
- **CLAUDE.md**: Evaluate whether this file needs updating (e.g., new patterns, architecture changes).
