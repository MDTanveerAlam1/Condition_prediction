
import streamlit as st
import pickle
import numpy as np
import pandas as pd

import streamlit as st
import pandas as pd
from PIL import Image

# Load dataset
@st.cache_data
def load_data():
    data = pd.read_csv("filter data.csv")
    data['condition'] = data['condition'].astype(str)
    return data

data = load_data()

# Load logo (optional)
logo = "📘 MedGuide AI"

# Title and Header Section
st.markdown(
    f"""
    <div style="text-align:center">
        <h1 style="color:#0072E3;">💊 MedGuide AI</h1>
        <h3 style="color:#444;">Find the Perfect Medication Match</h3>
        <p>Discover top-rated medications based on real user reviews.</p>
    </div>
    """, unsafe_allow_html=True
)

# Define condition alias dictionary
condition_aliases = {
    "depression": ["depression", "depressed", "mdd"],
    "high blood pressure": ["high blood pressure", "hypertension", "high bp", "bp"],
    "diabetes, type 2": ["diabetes, type 2", "type 2 diabetes", "t2d"]
}

def match_condition(user_input):
    user_input = user_input.lower().strip()
    for condition, aliases in condition_aliases.items():
        if user_input in aliases:
            return condition
    return None

# Input Section
st.markdown("### 🔍 Search by Condition")
condition_input = st.text_input("Enter a medical condition (e.g., Depression, Diabetes, High BP)", key="condition_input")

matched_condition = match_condition(condition_input)

if condition_input:
    if not matched_condition:
        st.warning("❌ Unrecognized condition. Try: Depression, High Blood Pressure, or Diabetes, Type 2.")
    else:
        condition_filtered = data[data['condition'].str.lower() == matched_condition.lower()].copy()

        if condition_filtered.empty:
            st.error("⚠️ No reviews found for this condition.")
        else:
            st.success(f"🔎 Showing drugs for: **{matched_condition.title()}**")

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

            # Top 3
            st.markdown("## 🌟 Top 3 Recommended Drugs")
            for i, row in drug_stats.head(3).iterrows():
                st.markdown(f"""
                <div style="border:1px solid #DDE; padding:10px; border-radius:10px; background-color:#f8faff; margin-bottom:10px;">
                    <h4 style="color:#0056B3;">{i+1}. {row['drugName']}</h4>
                    <ul>
                        <li>👍 Positive Reviews: <b>{int(row['positive_reviews'])}</b></li>
                        <li>⭐ Average Rating: <b>{row['avg_rating']:.2f}</b></li>
                        <li>💬 Total Reviews: <b>{int(row['num_reviews'])}</b></li>
                    </ul>
                </div>
                """, unsafe_allow_html=True)

                reviews = condition_filtered[
                    (condition_filtered['drugName'] == row['drugName']) & (condition_filtered['is_positive'])
                ]['review'].dropna().reset_index(drop=True)

                key = f"review_index_{i}"
                if key not in st.session_state:
                    st.session_state[key] = 0

                review_index = st.session_state[key]
                reviews_to_show = reviews[review_index:review_index + 2]

                for j, review in reviews_to_show.items():
                    st.markdown(f"> 💬 _Review {review_index + j + 1}_: {review}")

                if st.button(f"Next Reviews for {row['drugName']}", key=f"next_button_{i}"):
                    if review_index + 2 < len(reviews):
                        st.session_state[key] += 2
                    else:
                        st.session_state[key] = 0  # Reset

            # Other Drugs
            if len(drug_stats) > 3:
                st.markdown("## 💊 Other Drugs")
                for _, row in drug_stats.iloc[3:].iterrows():
                    st.markdown(f"""
                    <div style="border:1px solid #EEE; padding:8px; border-radius:8px; background-color:#ffffff; margin-bottom:10px;">
                        <b>{row['drugName']}</b><br>
                        ⭐ Rating: {row['avg_rating']:.2f} | 👍 Positive: {int(row['positive_reviews'])} | 💬 Reviews: {int(row['num_reviews'])}
                    </div>
                    """, unsafe_allow_html=True)

