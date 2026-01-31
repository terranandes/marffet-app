import sys
import os
from pathlib import Path

# Add project root to sys.path
BASE_DIR = Path(__file__).resolve().parents[2]
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

import pandera as pa
from pandera.typing import Series

# Define the strict schema for the Output Excel file
# This enforces types, checks for nulls, and validates logic (e.g., price > 0)

class StockListSchema(pa.DataFrameModel):
    id: Series[str] = pa.Field(coerce=True, description="Stock ID, must be string")
    name: Series[str] = pa.Field(nullable=True, description="Stock Name")
    
    # Financial metrics - allow nullable as some stocks might have missing data
    # But if present, must be float
    cagr_pct: Series[float] = pa.Field(nullable=True, ge=-100, le=10000)
    volatility_pct: Series[float] = pa.Field(nullable=True, ge=0)
    
    # We expect these columns to ideally exist if the pipeline is complete
    # But we mark some as nullable:True to be realistic about partial data
    
    class Config:
        coerce = True # Auto-convert types if possible
        strict = False # Allow extra columns (don't fail on new features)
