
import streamlit as st
import pickle
import numpy as np
import pandas as pd

# Related condition mappings
condition_aliases = {
    "depression": ["depression", "depressed", "major depressive disorder", "mdd"],
    "high blood pressure": ["high blood pressure", "hypertension", "high bp", "bp issue"],
    "diabetes, type 2": ["diabetes, type 2", "type 2 diabetes", "t2d", "diabetes type 2"]
}

# Normalize condition input
condition_input = st.text_input("Enter Condition (e.g. Depression, High BP, T2D, etc.)").lower().strip()

def match_condition(user_input):
    for standard_condition, aliases in condition_aliases.items():
        if user_input in [a.lower() for a in aliases]:
            return standard_condition
    return None

matched_condition = match_condition(condition_input)

if condition_input:
    if not matched_condition:
        st.warning("Couldn't recognize this condition. Try using terms like 'Depression', 'High BP', or 'Diabetes Type 2'.")
    else:
        # Filter for condition
        condition_filtered = data[data['condition'].str.lower() == matched_condition.lower()]
        
        if condition_filtered.empty:
            st.warning("No data found for this condition.")
        else:
            st.success(f"Found {len(condition_filtered)} reviews for **{matched_condition.title()}**")

            # Positive review logic
            condition_filtered["is_positive"] = condition_filtered["rating"] >= 7

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

            st.subheader("🌟 Top 3 Recommended Drugs (Based on Positive Reviews)")
            for i, row in drug_stats.head(3).iterrows():
                st.markdown(f"""
                    **{i+1}. {row['drugName']}**  
                    - 👍 Positive Reviews: {int(row['positive_reviews'])}  
                    - ⭐ Average Rating: {row['avg_rating']:.2f}  
                    - 💬 Total Reviews: {int(row['num_reviews'])}  
                    """)

            st.subheader("💊 Other Drugs for This Condition")
            for i, row in drug_stats.iloc[3:].iterrows():
                st.markdown(f"""
                    **{row['drugName']}**  
                    - 👍 Positive Reviews: {int(row['positive_reviews'])}  
                    - ⭐ Average Rating: {row['avg_rating']:.2f}  
                    - 💬 Reviews: {int(row['num_reviews'])}  
                    ---""")

