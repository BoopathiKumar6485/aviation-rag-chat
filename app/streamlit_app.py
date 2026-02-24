import streamlit as st
import requests
import json

# Page config
st.set_page_config(
    page_title="Aviation RAG Chat",
    page_icon="✈️",
    layout="wide"
)

# Title
st.title("✈️ Aviation Document Assistant")
st.markdown("Ask questions from your aviation PDFs!")

# API URL
API_URL = "http://localhost:8000"

# Check API health
@st.cache_data(ttl=10)
def check_health():
    try:
        response = requests.get(f"{API_URL}/health")
        return response.json()
    except:
        return None

# Sidebar
with st.sidebar:
    st.header("ℹ️ About")
    st.info(
        "This assistant answers questions based on aviation documents "
        "(PPL/CPL/ATPL textbooks, manuals, etc.)"
    )
    
    # Health check
    health = check_health()
    if health:
        st.success(f"✅ API Connected")
        st.caption(f"📚 {health.get('chunks_count', 0)} chunks loaded")
    else:
        st.error("❌ API Not Connected")
        st.caption("Make sure API is running: `uvicorn app.main:app --reload`")
    
    st.divider()
    
    # Debug mode toggle
    debug_mode = st.checkbox("🔍 Debug Mode", value=False)
    st.caption("Shows retrieved chunks")

# Main chat interface
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if "citations" in message and message["citations"]:
            with st.expander("📚 Sources"):
                for cit in message["citations"]:
                    st.caption(f"📄 {cit['document']} (Page {cit['page']})")

# Chat input
if prompt := st.chat_input("Ask a question about aviation..."):
    # Add user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Get response from API
    with st.chat_message("assistant"):
        with st.spinner("Searching documents..."):
            try:
                response = requests.post(
                    f"{API_URL}/ask",
                    json={"text": prompt, "debug": debug_mode}
                )
                
                if response.status_code == 200:
                    data = response.json()
                    
                    # Show answer
                    st.markdown(data["answer"])
                    
                    # Show citations
                    if data.get("citations"):
                        with st.expander("📚 Sources"):
                            for cit in data["citations"]:
                                st.caption(f"📄 **{cit['document']}** (Page {cit['page']})")
                                st.caption(f"💬 {cit['text'][:200]}...")
                    
                    # Show retrieved chunks in debug mode
                    if debug_mode and data.get("retrieved_chunks"):
                        with st.expander("🔍 Retrieved Chunks"):
                            for i, chunk in enumerate(data["retrieved_chunks"]):
                                st.caption(f"**Chunk {i+1}** (Score: {chunk['score']:.2f})")
                                st.caption(f"📄 {chunk['document']} (Page {chunk['page']})")
                                st.caption(f"💬 {chunk['text']}")
                                st.divider()
                    
                    # Save to session
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": data["answer"],
                        "citations": data.get("citations", [])
                    })
                else:
                    st.error(f"Error: {response.status_code}")
            except Exception as e:
                st.error(f"Connection Error: {e}")
                st.info("Make sure API is running: `uvicorn app.main:app --reload`")

# Footer
st.divider()
st.caption("🔍 Answers are based only on provided aviation documents")