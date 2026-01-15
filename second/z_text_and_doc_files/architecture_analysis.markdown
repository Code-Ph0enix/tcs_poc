## File Interoperability & Architecture

Here's how all your files work together in a layered architecture:

### **🏗️ Architecture Layers**

## 1. Core Infrastructure Layer
**Files:** `config.py`, `setup_chroma.py`

- `config.py` → Provides configuration to ALL files (API keys, paths, model names)[1]
- `setup_chroma.py` → Creates ChromaDB collections and embedding functions[2]
- **Relationship:** Setup runs once to initialize the database structure

## 2. Data Processing Layer
**Files:** `document_processor.py`, `index_icici_docs.py`

**Flow:**
```
.txt files → index_icici_docs.py → setup_chroma.py → ChromaDB
```

- `index_icici_docs.py` reads your corpus files[3]
- Uses `setup_chroma.py` to connect to ChromaDB[2]
- Chunks documents and stores embeddings[4]
- **Must run before agents can answer questions**

## 3. Retrieval Layer
**File:** `retriever.py`

- Connects to ChromaDB collections[5]
- Provides semantic search functionality
- Used by: `knowledge_agent.py`, `validate.py`

## 4. Utility Layer
**Files:** `cache_manager.py`, `memory_manager.py`, `observability.py`, `feedback_system.py`

These are **independent supporting systems** used by `supervisor_agent.py`:

- **cache_manager.py** → Prevents duplicate LLM calls[6]
- **memory_manager.py** → Maintains conversation context[7]
- **observability.py** → Logs performance metrics[8]
- **feedback_system.py** → Collects user ratings[9]

## 5. Agent Layer
**Files:** `knowledge_agent.py`, `marketing_agent.py`, `supervisor_agent.py`

**Knowledge Agent Flow:**
```
Query → retriever.py → ChromaDB → LLM (Groq) → Answer
```


**Marketing Agent Flow:**
```
Campaign params → LLM (Groq) → Generated content
```


**Supervisor Agent (Main Orchestrator):**
```
User Query 
  ↓
Check cache_manager (hit? return cached)
  ↓
Classify query (knowledge vs marketing)
  ↓
Route to → knowledge_agent OR marketing_agent
  ↓
Save to cache_manager
  ↓
Log to observability
  ↓
Store in memory_manager
  ↓
Return response
```


## 6. Testing Layer
**Files:** All `test_*.py` and `validate.py`

- `validate.py` → Tests retriever directly[10]
- `test_rag.py` → Tests knowledge_agent[11]
- `test_multi_agent.py` → Tests supervisor routing[12]
- `test_memory_cache.py` → Tests utility systems[13]
- `test_observability.py` → Tests monitoring[14]

### **🔄 Complete Data Flow**

**Initial Setup (Run Once):**
```
1. setup_chroma.py → Creates DB structure
2. index_icici_docs.py → Loads your documents into ChromaDB
3. validate.py → Verify indexing worked
```

**Runtime Flow (Every Query):**
```
User Query
    ↓
supervisor_agent.py
    ↓
[Check Cache] cache_manager.py ─── Cache Hit? → Return
    ↓ (Cache Miss)
[Classify Query] → Knowledge or Marketing?
    ↓                           ↓
knowledge_agent.py          marketing_agent.py
    ↓                           ↓
retriever.py                Groq LLM
    ↓
ChromaDB
    ↓
Groq LLM (combines docs + query)
    ↓
[Response Generated]
    ↓
cache_manager.py (save for next time)
    ↓
observability.py (log metrics)
    ↓
memory_manager.py (save to session)
    ↓
Return to user
    ↓
[Optional] feedback_system.py (collect rating)  
```

### **📦 Dependency Graph**

```
config.py ──────────────────┐
    ↓                       ↓
setup_chroma.py → index_icici_docs.py → ChromaDB
    ↓
retriever.py
    ↓
knowledge_agent.py ────┐
                       ↓
marketing_agent.py ────→ supervisor_agent.py ←── cache_manager.py
                              ↑                ←── memory_manager.py
                              ↑                ←── observability.py
                              ↑                ←── feedback_system.py
                              ↓
                         [All test files]
```

### **🎯 Key Interconnections**

**supervisor_agent.py is the central hub** that connects:
- Both agents (knowledge + marketing)[15]
- All 4 utility systems (cache, memory, logs, feedback)
- Groq LLM for classification
- Returns unified responses

**knowledge_agent.py is a RAG pipeline**:
1. Uses `retriever.py` for semantic search[16]
2. Formats retrieved docs as context
3. Sends to Groq LLM for generation

**All utility systems are independent**:
- They don't talk to each other
- Only `supervisor_agent.py` coordinates them
- Can be enabled/disabled with flags

The architecture follows a **clean separation of concerns** where each file has one specific job, making it easy to debug, test, and extend!