import streamlit as st
from openai import OpenAI

# 1. Page Configuration
st.set_page_config(page_title="OpenRouter Chatbot", page_icon="🤖", layout="centered")
st.title("🤖 OpenRouter Multi-Model Chat")
TARGET_MODEL = "nvidia/nemotron-3-nano-30b-a3b:free"

if "OPENROUTER_API_KEY" in st.secrets:
    api_key = st.secrets["OPENROUTER_API_KEY"]
else:
    st.error("Missing API Key! Please configure 'OPENROUTER_API_KEY' in your Streamlit Secrets.")
    st.stop()
   
# Maintain conversational session state history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Output structural chat bubbles across app reruns
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# User prompt loop
if prompt := st.chat_input("Ask Nemotron anything..."):
    # Render user chat instantly
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Dynamic target stream zone
    with st.chat_message("assistant"):
        response_placeholder = st.empty()
        full_response = ""
        
        try:
            stream = client.chat.completions.create(
                model=TARGET_MODEL,
                messages=[
                    {"role": m["role"], "content": m["content"]}
                    for m in st.session_state.messages
                ],
                stream=True,
            )
            
            for chunk in stream:
                if chunk.choices[0].delta.content is not None:
                    full_response += chunk.choices[0].delta.content
                    response_placeholder.markdown(full_response + "▌")
            
            response_placeholder.markdown(full_response)
            st.session_state.messages.append({"role": "assistant", "content": full_response})
            
        except Exception as e:
            st.error(f"Inference pipeline encountered an error: {e}")
