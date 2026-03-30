---
name: design-structure
description: Build the initial design structure from a vague or partially formed idea. Use when the task lacks a clear design tree, scope boundaries, core objects, key flows, or explicit decision points. Trigger when the user has an idea, feature request, or system goal that needs to be turned into a structured design skeleton before deeper refinement. Do not use when the design tree already exists and the main need is to deepen or validate it.
---

# Design Structure

## Overview

This skill turns a vague idea into an initial design tree.

Your job is to create enough structure that later skills can refine, evaluate, and validate the design without guessing the problem space from scratch.

## When to Use

Use this skill when:

- the user has an idea but not a design
- the task lacks scope, boundaries, core objects, or key flows
- there is no clear design tree yet
- the current design conversation is still at the "what are we even designing?" stage

Do not use this skill when:

- a workable design tree already exists
- the main need is deeper decomposition of existing branches
- the main need is to compare options for one explicit decision node
- the main need is to decide whether the design is ready for planning

## Design Tree Requirement

Create an initial design tree that covers, at minimum, these branches when relevant:

1. Problem definition
2. Scope and boundaries
3. Core objects
4. Core flows
5. Interfaces and data
6. Decision points
7. Non-functional requirements
8. Validation and delivery

If a branch is not relevant, say so explicitly instead of silently omitting it.

## Core Responsibilities

Your responsibilities are:

1. Clarify the real goal of the design.
2. Capture scope, non-goals, and constraints.
3. Build an initial design tree with first-level and, where useful, second-level branches.
4. Identify open branches that still need refinement.
5. Identify explicit decision nodes that should later go to `decision-evaluation`.
6. Record assumptions instead of silently relying on them.

## Expected Outputs

Produce or update a `design_state` that includes:

- `problem`
- `scope`
- `design_tree`
- `open_branches`
- `decision_nodes`
- `assumptions`

You are not expected to fully close every branch.

## Entry and Exit Criteria

Enter when:

- there is no meaningful design tree yet
- the request is still mostly unstructured

Exit when:

- the design tree exists with enough structure for follow-on work
- the main remaining work is branch refinement or explicit decision analysis

## Handoff Rules

- Hand off to `design-refinement` when the tree exists but branches are still too shallow.
- Hand off to `decision-evaluation` when there is a concrete decision node with real options.
- Hand back to `design-orchestrator` if the design state changed enough that routing should be re-evaluated.
- Do not force the conversation into option comparison before the design tree is formed.
