# Martian Investment System - Software Stack
**Version**: 2.0
**Date**: 2026-01-15
**Owner**: [PL][CODE][UI]

## 1. Frontend Layer
**"The Cyberpunk Visualizer"**

*   **Framework**: [Next.js 14](https://nextjs.org/) (React 18)
    *   *Why*: Server Actions, Robust Routing, easy deployment.
*   **Styling**: [TailwindCSS](https://tailwindcss.com/)
    *   *Theme*: Custom "Cyberpunk" palette (Cyan/Gold/Zinc-950).
    *   *Font*: 'Inter' (Google Fonts).
*   **Visualization**: [ECharts for React](https://git.hust.cc/echarts-for-react/)
    *   *Usage*: Bar Chart Race, Trend Lines, Portfolio Donut.
*   **State Management**: React `useState` / `useContext` (Lightweight).

## 2. Backend Layer
**"The Mathematical Core"**

*   **Framework**: [FastAPI](https://fastapi.tiangolo.com/) (Python 3.12)
    *   *Why*: Async performance, Auto-Swagger docs, easy simulation integration.
*   **Data Processing**: [Pandas](https://pandas.pydata.org/)
    *   *Usage*: Financial Simulation, Excel I/O, DataFrames.
*   **Authentication**: [Authlib](https://docs.authlib.org/) + Starlette Sessions.
    *   *Strategy*: OAuth 2.0 with Google.
*   **Database**: SQLite (via standard library) + JSON Flat Files.
    *   *Philosophy*: "Zero-Maintenance Persistence".

## 3. DevOps & Automation
*   **Containerization**: Docker (Multi-stage builds).
*   **Testing**: [Playwright](https://playwright.dev/) (Python Sync API).
    *   *Coverage*: Full E2E (Login -> UI -> Simulation -> Logout).
*   **CI/CD**: Manual Push -> Zeabur Auto-Deploy.
