import streamlit as st
import requests
import os

# DEFINE API ENDPOINTS
FLASK_BACKEND_URL = "https://rag-k377.onrender.com/rag"
PDF_PROCESS_ENDPOINT = f"{FLASK_BACKEND_URL}/pdf/process"
CHAT_ENDPOINT = f"{FLASK_BACKEND_URL}/chat"


# Upload PDF Section
st.sidebar.title("Upload and Process Documents")
st.sidebar.subheader("Upload PDF")
uploaded_file = st.sidebar.file_uploader("Choose a PDF file", type=['pdf'])

st.title("RAG BASED LLM CHAT APPLICATION")

if uploaded_file is not None:
    st.sidebar.write(f"File {uploaded_file.name} uploaded successfully!")

    # Save the uploaded file to a temporary directory
    temp_file_path = os.path.join("temp_dir", uploaded_file.name)
    os.makedirs("temp_dir", exist_ok=True)

    with open(temp_file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())

    # Call the /pdf/process endpoint to process the uploaded file
    with st.spinner("Processing the PDF..."):
        files = {'file': (uploaded_file.name, open(temp_file_path, 'rb'))}
        response = requests.post(PDF_PROCESS_ENDPOINT, files=files)

        if response.status_code == 200:
            st.sidebar.success("PDF processed successfully!")
            result = response.json()
            st.sidebar.write(f"File URL: {result['s3_url']}")
        else:
            st.sidebar.error("Failed to process the PDF.")
            st.sidebar.write(response.json())

# Chat Interface
st.header("Chat with LLM")
user_input = st.text_input("Enter your message:")

if st.button("Send"):
    if user_input:
        with st.spinner("Generating response..."):
            payload = {
                "messages": [{"role": "user", "content": user_input}]
            }
            response = requests.post(CHAT_ENDPOINT, json=payload)

            if response.status_code == 200:
                chat_result = response.json()
                st.write("**LLM Response:**")
                st.write(chat_result.get("answer", "No response generated"))

                st.write("**Sources:**")
                for source in chat_result.get("sources", []):
                    st.write(f"- {source}")
            else:
                st.error("Failed to get response from the LLM.")
                st.write(response.json())
    else:
        st.warning("Please enter a message before sending.")

footer = """
    <style>
    .footer {
        position: fixed;
        left: 0;
        bottom: 0;
        width: 100%;
        color: white;
        text-align: center;
        padding: 10px;
    }
    </style>
    <div class="footer">
        <p>Made with 🤍 and ☕</p>
    </div>
"""
st.markdown(footer, unsafe_allow_html=True)