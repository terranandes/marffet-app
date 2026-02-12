
import json
import os
# import pandas as pd # Lazy Import
from datetime import datetime, date, timedelta
from dateutil.relativedelta import relativedelta
from pathlib import Path
from typing import List, Dict, Any, Optional

from app.database import get_db
from app.config import STOCK_NAME_CACHE
from app.repositories import transaction_repo, target_repo, group_repo
from app.services import market_data_service
from app import dividend_cache
from app.services.market_cache import MarketCache

def get_target_summary(target_id: str, current_price: float = None) -> Dict[str, Any]:
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
        transactions = transaction_repo.list_transactions(conn, target_id)
        # Sort by date (repo returns desc, we need asc for calc?)
        # Logic in portfolio_db was: "ORDER BY date" (ASC default?)
        # Repo uses DESC. We should reverse it.
        transactions.sort(key=lambda x: x['date']) # Oldest first
    
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
    
    # --- Dividend Calculation ---
    dividend_history = []
    total_div_cash = 0.0
    
    with get_db() as conn:
        divs = transaction_repo.get_dividend_history(conn, target_id)
        # divs are ordered by ex_date DESC
        
        for d in divs:
            total_div_cash += d['total_cash']
            dividend_history.append({
                "year": d['ex_date'],
                "shares": d['shares_held'],
                "unit_cash": d['amount_per_share'],
                "total": d['total_cash']
            })

    # Legacy Fallback if DB empty
    if total_div_cash == 0:
        total_div_cash = _calculate_legacy_dividend_fallback(target_id, transactions)

    summary = {
        "total_shares": total_shares,
        "avg_cost": avg_cost,
        "total_cost": total_cost,
        "realized_pnl": realized_pnl,
        "tx_count": tx_count,
        "dividends": {
            "total_cash": total_div_cash,
            "history": dividend_history
        }
    }

    if current_price is not None:
        market_value = total_shares * current_price
        unrealized_pnl = market_value - total_cost
        unrealized_pnl_pct = (unrealized_pnl / total_cost * 100) if total_cost > 0 else 0
        
        summary.update({
            "market_value": market_value,
            "unrealized_pnl": unrealized_pnl,
            "unrealized_pnl_pct": unrealized_pnl_pct
        })
        
    return summary

def _calculate_legacy_dividend_fallback(target_id: str, transactions: List[Dict]) -> float:
    """Fallback to Legacy JSON Load for dividends."""
    total_div_cash = 0.0
    try:
        # Determine stock ID
        with get_db() as conn:
             target = target_repo.get_target(conn, target_id)
             stock_id = target['stock_id'] if target else None
             
        if not stock_id: return 0.0
        
        # Load JSON
        base_dir = Path(__file__).parent.parent # app/
        div_file = base_dir / "data/dividends_all.json"
        
        div_db = {}
        if div_file.exists():
            with open(div_file, "r") as f:
                full_db = json.load(f)
                div_db = full_db.get(str(stock_id), {})
        
        if str(stock_id) == "2330" and not div_db:
             div_db = {
                "2023": {"cash": 11.5}, "2024": {"cash": 15.0}, "2025": {"cash": 19.0}
             }
        
        if not div_db: return 0.0
        
        # Replay Holdings
        sorted_tx = sorted(transactions, key=lambda t: t['date'])
        start_year = 2006
        current_year = date.today().year
        
        for y in range(start_year, current_year + 1):
            year_str = str(y)
            div_info = div_db.get(year_str) or div_db.get(y)
            if not div_info: continue
            
            u_cash = 0
            if isinstance(div_info, dict): u_cash = div_info.get('cash', 0)
            elif isinstance(div_info, (int, float)): u_cash = div_info
            
            if u_cash <= 0: continue
            
            ex_date = f"{y}-07-01"
            shares_on_ex = 0
            for t in sorted_tx:
                if t['date'] <= ex_date:
                    if t['type'] == 'buy': shares_on_ex += t['shares']
                    elif t['type'] == 'sell': shares_on_ex -= t['shares']
                else: break
            
            if shares_on_ex > 0:
                total_div_cash += shares_on_ex * u_cash
                
    except Exception as e:
        print(f"[Diff Calc Error] {e}")
        
    return total_div_cash

def get_portfolio_history(user_id: str = "default", months: int = 12) -> List[Dict[str, Any]]:
    import pandas as pd
    """
    Get monthly portfolio value history.
    months=0 means return ALL data.
    """
    # Clean Code: logic moved to market_data_service
    
    end_date = datetime.now()
    if months == 0:
        with get_db() as conn:
             txs = transaction_repo.get_user_transactions(conn, user_id)
             if txs:
                 earliest = min(t['date'] for t in txs)
                 start_date = datetime.strptime(earliest[:7] + "-01", "%Y-%m-%d")
             else:
                 start_date = end_date - relativedelta(months=12)
    else:
        start_date = end_date - relativedelta(months=months)
        
    start_month_str = start_date.strftime("%Y-%m")
    
    # Fetch Data
    with get_db() as conn:
        transactions = transaction_repo.get_user_transactions(conn, user_id)
        # Repo returns sorted ASC
        db_dividends = transaction_repo.get_all_dividends_for_user(conn, user_id)
        
    if not transactions and not db_dividends:
        return []

    stock_ids = list(set([tx['stock_id'] for tx in transactions] + [d['stock_id'] for d in db_dividends]))
    
    # Load Cache
    cached_divs = {}
    for sid in stock_ids:
        c_data = dividend_cache.get_cached_dividends(sid)
        if c_data: cached_divs[sid] = c_data
        
    # Build Events
    events = []
    for tx in transactions:
        events.append({'date': tx['date'], 'type': 'tx', 'data': tx})
    for div in db_dividends:
        events.append({'date': div['date'], 'type': 'div_db', 'data': div})
    for sid, div_list in cached_divs.items():
        for div in div_list:
            events.append({
                'date': div['date'], 
                'type': 'div_cache', 
                'stock_id': sid,
                'amount_per_share': div['amount']
            })
            
    events.sort(key=lambda x: x['date'])
    
    # Fetch History Prices
    price_history = {}
    if stock_ids:
        try:
            # Clean Code: Use MarketCache (Single Source of Truth)
            s_date_str = start_date.strftime("%Y-%m-%d")
            price_history = _fetch_prices_from_market_cache(stock_ids)

        except Exception as e:
            print(f"[History] Price Fetch Error: {e}")

    # Simulation
    monthly_data = {}
    portfolio = {sid: {'shares': 0, 'total_cost': 0} for sid in stock_ids}
    cumulative_realized_pl = 0
    cumulative_dividends = 0
    
    current_iter_date = start_date
    event_idx = 0
    total_events = len(events)
    
    while current_iter_date <= end_date:
        month_key = current_iter_date.strftime("%Y-%m")
        month_end_date = (current_iter_date + relativedelta(months=1)) - relativedelta(days=1)
        month_end_str = month_end_date.strftime("%Y-%m-%d")
        
        while event_idx < total_events:
            event = events[event_idx]
            if event['date'] > month_end_str: break
            
            if event['type'] == 'tx':
                tx = event['data']
                sid = tx['stock_id']
                if sid not in portfolio: portfolio[sid] = {'shares': 0, 'total_cost': 0}
                
                if tx['type'] == 'buy':
                    portfolio[sid]['shares'] += tx['shares']
                    portfolio[sid]['total_cost'] += tx['shares'] * tx['price']
                else:
                    if portfolio[sid]['shares'] > 0:
                        avg_cost = portfolio[sid]['total_cost'] / portfolio[sid]['shares']
                        cost_of_shares_sold = tx['shares'] * avg_cost
                        proceeds = tx['shares'] * tx['price']
                        pl = proceeds - cost_of_shares_sold
                        cumulative_realized_pl += pl
                        portfolio[sid]['shares'] -= tx['shares']
                        portfolio[sid]['total_cost'] -= cost_of_shares_sold
                        if portfolio[sid]['shares'] <= 0:
                            portfolio[sid]['shares'] = 0
                            portfolio[sid]['total_cost'] = 0
                            
            elif event['type'] == 'div_db':
                div = event['data']
                cumulative_dividends += div['total_cash']
                
            elif event['type'] == 'div_cache':
                sid = event['stock_id']
                if sid in portfolio and portfolio[sid]['shares'] > 0:
                    cumulative_dividends += portfolio[sid]['shares'] * event['amount_per_share']
            
            event_idx += 1
            
        total_invested = sum(p['total_cost'] for p in portfolio.values())
        total_value = 0
        for sid, data in portfolio.items():
            shares = data['shares']
            if shares > 0:
                try:
                    ph = price_history.get(sid)
                    price = 0
                    if ph is not None and not ph.empty:
                        idx = ph.index.get_indexer([month_end_date], method='nearest')[0]
                        if idx != -1:
                            val = ph.iloc[idx]
                            price = val if pd.notna(val) else (data['total_cost']/shares)
                        else: price = (data['total_cost']/shares)
                    else: price = (data['total_cost']/shares)
                    total_value += shares * price
                except:
                    total_value += data['total_cost']
        
        monthly_data[month_key] = {
            "month": month_key,
            "cost": round(total_invested, 2),
            "value": round(total_value, 2),
            "realized": round(cumulative_realized_pl, 2),
            "dividend": round(cumulative_dividends, 2),
            "tx_count": event_idx // 2
        }
        current_iter_date += relativedelta(months=1)

    return list(monthly_data.values())



def get_portfolio_race_data(user_id: str = "default") -> List[Dict[str, Any]]:
    """Calculated race data using Trend Strategy."""
    import pandas as pd
    import calendar
    # Clean Code: logic moved to market_data_service
    
    # Calculate End Date (Current Quarter End)
    now = datetime.now()
    quarter_end_month = ((now.month - 1) // 3 + 1) * 3
    last_day = calendar.monthrange(now.year, quarter_end_month)[1]
    end_date = datetime(now.year, quarter_end_month, last_day)

    with get_db() as conn:
        txs = transaction_repo.get_user_transactions(conn, user_id)
        # We need stock names too. get_user_transactions joins group_targets?
        # Checked repo: Yes, it returns gt.stock_id. But not stock_name.
        # We need target details.
        targets = target_repo.get_targets_by_user(conn, user_id)
        # Create map: target_id -> {stock_name, asset_type}
        target_map = {t['id']: {'name': t['stock_name'], 'type': t['asset_type']} for t in targets}
    
    if not txs: return []
    
    # Enrich txs with metadata
    for tx in txs:
        # get_user_transactions returns stock_id.
        # It also returns target_id.
        tid = tx['target_id']
        if tid in target_map:
            tx['stock_name'] = target_map[tid]['name']
            tx['asset_type'] = target_map[tid]['type']
        else: # Should not happen if referential integrity holds
            tx['stock_name'] = tx['stock_id']
            tx['asset_type'] = 'stock'

    stock_ids = list(set(t['stock_id'] for t in txs))
    earliest_date_str = min(t['date'] for t in txs)
    start_date = datetime.strptime(earliest_date_str[:7] + "-01", "%Y-%m-%d")

    # Fetch Prices
    price_history = {}
    # Fetch Prices
    price_history = {}
    try:
        # Clean Code: Use MarketCache (Single Source of Truth)
        s_date_str = start_date.strftime("%Y-%m-%d")
        price_history = _fetch_prices_from_market_cache(stock_ids)

    except Exception as e:
        print(f"[Race] Price Fetch Error: {e}")

    # Simulate
    race_results = []
    portfolio = {sid: {'shares': 0, 'total_cost': 0} for sid in stock_ids}
    
    current_month = start_date.month
    months_to_add = (3 - (current_month % 3)) if (current_month % 3 != 0) else 0
    current_iter_date = start_date + relativedelta(months=months_to_add)
    
    event_idx = 0
    # txs is sorted? Repo sorts by date ASC.
    
    while current_iter_date <= end_date:
        month_key = current_iter_date.strftime("%Y-%m")
        month_end_date = (current_iter_date + relativedelta(months=1)) - relativedelta(days=1)
        month_end_str = month_end_date.strftime("%Y-%m-%d")
        
        while event_idx < len(txs):
            tx = txs[event_idx]
            if tx['date'] > month_end_str: break
            
            sid = tx['stock_id']
            if tx['type'] == 'buy':
                portfolio[sid]['shares'] += tx['shares']
                portfolio[sid]['total_cost'] += tx['shares'] * tx['price']
            else:
                if portfolio[sid]['shares'] > 0:
                    avg = portfolio[sid]['total_cost'] / portfolio[sid]['shares']
                    portfolio[sid]['shares'] -= tx['shares']
                    portfolio[sid]['total_cost'] -= tx['shares'] * avg
                    if portfolio[sid]['shares'] <= 0:
                        portfolio[sid]['shares'] = 0
                        portfolio[sid]['total_cost'] = 0
            event_idx += 1
            
        for sid, data in portfolio.items():
            shares = data['shares']
            if shares <= 0: continue
            
            market_val = 0
            ph = price_history.get(sid)
            found = False
            if ph is not None and not ph.empty:
                try:
                    idx = ph.index.get_indexer([month_end_date], method='nearest')[0]
                    if idx != -1:
                        p = ph.iloc[idx]
                        if pd.notna(p):
                            market_val = shares * float(p)
                            found = True
                except: pass
            
            if not found: market_val = data['total_cost']
            
            # Find metadata (any target with this stock_id)
            # We have target_map keyed by TARGET ID, not Stock ID.
            # Need stock metadata map.
            # Lazy way: search txs? Or build map earlier.
            # We built target_map. We can build stock_meta from it.
            name = sid
            atype = 'stock'
            for t in target_map.values(): # optimization possible
                if t['name'] and t['name'] != sid: 
                     name = t['name']
                     atype = t['type']
                     break
                     
            race_results.append({
                "id": sid,
                "name": name,
                "value": round(market_val, 2),
                "month": month_key,
                "asset_type": atype,
                "image": "/images/stock.png"
            })
            
        current_iter_date += relativedelta(months=3)
        
    return race_results

def get_portfolio_snapshot(user_id: str) -> Dict[str, Any]:
    """Get current portfolio state (Wealth, Cost, ROI)."""
    with get_db() as conn:
        targets = target_repo.get_targets_by_user(conn, user_id)
        
    stock_ids = list(set(t['stock_id'] for t in targets))
    prices = market_data_service.fetch_live_prices(stock_ids)
    
    total_market_value = 0.0
    total_cost = 0.0
    
    holdings = []
    
    for t in targets:
        # Lightweight summary? Or use get_target_summary?
        # get_target_summary queries transactions.
        # Loop 50 times * SQL query?
        # It's local SQLite, likely < 10ms total. 
        # Optimized approach: Load ALL transactions and compute in memory (CalculationService pattern).
        summary = get_target_summary(t['id'], prices.get(t['stock_id'], {}).get('price'))
        
        c = summary['total_cost']
        v = summary.get('market_value', c) # Fallback to cost if no price
        
        total_cost += c
        total_market_value += v
        
        holdings.append({
            "stock_id": t['stock_id'],
            "name": t['stock_name'],
            "value": v,
            "cost": c,
            "asset_type": t['asset_type']
        })
        
    total_roi = 0.0
    if total_cost > 0:
        total_roi = (total_market_value - total_cost) / total_cost * 100
        
    return {
        "total_wealth": total_market_value,
        "total_cost": total_cost,
        "total_roi": total_roi,
        "holdings": holdings
    }

def _fetch_prices_from_market_cache(stock_ids: List[str]) -> Dict[str, Any]:
    """Helper to fetch prices from MarketCache as pd.Series"""
    import pandas as pd
    results = {}
    for sid in stock_ids:
        # Use fast history (Daily V2 or Yearly V1)
        history = MarketCache.get_stock_history_fast(sid)
        if not history: continue
        
        dates = []
        prices = []
        
        for h in history:
            if 'date' in h:
                # V2 Daily
                dates.append(pd.to_datetime(str(h['date'])))
                prices.append(float(h['close']))
            else:
                # V1 Yearly - Approximate
                # Use Year start/end
                year = h['year']
                # Start
                dates.append(pd.to_datetime(f"{year}-01-01"))
                prices.append(float(h.get('open', 0)))
                # End
                dates.append(pd.to_datetime(f"{year}-12-31"))
                prices.append(float(h.get('close', 0)))
                
        if dates:
            s = pd.Series(data=prices, index=dates)
            s = s.sort_index()
            # Dedupe indices if needed
            s = s.groupby(s.index).last()
            results[sid] = s
            
    return results

def get_portfolio_ladder(user_id: str) -> Dict[str, Any]:
    """
    Get asset distribution ladder (Stock, ETF, CB, Cash).
    Cash denotes realized dividends (uninvested) + cash balance.
    """
    # 1. Get Market Value of Holdings (Live)
    snapshot = get_portfolio_snapshot(user_id)
    holdings = snapshot['holdings']
    
    alloc = {"stock": 0.0, "etf": 0.0, "cb": 0.0, "cash": 0.0}
    
    for h in holdings:
        val = h['value']
        atype = h.get('asset_type', 'stock').lower()
        if atype in alloc:
            alloc[atype] += val
        else:
            alloc['stock'] += val # Fallback
            
    # 2. Get Realized Cash (Dividends)
    # TODO: Add Cash Deposit/Withdrawal tracking? Currently only Dividends.
    with get_db() as conn:
        divs = transaction_repo.get_all_dividends_for_user(conn, user_id)
        
    total_div_cash = sum(d['total_cash'] for d in divs)
    alloc['cash'] += total_div_cash
    
    total_wealth = sum(alloc.values())
    
    ladder = []
    if total_wealth > 0:
        for k, v in alloc.items():
            ladder.append({
                "type": k,
                "value": round(v, 2),
                "pct": round((v / total_wealth) * 100, 1)
            })
            
    return {
        "total_wealth": total_wealth,
        "ladder": ladder
    }
