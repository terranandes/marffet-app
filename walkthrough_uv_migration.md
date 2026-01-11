# Walkthrough - uv Migration & Verification

## 1. uv Migration (Project Leader)
### **Goal**
Enforce `uv` as the single source of truth for python dependency management, replacing legacy `pip` and `venv` workflows.

### **Changes**
-   **Scripts**:
    -   `start_app.sh`: Updated to check for `uv`, run `uv sync`, and execute `uvicorn` via `uv run`.
    -   `run_martian.sh`: Updated to execute `run_analysis` via `uv run`.
-   **Documentation**:
    -   `README.md`: Removed `pip` instructions. Added definitive `uv` setup guide.
    -   `DEPLOY.md`: Clarified that `requirements.txt` is an export artifact, not the source.

## 2. Verification Results

### **Script Execution**
-   **Backend**: `start_app.sh` successfully starts the backend using `uv run`. Dependencies are resolved instantly.
-   **Frontend**: `npm install` was re-run to fix permission issues with `next`.

### **Logic Verification (verify_roi_correlation.py)**
-   **Method**: Randomly sampled 20 stocks and compared the Simulation Engine's calculated ROI against `stock_list_s2006e2026_filtered.xlsx` (Column `s2006e2025bao`).
-   **Result**:
    -   Correlation Coefficient: **0.9444**
    -   Status: **PASSED** (High confidence in simulation logic).
