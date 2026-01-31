import sys
import os
from pathlib import Path

# Add project root to sys.path
BASE_DIR = Path(__file__).resolve().parents[2]
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

import pytest
import pandas as pd
import os
import pandera as pa
from tests.schemas import StockListSchema

OUTPUT_PATH = "project_tw/output/stock_list_s2006e2025_unfiltered.xlsx"

def test_output_schema_validity():
    """
    Rigorously validate the output Excel against the defined Schema.
    checks types, constraints (e.g. volatility >= 0), and coercibility.
    """
    if not os.path.exists(OUTPUT_PATH):
        pytest.skip("Output file missing")
        
    df = pd.read_excel(OUTPUT_PATH)
    
    try:
        StockListSchema.validate(df, lazy=True)
    except pa.errors.SchemaErrors as err:
        print("Schema Validation Errors:")
        print(err.failure_cases)
        pytest.fail(f"Schema Validation Failed: {len(err.failure_cases)} errors found. See stdout.")
