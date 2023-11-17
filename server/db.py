import weaviate
from dotenv import load_dotenv
import os
import json

from llm import embed_texts

load_dotenv()
WEAVIATE_API_KEY = os.getenv("WEAVIATE_API_KEY")
COHERE_API_KEY = os.getenv("COHERE_API_KEY")
auth_config = weaviate.AuthApiKey(api_key=WEAVIATE_API_KEY)

client = weaviate.Client(
  url="https://cohere-hack-imnt0qiv.weaviate.network",
  auth_client_secret=auth_config, 
  additional_headers={
        "X-Cohere-Api-Key": COHERE_API_KEY,
    }

)
print("client ready: ", client.is_ready())

if False:
    document_schema = {
        "class": "Document",
        "description": "page or chunk of software documentation",
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

    client.schema.delete_all()
    client.schema.create_class(document_schema)

    client.batch.configure(
        batch_size=200,
        dynamic=True,
        timeout_retries=3,
    )

    test_documents = [
        "Rust is the most loved programming language",
        "Python is an interpreted programming language", 
        "Pythons are reptiles", 
        "programming is a lucrative career in the 21st century"
    ]
    embeddings = embed_texts(test_documents)

    with client.batch as batch:
        for doc, embedding in zip(test_documents, embeddings):
            properties = {
            "text": doc,
            "url": str(len(doc)),
            }
            vector = embedding

            batch.add_data_object(properties, "Document", None, vector)

    result = (
        client.query.aggregate("Document")
        .with_fields("meta { count }")
        .do()
    )
    print("Object count: ", result["data"]["Aggregate"]["Document"])

if False: # hybrid search
    response = (
        client.query
        .get("Document", ["text", "url"])
        .with_hybrid(
            query="coding",
            alpha=0
        )
        #.with_additional(["score", "explainScore"])
        .with_limit(3)
        .do()
    )

    print(json.dumps(response, indent=2))

if True: # vector search
    nearText = {"concepts": ["what type of animal are Pythons?"]}
    response = (
        client.query
        .get("Document", ["text", "url"])
        .with_near_text(nearText)
        #.with_limit(3)
        .do()
    )

    result = response['data']['Get']['Document']
    print(result)