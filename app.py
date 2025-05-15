
import streamlit as st
import pickle
import numpy as np
import pandas as pd

# Load dataset
@st.cache_data
def load_data():
    return pd.read_csv("filter data.csv")

data = load_data()

st.title("💊 Drug Review Explorer")
st.write("Enter a **drug name** to explore conditions, reviews, and ratings.")

# User inputs
drug_input = st.text_input("Enter Drug Name (e.g. Metformin, Zoloft, etc.)")
min_rating = st.slider("Minimum Rating Filter", min_value=1, max_value=10, value=1)

if drug_input:
    # Filter data for the drug name (case-insensitive)
    filtered_data = data[
        (data['drugName'].str.lower() == drug_input.lower()) &
        (data['rating'] >= min_rating)
    ]
    
    if filtered_data.empty:
        st.warning("No data found for this drug with the selected rating filter.")
    else:
        st.success(f"Found {len(filtered_data)} reviews for **{drug_input.title()}** (Rating ≥ {min_rating})")

        # Display unique conditions
        conditions = filtered_data['condition'].dropna().unique()
        st.subheader("🩺 Conditions Treated")
        for cond in conditions:
            st.markdown(f"- {cond}")

        # Display patient reviews
        st.subheader("📝 Patient Reviews")
        for idx, row in filtered_data.iterrows():
            st.markdown(f"""
                **Condition**: {row['condition']}  
                **Rating**: {row['rating']}  
                **Review**: {row['review']}  
                **Useful Count**: {row['usefulCount']}  
                ---
            """)
