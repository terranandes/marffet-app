import json
import math

def simulate_2019():
    print("--- 6669 2019 Simulation Verification ---")
    
    # 1. Load Data
    with open("data/raw/Market_2019_Prices.json") as f:
        prices = json.load(f)['6669'] # {'start': 370.0, 'end': 635.0} ...
        
    with open("data/raw/TWT49U_2019.json") as f:
        div_data = json.load(f)['data'][0] # Check first row (manual fix)
        # Verify it's 6669
        if '6669' not in div_data[1]:
             print("Warning: First row isn't 6669?")
             # Scan
             pass
        cash_div = float(div_data[6]) # 16.0
        
    p_start = prices['start'] # Expect 370.0
    p_end = prices['end']     # Expect 635.0
    p_avg = (p_start + p_end) / 2 # Simple avg for simulation if internal avg missing? 
    # Actually Calculator uses yearly_avg_prices = df.groupby...mean()
    # Since we don't have full history, I'll approximate Avg Price. 
    # Or I can assume `p_avg` roughly `(370+635)/2 = 502.5`.
    
    # User Question: "1,000,000 / 60000 buy parameters"
    # Actually Mars Strategy: Principal 1M + 60k Extra annually?
    # Logic:
    # Year 1 (Start): Principal + Extra.
    # verify_6669 earlier code: `amt = principal + 60_000` for first year.
    # So Total Invest 1,060,000.
    
    principal = 1_000_000
    extra = 60_000
    invest_amt = principal + extra
    
    print(f"1. Investment Date/Price:")
    print(f"   - Buy Date: Start of 2019 (Listing ~3/27)")
    print(f"   - Buy Price: {p_start}")
    print(f"   - Invest Amount: {invest_amt}")
    
    shares = invest_amt / p_start
    print(f"   - Shares Bought: {shares:.4f}")
    
    print(f"\n2. Dividend Application:")
    print(f"   - Cash Div: {cash_div}")
    total_cash_div = shares * cash_div
    print(f"   - Total Cash Recv: {total_cash_div:.2f}")
    
    # Reinvest at Avg Price
    # Let's estimate Avg Price.
    p_reinvest = (p_start + p_end) / 2
    if p_reinvest == 0: p_reinvest = p_start
    
    shares_added = total_cash_div / p_reinvest
    print(f"   - Reinvest Price (Est Avg): {p_reinvest:.2f}")
    print(f"   - Shares Added: {shares_added:.4f}")
    
    final_shares = shares + shares_added
    print(f"   - Total Shares: {final_shares:.4f}")
    
    print(f"\n3. End of 2019:")
    print(f"   - End Price: {p_end}")
    final_value = final_shares * p_end
    print(f"   - Final Value: {final_value:.2f}")
    
    roi = (final_value - invest_amt) / invest_amt * 100
    print(f"   - Total ROI 2019: {roi:.2f}%")
    
    print("\n--- Summary for User ---")
    print(f"Buy Price: {p_start}")
    print(f"Div Applied: {cash_div}")
    print(f"End Price: {p_end}")
    print(f"ROI: {roi:.1f}%")

if __name__ == "__main__":
    simulate_2019()
