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

    client = get_weaviate_client()
    client.schema.create_class(document_schema)
    client.batch.configure(
        batch_size=200,
        dynamic=True,
        timeout_retries=3,
    )

    df = load_dataset(library_name)
    for metadata in df['metadata'].values: 
        properties =  {
            'url': metadata['url'],
            'text': metadata['text'],
        }
        if 'title' in metadata: 
            properties['title'] = metadata['title']
        else: 
            properties['title'] = metadata['url']
    
    # TODO: integrate
     with client.batch as batch:
        for doc, embedding in zip(test_documents, embeddings):
            properties = {
            "text": doc,
            "url": str(len(doc)),
            }
            vector = embedding

            batch.add_data_object(properties, "Document", None, vector)


if __name__ == "__main__":
    create_documents('langchain')

    '''df = load_dataset('langchain')
    print(df.columns)
    for col in df.columns: 
        print(col, " : ", df[col].loc[69])'''