import streamlit as st
import pickle
import numpy as np

'''
# Load model and encoders
with open("model.pkl", "rb") as f:
    model = pickle.load(f)

with open("encoder.pkl", "rb") as f:
    label_encoders = pickle.load(f)

st.title("Drug Review Sentiment Prediction")
st.write("Enter your drug name, condition, and review to see sentiment prediction.")

# User input
drug_name = st.text_input("Drug Name")
condition = st.text_input("Condition")
review = st.text_area("Patient Review")

# Prediction button
if st.button("Predict Sentiment"):
    if not drug_name or not condition or not review:
        st.warning("Please fill all fields.")
    else:
        try:
            # Encode drug and condition
            drug_encoded = label_encoders['drugName'].transform([drug_name])[0]
            condition_encoded = label_encoders['condition'].transform([condition])[0]

            # You might need to add preprocessing steps (e.g., TF-IDF or tokenization for review)
            # For demonstration, we just join features
            input_features = [drug_encoded, condition_encoded]  # Plus review_vector if used

            # If your model uses vectorized review, add logic to transform `review`
            # For example: review_vector = tfidf.transform([review])

            # Make prediction
            prediction = model.predict([input_features])  # Adjust input format as needed

            sentiment = "Positive" if prediction[0] == 1 else "Negative"
            st.success(f"Predicted Sentiment: **{sentiment}**")

        except Exception as e:
            st.error(f"Error: {e}")



import streamlit as st
import pandas as pd

# Load dataset
@st.cache_data
def load_data():
    return pd.read_csv("filter data.csv")

data = load_data()

st.title("💊 Drug Review Explorer")
st.write("Enter a **drug name** to see all related conditions, reviews, and details.")

# User input
drug_input = st.text_input("Enter Drug Name")

if drug_input:
    # Filter case-insensitive match
    filtered_data = data[data['drugName'].str.lower() == drug_input.lower()]
    
    if filtered_data.empty:
        st.warning("No data found for this drug.")
    else:
        st.success(f"Found {len(filtered_data)} reviews for **{drug_input.title()}**")

        # List unique conditions
        conditions = filtered_data['condition'].dropna().unique()
        st.subheader("🩺 Conditions Treated")
        for cond in conditions:
            st.markdown(f"- {cond}")

        # Show review details
        st.subheader("📝 Patient Reviews")
        for idx, row in filtered_data.iterrows():
            st.markdown(f"""
                **Condition**: {row['condition']}  
                **Rating**: {row['rating']}  
                **Review**: {row['review']}  
                **Useful Count**: {row['usefulCount']}  
                ---
            """)
'''

import streamlit as st
import pandas as pd

# Load dataset
@st.cache_data
def load_data():
    return pd.read_csv("drugsCom_raw (1).tsv", sep='\t')

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
