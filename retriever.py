import chromadb
import ollama

CHROMA_DIR = "data/"
COLLECTION_NAME = "bookstack"

def retrieve(query):
    # 1. connect to existing ChromaDB PersistentClient at "data/"
    client = chromadb.PersistentClient(CHROMA_DIR)
    # 2. get the existing "bookstack" collection
    collection = client.get_or_create_collection(COLLECTION_NAME)
    # 3. embed the query using ollama.embeddings() with nomic-embed-text
    response = ollama.embeddings(
        model="nomic-embed-text",
        prompt=query   
    )
    # 4. extract the vector from the response
    vector = response["embedding"]
    # 5. call collection.query() with the vector, n_results=3
    result = collection.query(
        query_embeddings=[vector],  
        n_results=3                 
    )

    # 6. print the results
    # print(result)
    # 7. return the results
    return result

if __name__ == "__main__":
    # test it with a hardcoded query
    results = retrieve("how to install python on stations")
    print(results)

