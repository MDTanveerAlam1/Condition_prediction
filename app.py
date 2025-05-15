
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
st.write("Enter a medical **condition** to see the best-rated drugs based on patient reviews.")

# User input for condition
condition_input = st.text_input("Enter Condition (e.g. Depression, High Blood Pressure, etc.)")

if condition_input:
    # Filter by condition (case-insensitive)
    filtered_data = data[data['condition'].str.lower() == condition_input.lower()]
    
    if filtered_data.empty:
        st.warning("No data found for this condition.")
    else:
        st.success(f"Found {len(filtered_data)} reviews for **{condition_input.title()}**")

        # Group by drug, calculate average rating and count
        drug_ratings = (
            filtered_data
            .groupby('drugName')
            .agg(avg_rating=('rating', 'mean'), num_reviews=('rating', 'count'))
            .sort_values(by='avg_rating', ascending=False)
            .reset_index()
        )

        # Top 3 recommendations
        st.subheader("🌟 Top 3 Recommended Drugs")
        for i, row in drug_ratings.head(3).iterrows():
            st.markdown(f"""
                **{i+1}. {row['drugName']}**  
                - ⭐ Average Rating: {row['avg_rating']:.2f}  
                - 💬 Number of Reviews: {row['num_reviews']}  
                """)

        # Other drugs
        st.subheader("💊 Other Drugs for This Condition")
        for i, row in drug_ratings.iloc[3:].iterrows():
            st.markdown(f"""
                **{row['drugName']}**  
                - ⭐ Average Rating: {row['avg_rating']:.2f}  
                - 💬 Reviews: {row['num_reviews']}  
                ---""")
