# BUG-117-PL: Bar Chart Race (BCR) Duplicate Year Data Rendering Issue

**Reporter:** [PL]
**Component:** Frontend (BCR) & Backend (ROICalculator)
**Severity:** Medium
**Status:** FIXED

## Description
In the Bar Chart Race (BCR) tab, users observed duplicate bars rendering for the initial simulation year (e.g., year 2006). This caused phantom bars to appear, skewed the rank calculations, and caused jitter in the UI animation for the first frame. 

## Root Cause
The `roi_calculator.py` function `calculate_complex_simulation` added a synthetic "baseline" entry to the `history` array to represent the initial principal. This baseline entry was assigned `year: start_year`. 
Subsequently, the main loop processed the first simulation year (e.g., 2006) and added the actual performance data *also* tagged as `year: start_year`. 
When the backend API `/api/race-data` serialized this history, it emitted two separate records for the exact same year for every stock. The Next.js frontend Map deduplication grouped these into a single year block but attempted to render all records, creating duplicates.

## Fix Implemented
- **Backend (`app/services/roi_calculator.py`):** Changed the baseline entry's year tag from `start_year` to `start_year - 1`. 
- **Effect:** The baseline principal is now accurately reflected as the End-of-Year value for the preceding year (e.g., 2005), strictly segregating it from the first active simulation tick (2006).
- **Commit:** ec9bdf5.

## Verification
- Local python tests verified that the `history` length is precisely `Years + 1` with 100% unique year keys.
- BCR rendering verified to be smooth and deduplicated.
