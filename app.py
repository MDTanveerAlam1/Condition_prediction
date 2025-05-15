
import streamlit as st
import pickle
import numpy as np
import pandas as pd


# Load dataset
@st.cache_data
def load_data():
    data = pd.read_csv("filter data.csv")
    data['condition'] = data['condition'].astype(str)
    return data

data = load_data()

# Condition alias mapping
condition_aliases = {
    "depression": ["depression", "depressed", "major depressive disorder", "mdd"],
    "high blood pressure": ["high blood pressure", "high bp", "hypertension", "bp"],
    "diabetes, type 2": ["diabetes, type 2", "type 2 diabetes", "t2d", "type ii diabetes"]
}

# Normalize input to match known condition
def match_condition(user_input):
    user_input = user_input.lower().strip()
    for condition, aliases in condition_aliases.items():
        if user_input in aliases:
            return condition
    return None

# Streamlit UI
st.title("🧠 Condition-Based Drug Recommender")
st.write("Enter a medical **condition** (like Depression, T2D, or High BP) to see top-rated drugs based on positive user reviews.")

# Input
condition_input = st.text_input("Enter Condition (e.g. Depression, High BP, T2D, etc.)")
matched_condition = match_condition(condition_input)

if condition_input:
    if not matched_condition:
        st.warning("Couldn't recognize this condition. Try 'Depression', 'High Blood Pressure', or 'Diabetes, Type 2'.")
    else:
        condition_filtered = data[data['condition'].str.lower() == matched_condition.lower()].copy()

        if condition_filtered.empty:
            st.warning("No data found for this condition.")
        else:
            st.success(f"Found {len(condition_filtered)} reviews for **{matched_condition.title()}**")

            # Create positive review flag
            condition_filtered["is_positive"] = condition_filtered["rating"] >= 7

            # Drug statistics
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

            # Top 3 drugs with reviews and pagination
            st.subheader("🌟 Top 3 Recommended Drugs")

            for i, row in drug_stats.head(3).iterrows():
                drug = row['drugName']
                st.markdown(f"""
                    **{i+1}. {drug}**  
                    - 👍 Positive Reviews: {int(row['positive_reviews'])}  
                    - ⭐ Average Rating: {row['avg_rating']:.2f}  
                    - 💬 Total Reviews: {int(row['num_reviews'])}
                """)

                # Filter and sort positive reviews for this drug
                reviews = condition_filtered[
                    (condition_filtered['drugName'] == drug) &
                    (condition_filtered['rating'] >= 7)
                ].sort_values(by='rating', ascending=False)['review'].dropna().reset_index(drop=True)

                # Session state to keep track of review pagination
                key = f"review_index_{i}"
                if key not in st.session_state:
                    st.session_state[key] = 0

                review_index = st.session_state[key]
                reviews_to_show = reviews[review_index:review_index + 2]  # Show 2 at a time

                if not reviews_to_show.empty:
                    for j, review in enumerate(reviews_to_show):
                        st.markdown(f"> 💬 _Review {review_index + j + 1}_: {review}")
                else:
                    st.info("No more reviews to show.")

                # Button for next reviews
                if st.button(f"Next Reviews for {drug}", key=f"next_button_{i}"):
                    if review_index + 2 < len(reviews):
                        st.session_state[key] += 2
                    else:
                        st.session_state[key] = 0  # Reset when end reached

            # Other drugs (after top 3)
            st.subheader("💊 Other Drugs")
            for _, row in drug_stats.iloc[3:].iterrows():
                st.markdown(f"""
                    **{row['drugName']}**  
                    - 👍 Positive Reviews: {int(row['positive_reviews'])}  
                    - ⭐ Average Rating: {row['avg_rating']:.2f}  
                    - 💬 Reviews: {int(row['num_reviews'])}  
                    ---""")
