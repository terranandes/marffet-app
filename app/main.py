
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
import asyncio
import os
import sys

# Ensure project root is in path
sys.path.append(os.getcwd())

from project_tw.strategies.cb import CBStrategy
from project_tw.calculator import ROICalculator

app = FastAPI(title="Martian Investment System")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------- API Endpoints ----------------

@app.get("/api/results")
def get_results():
    """Return filtered results from Excel"""
    try:
        df = pd.read_excel("project_tw/output/stock_list_s2006e2025_filtered.xlsx")
        # Replace NaN
        df = df.fillna(0)
        return df.to_dict(orient="records")
    except Exception as e:
        return {"error": str(e)}

@app.get("/api/race-data")
def get_race_data():
    """Return year-by-year ranking data for Bar Chart Race"""
    try:
        df = pd.read_excel("project_tw/output/stock_list_s2006e2025_filtered.xlsx")
        
        race_data = []
        year_cols = [c for c in df.columns if 'bao' in c]
        
        for _, row in df.iterrows():
            for col in year_cols:
                try:
                    # Format: s2006e2007bao
                    year_str = col.split('e')[1][:4]
                    val = row[col]
                    
                    if pd.notnull(val) and val != 0:
                        race_data.append({
                            "year": int(year_str),
                            "id": str(row['id']),
                            "name": row['name'],
                            "roi": round(val, 2), # ROI %
                            "value": round(val, 2) # For chart
                        })
                except: pass
                
        return race_data
    except Exception as e:
        return {"error": str(e)}

@app.get("/api/cb/analyze")
async def analyze_cb(code: str):
    """Analyze CB Code on demand"""
    try:
        strategy = CBStrategy()
        results = await strategy.analyze_list([code])
        if results:
            return results[0]
        return {"action": "NOT_FOUND"}
    except Exception as e:
        return {"error": str(e)}


# ---------------- Static Files ----------------
# Must come LAST to avoid capturing API routes
# Create dir if not exists
os.makedirs("app/static", exist_ok=True)

app.mount("/static", StaticFiles(directory="app/static"), name="static")

@app.get("/")
async def read_index():
    return FileResponse("app/static/index.html")
