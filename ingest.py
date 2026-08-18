import os
import chromadb
import ollama
from langchain_text_splitters import RecursiveCharacterTextSplitter


directory = 'bookstack_exports'
def load_documents(directory):
    # loop through every .txt file in bookstack_exports/
    list_of_docs = []
    # filename = "devices.txt"

    for filename in os.listdir(directory):
        filepath = f"{directory}/{filename}"

        if filename.endswith(".txt"):
            with open(filepath, "r") as file:
                text = file.read()
                
                # Create a dictionary for this specific document
                doc_dict = {
                    "filename": filename,
                    "text": text
                }
                list_of_docs.append(doc_dict)
        print("File loaded is ", filename)


    # print which file was loaded
    # print("Dict is : ",files)
    # print("List of docs is :", list_of_docs)

    # return the list
    return list_of_docs


def chunk_documents(docs):
    # doc = load_documents(directory)

    # create a RecursiveCharacterTextSplitter
    #   chunk_size = 500
    #   chunk_overlap = 50
    #   separators = ["\n\n", "\n", ".", " "]
    splitter = RecursiveCharacterTextSplitter(
        chunk_size = 500,
        chunk_overlap = 50,
        separators=["\n\n", "\n", ".", " "]
    )
    
    list_of_metadata = []
    # give each chunk a unique id: filename_chunk_0, filename_chunk_1 etc
    for doc in docs:
        splits = splitter.split_text(doc["text"])
        for i, split in enumerate(splits):
            # print('i = ',i,split)
            # store source filename as metadata
            meta_data= {
                "id" : f"{doc['filename']}_chunk_{i}",
                "text" : split,
                "source" : doc["filename"]
            }
            list_of_metadata.append(meta_data)
    # print total number of chunks
    print('Number of chunks = ',meta_data["id"])
    # print("List of metadata = ", list_of_metadata)
    # return list of chunk dicts
    return list_of_metadata


def embed_and_store(chunks):
    # create a ChromaDB PersistentClient pointing at "data/" folder
    client = chromadb.PersistentClient(path="data/")
    # get or create a collection named "bookstack"
    collection = client.get_or_create_collection(name="bookstack")
    # for each chunk:
    for chunk in chunks:
        response = ollama.embeddings(
            model="nomic-embed-text",
            prompt=chunk["text"]    # the text you want to embed
        )
        vector = response["embedding"]
    #   call ollama.embeddings(model="nomic-embed-text", prompt=chunk text)
    #   add to chromadb collection with id, embedding, document text, and source metadata
        collection.add(
            ids=[chunk["id"]],
            embeddings=[vector],
            documents=[chunk["text"]],
            metadatas=[{"source": chunk["source"]}]
        )
        print(f"Embedded: {chunk['id']}")  # ✅ add this line
        # print when done
        # print(collection[chunk])
    print("Ingestion complete...")


if __name__ == "__main__":
    # call all 3 functions in order
    docs = load_documents('bookstack_exports')

    chunks = chunk_documents(docs)

    embed_and_store(chunks)




