# Product Datasheet: Martian Investment System

> **Vision**: Gamifying long-term investment strategies to prove that "Time in the market beats timing the market."

## 1. Executive Summary
The **Martian Investment System** is a web-based simulation and portfolio management tool designed to educate users on the benefits of long-term compounding. By comparing a user's manual trading performance ("My Race") against a mechanized, history-proven strategy ("Mars Strategy"), the platform visually demonstrates the efficacy of consistent investing.

## 2. Key Features

### 1. The "Mars" Strategy Simulation
-   **Philosophy**: "Time in the market beats timing the market."
-   **Mechanism**:
    -   Filters stocks via Low Volatility & High Efficiency (Gaussian Filter).
    -   Simulates annual contributions ($60k/year) + Dividend Reinvestment (DRIP) from **2006 to Present**.
    -   **Dynamic Start Year**: Users can benchmark performance starting from any year (e.g., 2024).
-   **Data Coverage**: Supports TWSE (Mainboard), TPEx (OTC), and **Bond ETFs** (e.g., 00679B).

### 2. Social Leaderboard (Community)
-   **Rankings**: See how your portfolio ROI stacks up against other "Martians".
-   **Public Profiles**: Share read-only views of your Asset Allocation and Top Holdings (without exposing sensitive dollar values).
-   **Privacy-First**: PII (Emails) and net worth are strictly hidden from public APIs.

### 3. Investment Visualization
-   **Wealth Path**: Interactive charts showing Net Worth growth vs. Benchmark.
-   **Dividend Receipts**: Granular breakdown of annual cash flow from dividends.
-   **Survivors Table**: identifying the "Thrivers" of the market over 20 years.

### 4. Guest Mode (No Login Required)
-   **No Account Needed**: Users can explore the app without signing up.
-   **Local Data Only**: All portfolio data stored in browser's localStorage.
-   **No Remote Storage**: Guest data is never uploaded to the server.
-   **Privacy First**: Perfect for users who want to try before committing.
-   **Limitations**: Reduced limits (3 groups, 10 targets, 10 transactions) and no AI Bot.

### 5. AI Copilot (Mars AI, Powered by Gemini)
-   **Role**: An intelligent investment assistant with tier-based personalities.
-   **User Context**: AI sees full portfolio summary + individual holdings (name, shares, avg cost, P/L).

#### Free Tier Personality
> *"You are Mars AI (Free Tier), an investment educator designed to build CONFIDENCE."*

| Trait | Description |
|-------|-------------|
| **Goal** | Explain WHY the Mars Strategy (Buy Top 50 & Hold) works |
| **Tone** | Encouraging, Patient, Educational |
| **Evidence** | Cites Bar Chart Race and CAGR data |
| **Limitation** | Does NOT give rebalancing advice |

#### Premium Tier Personality
> *"You are Mars AI (Premium Tier), a ruthless wealth manager designed to enforce DISCIPLINE."*

| Trait | Description |
|-------|-------------|
| **Goal** | Optimize returns through active REBALANCING |
| **Tone** | Precise, Data-Driven, Action-Oriented |
| **Focus** | SMA Divergence, Market Cap Ratios |
| **Advice** | Suggests selling overheated stocks (+20% vs SMA) |
| **Motto** | *"Execute the strategy. Don't fall in love with a stock."*

#### Free vs Premium Feature Comparison

| Feature | Guest | Free | Premium |
|---------|-------|------|---------|
| **AI Bot Personality** | None | Educator (encouragement) | Ruthless Wealth Manager (rebalancing advice) |
| **Portfolio Groups** | 3 max | 11 max | 30 max |
| **Targets per Group** | 10 max | 50 max | 200 max |
| **Transactions per Target** | 10 max | 100 max | 1000 max |
| **CB Notifications** | ❌ | ❌ | ✅ In-App notification plus Email alerts |
| **Rebalancing Notifications** | ❌ | ❌ | ✅ In-App notification plus Email alerts when portfolio needs rebalancing |
| **Bar Chart Race** | Basic | Basic | Advanced (custom metrics) |
| **Data Export** | ❌ | ❌ | ✅ CSV/Excel |

## 3. Target Audience
-   **Retail Investors**: Looking to backtest strategies.
-   **Financial Educators**: Demonstrating the power of compounding.
-   **Gamers**: Enjoying the competitive "Race" aspect of investing.

## 4. Market Fit
-   **Problem**: Most investment tools are either dry spreadsheets or high-frequency trading platforms.
-   **Solution**: Martian Investment combines the fun of a "Race" visualization with the rigor of historical data, making long-term holding exciting.
