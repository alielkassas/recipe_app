import streamlit as st
from openai import OpenAI

# 1. Page Configuration
st.set_page_config(page_title="OpenRouter Chatbot", page_icon="🤖", layout="centered")
st.title("🤖 OpenRouter Multi-Model Chat")

# 2. Sidebar Setup (API Key and Model Selection)
with st.sidebar:
    st.header("Configuration")
    
    # Securely input OpenRouter API Key
    api_key = st.text_input("Enter OpenRouter API Key:", type="password")
    if not api_key:
        st.warning("Please enter your API key to start chatting.")
        st.info("Get a key at [openrouter.ai](https://openrouter.ai/)")
    
    st.divider()
    
    # Let users pick popular OpenRouter models
    model_options = {
        "DeepSeek V3": "deepseek/deepseek-chat",
        "Meta Llama 3.3 70B": "meta-llama/llama-3.3-70b-instruct",
        "Google Gemini 2.5 Flash": "google/gemini-2.5-flash",
        "Anthropic Claude 3.5 Sonnet": "anthropic/claude-3.5-sonnet",
    }
    selected_model_label = st.selectbox("Choose a Model:", list(model_options.keys()))
    selected_model = model_options[selected_model_label]

# 3. Initialize OpenRouter/OpenAI Client & Session State
if api_key:
    # OpenRouter uses the OpenAI client but overrides the base URL
    client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=api_key,
        default_headers={
            "HTTP-Referer": "http://localhost:8501", # Required by OpenRouter for analytics rankings
            "X-Title": "Streamlit Chat App",         # Shows up in your OpenRouter analytics
        }
    )

# Maintain chat history across Streamlit reruns
if "messages" not in st.session_state:
    st.session_state.messages = []

# 4. Display Existing Chat History
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 5. Handle User Input & Stream Response
if prompt := st.chat_input("Type your message here..."):
    if not api_key:
        st.error("You need to enter an API key in the sidebar first!")
    else:
        # Display user message instantly
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Generate assistant response container
        with st.chat_message("assistant"):
            response_placeholder = st.empty()
            full_response = ""
            
            try:
                # Call OpenRouter API with streaming enabled
                stream = client.chat.completions.create(
                    model=selected_model,
                    messages=[
                        {"role": m["role"], "content": m["content"]}
                        for m in st.session_state.messages
                    ],
                    stream=True,
                )
                
                # Consume stream chunks in real-time
                for chunk in stream:
                    if chunk.choices[0].delta.content is not None:
                        full_response += chunk.choices[0].delta.content
                        response_placeholder.markdown(full_response + "▌")
                
                # Final clean render without cursor token
                response_placeholder.markdown(full_response)
                
                # Save assistant response to memory
                st.session_state.messages.append({"role": "assistant", "content": full_response})
                
            except Exception as e:
                st.error(f"An error occurred: {e}")
