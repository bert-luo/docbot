import streamlit as st
import json

# The JSON data as a string
json_data = '''
{  
    "response_id": "ea9eaeb0-073c-42f4-9251-9ecef5b189ef",  
    "text": "The tallest penguins, Emperor penguins, live in Antarctica.",  
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
            "start": 22,  
            "end": 38,  
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

# Load the JSON data into a Python dictionary
data = json.loads(json_data)

# Display the response text
st.write(data['text'])

# Display the token counts
token_count = data['token_count']
st.write(f"Prompt tokens: {token_count['prompt_tokens']}")
st.write(f"Response tokens: {token_count['response_tokens']}")
st.write(f"Total tokens: {token_count['total_tokens']}")
st.write(f"Billed tokens: {token_count['billed_tokens']}")

# Display the citations
st.subheader("Citations")
for citation in data['citations']:
    st.write(f"Citation text: {citation['text']}")
    # Assuming 'document_ids' is a list of IDs that correspond to 'documents'
    cited_docs = [doc for doc in data['documents'] if doc['id'] in citation['document_ids']]
    for doc in cited_docs:
        st.write(f"Title: {doc['title']}")
        st.write(f"Snippet: {doc['snippet']}")
        # Display URL if available
        if doc['url']:
            st.write(f"URL: {doc['url']}")

# You can add similar code to display 'documents' and 'search_queries' if needed