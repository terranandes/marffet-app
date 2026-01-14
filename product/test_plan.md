# Martian Investment System - Test Plan
**Version**: 2.0
**Date**: 2026-01-15
**Owner**: [CV] Agent

## 1. Automated Testing Strategy
We utilize **Playwright** for complete End-to-End (E2E) verification. The test suite simulates a real user journey through the application.

### 1.1 Test Suite Location
*   `tests/full_verification.py`

### 1.2 Key Test Cases
| ID | Feature | Description | Verify Criteria |
| :--- | :--- | :--- | :--- |
| **TC-01** | Landing | Load Home Page | Title contains "Martian", Login button visible. |
| **TC-02** | Simulation | Mars Strategy Page | "Calculating..." -> Data table appears. Stock rows > 0. |
| **TC-03** | Visualization | Bar Chart Race | Canvas element exists. "Start" button clickable. |
| **TC-04** | Private Routes | Portfolio Page | Redirects to Login if unauthenticated (or Guest mode). |
| **TC-05** | Guest Mode | Guest Access | Can view public pages without error. |
| **TC-06** | UI Experience | Dark Mode | Background color is Zinc-950/Black. |

### 1.3 Execution Flow
```bash
# 1. Start Backend
uvicorn app.main:app --port 8000 &

# 2. Start Frontend
cd frontend && npm start &

# 3. Run Verification
python tests/full_verification.py
```

## 2. Manual Verification Checklist
- [x] **Login Flow**: Click Login -> Google Account Picker -> Redirect to Dashboard.
- [x] **Logout Flow**: Click User Profile -> Sign Out -> Redirect to Login/Home.
- [x] **Cross-Domain**: Verify `https://martian-app` can fetch from `https://martian-api` without CORS errors.
- [x] **Mobile Responsive**: Sidebar creates Hamburger menu on small screens.
