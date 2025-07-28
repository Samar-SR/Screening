import streamlit as st
import requests


# Optional: Only if you're calling an API endpoint

def chat_running(message: str):
    response = requests.post("http://127.0.0.1:8000/chat", json={"user_message": message})
    return response.json()


st.title("📅 AI Meeting Scheduler")

user_input = st.text_area(
    "Enter a meeting request:",
    height=150,
    placeholder="e.g. Schedule a meeting with Alice and Bob next Friday at 3 PM in Room A"
)

if st.button("Schedule"):
    if user_input.strip():
        with st.spinner("Scheduling your meeting..."):
            # Option 1: If calling FastAPI server
            # response = chat_running(user_input)

            # Option 2: If using Langchain agent_executor
            response = chat_running(user_input)

            st.subheader("🧾 Extracted Event Details:")
            st.subheader("AI response: ")
            st.json(response['output'])
            st.subheader("Human message: ")
            st.json(response['input'])
    else:
        st.warning("Please enter a meeting request.")
