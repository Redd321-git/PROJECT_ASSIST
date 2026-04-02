# 🧠 Assistor - Personal AI Assistant with Memory , RAG & Tool calling

An AI orchestration system built using FastAPI, LLM orchestration, and vector memory (Weaviate). This project demonstrates a stateful, multi-step reasoning agent with memory consolidation, retrieval, and tool usage.

---

## 🚀 Features

- Multi-step reasoning loop (Planner → Execute → Evaluate)
- Memory system:
  - Episodic Memory
  - Semantic Memory
  - User Preferences
- RAG (Retrieval Augmented Generation) using Weaviate
- Tool execution framework
- Chat history tracking & summarization
- JWT-based authentication
- Modular and scalable architecture

---

## 🏗️ Architecture Overview

```
User → FastAPI → Assistor Agent
                      ↓
               State Manager
                      ↓
               Flow Manager
                      ↓
   LLM Interface | RAG Engine | Tools
```

---

## 🧩 Core Components

### Assistor (Main Agent)

- Controls the reasoning loop
- Executes multi-step decision-making
- Stops when final output is generated

> Defined in: `assistor.py`

### State Manager

- Maintains conversation state
- Tracks steps, summaries, and conversation count
- Handles memory consolidation

### Flow Manager

Executes each step of reasoning:

1. Builds LLM input
2. Calls LLM
3. Parses response
4. Executes tools and memory operations

### LLM Interface

- Connects to external/local LLM
- Handles response generation and summarization

> Defined in: `llm_interface.py`

### RAG Engine

- Retrieves relevant memory
- Stores new memory
- Integrates with Weaviate

> Defined in: `rag_engine.py`

---

## 🧠 Memory System

| Memory Type | Description |
|---|---|
| Episodic | Stores past interactions |
| Semantic | Stores knowledge |
| User Profile | Stores preferences |

---

## 🗄️ Database (PostgreSQL)

Main tables:

- `users`
- `user_active`
- `chats`
- `chat_summaries`
- `user_convo_count`
- `user_preference_blog`

> Defined in: `models.py`

---

## 🔐 Authentication

- JWT-based authentication
- Password hashing using bcrypt
- Session tracking

> Defined in: `security.py`

---

## 🌐 API Endpoints

### Authentication

| Method | Endpoint |
|---|---|
| POST | `/register` |
| POST | `/login` |
| GET | `/me` |

### Chat

| Method | Endpoint |
|---|---|
| POST | `/assist` |
| POST | `/create_new_chat` |
| POST | `/load_chat_ids` |
| POST | `/load_chat` |

### Session

| Method | Endpoint |
|---|---|
| POST | `/logout` |

> Defined in: `main.py`

---

## 🔄 Data Flow

1. User sends input
2. State is initialized
3. Agent loop starts:
   - LLM generates intent
   - Tools executed
   - Memory retrieved/stored
4. Final output generated
5. Chat stored and summarized

---

## ⚙️ Tech Stack

| Layer | Technology |
|---|---|
| Backend | FastAPI |
| Database | PostgreSQL |
| Vector DB | Weaviate |
| LLM Integration | External/local API |
| ORM | SQLAlchemy |
| Authentication | JWT + OAuth2 |
| HTTP Client | httpx |

---

## 🧪 Running the Project

### 1. Clone Repository

```bash
git clone <your-repo-url>
cd assistor
```

### 2. Setup Environment (`.env`)

```env
DB_USER=
DB_PASSWORD=
DB_HOST=
DB_PORT=
DB_NAME=

SECRET_KEY=
ALGORITHM=
ACCESS_TOKEN_EXPIRE_MINUTES=

LLM_REASONING_API_URL=

WEAVIATE_HOST=
WEAVIATE_PORT=
WEAVIATE_GRPC_PORT=

COHERE_API_KEY=
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Setup Database

```bash
python create_db.py
```

### 5. Run Server

```bash
uvicorn src.main:app --reload
```

---

## 🧠 Key Concepts Demonstrated

- Agentic AI systems
- Retrieval-Augmented Generation (RAG)
- Memory-based AI
- Multi-step reasoning
- Tool-augmented LLMs
- Stateful backend design

---

## 📌 Use Cases

- Personal AI assistant
- Knowledge retrieval system
- Conversational memory system
- Autonomous AI agents

---

## 🔮 Future Improvements

- Streaming responses
- Multi-agent architecture
- RL-based optimization
- Frontend dashboard
- Distributed workers

---

## 👨‍💻 Author

**A Ritesh Reddy**  
*Aspiring System Architect|Backend Engineer*
