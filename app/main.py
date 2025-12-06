
from fastapi import FastAPI, BackgroundTasks
from pydantic import BaseModel
from project_tw.strategies.mars import MarsStrategy
from project_tw.strategies.cb import CBStrategy, CBMyAdvice
from project_tw.crawler import TWSECrawler
import asyncio

app = FastAPI(title="Stock Strategy App (Mars & CB)")

class CrawlRequest(BaseModel):
    stock_code: str
    start_year: int
    end_year: int

class MarsRequest(BaseModel):
    stock_codes: list[str]
    start_year: int
    end_year: int
    std_threshold: float = 20.0

class CBRequest(BaseModel):
    cb_price: float
    stock_price: float
    conversion_price: float

# Global State (In-memory for MVP)
mars_portfolio = []
mars_strategy = MarsStrategy()
cb_strategy = CBStrategy()

@app.get("/")
def read_root():
    return {"status": "Online", "strategies": ["Mars", "CB"]}

@app.post("/api/crawl")
async def trigger_crawl(req: CrawlRequest):
    """Test endpoint to fetch one stock"""
    crawler = TWSECrawler()
    raw = await crawler.fetch_history(req.stock_code, req.start_year, req.end_year)
    df = crawler.parse_to_dataframe(raw)
    return {
        "stock": req.stock_code, 
        "data_points": len(df),
        "sample": df.head().to_dict() if not df.empty else None
    }

async def run_mars_analysis(req: MarsRequest):
    global mars_portfolio
    print("Starting Mars Analysis...")
    metrics = await mars_strategy.analyze_stock_batch(req.stock_codes, req.start_year, req.end_year)
    mars_portfolio = mars_strategy.filter_and_rank(metrics, req.std_threshold)
    print(f"Mars Analysis Complete. Found {len(mars_portfolio)} candidates.")

@app.post("/api/mars/analyze")
async def start_mars_analysis(req: MarsRequest, background_tasks: BackgroundTasks):
    """Start background analysis of a list of stocks."""
    background_tasks.add_task(run_mars_analysis, req)
    return {"status": "Analysis Started", "target_count": len(req.stock_codes)}

@app.get("/api/mars/portfolio")
def get_mars_portfolio():
    """Get the calculated Top 50"""
    return {"count": len(mars_portfolio), "portfolio": mars_portfolio}

@app.post("/api/cb/evaluate", response_model=CBMyAdvice)
def evaluate_cb(req: CBRequest):
    """
    Calculate Premium and return Advice.
    """
    # 1. Calc I2 (Premium)
    i2 = cb_strategy.calculate_premium(req.cb_price, req.stock_price, req.conversion_price)
    
    # 2. Get Advice
    advice = cb_strategy.evaluate(i2)
    return advice

@app.get("/api/cb/status")
def get_cb_status():
    return {"status": "Active", "message": "CB Strategy Ready."}
