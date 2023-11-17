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
    return response

def process_weave_response(response:str, library:str):
    docs = []
    # TODO: adjust for certainty 
    for i in response['data']['Get'][library]:
        temp = {}
        for j in i:
            temp[j] = i[j]
        docs.append(temp)
    return docs
        
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
    docs = process_weave_response(weaviate_response, library)
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


if __name__ == "__main__":
    query = 'what kind of animal are pythons?'
    print('RESPONSE: ', chat_completion(query, 'Document'))
    