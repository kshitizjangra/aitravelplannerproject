!pip langchain_google_genai
import os
import streamlit as st
from langchain_google_genai import ChatGoogleGenerativeAI
from google.api_core.retry import Retry

# Set environment variable for DNS resolver
os.environ["GRPC_DNS_RESOLVER"] = "native"

# Initialize Streamlit app
st.set_page_config(page_title="AI Travel Planner", layout="wide")
st.title("AI-Powered Travel Planner")

# Hardcoded API key (replace with your actual key)
api_key = "AIzaSyBRCfhHkA6Lr1Eeg8AdZcnGdGx3DHFC6wc"

# Custom retry policy
retry_policy = Retry(
    initial=1.0,     # Initial backoff delay (seconds)
    maximum=60.0,    # Maximum backoff delay
    multiplier=2.0,  # Backoff multiplier
    deadline=900.0   # Total timeout (15 minutes)
)

# Initialize Gemini model with retry policy
llm = ChatGoogleGenerativeAI(
    model="gemini-2.0-flash",
    google_api_key=api_key,
    temperature=0.7,
    retry=retry_policy
)

# User input
source = st.text_input("Source Location:")
destination = st.text_input("Destination Location:")
travel_mode = st.selectbox("Travel Mode:", ["All", "Train", "Bus", "Flight"])

# Generate travel recommendations
if st.button("Find Travel Options"):
    if not source or not destination:
        st.warning("Please enter both source and destination locations")
    else:
        # Create prompt
        prompt = f"Provide travel options from {source} to {destination} using {travel_mode}. " \
                 "Include estimated costs and duration. Format as bullet points."

        # Create message structure for Gemini
        messages = [
            {"role": "user", "content": prompt}
        ]

        # Invoke Gemini directly with retry policy
        try:
            response = llm.invoke(messages)
            st.success("Travel Recommendations:")
            st.write(response.content)
        except Exception as e:
            st.error(f"Error: {str(e)}")
