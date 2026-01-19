
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os
import sys
import asyncio

# Add project root to path
sys.path.append(os.getcwd())

from app.project_tw.strategies.cb import CBStrategy

st.set_page_config(page_title="Martian Investment", layout="wide", page_icon="🚀")

# Styling
st.markdown("""
<style>
    .reportview-container {
        background: #0e1117;
    }
    .main {
        background: #0e1117;
        color: white;
    }
    h1, h2, h3 {
        color: #00f2ea !important; /* Cyberpunk Cyan */
    }
    .stButton>button {
        color: #0e1117;
        background-color: #00f2ea;
        border-radius: 5px;
    }
</style>
""", unsafe_allow_html=True)

st.title("🚀 Martian Investment System")

tabs = st.tabs(["📊 Mars Strategy", "🏁 Bar Chart Race", "💰 Convertible Bond (CB)"])

@st.cache_data
def load_mars_data():
    path = 'app/project_tw/output/stock_list_s2006e2025_filtered.xlsx'
    if os.path.exists(path):
        return pd.read_excel(path)
    return pd.DataFrame()

df_mars = load_mars_data()

with tabs[0]:
    st.header("Mars Strategy - Top 50")
    if not df_mars.empty:
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Total Stocks", len(df_mars))
        with col2:
            st.metric("Filtered Candidates", len(df_mars[df_mars['valid_years'] > 5]))
            
        st.dataframe(df_mars[['id', 'name', 'price', 'cagr_pct', 'volatility_pct', 's2006e2025bao']])
    else:
        st.error("Data not found. Please run analysis pipeline.")

with tabs[1]:
    st.header("Mars Race 2006-2025")
    if not df_mars.empty:
        # Prepare Data for Race
        # We need a long format: Year | ID | Name | ROI
        race_data = []
        
        # Identify Year Columns
        year_cols = [c for c in df_mars.columns if 'bao' in c]
        
        for _, row in df_mars.iterrows():
            for col in year_cols:
                # format s2006e2007bao
                try:
                    end_year = int(col.split('e')[1][:4])
                    val = row[col]
                    if pd.notnull(val) and val != 0:
                        race_data.append({
                            'Year': end_year,
                            'ID': str(row['id']),
                            'Name': row['name'],
                            'Value': val,
                            'Label': f"{row['name']} ({row['id']})" 
                        })
                except: pass
                
        df_race = pd.DataFrame(race_data)
        
        if not df_race.empty:
            # Filter top 15 per year for performance
            df_race = df_race.sort_values(['Year', 'Value'], ascending=[True, False])
            df_race = df_race.groupby('Year').head(15)
            
            fig = px.bar(df_race, x="Value", y="Label", animation_frame="Year", 
                         orientation='h', range_x=[0, df_race['Value'].max()*1.1],
                         title="Cumulative ROI % (Base 2006)",
                         text="Value",
                         color="Value", color_continuous_scale="Viridis")
                         
            fig.update_layout(yaxis={'categoryorder':'total ascending'}, 
                              plot_bgcolor='#0e1117', paper_bgcolor='#0e1117',
                              font_color="white")
            
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("No time-series data found.")

with tabs[2]:
    st.header("Convertible Bond (Arbitrage)")
    
    cb_input = st.text_input("Enter Stock Code (e.g. 6533)", value="6533")
    
    if st.button("Analyze CB"):
        st.info(f"Analyzing {cb_input}...")
        
        async def run_cb():
            strategy = CBStrategy()
            return await strategy.analyze_list([cb_input])
            
        results = asyncio.run(run_cb())
        
        if results:
            for r in results:
                # Display Card
                bs_col = "green" if "BUY" in r['action'] else "red" if "SELL" in r['action'] else "grey"
                
                st.markdown(f"""
                <div style="border: 1px solid #333; padding: 15px; border-radius: 10px; margin-bottom: 10px;">
                    <h3 style="margin:0;">{r['code']} {r['name']}</h3>
                    <p>Stock: <b>{r['stock_price']}</b> | CB: <b>{r['cb_price']}</b> | Conv: <b>{r['conv_price']}</b></p>
                    <hr style="border-color: #333;">
                    <div style="display: flex; justify-content: space-between;">
                        <div>
                            <small>Premium Rate</small>
                            <h2 style="margin:0; color: {bs_col};">{r['premium']}%</h2>
                        </div>
                        <div style="text-align: right;">
                            <small>Signal</small>
                            <h2 style="margin:0; color: {bs_col};">{r['action']}</h2>
                        </div>
                    </div>
                     <p style="margin-top: 10px;"><i>{r['description']}</i></p>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.warning("No active CB found or data unavailable.")

