import streamlit as st

# App title and configuration
st.set_page_config(page_title="Chatbot UI")

header = st.container()
header.title("Coral RAG")
header.write("""<div class='fixed-header'/>""", unsafe_allow_html=True)

### Custom CSS for the sticky header
st.markdown(
    """
<style>
    div[data-testid="stVerticalBlock"] div:has(div.fixed-header) {
        position: sticky;
        top: 2.875rem;
        background-color: rgb(14 17 23);
        z-index: 999;
    }
    .fixed-header {
        border-bottom: 1px solid black;
    }
</style>
    """,
    unsafe_allow_html=True
)

# Dropdown for selecting a library
library = st.selectbox(
    "Select the library",
    ("langchain", "pandas", "pytorch")
)

# Initialize chat messages in session state if not present
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "How may I assist you today with " + library + "?"}]

# User input for chat
prompt = st.chat_input("Enter your message")

# Process the prompt if it's not None
if prompt:
    # Add user message to session state
    st.session_state.messages.append({"role": "user", "content": prompt})

    # Placeholder for generating a response (AI functionality to be added)
    response = "This is where the assistant's response will be generated for " + library + "."

    # Add assistant's response to session state
    st.session_state.messages.append({"role": "assistant", "content": response})

# Display chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])