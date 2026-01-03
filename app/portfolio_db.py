"""
Portfolio Database Module

SQLite database for user portfolio feature:
- User groups (up to 5 for free tier)
- Group targets (up to 20 per group for free tier)
- Buy/Sell transactions with cost, shares, date
"""

import sqlite3
import uuid
from pathlib import Path
from datetime import date, datetime
from typing import Optional
from contextlib import contextmanager

# Database file location
DB_PATH = Path(__file__).parent / "portfolio.db"

# Tier limits
FREE_MAX_GROUPS = 11
FREE_MAX_TARGETS_PER_GROUP = 50
FREE_MAX_TX_PER_TARGET = 50


@contextmanager
def get_db():
    """Context manager for database connections."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # Enable dict-like access
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def init_db():
    """Initialize database with schema."""
    with get_db() as conn:
        cursor = conn.cursor()
        
        # Users (Google Auth)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id TEXT PRIMARY KEY, -- Google sub ID
                email TEXT,
                name TEXT,
                nickname TEXT, -- Display Name for Leaderboard
                picture TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Migration: Add nickname if not exists
        try:
            cursor.execute("ALTER TABLE users ADD COLUMN nickname TEXT")
        except:
            pass

        # User Groups
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_groups (
                id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL DEFAULT 'default', 
                name TEXT NOT NULL,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
        """)
        
        # Group Targets (watched stocks/ETFs/CB)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS group_targets (
                id TEXT PRIMARY KEY,
                group_id TEXT NOT NULL,
                stock_id TEXT NOT NULL,
                stock_name TEXT,
                asset_type TEXT DEFAULT 'stock' CHECK(asset_type IN ('stock', 'etf', 'cb')),
                added_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (group_id) REFERENCES user_groups(id) ON DELETE CASCADE,
                UNIQUE(group_id, stock_id)
            )
        """)
        
        # Migration: Add asset_type column if not exists (for existing DBs)
        try:
            cursor.execute("ALTER TABLE group_targets ADD COLUMN asset_type TEXT DEFAULT 'stock'")
        except:
            pass  # Column already exists
        
        # Transactions (buy, sell, dividend)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS transactions (
                id TEXT PRIMARY KEY,
                target_id TEXT NOT NULL,
                type TEXT CHECK(type IN ('buy', 'sell', 'dividend')) NOT NULL,
                shares INTEGER NOT NULL,
                price REAL NOT NULL,
                date TEXT NOT NULL,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (target_id) REFERENCES group_targets(id) ON DELETE CASCADE
            )
        """)
        
        # Dividend History (for tracking dividend payments)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS dividend_history (
                id TEXT PRIMARY KEY,
                target_id TEXT NOT NULL,
                ex_date TEXT NOT NULL,
                pay_date TEXT,
                amount_per_share REAL NOT NULL,
                shares_held INTEGER NOT NULL,
                total_cash REAL NOT NULL,
                synced_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (target_id) REFERENCES group_targets(id) ON DELETE CASCADE,
                UNIQUE(target_id, ex_date)
            )
        """)
        
        # Enable foreign keys
        cursor.execute("PRAGMA foreign_keys = ON")
        
        print(f"[Portfolio DB] Initialized at {DB_PATH}")


# ============== GROUP OPERATIONS ==============

def create_group(name: str, user_id: str = "default") -> dict:
    """Create a new portfolio group."""
    with get_db() as conn:
        cursor = conn.cursor()
        
        # Check limit
        cursor.execute("SELECT COUNT(*) FROM user_groups WHERE user_id = ?", (user_id,))
        count = cursor.fetchone()[0]
        if count >= FREE_MAX_GROUPS:
            raise ValueError(f"Maximum {FREE_MAX_GROUPS} groups allowed for free tier")
        
        group_id = str(uuid.uuid4())
        cursor.execute(
            "INSERT INTO user_groups (id, user_id, name) VALUES (?, ?, ?)",
            (group_id, user_id, name)
        )
        return {"id": group_id, "name": name, "user_id": user_id}


def list_groups(user_id: str = "default") -> list:
    """List all groups for a user."""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, name, created_at FROM user_groups WHERE user_id = ? ORDER BY created_at",
            (user_id,)
        )
        return [dict(row) for row in cursor.fetchall()]


def delete_group(group_id: str) -> bool:
    """Delete a group and all its targets/transactions."""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("PRAGMA foreign_keys = ON")
        cursor.execute("DELETE FROM user_groups WHERE id = ?", (group_id,))
        return cursor.rowcount > 0


# ============== TARGET OPERATIONS ==============

def add_target(group_id: str, stock_id: str, stock_name: Optional[str] = None, asset_type: str = "stock") -> dict:
    """Add a stock/ETF target to a group."""
    if asset_type not in ('stock', 'etf', 'cb'):
        # Auto-detect asset type based on stock_id
        if stock_id.startswith('00'):
            asset_type = 'etf'
        elif len(stock_id) == 5 and stock_id.isdigit():
            asset_type = 'cb'
        else:
            asset_type = 'stock'
    
    with get_db() as conn:
        cursor = conn.cursor()
        
        # Check limit
        cursor.execute("SELECT COUNT(*) FROM group_targets WHERE group_id = ?", (group_id,))
        count = cursor.fetchone()[0]
        if count >= FREE_MAX_TARGETS_PER_GROUP:
            raise ValueError(f"Maximum {FREE_MAX_TARGETS_PER_GROUP} targets per group for free tier")
        
        if not stock_name:
            try:
                stock_name = fetch_stock_name(stock_id)
            except:
                pass

        target_id = str(uuid.uuid4())
        cursor.execute(
            "INSERT INTO group_targets (id, group_id, stock_id, stock_name, asset_type) VALUES (?, ?, ?, ?, ?)",
            (target_id, group_id, stock_id, stock_name, asset_type)
        )
        return {"id": target_id, "group_id": group_id, "stock_id": stock_id, "stock_name": stock_name, "asset_type": asset_type}



def list_targets(group_id: str) -> list:
    """List all targets in a group."""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, stock_id, stock_name, asset_type, added_at FROM group_targets WHERE group_id = ? ORDER BY added_at",
            (group_id,)
        )
        return [dict(row) for row in cursor.fetchall()]


def delete_target(target_id: str) -> bool:
    """Delete a target and all its transactions."""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("PRAGMA foreign_keys = ON")
        cursor.execute("DELETE FROM group_targets WHERE id = ?", (target_id,))
        return cursor.rowcount > 0


# ============== TRANSACTION OPERATIONS ==============

def add_transaction(target_id: str, tx_type: str, shares: int, price: float, tx_date: str) -> dict:
    """Add a buy/sell transaction."""
    if tx_type not in ('buy', 'sell'):
        raise ValueError("Transaction type must be 'buy' or 'sell'")
    
    with get_db() as conn:
        cursor = conn.cursor()
        
        # Check transaction limit
        cursor.execute("SELECT COUNT(*) FROM transactions WHERE target_id = ?", (target_id,))
        count = cursor.fetchone()[0]
        if count >= FREE_MAX_TX_PER_TARGET:
            raise ValueError(f"Maximum {FREE_MAX_TX_PER_TARGET} transactions per target for free tier")
        
        tx_id = str(uuid.uuid4())
        cursor.execute(
            "INSERT INTO transactions (id, target_id, type, shares, price, date) VALUES (?, ?, ?, ?, ?, ?)",
            (tx_id, target_id, tx_type, shares, price, tx_date)
        )
        return {
            "id": tx_id,
            "target_id": target_id,
            "type": tx_type,
            "shares": shares,
            "price": price,
            "date": tx_date
        }


def list_transactions(target_id: str) -> list:
    """List all transactions for a target."""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, type, shares, price, date, created_at FROM transactions WHERE target_id = ? ORDER BY date",
            (target_id,)
        )
        return [dict(row) for row in cursor.fetchall()]



def update_transaction(tx_id: str, shares: int, price: float, tx_date: str) -> bool:
    """Update an existing transaction."""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE transactions SET shares = ?, price = ?, date = ? WHERE id = ?",
            (shares, price, tx_date, tx_id)
        )
        return cursor.rowcount > 0


def delete_transaction(tx_id: str) -> bool:
    """Delete a transaction."""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM transactions WHERE id = ?", (tx_id,))
        return cursor.rowcount > 0


# ============== PORTFOLIO SUMMARY ==============

def get_target_summary(target_id: str, current_price: float = None) -> dict:
    """
    Calculate comprehensive summary for a single target.
    
    Returns:
        - total_shares: Net shares held
        - avg_cost: Average cost per share
        - total_cost: Total cost basis
        - realized_pnl: Realized P/L from completed sells
        - tx_count: Number of transactions
        - market_value: Current market value (if price provided)
        - unrealized_pnl: Unrealized P/L (if price provided)
        - unrealized_pnl_pct: % return (if price provided)
    """
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT type, shares, price FROM transactions WHERE target_id = ? ORDER BY date",
            (target_id,)
        )
        transactions = cursor.fetchall()
    
    total_shares = 0
    total_cost = 0.0
    realized_pnl = 0.0
    tx_count = len(transactions)
    
    for tx in transactions:
        if tx['type'] == 'buy':
            total_shares += tx['shares']
            total_cost += tx['shares'] * tx['price']
        else:  # sell
            sell_shares = tx['shares']
            sell_revenue = sell_shares * tx['price']
            if total_shares > 0:
                avg_cost_per_share = total_cost / total_shares
                cost_basis_sold = sell_shares * avg_cost_per_share
                realized_pnl += sell_revenue - cost_basis_sold
                total_shares -= sell_shares
                total_cost = max(0, total_shares * avg_cost_per_share)
    
    avg_cost = total_cost / total_shares if total_shares > 0 else 0
    
    result = {
        "total_shares": total_shares,
        "avg_cost": round(avg_cost, 2),
        "total_cost": round(total_cost, 2),
        "realized_pnl": round(realized_pnl, 2),
        "tx_count": tx_count
    }
    
    if current_price is not None and total_shares > 0:
        market_value = total_shares * current_price
        unrealized_pnl = market_value - total_cost
        unrealized_pnl_pct = (unrealized_pnl / total_cost * 100) if total_cost > 0 else 0
        
        result.update({
            "current_price": current_price,
            "market_value": round(market_value, 2),
            "unrealized_pnl": round(unrealized_pnl, 2),
            "unrealized_pnl_pct": round(unrealized_pnl_pct, 2)
        })
    
    return result


# ============== LIVE PRICE FETCHING ==============

def fetch_live_prices(stock_ids: list) -> dict:
    """
    Fetch live prices for Taiwan stocks using yfinance.
    Returns dict: {stock_id: {price, change, change_pct}}
    """
    import yfinance as yf
    
    prices = {}
    for sid in stock_ids:
        try:
            # Taiwan stocks have .TW or .TWO suffix
            ticker = f"{sid}.TW"
            stock = yf.Ticker(ticker)
            info = stock.fast_info
            
            current_price = info.get('lastPrice') or info.get('regularMarketPrice', 0)
            prev_close = info.get('previousClose', current_price)
            change = current_price - prev_close
            change_pct = (change / prev_close * 100) if prev_close else 0
            
            prices[sid] = {
                "price": round(current_price, 2),
                "change": round(change, 2),
                "change_pct": round(change_pct, 2)
            }
        except Exception as e:
            # Try .TWO for OTC stocks
            try:
                ticker = f"{sid}.TWO"
                stock = yf.Ticker(ticker)
                info = stock.fast_info
                current_price = info.get('lastPrice') or info.get('regularMarketPrice', 0)
                prev_close = info.get('previousClose', current_price)
                change = current_price - prev_close
                change_pct = (change / prev_close * 100) if prev_close else 0
                
                prices[sid] = {
                    "price": round(current_price, 2),
                    "change": round(change, 2),
                    "change_pct": round(change_pct, 2)
                }
            except:
                prices[sid] = {"price": 0, "change": 0, "change_pct": 0, "error": str(e)}
    
    return prices


def fetch_stock_name(stock_id: str) -> Optional[str]:
    """Fetch stock name from yfinance."""
    import yfinance as yf
    try:
        # Try TW then TWO
        for suffix in ['.TW', '.TWO']:
            ticker = yf.Ticker(f"{stock_id}{suffix}")
            # Try fetching explicit name
            info = ticker.info # This triggers a network request
            name = info.get('longName') or info.get('shortName')
            if name:
                return name
    except:
        pass
    return None


# ============== PORTFOLIO TREND ==============

def get_all_targets_by_type(user_id: str = "default") -> dict:
    """
    Get all portfolio targets grouped by asset type.
    Returns: {"stock": [...], "etf": [...]}
    """
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT gt.*, ug.name as group_name,
            COALESCE((SELECT SUM(CASE WHEN t.type='buy' THEN t.shares WHEN t.type='sell' THEN -t.shares ELSE 0 END) 
                      FROM transactions t WHERE t.target_id = gt.id), 0) as total_shares
            FROM group_targets gt
            JOIN user_groups ug ON gt.group_id = ug.id
            WHERE ug.user_id = ?
            ORDER BY gt.asset_type, gt.added_at
        """, (user_id,))
        
        result = {"stock": [], "etf": [], "cb": []}
        for row in cursor.fetchall():
            target = dict(row)
            asset_type = target.get("asset_type", "stock") or "stock"
            if asset_type not in result:
                asset_type = "stock"
            result[asset_type].append(target)
        
        return result


def get_portfolio_history(user_id: str = "default", months: int = 12) -> list:
    """
    Get monthly portfolio value history.
    Returns: [{"month": "2024-01", "cost": 1000000, "tx_count": 5}, ...]
    """
    from datetime import datetime
    from dateutil.relativedelta import relativedelta
    
    # Calculate start date (months ago)
    # Calculate start date (months ago) for display
    end_date = datetime.now()
    start_date = end_date - relativedelta(months=months)
    start_month_str = start_date.strftime("%Y-%m")
    
    with get_db() as conn:
        cursor = conn.cursor()
        
        # Get ALL transactions for user's targets to calculate correct running cost
        cursor.execute("""
            SELECT t.date, t.type, t.shares, t.price
            FROM transactions t
            JOIN group_targets gt ON t.target_id = gt.id
            JOIN user_groups ug ON gt.group_id = ug.id
            WHERE ug.user_id = ?
            ORDER BY t.date
        """, (user_id,))
        
        transactions = cursor.fetchall()
    
    # Build monthly aggregates
    monthly_data = {}
    running_cost = 0
    running_shares = 0
    
    for tx in transactions:
        month = tx['date'][:7]  # "YYYY-MM"
        if month not in monthly_data:
            # Carry over previous cost if month gap? No, we just need snapshot at end of month.
            # But here we are building "change events".
            # Actually simplest finding state at end of each month.
            pass

        if tx['type'] == 'buy':
            running_cost += tx['shares'] * tx['price']
            running_shares += tx['shares']
        else:
            if running_shares > 0:
                avg_cost = running_cost / running_shares
                running_shares -= tx['shares']
                running_cost = running_shares * avg_cost
        
        # Update/Overwrite the month's final state
        # (Since rows are ordered by date, the last update for a month is the final state)
        if month not in monthly_data:
            monthly_data[month] = {"month": month, "cost": 0, "tx_count": 0}
            
        monthly_data[month]['cost'] = round(running_cost, 2)
        monthly_data[month]['tx_count'] += 1
    
    # Fill in missing months and filter by requested window
    result = []
    current = start_date
    
    # Find initial cost basis before start_date
    # Find latest month in monthly_data that is < start_month_str
    prev_cost = 0
    sorted_months = sorted(monthly_data.keys())
    
    for m in sorted_months:
        if m < start_month_str:
            prev_cost = monthly_data[m]['cost']
        else:
            break
            
    while current <= end_date:
        month_key = current.strftime("%Y-%m")
        if month_key in monthly_data:
            # If we have data for this month, use it
            result.append(monthly_data[month_key])
            prev_cost = monthly_data[month_key]['cost']
        else:
            # Carry forward previous cost
            result.append({"month": month_key, "cost": prev_cost, "tx_count": 0})
        current += relativedelta(months=1)
    
    return result


def get_portfolio_race_data(user_id: str = "default") -> list:
    """
    Build race data for live portfolio BCR.
    Returns data structure compatible with existing D3.js race chart.
    """
    targets_by_type = get_all_targets_by_type(user_id)
    all_targets = targets_by_type['stock'] + targets_by_type['etf']
    
    if not all_targets:
        return []
    
    # Get all unique transaction dates
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT DISTINCT substr(t.date, 1, 7) as month
            FROM transactions t
            JOIN group_targets gt ON t.target_id = gt.id
            JOIN user_groups ug ON gt.group_id = ug.id
            WHERE ug.user_id = ?
            ORDER BY month
        """, (user_id,))
        months = [row['month'] for row in cursor.fetchall()]
    
    if not months:
        return []
    
    # Build race data per month
    race_data = []
    for month in months:
        for target in all_targets:
            # Get cumulative value for this target up to this month
            with get_db() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT type, shares, price FROM transactions
                    WHERE target_id = ? AND date <= ?
                    ORDER BY date
                """, (target['id'], month + "-31"))
                transactions = cursor.fetchall()
            
            total_shares = 0
            total_cost = 0
            for tx in transactions:
                if tx['type'] == 'buy':
                    total_shares += tx['shares']
                    total_cost += tx['shares'] * tx['price']
                else:
                    if total_shares > 0:
                        avg = total_cost / total_shares
                        total_shares -= tx['shares']
                        total_cost = total_shares * avg
            
            if total_cost > 0:
                race_data.append({
                    "month": month,
                    "id": target['stock_id'],
                    "name": target['stock_name'] or target['stock_id'],
                    "value": round(total_cost, 2),
                    "asset_type": target.get('asset_type', 'stock')
                })
    
    return race_data


# ============== DIVIDEND TRACKING ==============

def sync_dividends_for_target(target_id: str, stock_id: str) -> list:
    """
    Fetch and sync dividends from yfinance for a target.
    Returns list of newly recorded dividends.
    """
    import yfinance as yf
    from datetime import datetime
    
    # Try TW and TWO suffixes
    new_dividends = []
    
    for suffix in ['.TW', '.TWO']:
        try:
            ticker = yf.Ticker(f"{stock_id}{suffix}")
            dividends = ticker.dividends
            
            if dividends.empty:
                continue
            
            # Get current shares held for this target
            with get_db() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT SUM(CASE WHEN type='buy' THEN shares ELSE -shares END) as total_shares
                    FROM transactions 
                    WHERE target_id = ? AND type IN ('buy', 'sell')
                """, (target_id,))
                result = cursor.fetchone()
                shares_held = result['total_shares'] or 0
            
            if shares_held <= 0:
                break
            
            # Process each dividend
            for ex_date, amount in dividends.items():
                ex_date_str = ex_date.strftime('%Y-%m-%d')
                total_cash = shares_held * amount
                
                # Check if already recorded
                with get_db() as conn:
                    cursor = conn.cursor()
                    cursor.execute(
                        "SELECT id FROM dividend_history WHERE target_id = ? AND ex_date = ?",
                        (target_id, ex_date_str)
                    )
                    if cursor.fetchone():
                        continue  # Already exists
                    
                    # Record new dividend
                    div_id = str(uuid.uuid4())
                    cursor.execute("""
                        INSERT INTO dividend_history 
                        (id, target_id, ex_date, amount_per_share, shares_held, total_cash)
                        VALUES (?, ?, ?, ?, ?, ?)
                    """, (div_id, target_id, ex_date_str, amount, shares_held, total_cash))
                    
                    new_dividends.append({
                        "id": div_id,
                        "ex_date": ex_date_str,
                        "amount_per_share": round(amount, 4),
                        "shares_held": shares_held,
                        "total_cash": round(total_cash, 2)
                    })
            
            break  # Success, no need to try other suffix
            
        except Exception as e:
            continue
    
    return new_dividends


def get_dividend_history(target_id: str) -> list:
    """Get dividend history for a target."""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, ex_date, pay_date, amount_per_share, shares_held, total_cash, synced_at
            FROM dividend_history WHERE target_id = ?
            ORDER BY ex_date DESC
        """, (target_id,))
        return [dict(row) for row in cursor.fetchall()]


def get_total_dividends(user_id: str = "default") -> dict:
    """Get total dividend cash for a user."""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT SUM(dh.total_cash) as total_cash, COUNT(dh.id) as dividend_count
            FROM dividend_history dh
            JOIN group_targets gt ON dh.target_id = gt.id
            JOIN user_groups ug ON gt.group_id = ug.id
            WHERE ug.user_id = ?
        """, (user_id,))
        result = cursor.fetchone()
        return {
            "total_cash": round(result['total_cash'] or 0, 2),
            "dividend_count": result['dividend_count'] or 0
        }


def sync_all_dividends(user_id: str = "default") -> dict:
    """Sync dividends for all user's targets."""
    targets_by_type = get_all_targets_by_type(user_id)
    all_targets = targets_by_type.get('stock', []) + targets_by_type.get('etf', []) + targets_by_type.get('cb', [])
    
    synced = []
    for target in all_targets:
        new_divs = sync_dividends_for_target(target['id'], target['stock_id'])
        for div in new_divs:
            div['stock_id'] = target['stock_id']
            synced.append(div)
    
    return {
        "synced_count": len(synced),
        "dividends": synced
    }


# ============== USER PROFILE & LEADERBOARD ==============

def update_user_nickname(user_id: str, nickname: str) -> bool:
    """Update user's public nickname."""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("UPDATE users SET nickname = ? WHERE id = ?", (nickname, user_id))
        return cursor.rowcount > 0

def get_leaderboard_candidates() -> list:
    """
    Fetch all users to calculate leaderboard.
    Returns: [{id, nickname, name, picture}, ...]
    """
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, nickname, name, picture FROM users")
        return [dict(row) for row in cursor.fetchall()]

def get_user_public_profile(user_id: str) -> dict:
    """Get public profile for a user."""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT nickname, name, picture, created_at FROM users WHERE id = ?", (user_id,))
        row = cursor.fetchone()
        return dict(row) if row else {}


def get_public_portfolio(user_id: str) -> dict:
    """
    Get sanitized portfolio data for public viewing.
    Returns ROI%, Asset Allocation %, and Top Holdings (symbols only).
    NO absolute $ values.
    """
    # 1. Get User Profile
    profile = get_user_public_profile(user_id)
    if not profile:
        return None
        
    # 2. Get Targets
    targets_map = get_all_targets_by_type(user_id)
    all_targets = targets_map['stock'] + targets_map['etf'] + targets_map['cb']
    
    if not all_targets:
        return {
            "nickname": profile.get("nickname") or profile.get("name"),
            "picture": profile.get("picture"),
            "joined_at": profile.get("created_at"),
            "roi_pct": 0,
            "net_worth_grade": "N/A", # Fun grading?
            "allocation": [],
            "top_holdings": []
        }

    # 3. Fetch Prices & Calc Value
    stock_ids = list(set(t['stock_id'] for t in all_targets))
    prices = fetch_live_prices(stock_ids)
    
    total_market_value = 0
    total_cost = 0
    holdings_value = [] # (symbol, value, type)
    
    type_values = {"Stock": 0, "ETF": 0, "CB": 0}
    
    for t in all_targets:
        price = prices.get(t['stock_id'], {}).get('price', 0)
        shares = t['total_shares'] or 0
        
        if shares > 0:
            mv = shares * price
            total_market_value += mv
            
            # Asset Allocation
            atype = t.get('asset_type', 'stock')
            if atype == 'etf': type_values["ETF"] += mv
            elif atype == 'cb': type_values["CB"] += mv
            else: type_values["Stock"] += mv
            
            # For Top Holdings
            holdings_value.append({
                "symbol": t['stock_id'],
                "name": t['stock_name'],
                "value": mv
            })
            
            # Cost
            # We need summary for cost? get_target_summary queries a lot. 
            # Optimization: We can't easily get total cost without txns.
            # get_target_summary(t['id']) is reliable but slow in loop?
            # It's local DB, should be fine for <50 targets.
            summary = get_target_summary(t['id'])
            total_cost += summary['total_cost']

    # 4. ROI
    roi_pct = 0
    if total_cost > 0:
        roi_pct = ((total_market_value - total_cost) / total_cost) * 100
        
    # 5. Allocation %
    allocation = []
    if total_market_value > 0:
        for k, v in type_values.items():
            if v > 0:
                pct = round((v / total_market_value) * 100, 1)
                allocation.append({"label": k, "pct": pct})
    
    # 6. Top Holdings (Top 3 by value)
    holdings_value.sort(key=lambda x: x['value'], reverse=True)
    top_holdings = [
        {"symbol": h['symbol'], "name": h['name']} 
        for h in holdings_value[:5]
    ]
    
    return {
        "nickname": profile.get("nickname") or profile.get("name"),
        "picture": profile.get("picture"),
        "joined_at": profile.get("created_at")[:10], # YYYY-MM-DD
        "roi_pct": round(roi_pct, 2),
        "allocation": allocation,
        "top_holdings": top_holdings
    }


def fix_asset_types():
    """One-time fix for existing targets with wrong asset_type."""
    with get_db() as conn:
        cursor = conn.cursor()
        # Fix CBs: 5 digits, not starting with 00, currently 'stock'
        cursor.execute("""
            UPDATE group_targets 
            SET asset_type = 'cb' 
            WHERE length(stock_id) = 5 
              AND substr(stock_id, 1, 2) != '00' 
              AND asset_type = 'stock'
        """)
        # Fix ETFs: Starts with 00, currently 'stock'
        cursor.execute("""
            UPDATE group_targets 
            SET asset_type = 'etf' 
            WHERE substr(stock_id, 1, 2) = '00' 
              AND asset_type = 'stock'
        """)

# Initialize on import
if __name__ == "__main__":
    init_db()
    fix_asset_types()
    print("Database initialized successfully!")
else:
    # Run fix on module load to ensure existing data is corrected
    fix_asset_types()
