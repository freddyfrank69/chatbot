import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters.character import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationalRetrievalChain
from langchain_google_genai import ChatGoogleGenerativeAI

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)

# Load your API key
google_api_key = os.getenv("GOOGLE_API_KEY")

# Build Vector database
file_path = "./docs/PBL6.pdf"
loader = PyPDFLoader(file_path)
docs = loader.load()

# Split document into chunks
text_splitter = RecursiveCharacterTextSplitter(chunk_size=400, chunk_overlap=200)
doc_chunks = text_splitter.split_documents(docs)

# Embed the chunks and store them in a vector store
embeddings = HuggingFaceEmbeddings()
vectordb = FAISS.from_documents(doc_chunks, embeddings)

# Initialize Google Generative AI
llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash")
retriever = vectordb.as_retriever(search_kwargs={"k": 2})

memory = ConversationBufferMemory(
    llm=llm, output_key="answer", memory_key="chat_history", return_messages=True
)

chain = ConversationalRetrievalChain.from_llm(
    llm=llm, retriever=retriever, chain_type="map_reduce", memory=memory, verbose=True
)

@app.route("/chat", methods=["POST"])
def chat():
    user_input = request.json.get("message")
    if not user_input:
        return jsonify({"error": "No message provided"}), 400
    
    response = chain({"question": user_input, "chat_history": memory.chat_memory.messages})
    assistant_response = response["answer"]
    return jsonify({"response": assistant_response})

if __name__ == "__main__":
    app.run(debug=False)