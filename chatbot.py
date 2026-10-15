import ollama
from retriever import retrieve
# from duckduckgo_search import DDGS
from googlesearch import search
import time
import os



ollama_host = os.getenv("OLLAMA_HOST", "http://localhost:11434")
ollama.Client(host=ollama_host)

def is_casual(query):
    casual_phrases = ["hi", "hello", "hey", "bye", "good morning", "good afternoon", "how's it going"]
    return any(phrase in query.lower() for phrase in casual_phrases)


def ask(query, results=None, chat_history=None):
    
    if is_casual(query):
        yield "Hello! I'm BookBot, your CADTech IT assistant. Ask me anything about IT issues and I'll search our BookStack documentation for you."
        return

    if results is None:
        results = retrieve(query)
    
    top_distance = results["distances"][0][0]
    
    if top_distance > 370:
        yield "I don't know based on the available documentation."
        return
    
    context = "\n\n".join(results["documents"][0])

    system_prompt = """You are a helpful IT assistant for the College of Arts & Design at RIT.
        Use ONLY the BookStack documentation provided in the user message to answer.
        Provide the COMPLETE answer with ALL steps — do not stop early or cut short under any circumstances.
        If the answer is in the documentation, start with "Based on the BookStack documentation,"
        If the answer is NOT in the documentation, start with "This is not from BookStack documentation — please verify this answer."
        Do not include section references like "(Refer to X section)".
        Do not add conversational phrases like "let me know" or "please feel free".
        Include any links present in the documentation."""

    user_prompt = f"""BookStack documentation:
    {context}

    Question:
    {query}

    Answer:"""

    # build messages with history
    messages = [{"role": "system", "content": system_prompt}]

    if chat_history:
        for msg in chat_history[-6:]:
            messages.append({
                "role": msg["role"],
                "content": msg["content"]
            })

    messages.append({"role": "user", "content": user_prompt})

    response = ollama.chat(
        model="qwen2.5:14b",
        messages=messages,
        stream=True,
        options={
            "num_predict": 1024,
            "temperature": 0.1
        }
    )

    full_answer = ""
    for chunk in response:
        piece = chunk["message"]["content"]
        full_answer += piece
        yield piece

    return full_answer


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