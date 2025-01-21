import os
import asyncio
from typing import List
import streamlit as st
from streamlit_chat import message
from dotenv import load_dotenv
from supabase import create_client
from openai import AsyncOpenAI

from tiled_ai_expert import tiled_ai_expert, TiledAIDeps

# Load environment variables
load_dotenv()

# Initialize clients
openai_client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
supabase = create_client(
    os.getenv("SUPABASE_URL"),
    os.getenv("SUPABASE_SERVICE_KEY")
)

# Initialize dependencies
deps = TiledAIDeps(supabase=supabase, openai_client=openai_client)

# Set page config
st.set_page_config(
    page_title="Tiled AI Expert",
    page_icon="🗺️",
    layout="wide"
)

# Add custom CSS
st.markdown("""
<style>
.stChat {
    padding: 20px;
    border-radius: 10px;
    margin: 10px 0;
}
.user-message {
    background-color: #e6f3ff;
    text-align: right;
}
.assistant-message {
    background-color: #f0f0f0;
}
</style>
""", unsafe_allow_html=True)

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []

# Header
st.title("🗺️ Tiled AI Expert")
st.markdown("""
Welcome to the Tiled AI Expert! I can help you with:
- Map creation and editing
- Working with layers and tilesets
- Object placement and properties
- Export formats and game engine integration
- Automation and scripting
- Best practices and optimization

Ask me anything about Tiled!
""")

# Chat input
if prompt := st.chat_input("What would you like to know about Tiled?"):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # Get AI response
    with st.spinner("Thinking..."):
        result = asyncio.run(tiled_ai_expert.run(prompt, deps=deps))
        response = result.data
        
        # Add AI response to chat history
        st.session_state.messages.append({"role": "assistant", "content": response})

# Display chat history
for i, msg in enumerate(st.session_state.messages):
    if msg["role"] == "user":
        message(msg["content"], is_user=True, key=f"msg_{i}")
    else:
        message(msg["content"], is_user=False, key=f"msg_{i}")

# Sidebar with additional information
with st.sidebar:
    st.header("About")
    st.markdown("""
    This AI expert is trained on Tiled's documentation and can help you with any questions about using Tiled map editor.
    
    **Features:**
    - Real-time answers from documentation
    - Technical guidance
    - Best practices
    - Integration help
    - Performance tips
    """)
    
    st.header("Resources")
    st.markdown("""
    - [Tiled Documentation](https://doc.mapeditor.org/)
    - [Tiled GitHub](https://github.com/mapeditor/tiled)
    - [Community Forum](https://discourse.mapeditor.org/)
    """)
    
    # Clear chat button
    if st.button("Clear Chat"):
        st.session_state.messages = []
        st.experimental_rerun()

    # Add debug expander
    with st.expander("🔧 Debug Info"):
        if st.button("Check Database"):
            with st.spinner("Checking database..."):
                db_info = asyncio.run(tiled_ai_expert.check_database_content.run(deps=deps))
                st.code(db_info)
