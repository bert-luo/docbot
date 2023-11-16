import cohere
from cohere.responses.classify import Example
from dotenv import load_dotenv
import os
import requests
from bs4 import BeautifulSoup


load_dotenv()
COHERE_API_KEY = os.getenv("COHERE_API_KEY")
co = cohere.Client(COHERE_API_KEY)

url = "https://pandas.pydata.org/docs/reference/api/pandas.concat.html"
response = requests.get(url)
#soup = BeautifulSoup(response.text, 'html.parser')
sample_document = response.text

base_prompt = """
You are an expert programming assistant at Python that writes Python code and answers questions about Python and different libraries within.
The prompt you receive will always come in XML comepletely encompassed by <prompt> tags.
You will sometimes be provided with Python library documentation documents that you can but don't have to reference in your response, 
and the additional context will be provided within <context> tags with each document residing in <document> tags.
You should also ALWAYS respond in XML encompassed by <response> tags with any code you write residing in <code> tags. 
When writing code, you should add comments that explain your thought process.
Here is an example of a prompt you may receive as well as a high quality response: 

<prompt>
    what are some ways I can combine dataframes in Pandas?
    <context>
        <document>
            {sample_document}
        </document>
    </context>
</prompt>

<response>
    You can concatenate two Pandas DataFrames using the pd.concat() function. This function allows you to combine DataFrames either by rows (along the rows) or columns (along the columns), depending on the axis parameter.

    Here's an example of concatenating two DataFrames along rows:
    <code>
        import pandas as pd

        # Sample DataFrames
        data1 = {'A': [1, 2, 3], 'B': [4, 5, 6]}
        data2 = {'A': [7, 8, 9], 'B': [10, 11, 12]}

        df1 = pd.DataFrame(data1)
        df2 = pd.DataFrame(data2)

        # Concatenate along rows
        result = pd.concat([df1, df2], axis=0)

        print(result)
    </code>
        To concatenate along columns, set the axis parameter to 1:
    <code>
        result = pd.concat([df1, df2], axis=1)
    </code>
</response>

based on these guidelines, please try to prompts as best as you can.
"""

#print(base_prompt)

if True:
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

    response = co.generate(  
        model='command',   # -nightly
        prompt = prompt,  
        #max_tokens=200, # This parameter is optional. 
        temperature=0.5)

    intro_paragraph = response.generations[0].text
    print(intro_paragraph)


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