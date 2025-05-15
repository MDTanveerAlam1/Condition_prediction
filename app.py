import os
import streamlit as st
import pickle
import numpy as np
import pandas as pd
from PIL import Image

# Load dataset
@st.cache_data

def load_data():
    return pd.read_csv("filter data.csv")

data = load_data()

# Prepare UI Elements
st.set_page_config(page_title="MedGuide - Drug Recommender", page_icon="💊", layout="centered")
st.markdown("""
    <style>
    .main {
        background-color: #f2f9ff;
    }
    .stButton>button {
        background-color: #4da6ff;
        color: white;
        border-radius: 8px;
        font-weight: bold;
    }
    </style>
""", unsafe_allow_html=True)

# MedGuide Logo & Header

logo_path = "medguide_logo.png"
if os.path.exists(logo_path):
    logo = Image.open(logo_path)
    st.image(logo, width=120)

if logo:
    st.image(logo, width=120)
st.title("💊 MedGuide - Drug Recommender")
st.markdown("Find the **best medications** based on patient reviews & ratings.")

# Input condition
condition_input = st.text_input("🔍 Enter Medical Condition (e.g. Depression, Diabetes, etc.)")

# Match common variants for main conditions
synonyms = {
    "depression": ["depression", "depressive", "mental health"],
    "high blood pressure": ["blood pressure", "hypertension"],
    "diabetes, type 2": ["diabetes", "type 2 diabetes", "sugar"]
}

def match_condition(user_input):
    user_input = user_input.lower()
    for condition, keys in synonyms.items():
        if any(k in user_input for k in keys):
            return condition
    return user_input

# Filtering & Analysis
if condition_input:
    matched_condition = match_condition(condition_input)
    condition_filtered = data[data['condition'].str.lower() == matched_condition.lower()]

    if condition_filtered.empty:
        st.warning("⚠️ No reviews found for this condition. Try a different keyword.")
    else:
        st.success(f"✅ {len(condition_filtered)} reviews found for **{matched_condition.title()}**")

        # Mark positive reviews (rating >= 7)
        condition_filtered["is_positive"] = condition_filtered["rating"] >= 7

        # Group and rank drugs
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

        st.subheader("🌟 Top 3 Recommended Drugs")
        for i, row in drug_stats.head(3).iterrows():
            with st.container():
                st.markdown(f"""
                ### {i+1}. {row['drugName']}
                - 👍 **Positive Reviews**: {int(row['positive_reviews'])}
                - ⭐ **Average Rating**: {row['avg_rating']:.2f}
                - 💬 **Total Reviews**: {int(row['num_reviews'])}
                """)
                if st.button(f"📝 Show Reviews for {row['drugName']}", key=f"top_review_{i}"):
                    reviews = condition_filtered[condition_filtered['drugName'] == row['drugName']]
                    pos_reviews = reviews[reviews['rating'] >= 7][['review', 'rating']].head(3)
                    st.info("### Top Positive Reviews")
                    for r in pos_reviews.itertuples():
                        st.markdown(f"⭐ {r.rating}/10 - _{r.review[:250]}..._")

        # Other Drugs Section
        st.subheader("💊 Other Recommended Drugs")
        for i, row in drug_stats.iloc[3:].iterrows():
            with st.container():
                st.markdown(f"""
                **{row['drugName']}**
                - 👍 Positive Reviews: {int(row['positive_reviews'])}
                - ⭐ Average Rating: {row['avg_rating']:.2f}
                - 💬 Reviews: {int(row['num_reviews'])}
                """)
                if st.button(f"📖 Show Reviews for {row['drugName']}", key=f"review_{i}"):
                    reviews = condition_filtered[condition_filtered['drugName'] == row['drugName']]
                    pos_reviews = reviews[reviews['rating'] >= 7][['review', 'rating']].head(3)
                    st.info("### Top Positive Reviews")
                    for r in pos_reviews.itertuples():
                        st.markdown(f"⭐ {r.rating}/10 - _{r.review[:250]}..._")
                    if st.button(f"➡️ Next Reviews for {row['drugName']}", key=f"next_{i}"):
                        more_reviews = reviews[reviews['rating'] >= 7][['review', 'rating']].iloc[3:6]
                        for r in more_reviews.itertuples():
                            st.markdown(f"⭐ {r.rating}/10 - _{r.review[:250]}..._")

# Footer
st.markdown("""
---
Made with 💙 by MedGuide | All rights reserved © 2025
""")
