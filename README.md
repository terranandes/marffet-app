# Martian Investment System 🚀

A full-stack quantitative stock analysis platform integrating the **Mars Investment Method** and **Convertible Bond (CB) Arbitrage Strategies**.

![Dashboard](https://via.placeholder.com/800x400?text=Martian+Dashboard+Preview)

## ✨ Features

-   **Mars Strategy**: Automatic filtering of low-volatility, high-CAGR stocks (Gaussian Filter).
-   **CB Arbitrage**: Real-time evaluation of Convertible Bond conversion premium signals.
-   **Market Visualization**: Interactive **Bar Chart Race** of stock performance over time.
-   **Modern UI**: Built with React, Vite, and TailwindCSS for a premium experience.
-   **Robust Backend**: Powered by FastAPI and AsyncIO for efficient data crawling.

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
-   Python 3.10+
-   Node.js 18+

### Setup
1.  **Clone the repo**:
    ```bash
    git clone https://github.com/your-username/martian.git
    cd martian
    ```

2.  **Run the App (Auto-Setup)**:
    ```bash
    ./start_app.sh
    ```
    *The script will automatically create the Python environment and install all dependencies.*

---

## 📦 Deployment FAQ

**Q: Can I host this on GitHub Pages?**
A: **Partially.** GitHub Pages only hosts static websites (HTML/JS). This app requires a Python backend to fetch stock data (TWSE) and calculate metrics.
-   If you deploy *only* the Frontend to GitHub Pages, it will show the UI, but **all analysis features will fail** because there is no backend API to talk to.

**Q: Where should I deploy it?**
A: We recommend using a service that supports Docker or Python/Node apps, such as:
-   **Render** (Free tier available)
-   **Railway**
-   **Heroku**
-   **AWS / GCP**

---

## 🛠 Tech Stack

-   **Frontend**: React, TypeScript, TailwindCSS, Framer Motion, Plotly.js, TanStack Table.
-   **Backend**: FastAPI, Uvicorn, Python 3.12.
-   **Data**: AsyncIO Crawler (TWSE), Pandas (Analysis).
