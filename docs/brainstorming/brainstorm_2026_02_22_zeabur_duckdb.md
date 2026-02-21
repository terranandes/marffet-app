# Multi-Agent Brainstorming: Zeabur DuckDB Deployment

## 1. The Challenge
We have successfully rebuilt the market database using DuckDB locally, which now spans 20 years of data and accurately tracks splits and dividends with an 84.7% correlation. However, Zeabur instances are ephemeral, and running a full 20-year crawl/rebuild on every container startup is unacceptable (both for TWSE WAF limits and startup timeouts).

## 2. Options Considered
**Option A: Ship the entire `market.duckdb` binary**
- *Pros:* Instant startup.
- *Cons:* Binary DB files are not git-friendly, can bloat the repository, and merging conflicts are impossible to resolve. Changes made on Zeabur (like daily crawls) will be overwritten on the next deploy.

**Option B: Zeabur Persistent Volume + Local Parquet Bootstrapping**
- *Pros:* Parquet files are highly compressed, column-oriented, and perfect for version control. We can partition by year (e.g. `prices_2020.parquet`) to keep file sizes very small (< 15MB each). We mount a persistent `/data/` volume in Zeabur. On the *first* startup, the FastAPI app checks if `market.duckdb` exists in `/data/`. If not, it reads the bundled `.parquet` files and instantly initializes the persistent DuckDB. From then on, daily TWSE crawls append normally to the persistent DB.
- *Cons:* Slightly complex `app/main.py` startup logic.

## 3. Selected Strategy (Option B)
We will proceed with Option B as it guarantees zero data loss and adheres to CI/CD best practices.

**Data Flow:**
1. **Local Dump:** `scripts/ops/backup_duckdb.py` extracts local `market.duckdb` -> `data/backup/prices_YYYY.parquet` + `data/backup/dividends.parquet`.
2. **Git Commit:** These `.parquet` files are tracked in `git`.
3. **Zeabur Startup:** `app/main.py` detects an empty `/data/` volume -> Ingests Parquets in seconds -> Container starts.
4. **Nightly Job:** Runs `crawl_fast.py` inside Zeabur, appending directly to the persistent `/data/market.duckdb` via cron.

[SPEC] & [CODE] agree this is the most robust, memory-efficient way to handle DuckDB in the cloud.
