# PyLibrarian

## The Problem
It's no secret that when working with a new library, SDK, or API, software developers often waste hours and hours hopelessly poring over a sea of scattered documentation pages to find the one syntax example or function parameter datatype they needed.
With the arrival of AI tools such as ChatGPT, sometimes developers can get lucky and get the exact code they need simply by asking the LLM. However, traditional LLM’s knowledge pools are limited to their training data, so when they are asked about perhaps newer tech, they may be rendered useless, or even worse, hallucinate and spew nonsense, wasting even more of a developer’s time. 


## Our Solution
Pylibrarian is a special chatbot that solves all of these headaches by granting LLM access to complete documentation for Python’s most popular libraries using RAG architecture. We chose Python as the initial niche due to its widespread popularity and crucial role in developing the next wave of AI applications.

## How we built it
![System Diagram](https://imgur.com/a/R13NA21)

Pylibrarian was built by processing, embedding (using *cohere.embed*), and storing documentation pages into *Weaviate*’s vector database, with each library having it's own vector index. Upon a user query with a specified library, we can semantically search for the most relevant pages of documentation to that query. Using Cohere’s chat endpoint’s *document mode*, the chatbot synthesizes a response citing the documents, leading to far more consistent, grounded responses.

The most imortant part of this process was wrangling the data- AKA finding a scalable way to find, process, embed, and store every last page of documentaiton for a library. We did this by learning about webcrawling, sitemaps, etc. as well as finding existing datasets of software documentation people had already 'wrangled' 


## What's Next for PyLibrarian
- *Better UI*: I'll admit that UI was not a top priority in the rush of the hackathon, but modern chatbot responsive touches such as streaming the response or simply a loading wheel would be easy wins. Most notably, we could take advantage of Cohere chat's citation index markings that point the sources to the exact words in the response they reference. 

- *Complex Query Support*: The current system follows a standard RAG pipeline, which performs well in most cases but can sometimes struggle to retrieve relevant documents for semantically complex queries that may consist of multiple 'sub'-queries, such as "what methods in the library 