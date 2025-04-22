import streamlit as st
import pandas as pd
from utils.auth import get_user_analyses

# Set page config
st.set_page_config(
    page_title="Analysis History - Market Basket Analysis",
    page_icon="📊",
    layout="wide"
)

st.header("Analysis History")

# Add username input
default_username = st.session_state.get('last_analysis_username', 'public')
username = st.text_input("Enter your username to view analyses:", value=default_username)

if username:
    # Get analyses for the specified username
    analyses = get_user_analyses(username.strip())

    if analyses:
        # Convert to DataFrame for display
        df = pd.DataFrame([{
            "ID": a[0],
            "Filename": a[1],
            "Timestamp": a[2],
            "Transactions": a[3],
            "Items": a[4],
            "Min Support": a[5],
            "Min Confidence": a[6],
            "Min Lift": a[7],
            "Frequent Itemsets": a[8],
            "Rules": a[9]
        } for a in analyses])
        
        # Display the dataframe
        st.dataframe(df, use_container_width=True)
        
        # Add a button to view details
        if st.button("View Selected Analysis Details"):
            selected_id = st.selectbox("Select Analysis ID", options=df["ID"].tolist())
            if selected_id:
                # Store username in session state for analysis details page
                st.session_state['last_analysis_username'] = username
                st.switch_page(f"pages/analysis_details.py?id={selected_id}")
    else:
        st.info(f"No analyses found for username: {username}. Please check your username or go to the Analysis page to create new analyses.")
else:
    st.info("Please enter your username to view your analysis history.")
