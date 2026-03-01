# BUG-006-PL: My Race Target Name Collision and Merge Failure
**Reporter:** [PL]
**Component:** Backend (Portfolio Service - Race)
**Severity:** High
**Status:** CLOSED

## Description
In the "My Race" tab, the timeline bars are hallucinating incorrect names across different assets. The user has TSMC (2330), 6533, and 65331. However, the Race chart displays three bars all named variations of "晶心科...". E.g., TSMC's $82M bar is erroneously labeled as "晶心科...", effectively stripping "台積電" from the UI.

Additionally, the user requested that "For the same target, their data should be merged." This implies Race data might be outputting multiple bars per stock_id instead of aggregating market values grouping by stock_id / symbol. 

## Root Cause Hypothesis
In `get_portfolio_race_data()`, the algorithm builds DataFrames or dicts mapping `target_id` and timestamps. A leaky variable, a bad `merge()`, or a flawed string lookup causes `stock_name` to be globally overwritten by the final target in the group (e.g. 65331 晶心科一).

## Fix Strategy
Audit `get_portfolio_race_data` grouping logic. Ensure grouping/aggregation properly scopes variables and merges names based correctly on `stock_id`. If grouping by stock_id is required instead of `target_id`, aggregate their shares before applying market value calculations.
