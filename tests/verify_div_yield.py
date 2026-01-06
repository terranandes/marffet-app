import requests
import sys

try:
    res = requests.get('http://localhost:8000/api/race-data')
    data = res.json()
    
    # Filter for 2330
    tsmc = [d for d in data if d['id'] == '2330']
    tsmc.sort(key=lambda x: x['year'])
    
    found = False
    for entry in tsmc:
        dy = entry.get('div_yield', 'N/A')
        print(f"Year: {entry['year']} | ROI: {entry['roi']}% | DivYield: {dy}%")
        if entry['year'] == 2006 and dy != 'N/A' and dy > 0:
            found = True
            
    if found:
        print("SUCCESS: div_yield found for TSMC 2006")
    else:
        print("FAILURE: div_yield missing or zero for TSMC 2006")
        
except Exception as e:
    print(e)
