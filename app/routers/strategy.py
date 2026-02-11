from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from app.services.strategy_service import MarsStrategy
from io import BytesIO
import logging

# Setup Logging
logger = logging.getLogger(__name__)

router = APIRouter()

class MarsAnalyzeRequest(BaseModel):
    start_year: int = 2006
    stock_ids: List[str] = ["ALL"]

class ExportRequest(BaseModel):
    data: List[Dict[str, Any]]

@router.post("/mars/analyze")
async def analyze_mars(request: MarsAnalyzeRequest):
    """
    Analyze stocks using Mars Strategy (MarketCache + ROICalculator).
    Accepts start_year and optional list of stock_ids.
    """
    try:
        logger.info(f"Analyzing Mars Strategy for start_year={request.start_year}")
        strategy = MarsStrategy()
        results = await strategy.analyze(request.stock_ids, request.start_year)
        return results
    except Exception as e:
        logger.error(f"Error in analyze_mars: {e}")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

@router.post("/export")
async def export_results(request: ExportRequest):
    """
    Export strategy results to Excel.
    Expects a JSON body with 'data': List[Dict].
    Returns an Excel file download.
    """
    try:
        logger.info(f"Exporting {len(request.data)} rows to Excel")
        strategy = MarsStrategy()
        excel_bytes = strategy.export_to_excel(request.data)
        
        # Create a BytesIO object to stream
        buf = BytesIO(excel_bytes)
        buf.seek(0)
        
        filename = "mars_strategy_export.xlsx"
        
        return StreamingResponse(
            buf,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
    except Exception as e:
        logger.error(f"Error in export_results: {e}")
        raise HTTPException(status_code=500, detail=f"Export failed: {str(e)}")
