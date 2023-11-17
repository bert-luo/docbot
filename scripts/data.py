from context import download_embeddings
import pandas as pd
import sys
sys.path.append("../docbot/server")
# TODO: import llm and db
#from llm import embed_texts
from tqdm import tqdm

def download_dataset(library_name:str): 
    df = download_embeddings(library_name)
    df.to_parquet(f'data/{library_name}.parquet')

def load_dataset(library_name:str): 
    df = pd.read_parquet(f'data/{library_name}.parquet')
    return df

def create_documents(library_name:str):
    '''Assemble, embed, and store document from Fleet data into weaviate DB'''
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


if __name__ == "__main__":
    create_documents('langchain')

    '''df = load_dataset('langchain')
    print(df.columns)
    for col in df.columns: 
        print(col, " : ", df[col].loc[69])'''