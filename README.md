# RAG Chatbot

This project is a Retrieval-Augmented Generation (RAG) chatbot with a backend built in Python and a frontend developed using Next.js. The backend manages the data processing and retrieval using `chroma_db`, while the frontend provides a user-friendly interface.

## Features
- **Backend:** Python (Flask) with `chroma_db` for retrieval.
- **Frontend:** Next.js-based web interface.
- **Environment Configuration:** Uses `.env` for secure configuration.
- **Dependency Management:** Requirements and package dependencies handled via `requirements.txt` and `package.json`.

---

## Prerequisites
Ensure you have the following installed before proceeding:
- **Python 3.8+**
- **Node.js 16+**
- **Git**
- **pip** (Python package manager)
- **npm** (Node package manager)

## Installation & Setup

### 1. Clone the Repository
```sh
git clone https://github.com/hoangngxn/chatbot.git
cd rag-chatbot
```

### 2. Set Up the Backend
Navigate to the `backend` directory and create a virtual environment:
```sh
cd backend
```

Install dependencies:
```sh
pip install -r requirements.txt
```

Run the backend server:
```sh
python app.py
```

### 3. Set Up the Frontend
Navigate to the `frontend/rag-chatbot` directory:
```sh
cd ../frontend/rag-chatbot
```

Install dependencies:
```sh
npm install
```

Run the development server:
```sh
npm run dev
```

### 4. Access the Application
Once both servers are running:
- **Backend API:** `http://localhost:5000` (or configured port)
- **Frontend:** `http://localhost:3000`



---