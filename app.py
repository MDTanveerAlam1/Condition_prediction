
import streamlit as st
import pickle
import numpy as np
import pandas as pd


import streamlit as st
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

# Normalize user input to standard condition
def match_condition(user_input):
    user_input = user_input.lower().strip()
    for condition, aliases in condition_aliases.items():
        if user_input in aliases:
            return condition
    return None

# Streamlit interface
st.title("💊 Drug Recommendation System by Condition")
st.write("Enter a condition (e.g. **Depression**, **High BP**, or **Type 2 Diabetes**) to get recommended drugs with highest positive reviews and ratings.")

# Condition input
condition_input = st.text_input("Enter Condition:")
matched_condition = match_condition(condition_input)

if condition_input:
    if not matched_condition:
        st.warning("Unrecognized condition. Try: Depression, High Blood Pressure, or Diabetes, Type 2.")
    else:
        condition_filtered = data[data['condition'].str.lower() == matched_condition.lower()].copy()

        if condition_filtered.empty:
            st.error("No reviews found for this condition.")
        else:
            st.success(f"Showing results for: **{matched_condition.title()}**")

            # Mark positive reviews (rating >= 7)
            condition_filtered["is_positive"] = condition_filtered["rating"] >= 7

            # Compute drug stats
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

            # Show top 3 recommended drugs
            st.subheader("🌟 Top 3 Recommended Drugs (High Positive Reviews + High Rating)")
            for i, row in drug_stats.head(3).iterrows():
                drug = row['drugName']
                st.markdown(f"""
                    **{i+1}. {drug}**  
                    - 👍 Positive Reviews: {int(row['positive_reviews'])}  
                    - ⭐ Average Rating: {row['avg_rating']:.2f}  
                    - 💬 Total Reviews: {int(row['num_reviews'])}
                """)

                # Show positive reviews for top drugs
                reviews = condition_filtered[
                    (condition_filtered['drugName'] == drug) & (condition_filtered['rating'] >= 7)
                ]['review'].dropna().reset_index(drop=True)

                key = f"review_index_{i}"
                if key not in st.session_state:
                    st.session_state[key] = 0

                review_index = st.session_state[key]
                reviews_to_show = reviews[review_index:review_index + 2]

                if not reviews_to_show.empty:
                    for j, review in reviews_to_show.items():
                        st.markdown(f"> 💬 _Review {review_index + j + 1}_: {review}")
                else:
                    st.info("No more reviews to show.")

                if st.button(f"Next Reviews for {drug}", key=f"next_button_{i}"):
                    if review_index + 2 < len(reviews):
                        st.session_state[key] += 2
                    else:
                        st.session_state[key] = 0  # Reset if end reached

            # Display other drugs
            if len(drug_stats) > 3:
                st.subheader("💊 Other Drugs for This Condition")
                for _, row in drug_stats.iloc[3:].iterrows():
                    st.markdown(f"""
                        **{row['drugName']}**  
                        - 👍 Positive Reviews: {int(row['positive_reviews'])}  
                        - ⭐ Avg Rating: {row['avg_rating']:.2f}  
                        - 💬 Reviews: {int(row['num_reviews'])}
                        ---""")
