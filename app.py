import streamlit as st
import html 
import xml.etree.ElementTree as ET
import requests

FASTAPI_BASE_URL = "http://localhost:8000"

def fetch_data_from_api(endpoint):
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

documents = [
    {
        "title": "Tech in Health",
        "published": "Jul 20, 2023",
        "source": "wired.com",
        "snippet": "The digital health industry is experiencing explosive growth as technology continues to integrate with healthcare. Digital health companies are utilizing innovative technology such as artificial intelligence, blockchain, and mobile applications to transform the traditional healthcare model."
    },
    {
        "title": "Tech in Health",
        "published": "Jul 20, 2023",
        "source": "wired.com",
        "snippet": "The digital health industry is experiencing explosive growth as technology continues to integrate with healthcare. Digital health companies are utilizing innovative technology such as artificial intelligence, blockchain, and mobile applications to transform the traditional healthcare model."
    },
    {
        "title": "Tech in Health",
        "published": "Jul 20, 2023",
        "source": "wired.com",
        "snippet": "The digital health industry is experiencing explosive growth as technology continues to integrate with healthcare. Digital health companies are utilizing innovative technology such as artificial intelligence, blockchain, and mobile applications to transform the traditional healthcare model."
    },
    # Add more document dictionaries here
]

# Dropdown for selecting a library
library = st.selectbox(
    "Select the library",
    ("langchain", "pandas", "pytorch")
)

with st.sidebar:
    st.subheader("Related Documents")
    for doc in documents:
        st.write(f"**{doc['title']}**")
        st.caption(f"Published: {doc['published']} | Source: {doc['source']}")
        st.info(doc["snippet"], icon="📄")
        st.write("---")  # Separator line

# Initialize chat messages in session state if not present
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "How may I assist you today?"}]

# User input for chat
prompt = st.chat_input("Enter your message")
    

# Process the prompt if it's not None
if prompt:
    # Add user message to session state

    data = fetch_data_from_api("")  # Assuming you want to call the '/fetch/' endpoint
    
    st.session_state.messages.append({"role": "user", "content": prompt})

    code_response = """
    <response> 
    <text>I'm some text in a text element.</text>
    <code>print("I'm some code in a code element.")</code>
    <text>Here's some more text after the code.</text>
    </response>
    """

    

    # Instead of adding the response as normal text, format it as code
    st.session_state.messages.append({"role": "assistant", "content": data["message"]})
    st.session_state.messages.append({"role": "assistant", "content": code_response})
    st.session_state.prompt = ""

def display_xml_content(xml_content):
    # Parse the XML content
    root = ET.fromstring(xml_content)
    with st.chat_message(message["role"]):
        for elem in root:
            if elem.tag == 'text':
                # Directly display the text from <text> elements
                st.write(html.unescape(elem.text))
            elif elem.tag == 'code':
                # Display the code within <code> elements in a code block
                st.code(html.unescape(elem.text), language='python')
            # Check if there is any text following the current element (elem.tail)
            if elem.tail is not None:
                st.write(html.unescape(elem.tail.strip()))

# Display chat messages
for message in st.session_state.messages:
    if message["role"] == "assistant" and '<response>' in message["content"]:
        # Display mixed content for messages from the assistant that contain XML
        display_xml_content(message["content"])
    else:
        # For all other messages, display normally
        with st.chat_message(message["role"]):
            st.write(message["content"])