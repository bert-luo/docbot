import streamlit as st
import html 
import xml.etree.ElementTree as ET
import requests
import re
import weaviate
from dotenv import load_dotenv
import os
import json
import cohere
from cohere.responses.classify import Example
from prompt import base_prompt



load_dotenv()
WEAVIATE_API_KEY = os.getenv("WEAVIATE_API_KEY")
COHERE_API_KEY = os.getenv("COHERE_API_KEY")

co = cohere.Client(COHERE_API_KEY)

def embed_texts(texts: list[str]): 
    '''
    embed texts before storing them in vector DB
    '''
    response = co.embed(
        texts=texts,
        model='embed-english-v3.0',
        input_type='search_document'
    )
    return response.embeddings
        
def chat_completion(query:str, library:str, history:list[dict]=None): 
    '''
    Use RAG (Cohere + Weaviate) to generate chatbot response

    Given user query+message history, 
    use query to retrieve relevant documents from Weaviate cluster,
    feed into cohere's chat endpoint and return its response
    '''
    weaviate_response = query_weaviate(query, library)
    #print("WEAVIATE RESPONSE : " + str(weaviate_response))
    try: 
        docs = weaviate_response['data']['Get'][library]
    except Exception as e: 
        print("EXCEPTION : " + str(e))
        docs = []

    print("DOCS : " + str(docs))
    prompt = f'{library}\n' + query # base_prompt +
    response = co.chat(  
        prompt,
        model='command',   # -nightly
        #max_tokens=200, # This parameter is optional. 
        #return_preamble=True,
        preamble_override=base_prompt, 
        documents=docs,
        chat_history=history,
        temperature=0.5
    )
    response = {
    "response_id": response.response_id,
    "text": response.text,
    "generation_id": response.generation_id,
    "token_count": response.token_count,
    "meta": response.meta,
    "citations": response.citations,
    "documents": response.documents,
    "search_queries": response.search_queries
    }

    return response



def get_weaviate_client(): 
    auth_config = weaviate.AuthApiKey(api_key=WEAVIATE_API_KEY)
    client = weaviate.Client(
    url="https://cohere-hack-imnt0qiv.weaviate.network",
    auth_client_secret=auth_config, 
    additional_headers={
            "X-Cohere-Api-Key": COHERE_API_KEY,
        }
    )
    if client.is_ready(): 
        return client
    return False

def create_weaviate_index(index_name: str): 
    document_schema = {
        "class": index_name,
        "description": f"page or chunk of software documentation for {index_name}",
        "vectorizer": "text2vec-cohere",
        "moduleConfig": {
            "text2vec-cohere": {
                "model": "embed-english-v3.0", #TODO: use embed-english-light-v3.0 if too slow
                "truncate": "RIGHT"
            }, 
            "generative-cohere": {
            "model": "command-xlarge-nightly",  # Optional - Defaults to `command-xlarge-nightly`. Can also use`command-xlarge-beta` and `command-xlarge`
            "temperatureProperty": 0.5,  # Optional
            #"maxTokensProperty": <maxTokens>,  # Optional
            #"kProperty": <k>, # Optional
            #"stopSequencesProperty": <stopSequences>, # Optional
            #"returnLikelihoodsProperty": <returnLikelihoods>, # Optional
            },
        },
        "vectorIndexConfig": {
            "distance": "dot"
        },
        "properties": [
        {
            "name": "text",
            "dataType": [ "text" ],
            "description": "Doc body",
            "moduleConfig": {
                "text2vec-cohere": {
                    "skip": False,
                    "vectorizePropertyName": False
                }
            }
        },
        {
            "name": "url",
            "dataType": [ "text" ],
            "moduleConfig": { "text2vec-cohere": { "skip": True } }
        },
        ]
    }
    client = get_weaviate_client()
    client.schema.create_class(document_schema)


def query_weaviate(query: str, index_name: str): 
    '''
    Vector Search weaviate database with user query
    '''
    # TODO: Raise certainty
    client = get_weaviate_client()
    nearText = {
        "concepts": [query],
        "certainty": 0.0
        }
    response = (
        client.query
        .get(index_name, ["text", "url"])
        .with_near_text(nearText)
        .with_limit(2)
        .do()
    )
    return response

FASTAPI_BASE_URL = "http://localhost:10000"

def fetch_data_from_api(endpoint, payload=None):

    with st.spinner('Fetching data... Please wait.'):
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
header.title("PyLibrarian")
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
    "Select the library", (
        "Langchain",
        "Tensorflow",
        "Xgboost",
        "Streamlit"
        )
)

# Initialize chat messages in session state if not present
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "message": "How may I assist you today?", "sources": []}]

# User input for chat
prompt = st.chat_input("Enter your message")

if "source_count" not in st.session_state: 
    st.session_state.source_count = 0
    
# Process the prompt if it's not None
if prompt:
    # Construct the request payload
    sources = []


    # Send the request to the FastAPI server
    data = chat_completion(prompt, library, st.session_state.messages)
    # Process the response...
    # something to not print document if they have the same URL
    json_data = data
    if "documents" in st.session_state:
        if json_data['citations'] is not None:
            for new_doc in json_data['documents']:
                # Check if the new document's URL is already in the session state documents
                if not any(doc['url'] == new_doc['url'] for doc in st.session_state.documents):
                    # Append the new document if its URL is not found among the existing ones

                    st.session_state.source_count += 1
                    sources.append(f"Source {st.session_state.source_count}")
                    new_doc['id'] = f"Source {st.session_state.source_count}"
                    st.session_state.documents.append(new_doc)
        with st.sidebar:
            for document in st.session_state.documents: 
                st.info(f"{document['id']}", icon="📄")
                st.info(f"{document['url']}")
                st.write("---")  # Separator line

    if "documents" not in st.session_state and json_data["citations"] != None:
        st.session_state.documents = []
        for new_doc in json_data['documents']:
                # Check if the new document's URL is already in the session state documents
                if not any(doc['url'] == new_doc['url'] for doc in st.session_state.documents):
                    # Append the new document if its URL is not found among the existing ones
                    st.session_state.source_count += 1
                    sources.append(f"Source {st.session_state.source_count}")
                    new_doc['id'] = f"Source {st.session_state.source_count}"
                    st.session_state.documents.append(new_doc)
        with st.sidebar:
            for document in st.session_state.documents: 
                st.info(f"{document['id']}", icon="📄")
                st.info(f"{document['url']}")
                st.write("---")  # Separator line

    st.session_state.messages.append({"role": "user", "message": prompt, "sources": []})

    # Instead of adding the response as normal text, format it as code
    st.session_state.messages.append({"role": "assistant", "message": data["text"], "sources": sources})
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

    # Find all code blocks and text blocks
    code_blocks = code_block_regex.findall(response)
    text_blocks = code_block_regex.split(response)

    # Remove the code blocks from the text blocks
    text_blocks = [block for i, block in enumerate(text_blocks) if i % 2 == 0]

    # Iterate through the text and code blocks, displaying each appropriately
    for text, code in zip(text_blocks, code_blocks + ['']):
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
            if message["sources"] != []:
                for m in message["sources"]:
                    st.info(f"{m}")
    else:
        # For all other messages, display normally
        with st.chat_message(message["role"]):
            st.write(message["message"])