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

- **Tests**: Always run `pytest` after each change, even if no tests were modified. Always add or update tests when new logic, helpers, or state vars are introduced — tests are mandatory, not optional.
- **Docstrings**: Always add docstrings to new modules, classes, and public functions/methods (one-liner style). Update existing docstrings when behavior changes.
- **Dead code**: After removing UI elements or refactoring, check for variables, imports, or helpers that became unused and remove them.
- **Duplication**: Always check for duplicated code and extract shared helpers, constants, or base classes. Use string constants for repeated literals, shared UI components for repeated rendering patterns, and test mixin classes for repeated test logic across modules.
- **README**: Evaluate whether `README.md` needs updating (e.g., new features, changed behavior).
- **CLAUDE.md**: Evaluate whether this file needs updating (e.g., new patterns, architecture changes).

### Evaluating PR Review Comments (CodeRabbit, SonarQube, etc.)

When the user shares comments from automated review tools, **verify each finding against the current code before making any change**.

#### Triage Criteria

1. **Is it real?** — Read the actual code at the referenced location. Automated tools sometimes flag code that was already fixed, moved, or doesn't exist in the current diff.
2. **Is it relevant?** — Some suggestions target patterns that are intentional in this codebase (e.g., Reflex-specific conventions, `# NOSONAR` annotations, soft-delete patterns).
3. **Is it correct?** — Verify the suggested fix is technically sound. Tools sometimes propose changes that break framework-specific behavior (e.g., suggesting standard HTML attributes when Reflex/React requires camelCase or different prop types).
4. **Is it scoped?** — Only fix what the comment identifies. Don't expand the change to refactor surrounding code unless explicitly asked.

#### What to Verify for Each Comment

- Check the file and line number — confirm the flagged code still exists and matches the description.
- Reproduce the issue mentally or via tests — understand *why* it's a problem before fixing.
- If the suggestion involves a Reflex/Radix component, verify prop names and types against the actual framework API (e.g., `auto_complete` is a `bool` in `rx.input`, not a string).
- If the suggestion involves HTML/React, remember React uses camelCase attributes (`autoComplete`, not `autocomplete`).
- Run `pytest` after applying any fix.

#### Non-Goals (Do Not Blindly Apply)

- **Style-only suggestions** (rename variables, reorder imports) unless they fix a real readability problem.
- **"Consider using X"** suggestions that add complexity without fixing a bug or measurable issue.
- **Framework upgrade suggestions** (e.g., "use the new API") when the project pins a specific version.
- **Overengineering fixes** — e.g., adding error handling for scenarios that cannot occur, or creating abstractions for one-time patterns.
- **Suggestions that conflict with existing project patterns** — match what the codebase already does rather than introducing a new convention from one tool's opinion.
