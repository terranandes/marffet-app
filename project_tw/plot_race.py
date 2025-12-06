
import plotly.express as px
import pandas as pd
import numpy as np

def generate_bar_chart_race_plotly(df_rois: pd.DataFrame, n_bars: int = 10, title: str = "Stock ROI Race"):
    """
    Generate a Plotly Animation for Bar Chart Race.
    df_rois: DataFrame where Index is Date, Columns are Stock Codes, Values are ROI/Price.
    """
    # 1. Resample and Interpolate for smoothness
    # Assuming df is daily, maybe resample to weekly for animation speed or keep daily
    # Linear interpolation to handle missing values
    df_interp = df_rois.resample('D').mean().interpolate(method='linear')
    df_interp.index.name = 'date'
    
    # 2. Transform to Long Format for Plotly Express
    # Date | Stock | Value
    df_long = df_interp.reset_index().melt(id_vars='date', var_name='Stock', value_name='ROI')
    
    # 3. Filter Top N per frame (Optional, creates jitter if stocks jump in/out too fast)
    # A simplified approach for MVP: Just rank them every day
    df_long['Rank'] = df_long.groupby('date')['ROI'].rank(method='first', ascending=False)
    
    # Keep only Top N
    df_long = df_long[df_long['Rank'] <= n_bars]
    
    # 4. Create Plot
    # Note: animation_frame needs string or int, date works but can be slow if too many frames
    # Let's subset frames to every 5th or 10th day to keep it rendering fast
    dates = df_long['date'].unique()
    if len(dates) > 200:
        # Downsample frames
        skip = len(dates) // 100 # Target ~100 frames
        keep_dates = dates[::skip]
        df_long = df_long[df_long['date'].isin(keep_dates)]
        
    df_long['DateStr'] = df_long['date'].dt.strftime('%Y-%m-%d')
    df_long = df_long.sort_values(by=['date', 'Rank'])

    fig = px.bar(
        df_long, 
        x='ROI', 
        y='Stock', 
        animation_frame='DateStr', 
        orientation='h',
        range_x=[df_long['ROI'].min(), df_long['ROI'].max() * 1.1],
        title=title,
        text='ROI'
    )
    
    # Aesthetics
    fig.update_layout(
        yaxis={'categoryorder': 'total ascending'}, # Try to keep stable? Hard in simple Plotly
        xaxis_title="ROI (%)",
        yaxis_title="Stock",
        showlegend=False,
        height=600
    )
    
    # Speed
    fig.layout.updatemenus[0].buttons[0].args[1]['frame']['duration'] = 100
    fig.layout.updatemenus[0].buttons[0].args[1]['transition']['duration'] = 50
    
    return fig
