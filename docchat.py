import streamlit as st
from llama_index import VectorStoreIndex, ServiceContext, Document
from llama_index.llms import OpenAI
import openai
from llama_index import SimpleDirectoryReader

st.set_page_config(page_title="Chat with the Streamlit docs, powered by LlamaIndex", page_icon="🦙", layout="centered", initial_sidebar_state="auto", menu_items=None)
openai.api_key = st.secrets.openai_key
st.title("Chat with the PDF docs")
      
if "messages" not in st.session_state.keys(): # Initialize the chat messages history
    st.session_state.messages = [
        {"role": "assistant", "content": "Ask me a question from the above documents!"}]
st.write(" 1. MAS FINANCIAL ADVISERS ACT 2001\n")
st.write(" 2. FINANCIAL ADVISERS REGULATIONS\n")
st.write(" 3. INSURANCE (INTERMEDIARIES) REGULATIONS\n")
st.write(" 4. FINANCIAL ADVISERS (COMPLAINTS HANDLING AND RESOLUTION) REGULATIONS 2021\n")

@st.cache_resource(show_spinner=False)
def load_data():
    with st.spinner(text="Loading and indexing the PDF docs – hang tight! This should take 1-2 minutes."):
        reader = SimpleDirectoryReader(input_dir="./data", recursive=True)
        docs = reader.load_data()
        service_context = ServiceContext.from_defaults(llm=OpenAI(model="gpt-4", temperature=0.1, system_prompt="Provide the file name only. You are an expert on the MAS documents and your job is to answer technical questions. Assume that all questions are related to the MAS documents. Provide the file name only. Keep your answers technical and based on facts – do not hallucinate features.Always quote the file name from which you retrieved the answer."))
        index = VectorStoreIndex.from_documents(docs, service_context=service_context)
        return index

index = load_data()
#chat_engine = index.as_chat_engine(chat_mode="condense_question", verbose=True, system_prompt="You are an expert on the Streamlit Python library and your job is to answer technical questions. Assume that all questions are related to the Streamlit Python library. Keep your answers technical and based on facts – do not hallucinate features.")
chat_engine = index.as_chat_engine(chat_mode="condense_question", verbose=True)

if prompt := st.chat_input("Your question"): # Prompt for user input and save to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})

for message in st.session_state.messages: # Display the prior chat messages
    with st.chat_message(message["role"]):
        st.write(message["content"])

# If last message is not from assistant, generate a new response
if st.session_state.messages[-1]["role"] != "assistant":
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            response = chat_engine.chat(prompt)
            st.write(response.response)
            
            message = {"role": "assistant", "content": response.response}
            st.session_state.messages.append(message) # Add response to message history
