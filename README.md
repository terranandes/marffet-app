# Martian Investment System 🚀

A full-stack quantitative stock analysis platform verifying that **"Time in the market beats timing the market."**

Gamify your long-term investing by racing against the mechanized **Mars Strategy** and see if you can beat the market!

![Dashboard](frontend/public/martian_banner.png)

## ✨ Features

-   **Mars Strategy**: Backtest 20+ years of Taiwan stock history — find the Top 50 survivors with Gaussian filtering.
-   **Bar Chart Race**: Watch stocks compete in an animated time-series visualization.
-   **Compound Interest**: Simulate long-term compounding for single stocks or compare up to 3 assets.
-   **Portfolio Tracker**: Manage holdings and transactions with a sleek Webull-style UI, ECharts allocation donuts, and live P/L.
-   **Trend & My Race**: Personal investment curve + your holdings racing against each other.
-   **Cash Ladder**: Global leaderboard ranked by ROI — compete with other Martians.
-   **CB Arbitrage**: Convertible Bond premium monitoring and yield hunting.
-   **AI Copilot**: Investment assistant powered by Gemini (Free: Educator / Premium: Wealth Manager).
-   **Extreme Speed**: DuckDB + vectorized numpy resolves 20-year calculations in `<200ms`.
-   **Modern UI**: Next.js 16, TailwindCSS, skeleton loading, cyberpunk design.

---

## ☁️ Run on GitHub (Codespaces)

**You can run this full application directly in your browser without installing anything!**

1.  Click the **"Code"** button (green) at the top of this repository.
2.  Select **"Codespaces"** tab -> **"Create codespace on main"**.
3.  Wait for the environment to build.
4.  In the terminal, run:
    ```bash
    ./start_app.sh
    ```
5.  VS Code will show a popup: *"Your application running on port 5173 is available."*
6.  Click **"Open in Browser"**.
7.  🎉 The App is now running in the cloud!

---

## 💻 Local Installation

If you prefer to run it on your own machine:

### Prerequisites
-   Python 3.12 (Managed by `uv`)
-   **Bun** 1.x (Frontend Runtime)

### Setup (Required: uv)

We use `uv` for 10x faster setup and reliable dependency management.

1.  **Clone the repo**:
    ```bash
    git clone https://github.com/your-username/martian.git
    cd martian
    ```

2.  **Initialize & Run**:
    ```bash
    # Install uv (if you haven't yet)
    # curl -LsSf https://astral.sh/uv/install.sh | sh
    
    # Run the app directly
    ./start_app.sh
    ```
    *Open `http://localhost:8000` in your browser.*

4.  **Important**: Google Sign-In requires your `GOOGLE_CLIENT_ID` and `SECRET` in `.env`.
    *   Ensure your Google Cloud Console has `http://localhost:8000/auth/callback` added to "Authorized Redirect URIs".
    *   If you see `Error 400: redirect_uri_mismatch`, check if you are accessing via `127.0.0.1` vs `localhost`.

**Q: Can I host this on GitHub Pages?**
A: **Partially.** GitHub Pages only hosts static websites (HTML/JS). This app requires a Python backend to fetch stock data (TWSE) and calculate metrics.
-   If you deploy *only* the Frontend to GitHub Pages, it will show the UI, but **all analysis features will fail** because there is no backend API to talk to.

**Q: Where should I deploy it?**
A: We recommend using a service that supports Docker or Python/Node apps, such as:
-   **Zeabur**
-   **Render** (Free tier available)
-   **Railway**
-   **Heroku**
-   **AWS / GCP**

---

## ☕ Sponsorship & Memberships

Love the Martian Investment System? Support the project and unlock **Premium** or **VIP** features!
- ☕ **[Ko-fi](https://ko-fi.com/terranandes)**
- 💛 **[Buy Me a Coffee](https://buymeacoffee.com/terranandes)**

*Sponsoring grants you VIP/Premium access which is manually injected by the Game Master.*

---

## 🛠 Tech Stack

-   **Frontend**: Next.js 16 (React 18), TailwindCSS, ECharts, Recharts, Framer Motion.
-   **Backend**: FastAPI, Uvicorn, Python 3.12, uv (package manager).
-   **Data**: DuckDB (Market DataLake), SQLite (User Data), AsyncIO Crawler (TWSE/TPEx).
-   **DevOps**: Docker, Zeabur (auto-deploy), Playwright (E2E).
