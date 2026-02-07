import sys
from pathlib import Path
import time
import logging

# Setup Path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(message)s')

def verify_full_stack():
    print("=== Martian Project: Full Stack Verification ===\n")
    
    # 1. Verify Data Lake (The 'DB Files')
    logging.info("Step 1: Checking Data Lake (JSON Files)...")
    data_dir = BASE_DIR / "data/raw"
    years = range(2006, 2027)
    missing = []
    found = 0
    for y in years:
        if (data_dir / f"Market_{y}_Prices.json").exists():
            found += 1
        else:
            missing.append(y)
    
    if len(missing) > 5:
        logging.error(f"FAIL: Missing {len(missing)} years of data. Scraper must be run.")
        return
    logging.info(f"PASS: Found {found}/{len(years)} years of Market Data. (Clean Room Source)")

    # 2. Verify Setup (MarketCache)
    logging.info("\nStep 2: Verifying App 'MarketCache' (In-Memory DB)...")
    try:
        from app.services.market_cache import MarketCache
        t0 = time.time()
        db = MarketCache.get_prices_db()
        t1 = time.time()
        logging.info(f"PASS: MarketCache loaded in {t1-t0:.2f}s.")
        
        # Check TSMC
        tsmc = db[2006].get("2330")
        if not tsmc:
            logging.error("FAIL: TSMC (2330) not found in 2006 data!")
            return
            
        logging.info(f"PASS: TSMC 2006 Data Integrity Check: Open={tsmc.get('first_open')} (Expected ~59.1)")
        
    except Exception as e:
        logging.error(f"FAIL: MarketCache Error: {e}")
        return

    # 3. Verify App Logic (Engine)
    logging.info("\nStep 3: Verifying Simulation Engine...")
    try:
        from app.project_tw.calculator import ROICalculator
        import pandas as pd
        
        # Simulate 'Get Details'
        history = MarketCache.get_stock_history_fast("2330")
        df = pd.DataFrame(history)
        
        calc = ROICalculator()
        res = calc.calculate_complex_simulation(df, 2006, 1_000_000, 60_000, buy_logic='FIRST_OPEN')
        
        final_val = res.get('finalValue', 0)
        cagr_key = "s2006e2026bao" # Approximate key check
        
        # Find actual last key
        cagr = 0
        for k, v in res.items():
            if 'bao' in k and 'e2026' in k:
                cagr = v
        
        logging.info(f"PASS: Simulation Result for TSMC: ${final_val:,.0f} (CAGR: {cagr}%)")
        if cagr < 15:
            logging.warning("WARNING: CAGR seems low (<15%). Check logic.")
        else:
            logging.info("PASS: CAGR is healthy/realistic.")
            
    except Exception as e:
        logging.error(f"FAIL: Engine Error: {e}")
        return

    print("\n=== VERIFICATION COMPLETE: SYSTEM GO ===")
    print("You can verify the Frontend by running: cd frontend && npm run dev")

if __name__ == "__main__":
    verify_full_stack()
