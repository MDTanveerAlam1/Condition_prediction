
import streamlit as st
import pickle
import numpy as np
import pandas as pd

import streamlit as st
import pandas as pd

# Load dataset
@st.cache_data
def load_data():
    return pd.read_csv("filter data.csv")

data = load_data()

st.title("🧠 Condition-Based Drug Recommender")
st.write("Enter a medical **condition** to see top-rated drugs based on positive user reviews.")

# User input for condition
condition_input = st.text_input("Enter Condition (e.g. Depression, High Blood Pressure, Diabetes, Type 2]))

if condition_input:
    # Filter for condition (case-insensitive)
    condition_filtered = data[data['condition'].str.lower() == condition_input.lower()]
    
    if condition_filtered.empty:
        st.warning("No data found for this condition.")
    else:
        st.success(f"Found {len(condition_filtered)} reviews for **{condition_input.title()}**")

        # Create a positive review flag (rating >= 7)
        condition_filtered["is_positive"] = condition_filtered["rating"] >= 7

        # Group by drug and calculate metrics
        drug_stats = (
            condition_filtered.groupby('drugName')
            .agg(
                avg_rating=('rating', 'mean'),
                num_reviews=('rating', 'count'),
                positive_reviews=('is_positive', 'sum')
            )
            .sort_values(by=['positive_reviews', 'avg_rating'], ascending=False)
            .reset_index()
        )

        # Top 3 drugs
        st.subheader("🌟 Top 3 Recommended Drugs (Based on Positive Reviews)")
        for i, row in drug_stats.head(3).iterrows():
            st.markdown(f"""
                **{i+1}. {row['drugName']}**  
                - 👍 Positive Reviews: {int(row['positive_reviews'])}  
                - ⭐ Average Rating: {row['avg_rating']:.2f}  
                - 💬 Total Reviews: {int(row['num_reviews'])}  
                """)

        # Other drugs
        st.subheader("💊 Other Drugs for This Condition")
        for i, row in drug_stats.iloc[3:].iterrows():
            st.markdown(f"""
                **{row['drugName']}**  
                - 👍 Positive Reviews: {int(row['positive_reviews'])}  
                - ⭐ Average Rating: {row['avg_rating']:.2f}  
                - 💬 Reviews: {int(row['num_reviews'])}  
                ---""")
