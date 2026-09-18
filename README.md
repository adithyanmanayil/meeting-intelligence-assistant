# Meeting Intelligence & Follow-up Assistant

A lightweight **Meeting Intelligence & Follow-up Assistant** built as a technical evaluation project.

The application can:

* Ingest meeting transcripts
* Perform semantic search using RAG
* Answer questions using meeting context
* Provide source citations for retrieved information
* Detect follow-up email requests
* Generate follow-up emails from meeting information
* Ask for clarification when a request is ambiguous
* Use an MCP email tool for sending follow-up emails
* Run locally without requiring a paid cloud AI API

## Architecture

```text
                    ┌─────────────────────┐
                    │       CLI           │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │   Meeting Agent     │
                    │  Intent / Routing   │
                    └──────────┬──────────┘
                               │
                ┌──────────────┼──────────────┐
                │              │              │
                ▼              ▼              ▼
             Question        Email       Ambiguous
                │              │              │
                ▼              ▼              ▼
              RAG           RAG + MCP    Clarification
                │              │
                ▼              ▼
          Local LLM       Email Generator
                               │
                               ▼
                         MCP Email Tool
                               │
                               ▼
                              SMTP
```

## Technology Stack

* **Python 3**
* **Ollama** — local LLM inference
* **Llama 3.2** — local language model
* **Sentence Transformers** — text embeddings
* **FAISS** — vector similarity search
* **MCP Python SDK** — Model Context Protocol email tool
* **SMTP** — email delivery
* **pytest** — testing

## Project Structure

```text
meeting-intelligence/
├── README.md
├── requirements.txt
├── .env.example
├── .gitignore
│
├── data/
│   └── meetings/
│       ├── meeting_001.txt
│       ├── meeting_002.txt
│       └── meeting_003.txt
│
├── src/
│   ├── __init__.py
│   ├── main.py
│   ├── agent.py
│   ├── rag.py
│   ├── llm.py
│   ├── prompts.py
│   │
│   └── mcp_email/
│       ├── __init__.py
│       ├── server.py
│       └── client.py
│
├── tests/
│   ├── test_rag.py
│   └── test_agent.py
│
└── docs/
    └── architecture.md
```

## How It Works

### 1. Meeting Ingestion

Synthetic meeting transcripts are stored as text files under:

```text
data/meetings/
```

The RAG component reads the transcripts and splits them into searchable chunks.

### 2. Embeddings

Each transcript chunk is converted into a vector using:

```text
all-MiniLM-L6-v2
```

The vectors are stored in a FAISS index.

### 3. Retrieval

When a user asks a question, the question is embedded and compared against the meeting chunks.

The most relevant chunks are retrieved and passed to the local LLM.

### 4. Local LLM

Ollama runs the Llama 3.2 model locally.

The model receives only the retrieved meeting context and is instructed not to invent information.

Example:

```text
User:
What is the product launch date?

Assistant:
The product launch date is October 10, 2026.
[Source: meeting_001.txt]
```

### 5. Agent Routing

The application uses deterministic routing for predictable behavior.

```text
Question
   ↓
RAG
   ↓
Local LLM
```

For an email request:

```text
Email Request
   ↓
RAG
   ↓
Email Generation
   ↓
MCP Email Tool
   ↓
SMTP
```

For an unclear request:

```text
Ambiguous Request
   ↓
Ask User for Clarification
```

This avoids allowing the model to arbitrarily select tools and makes the application's behavior easier to test and demonstrate.

## Running the Application

### 1. Clone the repository

```bash
git clone <repository-url>
cd meeting-intelligence
```

### 2. Create a virtual environment

```bash
python -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Install Ollama

On Arch Linux:

```bash
sudo pacman -S ollama
```

Start the Ollama service:

```bash
sudo systemctl enable --now ollama
```

### 5. Download the local model

```bash
ollama pull llama3.2
```

No OpenAI API key is required.

### 6. Run the application

```bash
python -m src.main
```

## Example Queries

### Meeting Question

```text
What is the product launch date?
```

Expected response:

```text
The product launch date is October 10, 2026.
[Source: meeting_001.txt]
```

### Action Item

```text
Who is responsible for regression testing?
```

The assistant retrieves the relevant engineering meeting and identifies the responsible participant.

### Follow-up Email

```text
Send a follow-up email about the product launch meeting
```

The assistant:

1. Retrieves relevant meeting information
2. Generates a follow-up email
3. Presents the email for confirmation
4. Sends it through the MCP email tool
5. Uses SMTP for delivery

### Ambiguous Request

```text
Do something about the meeting
```

The assistant asks for clarification rather than guessing the user's intention.

## Environment Variables

Create a `.env` file when configuring email:

