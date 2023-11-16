from fastapi import FastAPI

app = FastAPI()

# run using 
# $ uvicorn api:app --reload

@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.get("/fetch/")
def chat(): 
    
    return {"message": "Hello World"}

@app.get("/chat/")
def chat(): 

    return {"message": "Hello World"}