
import asyncio
from project_tw.strategies.cb import CBStrategy

async def main():
    print("Initialize CB Strategy...")
    strategy = CBStrategy()
    
    # Target: 6533 (Andes)
    targets = ['6533']
    print(f"Analyzing: {targets}")
    
    results = await strategy.analyze_list(targets)
    
    print("\n=== Analysis Results ===")
    for r in results:
        print(r)

if __name__ == "__main__":
    asyncio.run(main())
