import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters.character import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from langchain.memory import ConversationBufferMemory
from langchain.memory import ConversationBufferWindowMemory
from langchain.chains import ConversationalRetrievalChain
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.document_loaders import TextLoader
from langchain.document_loaders import DirectoryLoader
from config import custom_instruction

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)

# Load your API key
google_api_key = os.getenv("GOOGLE_API_KEY")

# Build Vector database
file_path = "./docs/docs.txt"
# dir_path = "./docs"
loader = TextLoader(file_path, encoding="utf-8")
docs = loader.load()

# Split document into chunks
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=500
)
doc_chunks = text_splitter.split_documents(docs)

# Embed the chunks and store them in a vector store
embeddings = HuggingFaceEmbeddings()
vectordb = FAISS.from_documents(doc_chunks, embeddings)

# Initialize Google Generative AI with custom instruction
llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", system_message=custom_instruction)
retriever = vectordb.as_retriever(search_kwargs={"k": 3})

memory = ConversationBufferWindowMemory(
    k=3,  # Keep only the last 5 interactions
    memory_key="chat_history",
    return_messages=True
)

chain = ConversationalRetrievalChain.from_llm(
    llm=llm, retriever=retriever, chain_type="stuff", memory=memory, verbose=True
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
