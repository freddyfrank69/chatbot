# Set-up dependencies and API key
import os
from dotenv import load_dotenv

print("Setting up dependencies and loading environment variables...")

# Load environment variables from .env file
load_dotenv()

# Access the API key
google_api_key = os.getenv("GOOGLE_API_KEY")
print("Environment variables loaded. Google API key retrieved.")


# Build Vector database
from langchain_community.document_loaders import DirectoryLoader, PyPDFLoader
from langchain_text_splitters.character import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings

print("Building vector database...")

# Load data from folder
file_path = "./docs/PBL6.pdf"
print(f"Loading document from: {file_path}")
loader = PyPDFLoader(file_path)
docs = loader.load()

# Print the first 200 characters of the document
#print("Document loaded. First 200 characters:")
#print(docs[0].page_content[:200])

# Split the document into chunks
print("Splitting document into chunks...")
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=400,
    chunk_overlap=200
)
doc_chunks = text_splitter.split_documents(docs)
print(f"Document split into {len(doc_chunks)} chunks.")

# Embed the chunks and store them in a vector store
print("Embedding chunks and storing in vector store...")
embeddings = HuggingFaceEmbeddings()
vectordb = FAISS.from_documents(doc_chunks, embeddings)
print("Vector store created.")

# Save the vector store
print("Saving vector store to disk...")
vectordb.save_local("index")
print("Vector store saved to 'index' directory.")

# Build chain
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationalRetrievalChain
from langchain_google_genai import ChatGoogleGenerativeAI

print("Building conversational retrieval chain...")

llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash")
print("Google Generative AI model loaded.")

retriever = vectordb.as_retriever(
    search_kwargs={
        "k": 2,  # number of results to return
    }
)
print("Retriever set up with vector store.")

memory = ConversationBufferMemory(
    llm=llm,
    output_key="answer",
    memory_key="chat_history",
    return_messages=True
)
print("Conversation buffer memory initialized.")

chain = ConversationalRetrievalChain.from_llm(
    llm=llm,
    retriever=retriever,
    chain_type="map_reduce",
    memory=memory,
    verbose=True
)
print("Conversational retrieval chain created.")

# Chat loop
print("Starting chat loop. Type 'exit' to end the session.")
memory.clear()
while True:
    user_input = input("user: ")
    if user_input.lower() == "exit":
        print("Exiting chat loop.")
        break

    print("Processing user input...")
    response = chain({"question": user_input, "chat_history": memory.chat_memory.messages})
    assistant_response = response["answer"]

    print("assistant: ", assistant_response)

# To view chat history
# print(memory.chat_memory.messages)