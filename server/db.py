import weaviate
from dotenv import load_dotenv
import os
import json

from llm import embed_texts # TODO: put inside function

load_dotenv()
WEAVIATE_API_KEY = os.getenv("WEAVIATE_API_KEY")
COHERE_API_KEY = os.getenv("COHERE_API_KEY")

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

    client.schema.create_class(document_schema)

def add_documents(documents, index_name): 
    # TODO: implement
    return 

def query_weaviate(query: str, index_name: str): 
    '''
    Vector Search weaviate database with user query
    '''
    client = get_weaviate_client()
    nearText = {"concepts": [query]}
    response = (
        client.query
        .get(index_name, ["text", "url"])
        .with_near_text(nearText)
        #.with_limit(2)
        .do()
    )
    return response