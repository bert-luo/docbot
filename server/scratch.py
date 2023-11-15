import os
from dotenv import load_dotenv

import weaviate
import weaviate.classes as wvc

import langchain
import cohere
from langchain.embeddings import CohereEmbeddings
from langchain.vectorstores import Weaviate
from langchain.schema.document import Document

load_dotenv()
COHERE_API_KEY = os.getenv("COHERE_API_KEY")

embeddings = CohereEmbeddings(cohere_api_key=COHERE_API_KEY, model="embed-english-v3.0")
test_documents = [
    "Rust is the most loved programming language",
    "Python is an interpreted programming language", 
    "Pythons are reptiles", 
    "programming is a lucrative career in the 21st century"
]

'''client = weaviate.Client(
    embedded_options=weaviate.EmbeddedOptions(port=8080),
    additional_headers={
        "X-Cohere-Api-Key": COHERE_API_KEY,
    }
)'''
client = weaviate.connect_to_local(
    port=8080,
    grpc_port=50051
)
print("Client is Ready?", client.is_ready())

# without langchain
vectorstore = client.collections.create(
    name="Test_Database",
    vectorizer_config=None,  # If set to "none" you must always provide vectors yourself. Could be any other "text2vec-*" also.
    #generative_config=wvc.Configure.Generative.openai()  # Ensure the `generative-openai` module is used for generative queries
)

document_embeddings = embeddings.embed_documents(test_documents)

objs = []
for i, (d,e) in enumerate(zip(test_documents, document_embeddings)):
    objs.append(wvc.DataObject(
        properties={
            "text": d,
            "index": i,
        },
        vector=e
    ))

#vectorstore = client.collections.get("Question")
vectorstore.data.insert_many(objs)    # This uses batching under the hood

response = vectorstore.query.near_text(
    query="snake",
    limit=2
)

print(response.objects[0].properties)  # Inspect the first object



# using langchain
'''documents = []
for i, test_doc in enumerate(test_documents): 
    vstore_doc = Document(
                page_content=test_doc,
                metadata={
                    'source': str(i)
                }, 
            )

db = Weaviate.from_documents(documents, embeddings, index_name="WikipediaLangChain", client=client, by_text=False)
docs = db.similarity_search("is python compiled or interpreted?")
print(docs)'''

