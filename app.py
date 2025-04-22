import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from utils.auth import init_session_state

# Initialize session state
init_session_state()

# Set page config to wide mode
st.set_page_config(
    page_title="Market Basket Analysis",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- Fixed Theme Colors ---
bg_color = "#0e1117"
text_color = "white"
primary_color = "#ff4b4b"
plot_bg = "#0e1117"

# --- Custom CSS Styling ---
st.markdown(f"""
    <style>
        .main .block-container {{
            max-width: 1200px;
            padding-top: 2rem;
            padding-bottom: 2rem;
            margin: 0 auto;
        }}
        
        body {{
            background-color: {bg_color};
            color: {text_color};
        }}
        
        .nav-container {{
            background-color: {bg_color};
            padding: 1rem;
            display: flex;
            justify-content: space-between;
            align-items: center;
            max-width: 1200px;
            margin: 0 auto;
        }}
        
        .nav-links a {{
            color: {text_color};
            text-decoration: none;
            padding: 0.5rem 1.5rem;
            font-weight: 500;
            font-size: 16px;
            border: 1px solid transparent;
            border-radius: 8px;
        }}
        
        .nav-links a:hover,
        .nav-links .active {{
            border-color: {primary_color};
            color: {primary_color};
        }}
        
        .nav-auth {{
            color: {text_color};
            font-size: 14px;
            padding: 0.3rem 0.8rem;
            border: 1px solid {text_color};
            border-radius: 5px;
        }}
        
        /* Center all charts and containers */
        [data-testid="stVerticalBlock"] > [style*="flex"] {{
            gap: 2rem;
        }}
        
        .plot-container {{
            display: flex;
            justify-content: center;
            width: 100%;
        }}
        
        /* Ensure headers are centered */
        h1, h2, h3 {{
            text-align: center !important;
        }}
    </style>
""", unsafe_allow_html=True)

# Create a container for centered content
with st.container():
    # Navigation
    auth_status = "Logout" if st.session_state.get('authenticated', False) else "Login/Signup"
    auth_link = "/" if st.session_state.get('authenticated', False) else "/login"
    
    st.markdown(f"""
        <div class="nav-container">
            <div class="nav-logo">
                <img src="https://cdn-icons-png.flaticon.com/512/4275/4275619.png" height="40px" />
            </div>
            <div class="nav-links">
                <a class="active" href="/">Home</a>
                <a href="pages/1_analysis">Analysis</a>
                <a href="analysis_history">History</a>
                <a href="about">About</a>
            </div>
            <div class="nav-auth">
                <a href="{auth_link}" style="color: {text_color}; text-decoration: none;">{auth_status}</a>
            </div>
        </div>
    """, unsafe_allow_html=True)

    # Show user info if logged in
    if st.session_state.get('authenticated', False):
        st.sidebar.write(f"Logged in as: **{st.session_state.get('username')}**")
        if st.sidebar.button("Logout"):
            st.session_state.authenticated = False
            st.session_state.username = None
            st.experimental_rerun()

    # Debug section
    if st.sidebar.checkbox("Show Session State Debug"):
        st.sidebar.write("Current Session State:")
        st.sidebar.write(dict(st.session_state))

    # Title
    st.markdown(f"<h1 style='color:{text_color}; margin-bottom: 2rem;'>Market Basket Analysis Dashboard</h1>", unsafe_allow_html=True)

    # Create three columns with some padding
    col1, col2, col3 = st.columns(3)

    # First column - Line Chart
    with col1:
        st.markdown(f"<h3 style='color:{text_color};'>📈 Trend Analysis</h3>", unsafe_allow_html=True)
        
        line_data = pd.DataFrame({
            'Date': pd.date_range(start='2024-01-01', periods=7, freq='D'),
            'Value': [10, 15, 13, 18, 20, 17, 22]
        })
        
        line_chart = px.line(line_data, x='Date', y='Value',
                            title='Weekly Trend')
        line_chart.update_layout(
            plot_bgcolor=plot_bg,
            paper_bgcolor=plot_bg,
            font_color=text_color,
            margin=dict(t=30, l=10, r=10, b=10),
            height=300
        )
        st.plotly_chart(line_chart, use_container_width=True)

    # Second column - Scatter Plot
    with col2:
        st.markdown(f"<h3 style='color:{text_color};'>🔍 Product Analysis</h3>", unsafe_allow_html=True)
        
        np.random.seed(42)
        n_points = 40
        
        scatter_data = pd.DataFrame({
            'Sales': np.random.normal(100, 20, n_points),
            'Profit': np.random.normal(25, 5, n_points),
            'Category': np.repeat(['Electronics', 'Clothing', 'Food', 'Books'], n_points//4),
            'Volume': np.random.randint(50, 200, n_points)
        })
        
        scatter_plot = px.scatter(
            scatter_data,
            x='Sales',
            y='Profit',
            color='Category',
            size='Volume',
            color_discrete_sequence=px.colors.qualitative.Set2,
            title='Sales vs. Profit by Category',
            labels={
                'Sales': 'Sales Amount ($)',
                'Profit': 'Profit ($)',
                'Volume': 'Transaction Volume'
            },
            hover_data={
                'Sales': ':.0f',
                'Profit': ':.1f',
                'Volume': True,
                'Category': True
            }
        )

        scatter_plot.update_layout(
            plot_bgcolor=plot_bg,
            paper_bgcolor=plot_bg,
            font_color=text_color,
            title_x=0.5,
            margin=dict(t=30, l=10, r=10, b=10),
            height=300,
            legend=dict(
                yanchor="top",
                y=0.99,
                xanchor="right",
                x=0.99,
                bgcolor='rgba(0,0,0,0)'
            )
        )
        
        st.plotly_chart(scatter_plot, use_container_width=True)

    # Third column - Bar Chart
    with col3:
        st.markdown(f"<h3 style='color:{text_color};'>📊 Category Distribution</h3>", unsafe_allow_html=True)
        
        basket_data = pd.DataFrame({
            'Item': ['A', 'B', 'C', 'D'],
            'Count': [100, 20, 50, 70]
        })
        
        bar_chart = px.bar(basket_data, x='Item', y='Count', text='Count',
                          color='Item',
                          color_discrete_sequence=px.colors.qualitative.Set3)
        bar_chart.update_layout(
            plot_bgcolor=plot_bg,
            paper_bgcolor=plot_bg,
            font_color=text_color,
            showlegend=False,
            margin=dict(t=30, l=10, r=10, b=10),
            height=300
        )
        bar_chart.update_traces(textposition='outside')
        
        st.plotly_chart(bar_chart, use_container_width=True)

    # Add a spacer after the charts
    st.markdown("<br>", unsafe_allow_html=True)

    # Add a centered footer
    st.markdown(f"""
        <div style="text-align: center; padding: 2rem 0; color: {text_color};">
            <p>© 2024 Market Basket Analysis Dashboard</p>
        </div>
    """, unsafe_allow_html=True)     