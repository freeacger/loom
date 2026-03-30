# Terminal-Friendly Character Diagram Style Guide

> **Purpose:** Authoritative reference for ASCII/Unicode character diagrams across all skills.
> Update this file first, then propagate the relevant subset to each SKILL.md.
> This file is NOT published with skills — it stays in the source repo as an author reference.

## 1. Character Set

### 1.1 Primary Characters (safe in all modern terminals)

```
Box drawing:  ├── └── │ ─ ┌ ┐ ┬ ┴ ┼
Arrows:       → ← ↓ ↑
Blocks:       █ ░
Symbols:      ✓ ✗ ○ ●
Brackets:     [ ] { } < >
```

### 1.2 Banned Characters

- **Emoji** — variable width, breaks alignment
- **Mixed arrow styles** — never mix `→` with `--->` in the same diagram
- **Half-width CJK** — ambiguous width in different terminals
- **`:` or `.` as lifelines** — use `│` only

### 1.3 CJK Width Rule

CJK characters are double-width in monospace fonts. Never align ASCII-art columns to CJK character boundaries. Place tree structure on the left margin and let CJK text flow naturally after branch characters.

## 2. General Rules

- **Max width:** 78 characters (fits 80-column terminal with 1-char padding)
- **Code blocks:** Wrap all diagrams in fenced code blocks with no language tag
- **When to add a diagram:**

| Condition | Diagram type |
|-----------|-------------|
| 3+ nested items with parent-child relationships | Tree |
| 3+ components exchanging data or messages | Sequence/flow |
| A state has 3+ possible transitions | State machine |
| 3+ options compared across 2+ quantitative dimensions | Star ratings |
| A process fans out to 3+ parallel paths | DAG |

- **When NOT to add a diagram:**
  - A flat list or markdown table already communicates clearly
  - 2 nodes and 1 arrow (not enough structure)
  - Linear sequence with no branching (use numbered list)

## 3. Tree Diagrams

**Used by:** design-structure, design-refinement

```
design_tree
├── 1. Problem definition
│   ├── 1.1 Core problem
│   └── 1.2 Success metrics ✓
├── 2. Core flows [OPEN]
│   ├── 2.1 Happy path
│   └── 2.2 Error path
├── 3. Interfaces and data
│   └── 3.1 API contract [DRAFT]
├── 4. External integrations
│   └── 4.1 Payment provider SDK [RESEARCH]
└── 5. Decision points
    └── 5.1 Storage choice [DECISION]
```

**Rules:**
- First-level branches use `├──` (middle) and `└──` (last)
- Continuation lines: `│   ` (pipe + 3 spaces) for non-last parents, `    ` (4 spaces) for last
- Numbering: `1.`, `1.1`, `1.1.1` — required at first two levels, optional deeper
- Status markers at end of leaf text, space-separated

**Status markers:**

| Marker | Meaning |
|--------|---------|
| `[OPEN]` | Unresolved, needs refinement or decision |
| `[DECISION]` | Decision node with multiple real options |
| `[DRAFT]` | Tentative, may change |
| `[RESEARCH]` | Depends on an external tool, API, library, or service that has passed initial feasibility check but needs deeper validation |
| `✓` | Complete / verified |
| `✗` | Rejected / out of scope |

## 4. Sequence Diagrams

**Used by:** design-refinement

```
Client          API Server      Auth Service     DB
  │                │                │             │
  │── request ────→│                │             │
  │                │── verify ────→│             │
  │                │←── ok ────────│             │
  │                │── insert ─────────────────→│
  │←── response ───│                │             │
```

**Rules:**
- Three-column maximum. Split into two diagrams if more participants needed
- Participant names left-aligned at the top, ≤20 chars each
- Lifelines use `│`
- Messages: `──→` (left-to-right), `←──` (right-to-left)
- Message labels sit on the arrow line: `── label ──→`
- Labels ≤15 chars per segment; for longer labels use `── label ──→`
- Omit simple ACK return arrows unless they carry meaningful data

## 5. Data Flow Diagrams

**Used by:** design-refinement

```
Source
    │
    ▼
Transform ──── enrich ────→ Enrichment Service
    │                            │
    │                            │ metadata
    ▼                            ▼
Sink A                     Cache Store
    │
    └───────── aggregate ◄──────┘
```

**Rules:**
- Components are plain text (no `[` `]` boxes)
- Vertical flow: `│` and `▼`
- Horizontal flow: `──→`
- Feedback/return paths: `◄────`
- Labels above or alongside arrows

## 6. State Machine Diagrams

**Used by:** design-refinement

```
         ┌──────────┐
    ┌────│ Pending  │────┐
    │    └──────────┘    │
    │ timeout            │ approve
    ▼                    ▼
┌─────────┐        ┌───────────┐
│ Expired │        │ Approved  │
└─────────┘        └───────────┘
                        │
                   │ start
                   ▼
               ┌──────────┐     success     ┌───────────┐
               │ Running  │───────────────→│ Succeeded │
               └──────────┘                 └───────────┘
                    │
               │ fail
               ▼
           ┌─────────┐
           │ Failed  │──→ retry ──→ Pending
           └─────────┘
```

**Rules:**
- State boxes use `┌ ┐ └ ┘ ─ │`
- State names centered inside the box
- Transitions: `──→` with label above or below
- Self-loops: write as text annotation, don't draw
- Terminal states can include `✓` or `✗` markers

## 7. Comparison Charts

**Used by:** decision-evaluation

### 7.1 Star Ratings (quantitative comparison)

```
Overall Rating:

Auth0:      ★★★★☆  4/5
Keycloak:   ★★★☆☆  3/5
Self-build: ★☆☆☆☆  1/5

Dimension Breakdown:

Security:       Auth0 ★★★★★  Keycloak ★★★★☆  Self ★★☆☆☆
Speed-to-MVP:   Auth0 ★★★★★  Keycloak ★★★☆☆  Self ★☆☆☆☆
Cost-at-scale:  Auth0 ★★★☆☆  Keycloak ★★★★☆  Self ★★★★★
```

**Rules:**
- `★` (filled, U+2605) + `☆` (empty, U+2606), 5-star scale (max = ★★★★★)
- Always show all 5 stars (e.g. `★★☆☆☆`, never `★★`)
- Format: `label ★★★★☆  4/5`
- Overall rating section first, then Dimension Breakdown
- Breakdown section: one dimension per row, all options on same row
- Scale always stated explicitly

**When to use:** Only for 3+ options × 2+ quantitative dimensions. Use markdown tables for simple qualitative comparisons.

### 7.2 Architecture Topology

```
┌──────────────────┐
│  Load Balancer   │
└────────┬─────────┘
         │
    ┌────┴────┐
    ▼         ▼
 [API x2] [API x2]
    │         │
    └────┬────┘
         ▼
  ┌────────────┐
  │  Postgres  │
  └────────────┘
```

**Rules:**
- Boxes use `┌ ┐ └ ┘ ─ │`
- Components wrapped in boxes (unlike data flow diagrams)
- Vertical flow is primary
- Fan-out/fan-in uses `┌────┘` / `└────┐` / `└─────┬─────┘` patterns

## 8. DAG / Dependency Diagrams

**Used by:** design-orchestrator, task-brief (decompose mode)

```
          [task-brief]
               │
               ▼
      [design-orchestrator]
          │    │    │
     ┌────┘    │    └────┐
     ▼         ▼         ▼
[structure] [refine] [evaluate]
     │         │         │
     └────┬────┘─────────┘
          ▼
    [readiness-check]
          │
          ▼
    [writing-plans]
```

**Rules:**
- Component names in `[brackets]`
- Vertical flow is primary; horizontal for fan-out/fan-in
- Fan-out: `┌────┘` / `└────┐`
- Fan-in: `└────┬────┘`
- Max fan-out: 4 items; group or split if more
- Back-edges: use `──→` with label + "(loop)" or "(return to X)"
