import requests
from bs4 import BeautifulSoup
import re

def process_document(): 
    '''
    processes string of html into a document ready to be stored in a vector DB
    TODO: remove links, get headings, text, and code
    '''
    return 

def get_urls(url): 
    '''
    check if sitemap.xml exists, if so parse and extract urls
    '''
    return 

# Function to crawl and scrape documents related to the software package
def web_crawler(url, max_pages=1):
    '''
    Given base python software docs URL, crawl through and return all document URLS within the base URL
    '''
    visited_urls = set()
    document_urls = []

    # Crawl recursively up to a maximum number of pages
    def crawl_page(current_url, depth):
        print(current_url, depth, max_pages)
        if depth > max_pages:
            return

        try:
            visited_urls.add(current_url)
            response = requests.get(current_url)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                #print(soup.get_text())
                # Find all anchor tags and crawl recursively
                for link in soup.find_all('a', href=True):
                    next_link = link['href']
                    if next_link != "/" and next_link not in visited_urls and next_link.startswith('/'):
                        document_urls.append(next_link)
                        next_url = url+next_link
                        crawl_page(next_url, depth + 2)

        except Exception as e:
            print("Error:", e)

    crawl_page(url, 0)
    return document_urls


if __name__ == "__main__":
    # Set the URL to start crawling and the software package name
    starting_url = "https://api.python.langchain.com/en/latest/llms/langchain.llms.cohere.Cohere.html" #"https://docs.streamlit.io/knowledge-base"  # Replace with a starting URL knowledge-base
    software = "streamlit"  # Replace with the name of the software package

    # Start the crawler
    found_documents = web_crawler(starting_url)
    print("Found Documents:")
    for doc_url in found_documents:
        print(doc_url)
