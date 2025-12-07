
import asyncio
import pandas as pd
from project_tw.crawler import TWSECrawler
from project_tw.calculator import ROICalculator

class MarsStrategy:
    def __init__(self):
        self.crawler = TWSECrawler()
        self.calculator = ROICalculator()
        self.top_50 = []
        
    async def analyze_stock_batch(self, stock_codes: list, start_year: int, end_year: int, std_threshold: float = 100.0):
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
                # Enrich with Name (Simple Map for Demo)
                # In prod, this would look up from a database or stock_list.json
                name_map = {
                    '2330': 'TSMC', '2317': 'Hon Hai', '2412': 'Chunghwa', 
                    '2454': 'MediaTek', '0050': 'Yuanta 50', '2303': 'UMC',
                    '2881': 'Fubon Fin', '2882': 'Cathay Fin'
                }
                metrics['stock_name'] = name_map.get(code, code)
                # Map 'end_price' to 'price' for frontend consistency
                metrics['price'] = metrics.get('end_price', 0)
                
                results.append(metrics)
                
        return results

    def filter_and_rank(self, metrics_list, std_threshold=100.0):
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

    def save_to_excel(self, output_path: str):
        """
        Save the filtered Top 50 results to an Excel file.
        Matches the user's requested output format (approx).
        """
        if not self.top_50:
            print("No data to save.")
            return

        df = pd.DataFrame(self.top_50)
        # Reorder columns if needed for readability
        cols = ['stock_code', 'stock_name', 'price', 'cagr_pct', 'volatility_pct']
        # Add other cols if they exist
        existing_cols = df.columns.tolist()
        final_cols = [c for c in cols if c in existing_cols] + [c for c in existing_cols if c not in cols]
        
        df = df[final_cols]
        
        print(f"Saving filtered list to {output_path}...")
        df.to_excel(output_path, index=False)
        print("Save complete.")
