from fastapi import FastAPI
from pydantic import BaseModel

from llm import chat_completion

app = FastAPI()

# run using 
# $ uvicorn api:app --reload

class ChatRequest(BaseModel):
    message: str
    history: list[dict]

@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.get("/fetch/")
def create_documents(): 
    # fetch the urls given the base url of all docs
    # process each doc 
    # create new index and store them in weaviate 
    return {"message": "Hello World"}

@app.get("/chat/")
def chat(request: ChatRequest): 
    # given query, use co.chat connector mode
    response = chat_completion(request.message, request.history)
    return response