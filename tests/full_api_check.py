import httpx
import asyncio
import sys
from rich.console import Console
from rich.table import Table

console = Console()

BASE_URL = "http://localhost:8000"
# Use a mock session or just header if auth is simple (it relies on cookies usually)
# For local dev, we might need a valid session cookie for the user 'terranfund'
# But for now, let's try guest mode or public endpoints, and report Auth failures if 401.

endpoints = [
    # System
    {"name": "Health Check", "url": "/health", "method": "GET"},
    
    # Mars Strategy
    {"name": "Mars Data (Race)", "url": "/api/race-data?start_year=2006", "method": "GET"},
    
    # CB Strategy
    {"name": "CB Analysis", "url": "/api/cb/analyze", "method": "GET"},
    {"name": "CB Portfolio", "url": "/api/cb/portfolio", "method": "GET"},
    
    # Portfolio
    {"name": "Portfolio By Type", "url": "/api/portfolio/by-type", "method": "GET"},
    {"name": "Portfolio Trend", "url": "/api/portfolio/trend", "method": "GET"},
    {"name": "Portfolio Cash", "url": "/api/portfolio/cash", "method": "GET"},
    
    # GM Dashboard (Admin)
    {"name": "Admin Metrics", "url": "/api/admin/metrics", "method": "GET"},
    {"name": "Crawl Status", "url": "/api/admin/crawl/status", "method": "GET"},
    
    # Settings/Feedback
    {"name": "Feedback Categories", "url": "/api/feedback/categories", "method": "GET"},
]

async def check_endpoints():
    table = Table(title="Martian System Verification")
    table.add_column("Feature", style="cyan")
    table.add_column("Endpoint", style="magenta")
    table.add_column("Status", style="green")
    table.add_column("Latency", style="yellow")
    table.add_column("Note", style="white")

    # We need a cookie to access protected routes.
    # Since we can't easily login via script without simulating the whole OAuth flow (or dev bypass),
    # We will try to rely on 'terranfund' session if it exists in DB, or fail gracefully.
    # Actually, the local dev might allow some access?
    # Let's try to hit /auth/login first to see if we get a cookie session? 
    # No, that's OAuth.
    # We will run this and see which return 401.
    
    async with httpx.AsyncClient(base_url=BASE_URL, timeout=10.0, follow_redirects=True) as client:
        # 1. Check Health
        try:
            r = await client.get("/health")
            if r.status_code == 200:
                table.add_row("System", "/health", "✅ OK", f"{r.elapsed.total_seconds()*1000:.0f}ms", "Healthy")
            else:
                table.add_row("System", "/health", "❌ FAIL", "-", f"Status: {r.status_code}")
        except Exception as e:
            table.add_row("System", "/health", "❌ CRITICAL", "-", f"Connection Refused? {e}")
            console.print(table)
            return

        # 2. Check Other Endpoints
        # Note: Protected endpoints (Portfolio, Admin) will likely return 401 if we don't send cookies.
        # But 401 confirms the endpoint EXISTS and is protected, which is a partial pass.
        # 500 would be a fail.
        
        # Manually constructing a simple cookie if possible? 
        # In 'app/auth.py', typically sessions are signed.
        # We'll just report status.
        
        for ep in endpoints:
            try:
                r = await client.request(ep["method"], ep["url"])
                status = str(r.status_code)
                icon = "✅" if r.status_code == 200 else ("⚠️" if r.status_code in [401, 403] else "❌")
                
                note = ""
                if r.status_code == 200:
                    try:
                        data = r.json()
                        if isinstance(data, list):
                            note = f"Items: {len(data)}"
                        elif isinstance(data, dict):
                            note = "JSON OK"
                    except:
                        note = "Not JSON"
                elif r.status_code == 401:
                    note = "Auth Required (Expected)"
                elif r.status_code == 500:
                    note = "Internal Server Error!"
                
                table.add_row(ep["name"], ep["url"], f"{icon} {status}", f"{r.elapsed.total_seconds()*1000:.0f}ms", note)
            except Exception as e:
                table.add_row(ep["name"], ep["url"], "❌ ERROR", "-", str(e))

    console.print(table)

if __name__ == "__main__":
    asyncio.run(check_endpoints())
