
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

# UI Configuration
st.set_page_config(page_title="MedGuide - Drug Recommender", page_icon="💊", layout="centered")

# Custom CSS

# Inline CSS Styling
st.markdown("""
    <style>
    /* Background and font */
    .stApp {
        background-color: #f4faff;
        font-family: 'Segoe UI', sans-serif;
    }

    h1, h2, h3 {
        color: #004080;
    }

    /* Input styling */
    .stTextInput > div > div > input, .stTextArea textarea {
        border: 2px solid #4da6ff;
        border-radius: 8px;
        padding: 8px;
        font-size: 16px;
    }

    /* Button styling */
    .stButton>button {
        background-color: #007BFF;
        color: white;
        font-weight: bold;
        border-radius: 10px;
        padding: 10px 16px;
        border: none;
        transition: all 0.3s ease;
    }

    .stButton>button:hover {
        background-color: #0056b3;
        transform: scale(1.02);
    }

    /* Container card styling */
    .custom-container {
        background-color: #ffffff;
        padding: 20px;
        border-radius: 12px;
        border: 1px solid #d9e6f2;
        margin-bottom: 20px;
        box-shadow: 0 2px 5px rgba(0,0,0,0.05);
    }

    /* Navigation sidebar */
    .css-1d391kg { background-color: #e6f2ff; }
    </style>
""", unsafe_allow_html=True)


# Sidebar Navigation
st.sidebar.title("🔍 Navigation")
page = st.sidebar.radio("Go to", ["🏠 Home", "🧪 Predict Review", "ℹ️ About"])

# Logo and Header
logo_path = "medguide_logo.png"
if os.path.exists(logo_path):
    st.image(logo_path, width=120)

st.title("💊 MedGuide - Drug Recommender")

# -------------- HOME PAGE --------------
if page == "🏠 Home":
    st.markdown("Find the **best medications** based on patient reviews & ratings.")

    # Input condition
    condition_input = st.text_input("🔍 Enter Medical Condition (e.g. Depression, Diabetes, high blood pressure, etc.)")

    # Synonyms for matching
    synonyms = {
        "depression": ["depression", "depressive", "mental health", "major depressive disorder", "clinical depression", "low mood", "melancholy", "despair", "blue mood", "sadness"],
        "high blood pressure": ["blood pressure", "hypertension", "BP", "raised blood pressure", "high BP", "hypertensive"],
        "diabetes, type 2": ["diabetes", "type 2 diabetes", "sugar", "adult-onset diabetes", "non-insulin dependent diabetes", "T2D", "hyperglycemia"]
    }

    def match_condition(user_input):
        user_input = user_input.lower()
        for condition, keys in synonyms.items():
            if any(k in user_input for k in keys):
                return condition
        return user_input

    if condition_input:
        matched_condition = match_condition(condition_input)
        condition_filtered = data[data['condition'].str.lower() == matched_condition.lower()]

        if condition_filtered.empty:
            st.warning("⚠️ No Drugs and reviews found for this condition. Try a different keyword.")
        else:
            st.success(f"✅ {len(condition_filtered)} reviews found for **{matched_condition.title()}**")

            # Mark positive reviews
            condition_filtered["is_positive"] = condition_filtered["rating"] >= 7

            # Drug rankings
            drug_stats = (
                condition_filtered.groupby('drugName')
                .agg(avg_rating=('rating', 'mean'),
                     num_reviews=('rating', 'count'),
                     positive_reviews=('is_positive', 'sum'))
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
                        pos_reviews = reviews[reviews['rating'] >= 7][['review', 'rating']].sort_values(by='rating', ascending=False).head(3)
                        st.info("### Top Positive Reviews")
                        for r in pos_reviews.itertuples():
                            st.markdown(f"⭐ {r.rating}/10 - _{r.review[:250]}..._")

            # Toggle for Other Recommendations
            if st.button("📦 Show Other Recommended Drugs"):
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
                            pos_reviews = reviews[reviews['rating'] >= 7][['review', 'rating']].sort_values(by='rating', ascending=False).head(3)
                            st.info("### Top Positive Reviews")
                            for r in pos_reviews.itertuples():
                                st.markdown(f"⭐ {r.rating}/10 - _{r.review[:250]}..._")

# -------------- PREDICT PAGE --------------
elif page == "🧪 Predict Review":
    st.subheader("🧪 Test a New Review")
    review_input = st.text_area("💬 Enter a patient's review")
    condition_input = st.text_input("🏥 Enter Medical Condition")

    if st.button("🔍 Predict Sentiment"):
        if review_input and condition_input:
            try:
                # Create input dataframe
                input_df = pd.DataFrame([{
                    "review": review_input,
                    "condition": condition_input.lower()
                }])

                # Transform and predict
                transformed_input = encoder.transform(input_df)
                prediction = model.predict(transformed_input)
                sentiment = "Positive" if prediction[0] == 1 else "Negative"

                st.success(f"📊 Predicted Sentiment: **{sentiment}**")
            except Exception as e:
                st.error(f"❌ Error in prediction: {e}")
        else:
            st.warning("⚠️ Please enter both a review and a condition.")

# -------------- ABOUT PAGE --------------
elif page == "ℹ️ About":
    st.subheader("ℹ️ About MedGuide")
    st.markdown("""
    **MedGuide** is a drug recommender system that helps patients and medical professionals:
    - Discover top-rated medications
    - Understand patient sentiments through reviews
    - Make informed health decisions
    
    **Technologies Used:**
    - Machine Learning
    - Natural Language Processing
    - Streamlit
    
    Created with 💙 by the MedGuide Team.
    """)

# Footer
st.markdown("""
---
Made with 💙 by Tanveer | All rights reserved © 2025
""")
