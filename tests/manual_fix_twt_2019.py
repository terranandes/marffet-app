import json

data = {
    "stat": "OK",
    "date": "2019",
    "title": "Manual Fix",
    "data": [
        # Date, Code, Name, BeforeClose, AfterClose, StockDiv, CashDiv, ...
        # Standard columns: Date, Code, Name, ExDivBefore, ExDivAfter, CashDiv, StockDiv... 
        # Actually TWT49U columns: 
        # 0: Date (108/07/11)
        # 1: Code (6669)
        # 2: Name
        # 3: Ex-Right/Div Ref Price (Before)
        # 4: Ex-Right/Div Ref Price (After)
        # 5: Rights Value
        # 6: Cash Div Value (16.0)
        # 7: Stock Div Value (0.0)
        # Let's mock it sufficiently for crawler to parse.
        # Crawler expects: row[0]=Date, row[1]=Code, row[7]=Stock, row[6]=Check?
        # project_tw/crawler.py: 
        #   date_str = row[0]
        #   code = row[1]
        #   cash = float(row[5 or 6?])
        # Let's check crawler parsing logic.
        # It calls `fetch_ex_rights_history`.
        # Parsing:
        #   stock_div = float(r[7]) (if len > 7)
        #   cash_div = float(r[6])
        # So Index 7 is Stock, Index 6 is Cash.
        ["108/07/11", "6669", "緯穎", "400.0", "384.0", "0.0", "16.0", "0.0"]
    ]
}

with open("data/raw/TWT49U_2019.json", "w") as f:
    json.dump(data, f)

print("Manual TWT49U_2019.json created.")
