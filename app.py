import streamlit as st
from typing import Generator
from groq import Groq
import re
import os
from dotenv import load_dotenv
load_dotenv()
st.set_page_config(page_icon="💬", layout="wide", page_title="DeepSeek_ChatBoat")

def parse_reasoning(raw_text: str):
    """Extracts and removes <think> block content from the response."""
    reasoning_parts = re.findall(r"<think>(.*?)</think>", raw_text, flags=re.DOTALL)
    reasoning_text = "\n".join(reasoning_parts)
    cleaned_answer = re.sub(r"<think>.*?</think>", "", raw_text, flags=re.DOTALL)
    return cleaned_answer.strip(), reasoning_text.strip()

 
st.subheader("ChatBoat", divider="rainbow", anchor=False)
api_key = os.getenv("GROQ_API_KEY")
client = Groq(api_key=api_key)

# Initialize chat history and selected model
if "messages" not in st.session_state:
    st.session_state.messages = []

if "selected_model" not in st.session_state:
    st.session_state.selected_model = None




# CSS to hide the footer and GitHub logo
hide_streamlit_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            </style>
            """
st.markdown(hide_streamlit_style, unsafe_allow_html=True)


# Define model details
models = {
    "deepseek-r1-distill-llama-70b": {"name": "deep seek", "developer": "DeepSeek"}
}

# Layout for model selection and max_tokens slider
col1, col2 = st.columns(2)

with col1:
    model_option = list(models.keys())[0]  

# Detect model change and clear chat history if model has changed
if st.session_state.selected_model != model_option:
    st.session_state.messages = []
    st.session_state.selected_model = model_option

max_tokens_range = 10000

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    avatar = '🤖' if message["role"] == "assistant" else '👨‍💻'
    with st.chat_message(message["role"], avatar=avatar):
        st.markdown(message["content"])

def generate_chat_responses(chat_completion) -> str:
    """Concatenate chat response content from the Groq API response."""
    content = ""
    for chunk in chat_completion:
        if chunk.choices[0].delta.content:
            content += chunk.choices[0].delta.content
    return content

if prompt := st.chat_input("Enter your prompt here..."):
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("user", avatar='👨‍💻'):
        st.markdown(prompt)

    # Fetch response from Groq API
    try:
        chat_completion = client.chat.completions.create(
            model=model_option,
            messages=[
                {"role": m["role"], "content": m["content"]} for m in st.session_state.messages
            ],
            max_tokens=max_tokens_range,
            stream=True
        )

        # Generate the response
        response_content = generate_chat_responses(chat_completion)
        # cleaned_response, reasoning = parse_reasoning(response_content)

        # Display the cleaned response
        with st.chat_message("assistant", avatar="🤖"):
            st.write(response_content)

        # Append reasoning and full response to session_state.messages
        st.session_state.messages.append({"role": "assistant", "content": cleaned_response})

    except Exception as e:
        st.error(f"Error: {str(e)}", icon="🚨")
