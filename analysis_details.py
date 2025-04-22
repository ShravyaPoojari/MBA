import streamlit as st
import pandas as pd
import ast
from utils.auth import get_user_analyses, get_analysis_details

# Set page config
st.set_page_config(
    page_title="Analysis Details - Market Basket Analysis",
    page_icon="📊",
    layout="wide"
)

st.header("Analysis Details")

# Add username input
default_username = st.session_state.get('last_analysis_username', 'public')
username = st.text_input("Enter your username to view analyses:", value=default_username)

if username:
    # Get analyses for the specified username
    analyses = get_user_analyses(username.strip())

    if not analyses:
        st.info(f"No analyses found for username: {username}. Please check your username or go to the Analysis page to create new analyses.")
        st.stop()

    # Create a selection for analyses
    analysis_options = {f"{analysis[1]} ({analysis[2]})": analysis[0] for analysis in analyses}
    selected_analysis = st.selectbox("Select an analysis to view details:", options=list(analysis_options.keys()))

    if selected_analysis:
        analysis_id = analysis_options[selected_analysis]
        analysis, itemsets, rules = get_analysis_details(analysis_id, username.strip())
        
        if analysis:
            # Display basic information
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("Basic Information")
                st.write(f"**Filename:** {analysis[1]}")
                st.write(f"**Timestamp:** {analysis[2]}")
                st.write(f"**Transactions:** {analysis[3]}")
                st.write(f"**Items:** {analysis[4]}")
            
            with col2:
                st.subheader("Analysis Parameters")
                st.write(f"**Min Support:** {analysis[5]}")
                st.write(f"**Min Confidence:** {analysis[6]}")
                st.write(f"**Min Lift:** {analysis[7]}")
                st.write(f"**Frequent Itemsets:** {analysis[8]}")
                st.write(f"**Rules:** {analysis[9]}")
            
            # Display frequent itemsets
            st.subheader("Frequent Itemsets")
            if itemsets:
                itemset_data = []
                for itemset, support in itemsets:
                    # Convert string representation of frozenset to actual frozenset
                    try:
                        itemset_str = itemset.replace("frozenset(", "").replace(")", "")
                        itemset_list = ast.literal_eval(itemset_str)
                        itemset_data.append({
                            "Itemset": ", ".join(itemset_list),
                            "Support": support
                        })
                    except:
                        itemset_data.append({
                            "Itemset": itemset,
                            "Support": support
                        })
                
                itemset_df = pd.DataFrame(itemset_data)
                st.dataframe(itemset_df, use_container_width=True)
            else:
                st.write("No frequent itemsets found.")
            
            # Display association rules
            st.subheader("Association Rules")
            if rules:
                rule_data = []
                for rule in rules:
                    antecedents, consequents, support, confidence, lift = rule
                    
                    # Convert string representation of frozenset to actual frozenset
                    try:
                        antecedents_str = antecedents.replace("frozenset(", "").replace(")", "")
                        consequents_str = consequents.replace("frozenset(", "").replace(")", "")
                        
                        antecedents_list = ast.literal_eval(antecedents_str)
                        consequents_list = ast.literal_eval(consequents_str)
                        
                        rule_data.append({
                            "Antecedents": ", ".join(antecedents_list),
                            "Consequents": ", ".join(consequents_list),
                            "Support": support,
                            "Confidence": confidence,
                            "Lift": lift
                        })
                    except:
                        rule_data.append({
                            "Antecedents": antecedents,
                            "Consequents": consequents,
                            "Support": support,
                            "Confidence": confidence,
                            "Lift": lift
                        })
                
                rule_df = pd.DataFrame(rule_data)
                st.dataframe(rule_df, use_container_width=True)
            else:
                st.write("No rules found.")
        else:
            st.warning("Analysis not found.")
else:
    st.info("Please enter your username to view your analysis details.")
