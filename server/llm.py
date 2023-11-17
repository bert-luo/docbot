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

def chat_completion(query:str, history: list[dict]): 
    '''
    Use RAG (Cohere + Weaviate) to generate chatbot response

    Given user query+message history, 
    use query to retrieve relevant documents from Weaviate cluster,
    feed into cohere's chat endpoint and return its response
    '''
    # TODO: fetch docs from weaviate, either by connector mode or hybrid search
    docs = []

    prompt = base_prompt + query
    response = co.chat(  
        prompt,
        model='command',   # -nightly
        #max_tokens=200, # This parameter is optional. 
        documents=docs,
        chat_history=history,
        temperature=0.5
    )

    return response


if __name__ == "__main__":

    url = "https://pandas.pydata.org/docs/reference/api/pandas.concat.html"
    response = requests.get(url)
    #soup = BeautifulSoup(response.text, 'html.parser')
    sample_document = response.text

    

    #print(base_prompt)

    if False:
        test_url = "https://pandas.pydata.org/docs/reference/api/pandas.unique.html"
        test_response = requests.get(test_url)
        test_document = test_response.text

        prompt = base_prompt + """
        <prompt> 
            How do I get the unique values in my pandas df?
            <context>
            <document>
                {test_document}
            </document>
        </context>
        </prompt>
        """

        response = co.chat(  
            prompt,
            model='command',   # -nightly
            #prompt = prompt,  
            #max_tokens=200, # This parameter is optional. 
            temperature=0.5)

        #intro_paragraph = response.generations[0].text
        answer = response.text

        print(answer)


    if False: # attempt at intent classifier which I don't think we'll do anymore
        examples=[
        Example("What parameters does this function take", "explain"),
        Example("Is there a function that does this?", "explain"),

        Example("are there docs that explain ", "explain"),
        Example("What parameters does _ take", "explain"),

        Example("write a script that does this", "write code"),
        Example("create a function that does this", "write code"),
        
        ]
        inputs=[
        "Am I still able to return my order?",
        "When can I expect my package?",
        "Do you ship overseas?",
        ]

        response = co.classify(
        inputs=inputs,
        examples=examples,
        )
        print(response)