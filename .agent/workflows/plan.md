---
description: Create project plan using project-planner agent.
---

# /plan - Project Planning Mode <br>
No code writing - only plan file generation.

$ARGUMENTS

---
Do Step by step:
1. Use skill `brainstorming` to conceive how/what to achieve $ARGUMENTS
2. Use skill `writing-plans` to plan $ARGUMENTS according to previous brainstorming result
3. Write down current plan at `./docs/plan`
4. Use skill `multi-agent-brainstorming` to review preciously created plan
5. Write down current plan-review at `./docs/plan`