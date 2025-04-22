# Import Libraries
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.sparse import csr_matrix
from mlxtend.frequent_patterns import apriori, association_rules
from utils.auth import save_analysis
import numpy as np
from datetime import datetime

# Authentication check
if 'authenticated' not in st.session_state or not st.session_state['authenticated']:
    st.warning("Please log in to access this page.")
    st.markdown("[Go to Login](login)")
    st.stop()

# Get username from session state
username = st.session_state.get('username', '')
if not username:
    st.error("Session error: Username not found. Please log in again.")
    st.markdown("[Go to Login](login)")
    st.stop()

# Set page config
st.set_page_config(
    page_title="Market Basket Analysis",
    page_icon="📊",
    layout="wide"
)

# Debug information (optional)
if st.sidebar.checkbox("Show Session State Debug"):
    st.sidebar.write("Current Session State:", st.session_state)

# Title and Sidebar
st.title("Market Basket Analysis Dashboard")

st.sidebar.title("Upload Your Data")
st.sidebar.write("Upload a CSV file containing transaction data.")

# Welcome message
st.sidebar.markdown(f"👤 Welcome, **{username}**!")

# File Uploader
uploaded_file = st.sidebar.file_uploader("Choose a file", type=["csv"])

# Sidebar parameters for Apriori
min_support = st.sidebar.slider("Minimum Support", min_value=0.01, max_value=1.0, value=0.05, step=0.01)
min_confidence = st.sidebar.slider("Minimum Confidence", min_value=0.1, max_value=1.0, value=0.2, step=0.1)
min_lift = st.sidebar.slider("Minimum Lift", min_value=1.0, max_value=10.0, value=1.5, step=0.1)

# Data Preprocessing and EDA Functions
def clean_column_names(df):
    """
    Standardize column names by stripping spaces,
    converting to lower case and replacing spaces with underscores.
    """
    df.columns = df.columns.str.strip().str.lower().str.replace(' ', '_')
    return df

if uploaded_file is not None:
    # Read the data
    df = pd.read_csv(uploaded_file)
    filename = uploaded_file.name
    
    # Perform EDA for Data Preprocessing and Cleaning
    st.subheader("Data Preprocessing & Cleaning")
    
    # Clean column names for consistency
    df = clean_column_names(df)
    st.write("Cleaned Column Names:", list(df.columns))
    
    # Display first few rows of the data
    st.write("### Uploaded Data", df.head(10))
    
    # Data Shape and Types
    st.write("Data Shape:", df.shape)
    st.write("Data Types:", df.dtypes)
    
    # Missing Values Analysis
    missing_values = df.isnull().sum()
    st.write("Missing Values (Count):", missing_values)
    #st.write("Missing Values (Percentage):", (missing_values / len(df)) * 100)
    
    # Remove Duplicate Rows
    duplicate_count = df.duplicated().sum()
    st.write("Number of Duplicate Rows:", duplicate_count)
    if duplicate_count > 0:
        df = df.drop_duplicates()
        st.write("Duplicates removed. New data shape:", df.shape)
    
    # Outlier Detection: Box Plots for numeric columns (if any)
    numeric_cols = df.select_dtypes(include=['int64', 'float64']).columns.tolist()
    print(numeric_cols)
    # Create a color palette with as many colors as numeric columns

    # Box Plots for numeric columns
    if len(numeric_cols) > 0:
        st.write("### Box Plots for Numeric Columns (Outlier Detection)")
        colors = sns.color_palette("rainbow", n_colors=len(numeric_cols))

        for i, col in enumerate(numeric_cols):
            fig, ax = plt.subplots()
            sns.boxplot(y=df[col], ax=ax, color=colors[i])
            ax.set_title(f'Box Plot for {col}')
            st.pyplot(fig)
    else:
        st.write("No numeric columns available for outlier detection.")

    # Check for product-related columns and standardize them
    product_columns = [col for col in df.columns if 'product' in col.lower()]
    
    if not product_columns:
        st.error("No product-related columns found in the dataset. Please ensure your CSV file contains a column with product information.")
        st.stop()
    
    # Use the first product column found or let user select if multiple exist
    if len(product_columns) > 1:
        selected_product_col = st.selectbox("Select the product column to use for analysis:", product_columns)
        product_col = selected_product_col
    else:
        product_col = product_columns[0]
    
    st.write(f"Using '{product_col}' column for product analysis")
    
    # Check for transaction column
    transaction_columns = [col for col in df.columns if 'transaction' in col.lower() or 'order' in col.lower()]
    
    if not transaction_columns:
        st.error("No transaction-related columns found in the dataset. Please ensure your CSV file contains a column with transaction information.")
        st.stop()
    
    # Use the first transaction column found or let user select if multiple exist
    if len(transaction_columns) > 1:
        selected_transaction_col = st.selectbox("Select the transaction column to use for analysis:", transaction_columns)
        transaction_col = selected_transaction_col
    else:
        transaction_col = transaction_columns[0]
    
    st.write(f"Using '{transaction_col}' column for transaction analysis")
    
    # Rename columns for consistency in the rest of the code
    df = df.rename(columns={product_col: 'product', transaction_col: 'transactions'})
    
    # Frequency Distribution for product column
    st.write("### Frequency Distribution for Product Column")
    fig, ax = plt.subplots()
    product_counts = df['product'].value_counts()
    sns.countplot(data=df, x='product', order=product_counts.index)
    plt.xticks(rotation=90)
    plt.xlabel("Product")
    plt.ylabel("Frequency")
    st.pyplot(fig)
    
    # Additional EDA: Check unique transactions and items
    st.write("Unique Transactions:", df['transactions'].nunique())
    st.write("Unique Items:", df['product'].nunique())
    
    ###---- Proceed with Market Basket Analysis -----###  
    # Filter out infrequent products (example: products purchased more than 5 times)
    product_counts = df['product'].value_counts()
    min_product_frequency = st.sidebar.slider("Minimum Product Frequency", min_value=1, max_value=100, value=10, step=1)
    top_products = product_counts[product_counts > min_product_frequency].index
    df_filtered = df[df['product'].isin(top_products)]
    
    if len(df_filtered) == 0:
        st.error(f"No products meet the minimum frequency threshold of {min_product_frequency}. Please lower the threshold.")
        st.stop()
    
    st.write(f"Filtered data shape: {df_filtered.shape} (after removing infrequent products)")

    # Keep 50% of transactions
    df_filtered = df_filtered.sample(frac=0.5, random_state=42)
    st.write(f"Sampled data shape: {df_filtered.shape} (after sampling)")

    # Create a pivot table (binary matrix)
    try:
        basket = df_filtered.pivot_table(index='transactions', columns='product', aggfunc=lambda x: 1, fill_value=0)
        # Convert to int8 or bool to reduce memory
        basket = basket.astype('int8')  # or basket = basket.astype(bool)
        st.write("### Binary Matrix", basket.head(10))
        basket.columns = [str(col) for col in basket.columns]

        # Convert to sparse matrix for efficient processing
        basket_sparse = csr_matrix(basket.values)
        basket_df = pd.DataFrame.sparse.from_spmatrix(basket_sparse, columns=basket.columns)
        
        # Apply Apriori algorithm on the sparse matrix
        frequent_itemsets = apriori(basket_df, min_support=min_support, use_colnames=True)
        
        if len(frequent_itemsets) == 0:
            st.warning("No frequent itemsets found with the current support threshold. Try lowering the minimum support value.")
            st.stop()
        
        # Generate Association Rules
        rules = association_rules(frequent_itemsets, metric="confidence", min_threshold=min_confidence)
        rules = rules[rules['lift'] >= min_lift]
        
        if len(rules) == 0:
            st.warning("No association rules found with the current confidence and lift thresholds. Try lowering the minimum confidence or lift values.")
            st.stop()
        
        # Display Apriori Results
        st.write("### Frequent Itemsets", frequent_itemsets)
        st.write("### Association Rules", rules)
        
        # Visualization 1: Frequent Itemsets Chart
        st.subheader("Frequent Itemsets Chart")
        top_items = frequent_itemsets.nlargest(10, 'support')
        plt.figure(figsize=(10, 6))
        sns.barplot(data=top_items, x='support', y=top_items['itemsets'].astype(str), palette="Blues_d")
        plt.title("Top Frequent Itemsets")
        plt.xlabel("Support")
        plt.ylabel("Itemsets")
        st.pyplot(plt)
        
        # Visualization 2: Rules Scatter Plot
        st.subheader("Association Rules Scatter Plot")
        plt.figure(figsize=(10, 6))
        sns.scatterplot(data=rules, x="support", y="confidence", size="lift", hue="lift", palette="cool", sizes=(50, 300))
        plt.title("Rules Scatter Plot")
        plt.xlabel("Support")
        plt.ylabel("Confidence")
        st.pyplot(plt)
        
        
        # Save Analysis button
        if st.button("Save Analysis"):
            if not username:
                st.error("Session error: Username not found. Please log in again.")
                st.stop()

            try:
                # Prepare data for saving
                analysis_data = {
                    'username': username,
                    'timestamp': datetime.now(),
                    'rules': rules.to_dict(),
                    'support_threshold': min_support,
                    'confidence_threshold': min_confidence,
                    'lift_threshold': min_lift,
                    'total_rules': len(rules)
                }
                
                # Save analysis
                save_analysis(analysis_data)
                st.success(f"Analysis saved successfully for user {username}!")
                
                # Store username in session state for analysis history
                st.session_state['last_analysis_username'] = username
                
            except Exception as e:
                st.error(f"Error saving analysis: {str(e)}")
                st.error("Please check your data format and try again.")
    
    except Exception as e:
        st.error(f"Error during market basket analysis: {str(e)}")
        st.write("Please check your data format and try again.")
    
else:
    st.info("Please upload a CSV file to start the analysis.")   