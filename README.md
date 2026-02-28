# AI Debate System

A multi-agent reasoning system that evaluates topics through structured debates, providing balanced and transparent conclusions.

![AI Debate System Dashboard](assets/hero_0.jpg)
![AI Debate System Reasoning](assets/hero_1.jpg)

## Architecture

- Backend: FastAPI, LangGraph, Google Gemini API
- Frontend: Next.js, NextUI
- Agents: 
  - Pro Agent: Highlights supporting arguments.
  - Con Agent: Presents opposing arguments.
  - Neutral Agent: Gathers objective facts.
  - Judge Agent: Synthesizes a final reasoned judgment.

## Requirements

- Python 3.11 or higher
- Node.js 18 or higher
- Google Gemini API Key

## Installation

### 1. Clone the Repository
```bash
git clone https://github.com/hoangvu1806/AgentDebate.git
cd AgentDebate
```

### 2. Backend Setup
Create a virtual environment:
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate
```

Install dependencies:
```bash
pip install -r requirements.txt
```

Set environment variables:
Create a `.env` file in the root directory and add the following configuration:
```env
GEMINI_API_KEY=your_gemini_api_key_here
MODEL_NAME=gemini-2.5-flash

LLM_TEMPERATURE=0.7
LLM_TOP_P=0.95
LLM_MAX_TOKENS=4096

DEBATE_MAX_ROUNDS=3
DEBATE_STREAMING=true
DEBATE_ENABLE_NEUTRAL=true
```

### 3. Frontend Setup
Navigate to the frontend folder and install dependencies:
```bash
cd frontend
npm install
```

## Running the Application

1. Start the backend:
```bash
python src/server.py
```

2. Start the frontend:
```bash
cd frontend
npm run dev
```

3. Open your browser and navigate to `http://localhost:3000`.
