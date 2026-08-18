import ollama
from retriever import retrieve
# from duckduckgo_search import DDGS
from googlesearch import search
import time


def ask(query):
    # 1. call retrieve(query) to get relevant chunks
    results = retrieve(query)

    top_distance = results["distances"][0][0]
    
    if top_distance > 370:  # tune this number based on testing
        yield "I don't know based on the available documentation."
        return
    
    context = "\n\n".join(results["documents"][0])
    

    # 2. join the chunks into a context string
    context = "\n\n".join(results["documents"][0]) 
    # 3. build the prompt with context + query
    prompt = f"""
        You are a helpful IT assistant for the College of Arts & Design at RIT.

        First, check if the answer is in the BookStack documentation provided below.

        If the answer IS in the BookStack documentation:
        - Answer using ONLY the documentation
        - Start with "Based on the BookStack documentation,"
        - Provide the complete answer with all steps
        - Do not add any outside information

        If the answer is NOT in the BookStack documentation:
        - Provide a helpful general answer based on your knowledge
        - Start with "This is not from BookStack documentation — please verify this answer."
        - Still try to be as helpful as possible for the IT tech

        Do not include section references like "(Refer to X section)" in your answer.
        Do not add conversational phrases like "let me know" or "please feel free".

        BookStack documentation:
        {context}

        Question:
        {query}

        Answer:
    """


    # 4. call ollama.chat() with llama3.1 model and the prompt
    response = ollama.chat(
        model="mistral:7b",
        messages=[
            {
                "role": "system",
                "content": "You are an IT assistant. You ONLY answer using the provided context. If the context does not contain the answer, say exactly: 'I don't know based on the available documentation.' Never add links, outside resources, or information not in the context."
            },
            {
                "role": "user", 
                "content": prompt
            }
        ],
        stream=True
    )


    full_answer = ""
    for chunk in response:
        piece = chunk["message"]["content"]
        full_answer += piece
        yield piece  # ← sends each word as it arrives
    
    # store full answer for "don't know" check
    return full_answer


def web_search(query):
    query_formatted = query.replace(" ", "+")
    return f"1. Search Google: https://www.google.com/search?q={query_formatted}\n\n2. Search Reddit: https://www.reddit.com/search/?q={query_formatted}\n\n3. Search Microsoft Support: https://support.microsoft.com/en-us/search/results?query={query_formatted}"


if __name__ == "__main__":
    
    # answer = ask("machine won't display")
    web_results = web_search("how to fix printer offline error")
    print("Web results:", web_results)

    # print(answer)