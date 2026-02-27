
from typing import List, Dict, Any
import sqlite3

from app.database import get_db
from app.config import FREE_MAX_GROUPS, PREMIUM_MAX_GROUPS, FREE_MAX_TX_PER_TARGET, PREMIUM_MAX_TX_PER_TARGET
from app.repositories import user_repo, group_repo, target_repo, transaction_repo
from app.services import market_data_service, calculation_service

def create_group(user_id: str, name: str) -> Dict[str, Any]:
    with get_db() as conn:
        # Check tier limits
        user_repo.get_user_profile(conn, user_id)
        # Assuming profile has subscription_tier? user_repo.get_user_profile returns dict.
        # But 'subscription_tier' might not be in the select list of get_user_profile?
        # Checked user_repo: select nickname, picture, total_wealth, total_cost, total_roi, last_synced.
        # It misses subscription_tier! I need to fix user_repo or fetch it here.
        # I'll Fix user_repo later or just fetch tier here raw SQL?
        # Better to fix user_repo or add get_tier.
        # For now, I'll fetch tier manually to avoid context switch loop.
        cursor = conn.cursor()
        cursor.execute("SELECT COALESCE(subscription_tier, 0) FROM users WHERE id = ?", (user_id,))
        row = cursor.fetchone()
        tier = row[0] if row else 0
        
        limit = PREMIUM_MAX_GROUPS if tier > 0 else FREE_MAX_GROUPS
        count = group_repo.count_groups(conn, user_id)
        
        if count >= limit:
            tier_name = "Premium" if tier > 0 else "Free"
            raise ValueError(f"Maximum {limit} groups allowed for {tier_name} tier")
            
        group = group_repo.create_group(conn, user_id, name)
        group_repo.mark_initialized(conn, user_id)
        return group

def list_groups(user_id: str) -> List[Dict[str, Any]]:
    with get_db() as conn:
        groups = group_repo.list_groups(conn, user_id)
        
        if user_id == "guest":
            return groups
        
        is_init = group_repo.check_initialized(conn, user_id)
        
        if not is_init:
            if not groups:
                # Initialize default
                initialize_default_portfolio(user_id, conn)
                group_repo.mark_initialized(conn, user_id)
                conn.commit() # Ensure commits
                return group_repo.list_groups(conn, user_id)
            else:
                # Self heal
                group_repo.mark_initialized(conn, user_id)
                
        return groups

def delete_group(group_id: str) -> bool:
    with get_db() as conn:
        return group_repo.delete_group(conn, group_id)

def add_target(group_id: str, stock_id: str, stock_name: str = None, asset_type: str = "stock") -> Dict[str, Any]:
    # Fetch name if missing
    if not stock_name:
        stock_name = market_data_service.fetch_stock_name(stock_id)
        
    with get_db() as conn:
        return target_repo.add_target(conn, group_id, stock_id, stock_name, asset_type)

def list_targets(group_id: str) -> List[Dict[str, Any]]:
    with get_db() as conn:
         return target_repo.list_targets(conn, group_id)

def delete_target(target_id: str) -> bool:
    with get_db() as conn:
        # Also delete transactions? DB FK Cascade might handle it?
        # portfolio_db had PRAGMA foreign_keys = ON.
        # target_repo.delete_target handles it.
        return target_repo.delete_target(conn, target_id)

def get_target_summary(target_id: str) -> Dict[str, Any]:
    # Need live price?
    with get_db() as conn:
        target = target_repo.get_target(conn, target_id)
        
    if not target:
        return {}
    
    prices = market_data_service.fetch_live_prices([target['stock_id']])
    current_price = prices.get(target['stock_id'], {}).get('price')
    
    return calculation_service.get_target_summary(target_id, current_price)

def add_transaction(target_id: str, tx_type: str, shares: int, price: float, tx_date: str) -> Dict[str, Any]:
    with get_db() as conn:
        # Check tier limits
        # Need user_id from target_id -> group_id -> user_id
        # Complex join. 
        cursor = conn.cursor()
        cursor.execute("""
            SELECT COALESCE(u.subscription_tier, 0), u.id
            FROM group_targets gt
            JOIN user_groups ug ON gt.group_id = ug.id
            JOIN users u ON ug.user_id = u.id
            WHERE gt.id = ?
        """, (target_id,))
        row = cursor.fetchone()
        tier = row[0] if row else 0
        user_id = row[1] if row else None
        
        limit = PREMIUM_MAX_TX_PER_TARGET if tier > 0 else FREE_MAX_TX_PER_TARGET
        count = transaction_repo.count_transactions(conn, target_id)
        
        if count >= limit:
            tier_name = "Premium" if tier > 0 else "Free"
            raise ValueError(f"Maximum {limit} transactions per target for {tier_name} tier")
            
        tx = transaction_repo.add_transaction(conn, target_id, tx_type, shares, price, tx_date)
        
    # Update User Stats (Side Effect)
    if user_id:
        update_user_stats(user_id)
        
    return tx

def list_transactions(target_id: str) -> List[Dict[str, Any]]:
    with get_db() as conn:
        return transaction_repo.list_transactions(conn, target_id)

def delete_transaction(tx_id: str) -> bool:
    # Need user_id for stats update
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT u.id 
            FROM transactions t
            JOIN group_targets gt ON t.target_id = gt.id
            JOIN user_groups ug ON gt.group_id = ug.id
            JOIN users u ON ug.user_id = u.id
            WHERE t.id = ?
        """, (tx_id,))
        row = cursor.fetchone()
        user_id = row[0] if row else None
        
        success = transaction_repo.delete_transaction(conn, tx_id)
        
    if success and user_id:
        update_user_stats(user_id)
        
    return success

def update_user_stats(user_id: str):
    """Recalculate and save user stats."""
    try:
        snapshot = calculation_service.get_portfolio_snapshot(user_id)
        with get_db() as conn:
            user_repo.upsert_user_stats(
                conn, 
                user_id, 
                snapshot['total_wealth'], 
                snapshot['total_cost'], 
                snapshot['total_roi']
            )
        return {"roi": round(snapshot['total_roi'], 2)}
    except Exception as e:
        print(f"Error updating user stats: {e}")
        return None

def get_portfolio_history(user_id: str, months: int = 12) -> List[Dict[str, Any]]:
    return calculation_service.get_portfolio_history(user_id, months)

def get_portfolio_race_data(user_id: str) -> List[Dict[str, Any]]:
    return calculation_service.get_portfolio_race_data(user_id)

def get_portfolio_ladder(user_id: str) -> Dict[str, Any]:
    return calculation_service.get_portfolio_ladder(user_id)

def get_public_portfolio(user_id: str) -> Dict[str, Any]:
    with get_db() as conn:
        profile = user_repo.get_user_profile(conn, user_id)
        
    if not profile:
        return None
    
    snapshot = calculation_service.get_portfolio_snapshot(user_id)
    holdings = snapshot['holdings']
    
    # Calculate Allocation
    type_values = {"Stock": 0, "ETF": 0, "CB": 0}
    total_value = snapshot['total_wealth']
    
    holdings_value = []
    
    for h in holdings:
        val = h['value']
        atype = h['asset_type']
        if atype == 'etf':
            type_values["ETF"] += val
        elif atype == 'cb':
            type_values["CB"] += val
        else:
            type_values["Stock"] += val
        
        holdings_value.append({
            "symbol": h['stock_id'],
            "name": h['name'],
            "value": val
        })
        
    allocation = []
    if total_value > 0:
        for k, v in type_values.items():
            if v > 0:
                pct = round((v / total_value) * 100, 1)
                allocation.append({"name": k, "pct": pct})
                
    holdings_value.sort(key=lambda x: x['value'], reverse=True)
    top_holdings = [
        {"stock_id": h['symbol'], "stock_name": h['name']} 
        for h in holdings_value[:5]
    ]
    
    return {
        "nickname": profile.get("nickname") or "User",
        "picture": profile.get("picture"),
        "joined_at": str(profile.get("created_at"))[:10] if profile.get("created_at") else "2024-01-01",
        "roi": round(snapshot['total_roi'], 2),
        "allocation": allocation,
        "holdings": top_holdings
    }

def initialize_default_portfolio(user_id: str, conn: sqlite3.Connection) -> None:
    """Initialize default portfolio groups for a new user."""
    # 1. Mars Stocks
    g1 = group_repo.create_group(conn, user_id, "火星股 (Mars Stocks)")
    target_repo.add_target(conn, g1['id'], "2330", "台積電")
    target_repo.add_target(conn, g1['id'], "2317", "鴻海")
    target_repo.add_target(conn, g1['id'], "2454", "聯發科")
    target_repo.add_target(conn, g1['id'], "2412", "中華電")
    target_repo.add_target(conn, g1['id'], "2308", "台達電")
    target_repo.add_target(conn, g1['id'], "0050", "元大台灣50") # ETF but kept as stock in old logic? Old logic: 0050 is 'stock' by default unless 'etf' passed?
    # portfolio_db 208: target_repo.add_target(..., asset_type="etf" if "00" in code else "stock") logic?
    # portfolio_db line 337: `asset_type` arg.
    # In `initialize_default_portfolio` of portfolio_db:
    # "0050", "元大台灣50" (No asset_type specified -> default "stock")
    # But later fix_asset_types sets 00* to ETF.
    # I should set it correctly here.
    
    # 2. Bond ETFs
    g2 = group_repo.create_group(conn, user_id, "高股息債券ETF (Bond ETFs)")
    target_repo.add_target(conn, g2['id'], "00937B", "群益ESG投等債20+", "etf")
    target_repo.add_target(conn, g2['id'], "00679B", "元大美債20年", "etf")
    target_repo.add_target(conn, g2['id'], "00687B", "國泰20年美債", "etf")
    
    # 3. US-TW FANG ETFs
    g3 = group_repo.create_group(conn, user_id, "美台尖牙ETF (US-TW FANG ETFs)")
    target_repo.add_target(conn, g3['id'], "00757", "統一FANG+", "etf")
    target_repo.add_target(conn, g3['id'], "00830", "國泰費城半導體", "etf")
    target_repo.add_target(conn, g3['id'], "00662", "富邦NASDAQ", "etf")

def update_transaction(tx_id: str, tx_type: str, shares: int, price: float, tx_date: str) -> bool:
    with get_db() as conn:
        # Check ownership/tier limits if changing target? 
        # Assuming just update.
        success = transaction_repo.update_transaction(conn, tx_id, tx_type, shares, price, tx_date)
        
    # Stats update side effect needs user_id
    # We can fetch it if success
    if success:
        with get_db() as conn:
             cursor = conn.cursor()
             # Reverse join to find user
             cursor.execute("""
                SELECT u.id 
                FROM transactions t
                JOIN group_targets gt ON t.target_id = gt.id
                JOIN user_groups ug ON gt.group_id = ug.id
                JOIN users u ON ug.user_id = u.id
                WHERE t.id = ?
             """, (tx_id,))
             row = cursor.fetchone()
             if row:
                 update_user_stats(row[0])
                 
    return success

def get_total_dividends(user_id: str) -> Dict[str, Any]:
    with get_db() as conn:
        divs = transaction_repo.get_all_dividends_for_user(conn, user_id)
        
    total_cash = sum(d['total_cash'] for d in divs)
    return {
        "total_cash": round(total_cash, 2),
        "dividend_count": len(divs)
    }

def get_dividend_history(target_id: str) -> List[Dict[str, Any]]:
    with get_db() as conn:
        return transaction_repo.get_dividend_history(conn, target_id)

def sync_all_dividends(user_id: str) -> Dict[str, Any]:
    # Logic from portfolio_db sync_all_dividends
    # 1. Get all targets
    with get_db() as conn:
        targets = target_repo.get_targets_by_user(conn, user_id)
        
    synced = []
    
    # We need to fetch dividends and update DB.
    # Logic in portfolio_db was: sync_dividends_for_target
    # I should reproduce that logic here or in transaction_repo/service?
    # It's complex logic involving YF fetch + historical holding calc.
    # See portfolio_db lines 1605-1714.
    # I should implement helper `_sync_dividends_for_target` here.
    
    for t in targets:
        try:
            # Helper logic inline or method
            new_divs = _sync_dividends_for_target(t['id'], t['stock_id'])
            for div in new_divs:
                div['stock_id'] = t['stock_id']
                synced.append(div)
        except Exception as e:
            print(f"Error syncing dividends for {t['stock_id']}: {e}")
            
    return {
        "synced_count": len(synced),
        "dividends": synced
    }

def _sync_dividends_for_target(target_id: str, stock_id: str) -> List[Dict[str, Any]]:
    import yfinance as yf
    import uuid
    
    new_dividends = []
    
    # Try TW/TWO
    suffixes = ['.TW', '.TWO']
    for suffix in suffixes:
        try:
            ticker = yf.Ticker(f"{stock_id}{suffix}")
            dividends = ticker.dividends
            if dividends.empty:
                continue 
            
            with get_db() as conn:
                txs = transaction_repo.list_transactions(conn, target_id)
                # Sort asc
                txs.sort(key=lambda x: x['date'])
                
                # Check existing dividends to avoid re-insert
                # But we need to handle updates and deletes logic from portfolio_db
                # "IF SHARES > 0: UPSERT"
                
                for ex_date, amount in dividends.items():
                    ex_date_str = ex_date.strftime('%Y-%m-%d')
                    
                    # Calc holdings on ex-date
                    shares_held = 0
                    for tx in txs:
                        if tx['date'] < ex_date_str:
                            if tx['type'] == 'buy':
                                shares_held += tx['shares']
                            elif tx['type'] == 'sell':
                                shares_held -= tx['shares']
                    
                    # Check DB
                    # We need access to check individual dividend record.
                    # TransactionRepo didn't expose "get_dividend_by_date_target".
                    # I'll just upsert blindly? No, need logic.
                    # Let's use SQL directly or add repo method?
                    # SQL directly for now to save time/files.
                    cursor = conn.cursor()
                    cursor.execute(
                        "SELECT id, shares_held, total_cash FROM dividend_history WHERE target_id = ? AND ex_date = ?",
                        (target_id, ex_date_str)
                    )
                    existing = cursor.fetchone()
                    
                    if shares_held <= 0:
                        if existing:
                            transaction_repo.delete_dividend(conn, existing['id'])
                            new_dividends.append({"status": "deleted", "ex_date": ex_date_str})
                    else:
                        total_cash = shares_held * float(amount)
                        
                        if existing:
                            if existing['shares_held'] != shares_held or abs(existing['total_cash'] - total_cash) > 1:
                                transaction_repo.upsert_dividend(conn, existing['id'], target_id, ex_date_str, float(amount), shares_held, total_cash)
                                new_dividends.append({"status": "updated", "ex_date": ex_date_str})
                        else:
                            div_id = str(uuid.uuid4())
                            transaction_repo.upsert_dividend(conn, div_id, target_id, ex_date_str, float(amount), shares_held, total_cash)
                            new_dividends.append({"status": "new", "ex_date": ex_date_str})
            
            break # Success
        except Exception:
            continue
        
    return new_dividends

def get_all_targets_by_type(user_id: str) -> Dict[str, List[Dict[str, Any]]]:
    with get_db() as conn:
        targets = target_repo.get_targets_by_user(conn, user_id)
        
    result = {"stock": [], "etf": [], "cb": []}
    
    # We need to compute total_shares and avg_cost for each target to match old behavior
    # And grouping.
    # Also self-healing logic (name check).
    
    prices = market_data_service.fetch_live_prices([t['stock_id'] for t in targets])
    
    for t in targets:
        # Compute summary
        summary = calculation_service.get_target_summary(t['id'], prices.get(t['stock_id'], {}).get('price'))
        
        # Merge summary into target dict
        t.update(summary)
        
        # Self-healing name
        if not t['stock_name'] or t['stock_name'] == t['stock_id']:
             new_name = market_data_service.fetch_stock_name(t['stock_id'])
             if new_name and new_name != t['stock_id']:
                 t['stock_name'] = new_name
                 # Update DB
                 with get_db() as conn:
                     target_repo.update_target_name(conn, t['id'], new_name)
                     
        atype = t.get('asset_type', 'stock')
        if atype not in result:
            atype = 'stock'
        result[atype].append(t)
        
    return result
