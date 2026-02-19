"""
Script to identify and fix stock data discrepancies based on correlation report.
Reads docs/product/correlation_report_full.csv and runs crawl_fast.py for problematic tickers.
"""
import csv
import subprocess
import os
import sys

def main():
    report_path = "docs/product/correlation_report_full.csv"
    if not os.path.exists(report_path):
        # Try alternate path
        report_path = "tests/analysis/correlation_report_full.csv"
        if not os.path.exists(report_path):
            print(f"❌ Report not found at {report_path}")
            sys.exit(1)
            
    print(f"📖 Reading report from {report_path}...")
    
    targets = []
    
    with open(report_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            code = row.get('code')
            status = row.get('status')
            diff_str = row.get('diff', '0')
            
            try:
                diff = float(diff_str)
            except:
                diff = 0.0
                
            # Criteria:
            # 1. Status is 'No Data' or 'Mismatch'
            # 2. Or Absolute Diff > 5.0 (percentage points)
            
            if status in ['No Data', 'Mismatch']:
                targets.append(code)
            elif abs(diff) > 5.0:
                if code not in targets:
                    targets.append(code)
                    
    if not targets:
        print("✅ No discrepancies found to fix.")
        return

    # De-duplicate
    targets = sorted(list(set(targets)))
    
    print(f"🔍 Found {len(targets)} stocks to fix: {targets}")
    
    # Run crawl_fast.py
    # We can pass them all in one go? 
    # crawl_fast.py takes --tickers "1101 2330" (space separated? or comma?)
    # Let's check crawl_fast.py arg parser.
    # It usually uses nargs='+' or splits by comma.
    # crawl_fast.py: parser.add_argument("--tickers", nargs="+", ...)
    # So space separated.
    
    tickers_arg = ",".join(targets)
    cmd = [
        "uv", "run", "python3", "scripts/ops/crawl_fast.py",
        "--tickers", tickers_arg,
        "--start-year", "2000"
    ]
    
    print(f"🚀 Launching fix for {len(targets)} stocks...")
    # print(" ".join(cmd))
    
    subprocess.run(cmd, check=True)
    
    print("✨ Fix complete. Please re-run correlation report to verify.")

if __name__ == "__main__":
    main()
