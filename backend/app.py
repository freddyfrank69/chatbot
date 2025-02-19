import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
from langchain_community.document_loaders import TextLoader, PyPDFLoader, CSVLoader, UnstructuredMarkdownLoader, Docx2txtLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from langchain.memory import ConversationBufferWindowMemory
from langchain.chains import ConversationalRetrievalChain
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from config import custom_instruction

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)

# Define the folder containing documents
docs_folder = "./docs"
documents = []

# Loop through all files and load documents based on file type
for file_name in os.listdir(docs_folder):
    file_path = os.path.join(docs_folder, file_name)

    if file_name.endswith(".txt"):
        loader = TextLoader(file_path, encoding="utf-8")
    elif file_name.endswith(".md"):
        loader = UnstructuredMarkdownLoader(file_path)
    elif file_name.endswith(".pdf"):
        loader = PyPDFLoader(file_path)
    elif file_name.endswith(".csv"):
        loader = CSVLoader(file_path)
    elif file_name.endswith(".docx"):
        loader = Docx2txtLoader(file_path)
    else:
        continue  # Skip unsupported file types

    documents.extend(loader.load())

# Split documents into chunks
text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=500)
doc_chunks = text_splitter.split_documents(documents)

# Embed the chunks and store in FAISS vector store
embeddings = HuggingFaceEmbeddings()
vectordb = FAISS.from_documents(doc_chunks, embeddings)

# Initialize local LLM (Ollama)
llm = ChatOpenAI(
    model="llama3.2",  # Change model as needed for Ollama
    base_url="http://localhost:11434/v1",
    api_key="ollama"  # Required but unused
)

retriever = vectordb.as_retriever(search_kwargs={"k": 3})

memory = ConversationBufferWindowMemory(
    k=3,
    memory_key="chat_history",
    return_messages=True
)

prompt_template = PromptTemplate(
    input_variables=["chat_history", "question", "context"],
    template=f"{custom_instruction}\n\nChat History:\n{{chat_history}}\n\nContext:\n{{context}}\n\nQuestion:\n{{question}}\n\nAnswer:"
)

chain = ConversationalRetrievalChain.from_llm(
    llm=llm, 
    retriever=retriever, 
    chain_type="stuff", 
    memory=memory, 
    verbose=True,
    combine_docs_chain_kwargs={"prompt": prompt_template}
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