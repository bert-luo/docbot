from context import download_embeddings
import pandas as pd
import sys

from llm import embed_texts
from db import get_weaviate_client, create_weaviate_index

from tqdm import tqdm

def download_dataset(library_name:str): 
    df = download_embeddings(library_name)
    df.to_parquet(f'data/{library_name}.parquet')

def load_dataset(library_name:str): 
    df = pd.read_parquet(f'data/{library_name}.parquet')
    return df

def create_documents(library_name:str):
    '''Assemble, embed, and store document from Fleet data into weaviate DB''' 
    print(f'creating new vector index: {library_name}') # TODO: change when done testing
    create_weaviate_index(library_name)
    client = get_weaviate_client()
    client.batch.configure(
        batch_size=200,
        dynamic=True,
        timeout_retries=3,
    )

    df = load_dataset(library_name)
    objects = [{'url': metadata['url'],'text': metadata['text']} for metadata in df['metadata'].values]
    texts = [obj['text'] for obj in objects]
    embeddings = embed_texts(texts)
    print('embeddings created')

    with client.batch as batch:
        print('starting storage process...')
        for properties, embedding in tqdm(zip(objects, embeddings)):
            batch.add_data_object(properties, library_name, None, embedding)

    result = (
        client.query.aggregate(library_name)
        .with_fields("meta { count }")
        .do()
    )
    try:
        print("Object count: ", result["data"]["Aggregate"][library_name])
    except:
        capitalized = library_name[0].upper() + library_name[1:]
        print("Object count: ", result["data"]["Aggregate"][capitalized])

if __name__ == "__main__":
    lib = 'streamlit'
    download_dataset(lib)
    if False:
        client = get_weaviate_client()
        client.schema.delete_class(lib) 
    create_documents(lib)
