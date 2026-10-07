import requests
import os
from dotenv import load_dotenv

load_dotenv()

BASE_URL = os.getenv("BOOKSTACK_URL")
TOKEN_ID = os.getenv("BOOKSTACK_TOKEN_ID")
TOKEN_SECRET = os.getenv("BOOKSTACK_TOKEN_SECRET")

def get_headers():
    # return dict with Authorization and Content-Type
    header ={
        "Authorization" : f"Token {TOKEN_ID}:{TOKEN_SECRET}",
        "Content-Type" : "application/json"
    }
    return header

def get_all_page_ids():
    # paginate through GET /api/pages?count=500&offset=0
    offset = 0
    total = 1
    pages = []
    while offset < total:
        result = requests.get(f'{BASE_URL}/api/pages?count=500&offset={offset}', headers=get_headers())
        data = result.json()
        total = data["total"]

        for item in data["data"]        :
            pages.append({"id" : item["id"], "name": item["name"]})
        offset += 500

        print('Total pages founda are: ', len(pages))
        return pages


def get_page_content(page_id, page_name):
    result = requests.get(f'{BASE_URL}/api/pages/{page_id}/export/plaintext', headers=get_headers())
    data = result.text
    page_content = {}
    page_content["filename"] = page_name
    page_content["text"] = data

    return page_content


def get_all_content():

    pages = get_all_page_ids()
    total = len(pages)
    docs = []
    for i, page in enumerate(pages):
        doc = get_page_content(page["id"], page["name"])
        if len(doc["text"]) < 50:
            print(f"SKIPPED ({len(doc['text'])} chars): {page['name']}")
            continue
        docs.append(doc)

        print (f"({i+1}/{total}) Fetched: {page['name']}")
    return docs
    

if __name__ == "__main__":
    docs = get_all_content()
    print(f"Total docs ready for ingestion: {len(docs)}")

