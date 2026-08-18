import streamlit as st
from chatbot import ask, web_search
from retriever import retrieve

# page config
st.set_page_config(page_title="BookBot", page_icon="📚")
st.title("BookBot - CADTech IT Assistant")





st.markdown("""
    <style>
        .stApp {
            background-color: #1a1a1a;
        }
        
        /* RIT orange title */
        h1 {
            color: #F76902 !important;
            font-size: 32px !important;
        }
        
        /* chat input */
        .stChatInput input {
            border: 2px solid #F76902 !important;
            border-radius: 8px;
            background-color: #242424 !important;
            color: white !important;
        }
        
        /* assistant message bubble */
        [data-testid="stChatMessageContent"] {
            background-color: #242424;
            border-left: 3px solid #F76902;
            border-radius: 0px 10px 10px 0px;
            padding: 12px;
        }
        
        /* user message bubble */
        [data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarUser"]) 
        [data-testid="stChatMessageContent"] {
            background-color: #2d2d2d;
            border-left: 3px solid #888888;
        }
        
        /* web search button */
        .stButton button {
            background-color: #F76902;
            color: white;
            border: none;
            border-radius: 8px;
            padding: 8px 20px;
            font-weight: 600;
        }
        
        .stButton button:hover {
            background-color: #d45d00;
            color: white;
        }

        /* header */
        .header-container {
            display: flex;
            align-items: center;
            gap: 16px;
            padding-bottom: 16px;
            border-bottom: 3px solid #F76902;
            margin-bottom: 24px;
        }

        .header-title {
            font-size: 28px;
            font-weight: 700;
            color: #FFFFFF;
        }

        .header-subtitle {
            font-size: 13px;
            color: #888888;
            margin-top: 2px;
        }
        
    </style>
    
""", unsafe_allow_html=True)

# header with logo
col1, col2 = st.columns([1, 8])
with col1:
    st.image("rit_logo.jpg", width=80)
with col2:
    st.markdown("""
        <div class="header-container">
            <div>
                <div class="header-title">BookBot</div>
                <div class="header-subtitle">
                    CADTech IT Assistant — College of Arts & Design &nbsp;
                    <span style="color: #4CAF50;">● Online</span>
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)






# initialize chat history in session state
# st.session_state is like a dict that persists between reruns
if "messages" not in st.session_state:
    # create empty list to store chat messages
    st.session_state.messages = []

    pass





if "show_web_search" not in st.session_state:
    # create a boolean flag, default False
    st.session_state.show_web_search = False
    pass



if "last_query" not in st.session_state:  # ← add here
    st.session_state.last_query = ""



# display all previous messages from history
for message in st.session_state.messages:
    # use st.chat_message() to display each message
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
    # each message dict has "role" and "content" keys
    pass




# chat input box at bottom of page
if prompt := st.chat_input("Ask me anything about IT issues..."):
    # 1. save last query
    st.session_state.last_query = prompt
    
    # 2. add user message to history
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # 3. display user message
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # 4. call ask() with a loading spinner
    with st.spinner("Searching BookStack..."):
        results = retrieve(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            # get the generator from ask()
            stream = ask(prompt)
            # grab first chunk to confirm LLM has started
            first_chunk = next(stream)
        
        # now stream the rest word by word including first chunk
        def full_stream():
            yield first_chunk
            for piece in stream:
                yield piece
        
        answer = st.write_stream(full_stream())

    st.session_state.messages.append({
        "role": "assistant",
        "content": answer
    })

    # remove both existing if statements and replace with this one
    if any(phrase in answer.lower() for phrase in [
        "not from bookstack",
        "i don't know",
        "not provided",
        "general steps",
        "please verify",
        "not in the documentation"
    ]):
        st.session_state.show_web_search = True





if st.session_state.show_web_search:
    if st.button("Search the web instead?"):
        # 1. call web_search() with last user query
        results = web_search(st.session_state.last_query)
        
        # 2. display web results
        with st.chat_message("assistant"):
            st.markdown("Here are some web results:")
            st.markdown(results)
        
        # 3. add to chat history
        st.session_state.messages.append({
            "role": "assistant",
            "content": f"Here are some web results:\n\n{results}"
        })
        
        # 4. reset flag so button disappears
        st.session_state.show_web_search = False



# add this at the very bottom of app.py
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: #444444; font-size: 11px;'>Powered by RIT CADTech · BookBot v1.0 · College of Arts & Design</div>",
    unsafe_allow_html=True
)