import os
import streamlit as st
from langchain_google_genai import ChatGoogleGenerativeAI
from google.api_core.retry import Retry

# Set environment variable for DNS resolver
os.environ["GRPC_DNS_RESOLVER"] = "native"

# Initialize the Streamlit app
st.set_page_config(page_title="AI Travel Planner", layout="wide")
st.title("AI-Powered Travel Planner")

# Storing the API key in session state
if "api_key" not in st.session_state:
    st.session_state.api_key = None
if "llm" not in st.session_state:
    st.session_state.llm = None

# Custom retry policy
retry_policy = Retry(
    initial=1.0,     # Initial backoff delay (in seconds)
    maximum=60.0,    # Maximum backoff delay (in seconds)
    multiplier=2.0,  # Backoff multiplier
    deadline=900.0   # Total timeout (15 minutes)
)

# Inputting API Key (Google Gemini) in the sidebar
with st.sidebar:
    st.title("Configuration")
    api_key = st.text_input(
        "Enter your Google Gemini API Key",
        placeholder="Paste your API key here...",
        key="api_key_input"
    )

    if api_key != st.session_state.api_key:
        st.session_state.api_key = api_key
        # Reinitialize the model when API key changes
        if api_key:
            try:
                st.session_state.llm = ChatGoogleGenerativeAI(
                    model="gemini-2.0-flash", # You can change the model
                    google_api_key=api_key,
                    temperature=0.7,
                    retry=retry_policy
                )
            except Exception as e:
                st.error(f"Invalid API Key or authentication error: {e}")
        else:
            st.session_state.llm = None

# User input
source = st.text_input("Source Location:", "")
destination = st.text_input("Destination Location:", "")
travel_mode = st.selectbox(
    "Travel Mode:",
    ["All", "Train", "Bus", "Flight"],
    index=0
)

# Generate travel recommendations
if st.button("Search Travel Options") and st.session_state.llm:
    if not source or not destination:
        st.warning("Please enter both source and destination locations")
    else:
        # Create prompt
        prompt = f"Provide travel options from {source} to {destination} using {travel_mode}. " \
                 "Include estimated costs and duration. Format as bullet points."

        # Creating a message structure for the AI model
        messages = [
            {"role": "user", "content": prompt}
        ]

        # Invoke Gemini directly with retry policy
        try:
            if st.session_state.llm:  # Ensure that the llm is initialized
                response = st.session_state.llm.invoke(messages)
                st.success("✈️ Travel Recommendations:")
                st.write(response.content)
        except Exception as e:
            st.error(f"Error: {str(e)}")
else:
    st.warning("Please Input your API Key to use this tool..")
