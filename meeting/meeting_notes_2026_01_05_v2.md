# Agents Sync Meeting: 2026-01-05 (Session 2)

**Topic**: transition to Phase 2 Execution - Social & Sharing

## 1. Roundtable Discussion

**[PM] (The Visionary)**:
"Great work on the docs. Now, let's look at the product. The 'Leaderboard' is the heart of our social strategy. Right now, clicking a user does... nothing useful. We need that Profile Modal to tell a story: 'How is this person allocating their assets?' without revealing 'How rich are they?'."

**[SPEC] (The Architect)**:
"The privacy model is clear. We expose portions (% of portfolio), not scalars (dollar amounts). The Schema in `product/specifications.md` holds. [CODE], ensure your SQL queries only return relative data."

**[CODE] (The Builder)**:
"Understood. I have a plan for `get_public_portfolio(user_id)` in `portfolio_db.py`.
1.  Fetch all transactions for the user.
2.  Calculate current distinct holdings and their latest market value.
3.  Sum total value.
4.  Divide each holding by total to get %.
5.  Return the list sorted by %.
I'll also need to handle the case where a user has NO data (graceful filtering)."

**[UI] (The Designer)**:
"Once [CODE] gives me that JSON, I'll render it. A simple Pie Chart is okay, but a 'Donut' looks more premium. I can use the existing Plotly.js library we already load for the Mars charts. It's heavier than raw SVG but guarantees consistency."

**[CV] (The Critic)**:
"I surely hope we don't break the build. I'll watch the `verify_api_headless.py`. If you change the API signature, please update the test. Also, [PL], we still have that environment issue with Playwright. Can we turbo-fix that later?"

**[PL] (The Driver)**:
"Let's park the Playwright environment fix for now; the Headless checks are serving us well.
**Plan**:
1.  [CODE] implements backend logic.
2.  [UI] implements frontend visualization.
3.  We test manually + headless."

## 2. Action Items

-   **[CODE]**: Implement `get_public_portfolio` in `app/portfolio_db.py`.
-   **[UI]**: Update `index.html` / `main.js` to render the Asset Allocation chart in the modal.
