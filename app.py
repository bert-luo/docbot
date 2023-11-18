import streamlit as st
import html 
import xml.etree.ElementTree as ET
import requests
import json

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

json_data = '''
{  
    "response_id": "ea9eaeb0-073c-42f4-9251-9ecef5b189ef",  
    "text": "<response>\\n    <text>I'm some text in a text element.</text>\\n    <code>print(\\"I'm some code in a code element.\\")</code>\\n    <text>Here's some more text after the code.</text>\\n</response>",  
    "generation_id": "1b5565da-733e-4c14-9ff5-88d18a26da96",  
    "token_count": {  
        "prompt_tokens": 445,  
        "response_tokens": 13,  
        "total_tokens": 458,  
        "billed_tokens": 20  
    },  
    "meta": {  
        "api_version": {  
            "version": "2022-12-06"  
        }  
    },  
    "citations": [  
        {  
            "start": 2,  
            "end": 15,  
            "text": "Emperor penguins",  
            "document_ids": [  
                "doc_0"  
            ]  
        },  
        {  
            "start": 48,  
            "end": 59,  
            "text": "Antarctica.",  
            "document_ids": [  
                "doc_1"  
            ]  
        }  
    ],  
    "documents": [  
        {  
            "id": "doc_0",  
            "title": "Tall penguins",  
            "snippet": "Emperor penguins are the tallest.",  
            "url": ""  
        },  
        {  
            "id": "doc_1",  
            "title": "Penguin habitats",  
            "snippet": "Emperor penguins only live in Antarctica.",  
            "url": ""  
        }  
    ],  
    "search_queries": []  
}
'''
def wrap_in_xml(text, start, end, num):
    return text[:end+1] + f"^[{num}]" + text[end+1:]


# Dropdown for selecting a library
library = st.selectbox(
    "Select the library",
    ("langchain","Document", "pandas", "pytorch")
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

    print("HISTORY: " + str(chat_request_payload['history']))
    # Send the request to the FastAPI server
    print(chat_request_payload)
    data = fetch_data_from_api("chat/", payload=chat_request_payload)
    print(data)
    # Process the response...

    json_data = data
    print("JSON DATA " + str(json_data))
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

def display_xml_content(xml_content):
    root = ET.fromstring(xml_content)
    for elem in root:
        if elem.tag == 'text':
            # Directly display the text from <text> elements
            st.markdown(html.unescape(elem.text))
        elif elem.tag == 'code':
            # Display the code within <code> elements in a code block
            st.code(html.unescape(elem.text), language='python')
        # Check if there is any text following the current element (elem.tail)
        if elem.tail is not None:
                st.write(html.unescape(elem.tail.strip()))

# Display chat messages
for message in st.session_state.messages:
    print(message)
    if message["role"] == "assistant" and "message" in message and'<response>' in message["message"]:
        with st.chat_message(message["role"]):
            display_xml_content(message["message"])
    else:
        # For all other messages, display normally
        with st.chat_message(message["role"]):
            if "message" in message:
                st.write(message["message"])
            else:
                st.write(message["message"])
            # display_xml_content(message["content"])