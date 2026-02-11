import asyncio
import os
import json
import shutil
import pytest
from pathlib import Path
from app.services.market_data_service import _merge_data_dict

@pytest.mark.asyncio
async def test_smart_merge_logic():
    print("Starting Verification: Smart Merge Logic (No Overwrite)")
    
    # 1. Existing data (Manual Patch)
    existing = {
        "2330": {"summary": {"note": "MANUAL_PATCH_DO_NOT_OVERWRITE"}}
    }
    
    # 2. Fresh download results
    new_data = {
        "2330": {"summary": {"note": "FRESH_DOWNLOAD_BAD_VALUE"}}, # Should be ignored
        "2303": {"summary": {"note": "NEW_DATA"}}                   # Should be added
    }
    
    # 3. Apply Smart Merge
    # Safe Mode (overwrite=False)
    merged = _merge_data_dict(existing, new_data, overwrite=False)
    
    # 4. Verify Results
    final_2330 = merged["2330"]["summary"]["note"]
    final_2303 = merged["2303"]["summary"]["note"]
    
    print(f"\nResults:")
    print(f"2330 Note: {final_2330}")
    print(f"2303 Note: {final_2303}")
    
    assert final_2330 == "MANUAL_PATCH_DO_NOT_OVERWRITE"
    assert final_2303 == "NEW_DATA"
    print("\n✅ Verification SUCCESS: Smart Merge preserved existing data and added new data.")

if __name__ == "__main__":
    asyncio.run(test_smart_merge_logic())
