
import streamlit as st
import pandas as pd
from project_tw.strategies.mars import MarsStrategy
from project_tw.strategies.cb import CBStrategy
from project_tw.crawler import get_stock_history_df
from project_tw.plot_race import generate_bar_chart_race_plotly
import numpy as np

# Page Config
st.set_page_config(
    page_title="Martian Stock App",
    page_icon="🚀",
    layout="wide"
)

# Title and Intro
st.title("🚀 Martian Investment System")
st.markdown("""
**Core Philosophy**:
1.  **Mars Strategy**: Low Volatility, Stable Growth (Gaussian Filters).
2.  **CB Strategy**: Arbitrage & Hedging using Convertible Bonds.
""")

# Sidebar - Settings
st.sidebar.header("⚙️ Configuration")
start_year = st.sidebar.number_input("Start Year", 2010, 2024, 2019)
end_year = st.sidebar.number_input("End Year", 2020, 2030, 2024)
std_threshold = st.sidebar.slider("Volatility Threshold (%)", 5.0, 50.0, 20.0)

# Initialize Strategies
if 'mars_strategy' not in st.session_state:
    st.session_state.mars_strategy = MarsStrategy()
if 'cb_strategy' not in st.session_state:
    st.session_state.cb_strategy = CBStrategy()

# Tabs
tab_mars, tab_cb, tab_viz = st.tabs(["🪐 Mars Strategy", "💰 CB Strategy", "📊 Visualization"])

# --- TAB 1: MARS STRATEGY ---
with tab_mars:
    st.header("Mars Strategy: Low Volatility Selector")
    st.info(f"Finding stocks with Annualized Volatility < {std_threshold}%")
    
    col1, col2 = st.columns([1, 3])
    with col1:
        # Input for specific stock analysis (Demo mode)
        target_stock = st.text_input("Test Stock Code", "2330")
        if st.button("Analyze Single Stock"):
            with st.spinner(f"Crawling {target_stock}..."):
                # Use async crawler in sync streamlit
                # loop = asyncio.new_event_loop()
                # asyncio.set_event_loop(loop)
                try:
                    df = get_stock_history_df(target_stock, start_year, end_year)
                    if not df.empty:
                        st.session_state.current_df = df
                        calc = st.session_state.mars_strategy.calculator
                        metrics = calc.calculate_metrics(df)
                        if metrics:
                            st.success("Analysis Complete!")
                            st.json(metrics)
                            
                            # Check Threshold
                            vol = metrics['volatility_pct']
                            if vol < std_threshold:
                                st.balloons()
                                st.success(f"✅ Qualified! Volatility {vol:.2f}% < {std_threshold}%")
                            else:
                                st.error(f"❌ Rejected. Volatility {vol:.2f}% > {std_threshold}%")
                        else:
                            st.warning("Insufficient metrics data.")
                    else:
                        st.error("No data found. Checking TWSE...")
                except Exception as e:
                    st.error(f"Error: {e}")

    with col2:
        st.subheader("Price History")
        if 'current_df' in st.session_state and not st.session_state.current_df.empty:
            st.line_chart(st.session_state.current_df['close'])

# --- TAB 2: CB STRATEGY ---
with tab_cb:
    st.header("CB Strategy: Convertible Bond Arbitrage")
    st.markdown("Enter the market parameters to get the Action Signal.")
    
    c1, c2, c3 = st.columns(3)
    with c1:
        cb_price = st.number_input("CB Market Price", 90.0, 200.0, 105.0)
    with c2:
        stock_price = st.number_input("Stock Market Price", 10.0, 1000.0, 100.0)
    with c3:
        conv_price = st.number_input("Conversion Price", 10.0, 1000.0, 95.0)
        
    if st.button("Evaluate CB Signal"):
        strat = st.session_state.cb_strategy
        premium = strat.calculate_premium(cb_price, stock_price, conv_price)
        advice = strat.evaluate(premium)
        
        st.divider()
        st.metric(label="Conversion Premium Rate (I2)", value=f"{premium:.2f}%")
        
        # Display Advice
        color_map = {
            "red": "🔴",
            "orange": "🟠",
            "green": "🟢",
            "blue": "🔵",
            "purple": "🟣",
            "black": "⚫"
        }
        icon = color_map.get(advice.color, "⚪")
        
        st.subheader(f"{icon} Signal: {advice.signal.value}")
        st.markdown(f"**Action**: {advice.action_short}")
        st.info(f"**Reasoning**: {advice.action_detail}")

# --- TAB 3: VISUALIZATION ---
with tab_viz:
    st.header("Visualization Playground: Bar Chart Race")
    st.write("Visualizing Stock Performance over time.")
    
    if st.button("Generate Demo Race"):
        # Create Dummy Data for Demo
        st.info("Generating random demo data...")
        dates = pd.date_range(start="2023-01-01", periods=100)
        data = np.random.randn(100, 10).cumsum(axis=0)
        df_dummy = pd.DataFrame(data, index=dates, columns=[f"Stock_{i}" for i in range(10)])
        
        fig = generate_bar_chart_race_plotly(df_dummy, title="Demo Race (Cumulative Random Walk)")
        st.plotly_chart(fig, use_container_width=True)
    
    if 'current_df' in st.session_state and not st.session_state.current_df.empty:
        st.divider()
        st.subheader("Real Data Race (Using current single stock)")
        st.write("Note: A real race needs multiple stocks. This will just show one bar moving.")
        # Mocking comparison with flat line for demo
        df_single = st.session_state.current_df[['close']].copy()
        df_single.rename(columns={'close': target_stock}, inplace=True)
        # Add a benchmark
        df_single['Benchmark_0%'] = df_single[target_stock].iloc[0]
        
        fig_real = generate_bar_chart_race_plotly(df_single, title=f"{target_stock} vs Benchmark")
        st.plotly_chart(fig_real, use_container_width=True)

