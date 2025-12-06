
import asyncio
import pandas as pd
from project_tw.crawler import TWSECrawler
from project_tw.calculator import ROICalculator

class MarsStrategy:
    def __init__(self):
        self.crawler = TWSECrawler()
        self.calculator = ROICalculator()
        self.top_50 = []
        
    async def analyze_stock_batch(self, stock_codes: list, start_year: int, end_year: int, std_threshold: float = 20.0):
        """
        Analyze a batch of stocks and return metrics.
        """
        results = []
        
        for code in stock_codes:
            # 1. Fetch Data
            # Note: sequential fetch here effectively throttled by Crawler's internal sleep
            raw_data = await self.crawler.fetch_history(code, start_year, end_year)
            df = self.crawler.parse_to_dataframe(raw_data)
            
            if df.empty or len(df) < 200: # Ensure enough data points
                continue
                
            # 2. Calculate Metrics
            metrics = self.calculator.calculate_metrics(df)
            
            if metrics:
                metrics['stock_code'] = code
                results.append(metrics)
                
        return results

    def filter_and_rank(self, metrics_list, std_threshold=20.0):
        """
        Apply Mars logic:
        1. Low Volatility (std < threshold)
        2. Stable Growth (Rank by CAGR)
        """
        df = pd.DataFrame(metrics_list)
        if df.empty:
            return []
            
        # Filter
        qualified = df[df['volatility_pct'] <= std_threshold]
        
        # Rank desc by CAGR
        ranked = qualified.sort_values(by='cagr_pct', ascending=False)
        
        # Take Top 50
        self.top_50 = ranked.head(50).to_dict('records')
        return self.top_50
