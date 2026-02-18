
import math

def solve_split(code, year, prior, ref, true_cash=None, true_stock=None):
    # Total Value = Prior - Ref
    # Cash = Total - (Ref * Stock/10)
    
    total_val = prior - ref
    candidates = []
    
    # Iterate Stock from 0.0 to 5.0 in 0.01 steps (cover 0.1, 0.05, etc.)
    # Most stock dividends are multiples of 0.1 or 0.05
    steps = [x * 0.01 for x in range(0, 501)] # 0.00 to 5.00
    
    print(f"--- {code} {year} ---")
    print(f"Prior: {prior}, Ref: {ref}, Total: {total_val:.4f}")
    if true_cash is not None:
        print(f"TRUE: Cash={true_cash}, Stock={true_stock}")
        
    for s in steps:
        # Implied Cash
        implied_cash = total_val - (ref * s / 10.0)
        
        if implied_cash < 0: continue
        
        # Check "Niceness" of Cash
        # Perfect nice: distance to nearest 0.01 is 0
        rounded_cash = round(implied_cash, 2)
        diff = abs(implied_cash - rounded_cash)
        
        # Heuristic: Stock is usually simple (X.X or X.XX)
        # Cash is usually simple (X.XX)
        
        # Score: minimizes (diff_cash + diff_stock_complexity)
        # We simulate "simple stock" by preferring x.0, x.5, x.1
        
        complexity = 0.0
        s_rounded = round(s, 2)
        if abs(s_rounded % 1.0) < 0.001: complexity = 0     # 1.0, 2.0
        elif abs(s_rounded % 0.5) < 0.001: complexity = 0.1 # 0.5, 1.5
        elif abs(s_rounded % 0.1) < 0.001: complexity = 0.2 # 0.1, 0.2
        else: complexity = 0.5 # 0.05, 0.01
        
        score = diff * 100 + complexity
        
        candidates.append({
            'stock': s_rounded,
            'cash': rounded_cash,
            'raw_cash': implied_cash,
            'score': score,
            'diff': diff
        })
        
    # Sort by score
    candidates.sort(key=lambda x: x['score'])
    
    # Print top 5
    for i, c in enumerate(candidates[:5]):
        match = "✅" if true_cash and abs(c['cash'] - true_cash) < 0.02 and abs(c['stock'] - true_stock) < 0.02 else ""
        print(f"#{i+1}: Stock={c['stock']:.2f}, Cash={c['cash']:.2f} (Err={c['diff']:.5f}) Score={c['score']:.3f} {match}")

# Test Cases
# 2892 (2024): Prior=28.25, Ref=26.60 -> True: Cash=0.85, Stock=0.3
solve_split("2892", 2024, 28.25, 26.60, 0.85, 0.3)

# 2889 (國票金) 2024: Prior=15.90, Ref=??? (Need to look up)
# From Goodinfo: 2024 Cash=0.73, Stock=0.246. Prior=17.05, Ref=15.92 (approx)
# Let's test if TWT49U data supports this.
solve_split("2889", 2024, 17.05, 15.92, 0.73, 0.246)
# Note: 0.246 is weird. Let's see if solver finds it.

# 5876 (上海商銀) 2024: Cash=1.8, Stock=0.
# Prior=48.05. Ref=46.25.
# Total=1.8. Stock=0.
solve_split("5876", 2024, 48.05, 46.25, 1.8, 0.0)

