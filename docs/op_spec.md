# OP — Personal Operations Planner Specification

## 1. Overview & Philosophy

**OP** is a terminal-centric personal operating layer designed to answer one central question: **"What deserves my attention now, what am I trying to move forward, what repeats, and what is fixed in time?"**

OP is not a generic task manager or an administrative database to manually curate. Instead, it acts as a **calculated projection** over personal data streams—combining a modified Getting Things Done (GTD) workflow, habit tracking, financial tracking, calendar integration, and periodic reviews into a unified terminal dashboard.

### Core Principles
- **Radical Simplicity**: A lightweight architecture prioritizing clarity and ease of maintenance over complexity.
- **Projection over State**: The dashboard and views are computed dynamically from primary records rather than manually maintained.
- **Low Friction Capture**: Plain-text capture without mandatory structure at creation time.
- **Resource Reference, Not Storage**: OP links to external resources (Obsidian notes, Git repositories, filesystem paths, URLs) rather than becoming a document store.
- **Rule-Based Recurrence**: Recurrence is evaluated on the fly rather than generating unbounded future records.
- **State Progression over Deletion**: Completed projects, cancelled tickets, and historical items transition state to maintain long-term personal context.
- **Single Flat File Persistence**: Storage relies on a single JSON document (`planner.json`) acting as a simple, transparent database inside `OP_DATA_DIR`.

---

## 2. LLM & Machine Agent Guidelines

This is a personal programming project built for enjoyment and deliberate practice. Human and AI roles are strictly partitioned as follows:

1. **Application Code Ownership**: All application source code (`src/`) is written exclusively by the human developer. LLM agents must **never** write application code or offer unsolicited code suggestions unless explicitly requested.
2. **Git & Version Control**: LLM agents must **never** execute `git commit`, `git push`, or alter git history.
3. **Authorized Agent Responsibilities**:
   - **Specification Maintenance**: Keep this specification document ([`docs/op_spec.md`](file:///Users/vernon/lab/op/docs/op_spec.md)) organized, accurate, and aligned with development discussions.
   - **Ticket System Management**: Define, track, and manage development tickets, milestones, and task breakdowns.
   - **Testing & E2E Verification**: Write, maintain, and expand end-to-end (E2E), integration, and unit tests in `tests/`.
4. **Agent Attribution & Code Auditing**:
   - Whenever an LLM writes or modifies a test file, test class, test function, or helper, it **must** include an explicit comment or docstring specifying the exact agent name/model that generated it (e.g., `# Authored by Antigravity Agent (Gemini 3.7 Flash)` or `"""Authored by Antigravity Agent (Gemini 3.7 Flash) for E2E validation."""`).
   - This ensures transparent provenance and facilitates code auditing.
5. **License Compliance (MIT)**:
   - Any code or tests contributed by an AI agent must strictly conform to the project's **MIT License**.
   - Agents must not introduce proprietary, copyrighted, copyleft/GPL-tainted, or license-incompatible code snippets.

---

## 3. Storage & Data Architecture

To achieve maximum simplicity, portability, and zero-infrastructure overhead, OP stores all data in a **single JSON file** (`planner.json`) located in `OP_DATA_DIR` (configured via environment variable, defaulting to `~/.op`).

### Directory Layout
```text
OP_DATA_DIR/
└── planner.json         # Unified JSON document storing all planner data
```

### Base Document Schema
The base structure initialized by `op` (defined in `config.py`) consists of top-level dictionary tables:

```json
{
  "bucket": {},
  "projects": {},
  "tickets": {},
  "parked": {},
  "habits": {},
  "habit_log": {},
  "accounts": {},
  "balances": {},
  "calendar": {}
}
```

### Architecture Benefits
- **Atomic Operations**: Straightforward whole-document reads and writes eliminate multi-file synchronization edge cases.
- **Portability & Backups**: A single file makes snapshots, version control, syncing (e.g., via Syncthing/Dropbox/Git), and manual inspection trivial.
- **Zero Query Overhead**: In-memory dictionary manipulation with simple persistence semantics.

---

## 4. Domain Model & Entities

```text
                     CAPTURE
                        │
                      bucket
                        │
                     Process
           ┌────────────┼────────────┐
           ▼            ▼            ▼
        projects     tickets       parked
           │            │     (Someday / Maybe)
           └──── tickets ┘
                  │
                  ▼
             WORK STREAM

  habits & habit_log ───────┐
  calendar ─────────────────┤
  projects & tickets ───────┼───►  DASHBOARD ("What matters now?")
  Periodic Reviews ─────────┤
  accounts & balances ──────┘
```

### 4.1 Bucket (Unprocessed Capture)
The entry point for all raw thoughts, tasks, and ideas with near-zero friction.
- **Stored In**: `planner.json["bucket"]` (keyed by item ID)
- **Fields**: ID, raw text content, capture timestamp, status (`fresh`, `scheduled`, `processed`, `archived`).
- **Lifecycles**:
  - `fresh`: Newly captured item awaiting processing.
  - `scheduled`: Deferred to surface on or after a future date.
  - `processed`: Converted into a project, ticket, or habit.
  - `parked`: Moved to `planner.json["parked"]` as a someday/maybe item.

### 4.2 Parked (Someday / Maybe)
Ideas, aspirational projects, or deferred items that have no active commitment today.
- **Stored In**: `planner.json["parked"]` (keyed by item ID)
- **Fields**: ID, title/description, category/area, parked timestamp, review cadence/trigger, status (`parked`, `reactivated`, `archived`).
- **Surfacing**: Reviewed during periodic review cadences (weekly/monthly) or activated into active projects/tickets when ready.

### 4.3 Projects
A high-level outcome or deliverable with defined completion criteria.
- **Stored In**: `planner.json["projects"]` (keyed by UUID string)
- **Fields**: `pk` (UUID), `name`, `spec` (description), `done_when` (completion criteria), `state` (`not_started`, `active`, `done`, `archived`), `date_created` (ISO date), `resources` (dictionary of `ProjectResource` models).
- **Resource Pointers (`ProjectResource`)**: Structured metadata items with `type` (e.g., `repo`, `doc`, `link`), human-readable `label`, and external `location` (filesystem path, URL, Obsidian note).
- **CLI Commands**:
  - `op project create <id>`: Promote a bucket item into a project and discard the bucket item.
  - `op project list [--all|--state [new|done|archived]]`: List projects.
  - `op project show <id>`: Display project details and its attached resources.
  - `op project set <id>`: Interactively transition project lifecycle state.
  - `op project resources --add <id>`: Interactively attach one or more resources to an existing project.
  - `op project resources --remove <id>`: Interactively select and remove a resource from a project.
- **Tickets Link**: A project will aggregate related tickets.

### 4.4 Tickets (Actionable Work Units)
Individual executable steps. Diverging from strict single-next-action GTD, a project may have multiple parallel actionable tickets simultaneously, or tickets may exist as standalone next actions.
- **Stored In**: `planner.json["tickets"]` (keyed by UUID string)
- **Fields**: `pk` (UUID), `title`, `state` (`open`, `in_progress`, `done`, `cancelled`), `project` (optional project UUID string or `None`), `actionable` boolean, `context` string, `date_created` (ISO date), `date_completed` (optional ISO date), `time_bound` boolean, `due_at` (optional ISO datetime).
- **Validation Rules**:
  - `time_bound` is automatically inferred as `True` if `due_at` is set.
  - If `time_bound=True`, a valid `due_at` must be supplied.
- **CLI Commands**:
  - `op ticket create`: Interactively create a standalone next-action ticket.
  - `op ticket create <id>`: Convert a bucket item into a ticket (discarding the bucket) or attach a new ticket/action to an existing project.

### 4.5 Habits & Routines
Recurring items structured with a strict separation between **Definition** and **History**.

- **Habit Definitions (`planner.json["habits"]`)**:
  - Name, description, cadence rule (e.g., daily, weekdays, weekly on Saturday), target frequency.
  - `tracked` flag:
    - **Tracked Habits** (`tracked = true`): Core habits where historical compliance, streaks, and trends matter (e.g., language study, exercise). Changes in schedule do not rewrite historical expectations.
    - **Untracked Routines** (`tracked = false`): Recurring maintenance tasks that need to surface at specific times without generating historical statistics or log noise (e.g., laundry, taking out trash).
- **Habit Log (`planner.json["habit_log"]`)**:
  - Immutable historical execution entries: `date`, `habit_id`, `status` (`done`, `skipped`, `failed`), notes.
- **Recurrence Engine**: Dynamically derives whether a routine applies to the current date on-the-fly rather than populating static future records.

### 4.6 Calendar Integration & Time Models
- **Stored In**: `planner.json["calendar"]`
- **Hard Landscape**: Fixed-time commitments, meetings, flights, and appointments (integrated with Google Calendar). These represent non-negotiable time occupied.
- **Deadlines vs. Appointments**:
  - **Appointment**: Event anchored to a specific time interval (e.g., "Flight departs 11:30").
  - **Deadline**: Boundary date before which work can be completed asynchronously (e.g., "Submit tax form by Aug 17").

### 4.7 Finances
Lightweight daily balance tracking across user-defined accounts.
- **Stored In**: `planner.json["accounts"]` (definitions/metadata) and `planner.json["balances"]` (timestamped balance logs).
- **Accounts**: Checking, savings, investments, credit cards, loans.
- **Balance Logging**: Accounts record balance snapshots with timestamps.
- **Rolled Balances**: If an account balance is not updated on a given day, the previous recorded balance is automatically rolled forward (assuming zero net change).
- **Daily Net Worth**: Sum of all asset balances minus liabilities computed on demand for any date.

### 4.8 Reviews (First-Class Concept)
Dedicated diagnostic and reflective modes assembled for recurring review cadences:
- **Cadences**: Weekly (Sunday), Monthly, Annual / Birthday.
- **Aggregated Review Projections**:
  - Unprocessed bucket items and parked items
  - Active projects with no actionable tickets
  - Stale / stagnant projects
  - Habit adherence trends and drifting routines
  - Waiting / blocked tickets
  - Upcoming hard-calendar landscape for the upcoming period

### 4.9 Dashboard
The primary daily terminal projection computed at runtime. Synthesizes today’s state across all modules:
1. Hard landscape calendar events for today.
2. Tracked habits and untracked routines scheduled for today.
3. Priority actionable tickets matching the active context.
4. Alerts: Unprocessed bucket count, unreviewed accounts, or blocked dependencies.

---

## 5. Development & Ticket Workflow

To facilitate incremental, test-driven development:
- **Ticket Tracking**: Milestones and task tickets will be defined in dedicated tracking documents managed by the LLM agent.
- **Test-Driven Collaboration**:
  - Human specifies the next feature/component.
  - LLM prepares end-to-end / integration tests and fixtures with proper LLM attribution docstrings specifying agent/model.
  - Human writes the implementation code in `src/` to satisfy the tests.
  - LLM validates tests, updates test suites, and updates the spec/tickets accordingly.
