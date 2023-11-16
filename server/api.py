from fastapi import FastAPI

app = FastAPI()

# run using 
# $ uvicorn api:app --reload

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
def chat(): 
    # given query, use co.chat connector mode
    return {"message": "Hello World"}