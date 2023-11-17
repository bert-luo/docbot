import cohere
from cohere.responses.classify import Example
from dotenv import load_dotenv
import os
import requests
from bs4 import BeautifulSoup

from prompt import base_prompt


load_dotenv()
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
    # TODO: fetch docs from weaviate, either by connector mode or hybrid search
    from db import query_weaviate
    weaviate_response = query_weaviate(query, library)
    try: 
        docs = response['data']['Get'][library]
    else: 
        docs = []

    prompt = query # base_prompt +
    response = co.chat(  
        prompt,
        model='command',   # -nightly
        #max_tokens=200, # This parameter is optional. 
        preamble_override=base_prompt, 
        documents=docs,
        chat_history=history,
        temperature=0.5
    )
    return response


if __name__ == "__main__":
    query = 'what kind of animal are pythons?'
    chat_completion(query, 'Document')
    #print('RESPONSE: ', chat_completion(query, 'Document'))
    #print(embed_texts(['test 1', 'i am gay']))
    