---
description: Create project plan, reiview the plan and generate Ralph loop PRD
---

# /ralph_plan - Project Planning Mode with a long-series/comprehensive coverage <br>
No code writing - only plan file generation.

$ARGUMENTS

---
Steps:
1. Use skill `brainstorming` to conceive how/what to achieve $ARGUMENTS
2. Use skill `writing-plans` to plan $ARGUMENTS according to previous brainstorming result
3. Write down the plan so far in to `./docs/plan`.
4. Use skill `multi-agent-brainstorming` to review previously created plan
5. Write down the plan-reivew in to `./docs/plan`.
6. Transform the plan plus the plan-review into a PRD task file as follows :<br>
`Task File Format
The task file is read-only - the agent never modifies it. Write a proper PRD or specification document, but organize it into discrete, actionable tasks so the agent can identify what to work on next by cross-referencing progress.txt.

Example:

# PRD: User Management System

## Overview
Build a user management system with authentication, profiles, and admin controls.

## Task 1: Authentication
Implement JWT-based authentication with login/logout endpoints.
- POST /api/auth/login
- POST /api/auth/logout
- Token refresh mechanism

## Task 2: User Profiles
Create user profile CRUD operations.
- GET/PUT /api/users/:id
- Profile picture upload
- Email verification

## Task 3: Admin Dashboard
Build admin interface for user management.
- List all users with pagination
- Suspend/activate accounts
- View user activity logs

The key is clear task boundaries - each ## Task N: section should be a self-contained unit of work that the agent can complete in one iteration.`

7. Write down the {plan}_PRD.md at `./docs/plan`.