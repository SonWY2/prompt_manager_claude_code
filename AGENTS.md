# AI Agents Development Guide

**Last Updated**: 2026-02-22

## Overview

This document defines the development standards and architectural patterns that must be followed during AI Agent development. All AI Agents and developers must comply with these rules.

---

## 1. User Interaction Guidelines

### 1.1. Language
- **Rule**: Always interact with users in **Korean**.
- **Implementation**:
  - Write all questions, explanations, and suggestions in Korean
  - Write code comments in Korean (exception: when agreed upon within the team)
  - Technical terms may be used in their original language

### 1.2. Decision Making
- **Rule**: All decisions must be made **after discussion** with the user.
- **Implementation**:
  - Present multiple options before design decisions
  - State pros and cons of each option
  - Provide recommended option with rationale
  - Proceed with implementation after final user approval

### 1.3. Prohibit Magic Numbers
- **Rule**: Never use **Magic Numbers**.
- **Implementation**:
  - Define constants explicitly (UPPER_CASE_NAMING)
  - Central management in config files or config modules
  - Document meaning in comments (when unavoidable)

### 1.4. Design Specification Compliance
- **Rule**: When a design data file exists as an .md file, **you must use that design exactly as-is** to construct the UI.
- **Implementation**:
  - Verify the design .md file first before starting UI work
  - Implement all specs specified in the design file (layout, colors, fonts, margins, etc.) exactly
  - Only add elements not specified in the design file at developer's discretion
  - When implementation needs to differ from the design file, discuss with the user first before deciding
  - Design file paths are specified in project documentation

---

## 2. File Structure Guidelines

### 2.1. Python File Length Limit
- **Rule**: All Python files must not exceed **500 lines**.
- **Reasoning**: Ensure readability, maintainability, and testability
- **Action**: Immediately perform **modularization** when exceeding 500 lines

### 2.2. File Documentation
- **Rule**: All newly created files must include `[overview]` and `[description]` tags in the top docstring.

### 2.3. File Search Optimization
- **Reasoning**: Enable understanding of file purpose during search through `[overview]` and `[description]` tags.

### 2.4. Module Documentation
- **Rule**: When a specific module is created (folder-based), a `usage.md` file must be created under that folder.
- **Implementation**:
  - Clearly organize module usage instructions
  - **Include diagrams**: Create various diagrams to help developers understand, such as Class Diagram, Sequence Diagram, State Diagram
  - **ASCII visualization**: Visualize diagrams in ASCII art so they can be clearly understood in text format
  - Include actual usage examples and code samples
  - Specify dependencies and interactions between modules
- **Purpose**: Help developers quickly understand and utilize the structure and behavior of modules.

### 2.5. Module Map & Documentation Synchronization
- **Rule**: Always reference the repository module map before editing code, and keep the module map in sync with major code changes.
- **Implementation**:
  - Use the module map in this document as the first source of truth for deciding where to read/edit code.
  - Treat the following as synchronization triggers:
    - File/folder add, delete, rename, or move in `src/`
    - Public interface changes (constructor signature, exported class/function, cross-module contract)
    - Dependency direction changes across `gui/core/data/utils`
    - Plugin hook/interface changes (`TaskPlugin`, `LLMPlugin`, `ProviderPlugin`)
    - Integration boundary changes (entrypoint flow, prompt execution flow, snapshot format)
  - Apply code and document updates in the same change set whenever possible.
  - On mismatch between docs and code, update `AGENTS.md` first, then align `usage.md` and `README.md`.
- **Purpose**: Prevent stale architecture docs and ensure every action references the correct module boundary.

---

## 3. Core Architectural Principles

### 3.1. Modularity
- **Rule**: All new features must be implemented as **separate modules**.
- **Implementation**:
  - One module = one clear responsibility
  - Minimal dependencies between modules
  - Interface-based communication

### 3.2. Independence
- **Rule**: Modules must operate **independently**.
- **Implementation**:
  - Prohibit direct access to other modules' internal state
  - Communicate only through explicitly defined interfaces
  - Use Dependency Injection

---

## 4. Main Logic & Plugin Architecture

### 4.1. The Pattern
The core architecture pattern is the **Main Logic + Plugin** pattern.

1. **Main Logic**: Defines basic control flow (performs core tasks)
2. **Plugins**: Encapsulates additional/optional behaviors (extensions)

### 4.2. Implementation Rules

**Main Logic**:
- Must define extension points (hooks)
- Do not hardcode optional logic
- Provide dynamic/explicit plugin loading mechanism

**Plugins**:
- Implement standard interfaces defined by Main Logic
- Located in `plugins/` subdirectory of extension modules
- Loaded only when needed

### 4.3. Directory Structure
```
my_module/
├── core.py                # Main Domain Logic
├── plugin_interface.py    # Interface Definition (ABC)
└── plugins/               # Plugin Implementations
```

---

## 5. Utility Functions

Utility functions should be logically organized to maintain a clean codebase.

### 5.1. Standard Utilities
- **Rule**: Pure utility functions that do not depend on domain logic must be organized in the `utils/` directory.

### 5.2. Placement Rules
- **Local Utilities**: Utilities used only in a single module → `[module_name]/utils/`
- **Global Utilities**: Utilities shared by multiple modules → project-level `src/utils/`

### 5.3. Naming Convention
- Use descriptive filenames within `utils/` directory

---

## 6. Code Style Guidelines

### 6.1. Imports
- **Ordering**: Standard library → Third-party → Local modules
- **Grouping**: Blank line between each group
- **Style**: `from x import y` (prefer specific imports)
- **No Wildcards**: Do not use `from module import *`

```python
# ✅ Good
import json
from pathlib import Path

import requests
from PySide6.QtWidgets import QWidget

from src.core.task_manager import TaskManager
```

### 6.2. Type Hints
- **Rule**: Add type hints to all functions
- **Complex Types**: Use `typing` module (`List`, `Dict`, `Optional`, `Union`)
- **Custom Types**: Define `TypeAlias` for complex types

```python
from typing import List, Dict, Optional, TypeAlias

TaskId: TypeAlias = str

def get_task(task_id: TaskId) -> Optional[Task]:
    """Retrieve task by ID"""
    ...
```

### 6.3. Naming Conventions
- **Variables/Functions**: `snake_case`
- **Classes**: `PascalCase`
- **Constants**: `UPPER_CASE`
- **Private members**: `_leading_underscore`

### 6.4. Error Handling
- **Specific Exceptions**: Use specific exceptions
- **Never silent catch**: Prohibit empty `except:` blocks
- **Logging**: Use logging module
- **Custom exceptions**: Define domain-specific exception classes

```python
# ✅ Good
from src.utils.exceptions import TaskNotFoundError

try:
    task = get_task(task_id)
except TaskNotFoundError as e:
    logger.error(f"Task not found: {task_id}")
    raise
```

---

## 7. Build, Lint, Test Commands

### 7.1. Installation
```bash
# Create virtual environment
python3.12 -m venv venv
source venv/bin/activate  # Linux/Mac

# Install dependencies
pip install -r requirements.txt
```

### 7.2. Linting (Recommended Tools)
```bash
# Ruff (fast Python linter/formatter)
pip install ruff
ruff check src/               # Linting
ruff check --fix src/         # Auto-fix

# mypy (type checking)
pip install mypy
mypy src/
```

### 7.3. Testing (Recommended Setup)
```bash
# Install pytest
pip install pytest pytest-cov pytest-qt

# Run all tests
pytest tests/

# Run single test
pytest tests/test_task_manager.py::test_create_task

# Run specific test directory
pytest tests/core/

# Coverage report
pytest --cov=src --cov-report=html tests/
```

### 7.4. Formatting (Recommended)
```bash
# Black (code formatter)
pip install black
black src/ tests/

# isort (import organizer)
pip install isort
isort src/ tests/
```

---

## 8. Agent Instructions

### 8.1. System Prompt Injection
When requesting work from an AI Agent, activate the following rule:

> "Always follow the architectural patterns and rules defined in `AGENTS.md`."

### 8.2. Workflow Checklist

Before starting work:
- [ ] Familiarize yourself with architectural patterns in `AGENTS.md`
- [ ] Locate target code via the repository module map first (do not jump across layers blindly)
- [ ] Check file length (keep within 500 lines)
- [ ] Discuss decisions with user
- [ ] Confirm inclusion of `[overview]`, `[description]` tags
- [ ] Identify whether `AGENTS.md` module map sync is required for this change

During development:
- [ ] Maintain modularity (single responsibility principle)
- [ ] Ensure independence (prevent side effects)
- [ ] Confirm no Magic Numbers
- [ ] Follow plugin pattern (extensible features)
- [ ] Keep code updates and module-map documentation updates in the same work unit when triggers are met

When completing work:
- [ ] Confirm file length is 500 lines or less
- [ ] Complete documentation ([overview], [description])
- [ ] When creating module, write usage.md and include diagrams
- [ ] Verify `AGENTS.md` module map still matches actual `src/` structure and dependency direction
- [ ] No LSP Diagnostics errors
- [ ] Verify compliance with architectural standards

---

## 9. Repository Module Map (Authoritative)

### 9.1. Runtime Entry Flow

```
main.py
  -> src/gui/main.py
       -> src/gui/main_window.py

run.py
  -> src/gui/main_window.py
```

### 9.2. Layer Map and Responsibilities

- `src/gui/`:
  - UI composition and user interaction orchestration.
  - Key orchestrators:
    - `src/gui/main_window.py`: main coordinator for task/version/provider flows.
    - `src/gui/main_window_ui.py`: menu/toolbar/layout assembly.
    - `src/gui/prompt_runner.py`: prompt render + LLM call + result viewer update.
  - GUI helper/integration modules:
    - `src/gui/main_window_helpers.py`, `src/gui/main_window_constants.py`
    - `src/gui/theme.py`, `src/gui/qt_platform.py`
    - `src/gui/widgets/modal_dialog_factory.py`, `src/gui/widgets/result_viewer_styles.py`
  - Feature widgets:
    - task/prompt/result widgets and provider management widgets under `src/gui/widgets/`.

- `src/core/`:
  - Main business logic and extension hooks.
  - Domain managers:
    - `task_manager.py`, `version_manager.py`, `provider_manager.py`, `llm_service.py`
  - Supporting domain logic:
    - `template_engine.py`, `prompt_snapshot.py`, `plugin_interface.py`

- `src/data/`:
  - Persistent model and repository layer.
  - `models.py` (Pydantic models), `repository.py` (CRUD abstraction), `database.py` (TinyDB lifecycle).

- `src/utils/`:
  - Shared, domain-independent utilities and constants.
  - `config.py`, `id_generator.py`, `string_utils.py`, `logger.py`

### 9.3. Dependency Direction Rules

- Primary allowed direction:
  - `Entrypoint -> GUI -> Core -> Data -> Utils`
- Additional allowed path:
  - `GUI -> Data models` only for UI representation needs (for example provider dialog/list typing).
- Forbidden direction:
  - `Data -> Core/GUI`
  - `Core -> GUI`
  - `Utils -> Core/Data/GUI`

### 9.4. Plugin and Extension Boundaries

- `TaskPlugin` interface: `src/core/plugin_interface.py`, executed by `TaskManager` hooks.
- `LLMPlugin` interface: `src/core/llm_service.py`, executed at `before_call` and `after_call` hooks.
- `ProviderPlugin` interface: `src/core/provider_manager.py`, executed around provider lifecycle and connection test hooks.
- Plugin implementation location policy:
  - Place concrete plugin implementations in a module-local `plugins/` directory when introduced.
  - Current repository state: interfaces/hooks exist, but concrete `plugins/` implementations are not yet present.

### 9.5. Special Integration Boundaries

- Prompt execution boundary: `src/gui/prompt_runner.py`
  - Converts editor input to rendered prompt and delegates LLM execution.
- Prompt snapshot boundary: `src/core/prompt_snapshot.py`
  - Owns serialize/deserialize contract for `Version.content` payload.

### 9.6. Module Map Maintenance Rules

- Any trigger in section 2.5 requires updating this section (`## 9`) in the same work stream.
- If code and map diverge, architecture corrections must be documented here before task completion.
- This section is the mandatory reference point for future code navigation and edit planning.

---

## 10. FAQ

**Q: What if I need code longer than 500 lines?**
A: Separate functionality logically into multiple modules.

**Q: When should I use the plugin pattern?**
A: Use when features are extensible or require optional behavior.

**Q: What's the difference between Utils and Helper?**
A: Utils = Pure functions (domain-independent), Helper = Domain-specific logic.

**Q: What's the difference between [overview] and [description]?**
A: overview = One-line summary (for searching), description = Detailed explanation (for understanding).

**Q: When should I write usage.md?**
A: Write under the corresponding folder whenever a new module (folder) is created. It is not needed when modifying a single file.

**Q: What diagrams should be included in usage.md?**
A: Include necessary diagrams in ASCII art format depending on module characteristics: Class Diagram (class structure), Sequence Diagram (method call flow), State Diagram (state transitions).

**Q: When must I update the module map in AGENTS.md?**
A: Update it whenever a module boundary, dependency direction, public cross-module interface, plugin hook/interface, or integration flow changes.

---

*This document will be continuously updated as the project progresses. Submit change suggestions via issues.*
