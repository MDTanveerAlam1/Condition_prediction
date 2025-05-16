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

# Load model and encoder
model_path = "model.pkl"
encoder_path = "encoder.pkl"

with open(model_path, "rb") as f:
    model = pickle.load(f)

with open(encoder_path, "rb") as f:
    encoder = pickle.load(f)

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
logo = None

if os.path.exists(logo_path):
    logo = Image.open(logo_path)

if logo:
    st.image(logo, width=120)
st.title("💊 MedGuide - Drug Recommender")
st.markdown("Find the **best medications** based on patient reviews & ratings.")

# Input condition
condition_input = st.text_input("🔍 Enter Medical Condition (e.g. Depression, Diabetes, high blood pressure, etc.)")

# Match common variants for main conditions
synonyms = {
    "depression": [
        "depression", "depressive", "mental health", "major depressive disorder",
        "clinical depression", "low mood", "melancholy", "despair", "blue mood", "sadness"
    ],
    "high blood pressure": [
        "blood pressure", "hypertension", "BP", "raised blood pressure", "high BP", "hypertensive"
    ],
    "diabetes, type 2": [
        "diabetes", "type 2 diabetes", "sugar", "adult-onset diabetes",
        "non-insulin dependent diabetes", "T2D", "hyperglycemia"
    ]
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
        st.warning("⚠️ No Drugs and reviews found for this condition. Try a different keyword.")
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

        # 🎯 Predict Sentiment from User Input
        st.subheader("🧪 Test Your Own Review")
        user_review = st.text_area("💬 Enter a patient's review for prediction")

        if user_review:
            try:
                input_df = pd.DataFrame([{
                    "review": user_review,
                    "condition": matched_condition
                }])
                
                # Transform the input using encoder (assumes it handles preprocessing)
                transformed_input = encoder.transform(input_df)

                # Predict sentiment
                prediction = model.predict(transformed_input)
                sentiment = "Positive" if prediction[0] == 1 else "Negative"

                st.success(f"📊 **Predicted Sentiment: {sentiment}**")
            except Exception as e:
                st.error(f"⚠️ Prediction failed: {e}")

# Footer
st.markdown("""
---
Made with 💙 by Tanveer | All rights reserved © 2025
""")
