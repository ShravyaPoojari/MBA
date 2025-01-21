# Import Libraries
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.sparse import csr_matrix
from mlxtend.frequent_patterns import apriori, association_rules

# Title and Sidebar
st.title("Market Basket Analysis Dashboard")
st.sidebar.title("Upload Your Data")
st.sidebar.write("Upload a CSV file containing transaction data.")

# File Uploader
uploaded_file = st.sidebar.file_uploader("Choose a file", type=["csv"])

# Parameters for Apriori
min_support = st.sidebar.slider("Minimum Support", min_value=0.01, max_value=1.0, value=0.05, step=0.01)
min_confidence = st.sidebar.slider("Minimum Confidence", min_value=0.1, max_value=1.0, value=0.2, step=0.1)
min_lift = st.sidebar.slider("Minimum Lift", min_value=1.0, max_value=10.0, value=1.5, step=0.1)

# Process the Uploaded File
if uploaded_file is not None:
    # Read the data
    df = pd.read_csv(uploaded_file)
    st.write("### Uploaded Data", df.head(10))

    # Pivot the data to create a binary matrix
    #basket = df.pivot_table(index='Transaction ID', columns='Product', aggfunc=lambda x: 1, fill_value=0)
    #st.write("### Binary Matrix", basket.head(10))

   # # Apriori Analysis
   # frequent_itemsets = apriori(basket, min_support=min_support, use_colnames=True)
   # rules = association_rules(frequent_itemsets, metric="confidence", min_threshold=min_confidence)
   # rules = rules[rules['lift'] >= min_lift]

   # # Display Results
   # st.write("### Frequent Itemsets", frequent_itemsets)
   # st.write("### Association Rules", rules
  

    # Reduce dataset size (example: filter products purchased more than 5 times)
    product_counts = df['Product'].value_counts()
    top_products = product_counts[product_counts > 5].index
    df = df[df['Product'].isin(top_products)]
    
    # Create a pivot table (binary matrix)
    basket = df.pivot_table(index='Transaction ID', columns='Product', aggfunc=lambda x: 1, fill_value=0)
    st.write("### Binary Matrix", basket.head(10))

    # Convert to sparse matrix
    basket_sparse = csr_matrix(basket.values)
    
    # Use Apriori on sparse data
    basket_df = pd.DataFrame.sparse.from_spmatrix(basket_sparse, columns=basket.columns)
    frequent_itemsets = apriori(basket_df, min_support=0.1, use_colnames=True)
    
    # Generate rules
    rules = association_rules(frequent_itemsets, metric="confidence", min_threshold=0.2)
    
    # Display results
    print(frequent_itemsets)
    print(rules)


    # Visualization 1: Frequent Itemsets
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

    # Visualization 3: Network Graph
    st.subheader("Association Rules Network Graph")
    import networkx as nx
    G = nx.DiGraph()
    for _, rule in rules.iterrows():
        antecedents = ", ".join(list(rule["antecedents"]))
        consequents = ", ".join(list(rule["consequents"]))
        G.add_edge(antecedents, consequents, weight=rule["lift"])

    plt.figure(figsize=(12, 8))
    pos = nx.spring_layout(G, seed=42)
    nx.draw(G, pos, with_labels=True, node_color="skyblue", node_size=3000, font_size=10, edge_color="gray")
    edge_labels = nx.get_edge_attributes(G, 'weight')
    nx.draw_networkx_edge_labels(G, pos, edge_labels={k: f"{v:.2f}" for k, v in edge_labels.items()})
    plt.title("Association Rules Network Graph")
    st.pyplot(plt)

else:
    st.info("Please upload a CSV file to start the analysis.")

