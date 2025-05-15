
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

st.set_page_config(page_title="MedGuide - Drug Recommender", layout="centered")
st.title("💊 MedGuide - Drug Recommender")
st.markdown("""
<style>
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
</style>
""", unsafe_allow_html=True)

# Input from user
condition_input = st.text_input("🔍 Enter a medical condition (e.g., Depression, Diabetes, etc.)")

if condition_input:
    # Normalize condition input
    normalized_input = condition_input.strip().lower()

    # Expand matching logic
    data['condition_lower'] = data['condition'].str.lower()
    matched_conditions = data[data['condition_lower'].str.contains(normalized_input)]

    if matched_conditions.empty:
        st.warning("No data found for this condition.")
    else:
        st.success(f"Found {len(matched_conditions)} reviews for condition containing: '{condition_input.title()}'")

        matched_conditions["is_positive"] = matched_conditions["rating"] >= 7

        # Group by drug
        drug_stats = (
            matched_conditions.groupby('drugName')
            .agg(
                avg_rating=('rating', 'mean'),
                num_reviews=('rating', 'count'),
                positive_reviews=('is_positive', 'sum')
            )
            .sort_values(by=['positive_reviews', 'avg_rating'], ascending=False)
            .reset_index()
        )

        # Top 3 Recommendations
        st.subheader("🌟 Top 3 Recommended Drugs")
        for i, row in drug_stats.head(3).iterrows():
            st.markdown(f"""
                <div style='border:1px solid #DDD; border-radius:8px; padding:10px; margin-bottom:10px;'>
                <b>{i+1}. {row['drugName']}</b><br>
                ⭐ Average Rating: {row['avg_rating']:.2f}<br>
                👍 Positive Reviews: {int(row['positive_reviews'])}<br>
                💬 Total Reviews: {int(row['num_reviews'])}
                </div>
            """, unsafe_allow_html=True)

        # Other Drugs
        if len(drug_stats) > 3:
            st.subheader("💊 Other Drugs")
            for idx, row in drug_stats.iloc[3:].iterrows():
                drug_name = row['drugName']
                reviews = matched_conditions[
                    (matched_conditions['drugName'] == drug_name) &
                    (matched_conditions['is_positive'])
                ]['review'].dropna().reset_index(drop=True)

                key_base = drug_name.replace(" ", "_").lower()
                review_key = f"review_index_{key_base}"
                button_key = f"show_reviews_{key_base}"
                next_button_key = f"next_button_{key_base}"

                if review_key not in st.session_state:
                    st.session_state[review_key] = 0

                st.markdown(f"""
                <div style='border:1px solid #EEE; padding:8px; border-radius:8px; background-color:#ffffff; margin-bottom:10px;'>
                    <b>{drug_name}</b><br>
                    ⭐ Rating: {row['avg_rating']:.2f} | 👍 Positive: {int(row['positive_reviews'])} | 💬 Reviews: {int(row['num_reviews'])}
                </div>
                """, unsafe_allow_html=True)

                if st.button(f"Show Reviews for {drug_name}", key=button_key):
                    review_index = st.session_state[review_key]
                    reviews_to_show = reviews[review_index:review_index + 2]

                    for i, review in reviews_to_show.items():
                        st.markdown(f"> 💬 _Review {review_index + i + 1}_: {review}")

                    if st.button(f"Next Reviews for {drug_name}", key=next_button_key):
                        if review_index + 2 < len(reviews):
                            st.session_state[review_key] += 2
                        else:
                            st.session_state[review_key] = 0  # Reset
