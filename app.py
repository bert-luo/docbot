import streamlit as st
import html 
import xml.etree.ElementTree as ET
import requests
import json
import re

FASTAPI_BASE_URL = "http://localhost:8500"

def fetch_data_from_api(endpoint, payload=None):
    if payload:
        response = requests.post(f"{FASTAPI_BASE_URL}/{endpoint}", json=payload)
    else:
        response = requests.get(f"{FASTAPI_BASE_URL}/{endpoint}")
    if response.status_code == 200:
        return response.json()
    else:
        st.error("Failed to fetch data from the API")
        return {}

# App title and configuration
st.set_page_config(page_title="Chatbot UI")

# Header
header = st.container()
header.title("Docbot")
header.write("""<div class='fixed-header'/>""", unsafe_allow_html=True)

# Custom CSS for the sticky header
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

def wrap_in_xml(text, start, end, num):
    return text[:end+1] + f"^[{num}]" + text[end+1:]


# Dropdown for selecting a library
library = st.selectbox(
    "Select the library",
    ("Langchain","Document", "pandas", "pytorch")
)

# Initialize chat messages in session state if not present
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "message": "How may I assist you today?"}]

# User input for chat
prompt = st.chat_input("Enter your message")
    
# Process the prompt if it's not None
if prompt:
    # Construct the request payload
    chat_request_payload = {
        "message": prompt,
        "history": st.session_state.messages,
        "library": library
    }

    # Send the request to the FastAPI server
    data = fetch_data_from_api("chat/", payload=chat_request_payload)
    # Process the response...

    json_data = data
    if "documents" in st.session_state and json_data['citations'] != None:
        with st.sidebar:
            for document in st.session_state.documents: 
                st.write(f"**{document['title']}**")
                st.info(f"Source: {document['id']}", icon="📄")
                st.info(f"{document['snippet']}")
                st.write("---")  # Separator line

    if "documents" not in st.session_state and json_data["citations"] != None:
        st.session_state.documents = json_data["documents"]
        with st.sidebar:
            for document in st.session_state.documents: 
                st.write(f"**{document['title']}**")
                st.info(f"Source: {document['id']}", icon="📄")
                st.info(f"{document['snippet']}")
                st.write("---")  # Separator line

    st.session_state.messages.append({"role": "user", "message": prompt})

    # Instead of adding the response as normal text, format it as code
    st.session_state.messages.append({"role": "assistant", "message": data["text"]})
    # if "citations" in json_data:
    #     for citation in json_data["citations"]:
    #         start = citation["start"]
    #         end = citation["end"]
    #         wrapped_text = wrap_in_xml(json_data['text'], start, end, 1)
    #         print(wrapped_text)
    #     st.session_state.messages.append({"role": "assistant", "content": json_data['text']})
    # else:
    #     st.session_state.messages.append({"role": "assistant", "content": json_data['text']})
    st.session_state.prompt = ""

def display_mixed_content(response):
    # Regular expression to find code blocks
    code_block_regex = re.compile(r'```(.*?)```', re.DOTALL)
    code_blocks = code_block_regex.findall(response)
    text_blocks = code_block_regex.split(response)

    # Iterate through the text and code blocks, displaying each appropriately
    for text, code in zip(text_blocks, code_blocks + ['']):
        # print("TEXT : " + str(text))
        # print("CODE : " + str(code))
        if text.strip():
            st.write(text.strip())
        if code.strip():
            st.code(code.strip(), language='python')

# Display chat messages
for message in st.session_state.messages:
    # print(message)
    if message["role"] == "assistant":
        with st.chat_message(message["role"]):
            display_mixed_content(message["message"])
    else:
        # For all other messages, display normally
        with st.chat_message(message["role"]):
            st.write(message["message"])