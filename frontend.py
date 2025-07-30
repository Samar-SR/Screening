import streamlit as st
import requests


# --- Backend API Call ---
# MODIFIED: The function now sends the full job context with each request.
# This allows the backend to be stateless and have all necessary information
# to generate a relevant response, whether it's the first question or a follow-up.
def chat_running(message: str, job_title: str, job_description: str, total_question: int):
    """Sends a message and job context to the backend chat API and returns the response."""
    try:
        # The payload now includes all the context from the session state.
        payload = {
            "user_message": message,
            "job_title": job_title,
            "job_description": job_description,
            "total_question": total_question
        }
        response = requests.post("http://127.0.0.1:8000/chat", json=payload)
        response.raise_for_status()  # Raise an exception for bad status codes (4xx or 5xx)
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Failed to connect to the backend API: {e}")
        return None


# --- Initialize Session State ---
# CONSOLIDATED: Grouped session state initialization for better readability.
# ADDED: 'messages' to store the chat history.
if 'job_details_set' not in st.session_state:
    st.session_state.job_details_set = False
    st.session_state.job_title = ""
    st.session_state.job_description = ""
    st.session_state.total_question = 3 # A sensible default
    st.session_state.messages = [] # To store chat history

st.title("📅 AI Screening")

# --- UI Logic ---
# We use the 'job_details_set' flag in session_state to decide what to show.

# STEP 1: Collect Job Details
if not st.session_state.job_details_set:
    st.header("1. Enter Job Details")

    # Using session state directly for input widgets helps preserve state on reruns
    job_title_input = st.text_area(
        "Enter the job title:",
        value=st.session_state.job_title,
        height=100,
        placeholder="e.g. Senior Python Developer"
    )

    job_description_input = st.text_area(
        "Enter the job description:",
        value=st.session_state.job_description,
        height=200,
        placeholder="e.g. We are looking for a Senior Python Developer with experience in building scalable web applications..."
    )

    total_question_input = st.number_input(
        "Enter total number of questions:",
        min_value=1,
        max_value=10,
        value=st.session_state.total_question,
        help="Set the number of screening questions the AI should ask."
    )

    if st.button("Confirm Job Details"):
        if job_title_input.strip() and job_description_input.strip():
            # Save details to session state, set the flag, and clear old chat
            st.session_state.job_title = job_title_input
            st.session_state.job_description = job_description_input
            st.session_state.total_question = total_question_input
            st.session_state.job_details_set = True
            st.session_state.messages = [] # Clear previous chat history
            st.rerun()
        else:
            st.warning("Please provide both the job title and description.")

# STEP 2: Main Chat Interface
else:
    # Display the confirmed job details in an expander
    with st.expander("✅ Confirmed Job Details", expanded=False):
        st.markdown(f"**Title:** {st.session_state.job_title}")
        st.markdown(f"**Description:**")
        st.info(st.session_state.job_description)
        st.markdown(f"**Total Questions:** {st.session_state.total_question}")
        if st.button("Edit Job Details"):
            st.session_state.job_details_set = False
            st.rerun()

    st.header("2. Start the Conversation")

    # Display chat messages from history on app rerun
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # NEW: Logic for the first, automatic API call.
    # If the chat history is empty, the conversation is new.
    # We trigger the first API call automatically without user input.
    if not st.session_state.messages:
        with st.chat_message("assistant"):
            with st.spinner("AI is generating the first question..."):
                # Call the backend with an empty message to signal the start.
                # The backend should use the job details to generate the first question.
                response = chat_running(
                    message="Start the Ai screening", # Empty message for the initial call
                    job_title=st.session_state.job_title,
                    job_description=st.session_state.job_description,
                    total_question=st.session_state.total_question
                )
                if response:
                    first_message = response
                    st.markdown(first_message)
                    # Add the AI's first message to the chat history
                    st.session_state.messages.append({"role": "assistant", "content": first_message})
                else:
                    st.error("The AI failed to start the conversation. Please check the backend.")

    # Use st.chat_input for a better user experience.
    # This will handle user input for all subsequent messages.
    if prompt := st.chat_input("Your response to the AI..."):
        # Add user message to chat history and display it
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Get and display AI response in a new chat message container
        with st.chat_message("assistant"):
            with st.spinner("AI is thinking..."):
                response = chat_running(
                    message=prompt,
                    job_title=st.session_state.job_title,
                    job_description=st.session_state.job_description,
                    total_question=st.session_state.total_question
                )
                if response:
                    ai_response = response
                    st.markdown(ai_response)
                    # Add AI response to chat history
                    st.session_state.messages.append({"role": "assistant", "content": ai_response})
                else:
                    st.error("The AI failed to respond. Please try again.")