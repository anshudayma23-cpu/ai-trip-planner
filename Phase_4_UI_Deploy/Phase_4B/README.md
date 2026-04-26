# Wanderlust AI: Autonomous Swarm Trip Planner 🌍✈️

Wanderlust AI is a sophisticated multi-agent system built with LangGraph, FastAPI, and vanilla JavaScript. It orchestrates a "swarm" of specialized AI agents to plan, research, budget, and write beautiful, highly detailed travel itineraries based on natural language constraints.

## 🧠 Architecture Overview

The system runs on an asynchronous LangGraph workflow with 6 distinct agents:

1. **Orchestrator**: Parses natural language requests into structured constraints (Cities, Budget, Preferences).
2. **Researcher**: Uses the Tavily API to actively scrape the web for live, up-to-date travel information based on user preferences.
3. **Logistics**: Acts as the trip manager. Allocates nights, intercity transport, and splits days into morning/afternoon/evening blocks.
4. **Budget Auditor**: Calculates estimated costs and validates them against the user's hard budget.
5. **QA Reviewer**: A critic that audits the entire itinerary. If the trip is over budget, packed too tightly, or misses preferences, it sends it back for revision (Max 3 revisions).
6. **Synthesizer**: A premium travel writer agent that takes the final data and generates a beautiful markdown-formatted magazine-style itinerary.

## ⚡ Features

- **Live Streaming UI**: Watch the agents think and pass state in real-time via WebSockets.
- **Auto-Fallback LLM Engine**: Defaults to Google's ultra-fast `gemini-1.5-flash` with a massive free tier. If Gemini hits a rate limit or fails, it automatically fails over to Groq's `llama-3.3-70b-versatile` ensuring 100% uptime.
- **In-Memory Caching**: Identical queries return instantly from memory.
- **Premium Glassmorphism Design**: Fully responsive, dark-mode, animated frontend.

## 🚀 Getting Started

### Prerequisites
- Python 3.11+
- API Keys for Google (Gemini), Groq, and Tavily.

### 1. Installation

Clone the repository and install the requirements:

```bash
pip install -r requirements.txt
```

### 2. Environment Variables

Create a `.env` file in the root directory (you can copy `.env.example`):

```env
GOOGLE_API_KEY=your_gemini_key
GROQ_API_KEY=your_groq_key
TAVILY_API_KEY=your_tavily_key
```

### 3. Run Locally

Start the FastAPI server:

```bash
python -m src.api.main
```

Then open your browser to `http://localhost:8010`

### 4. Run with Docker

To containerize and run the app:

```bash
docker build -t wanderlust-ai .
docker run -p 8010:8010 wanderlust-ai
```

## 🛠️ Testing the System

Try inputting complex, highly constrained queries to watch the QA Review loop in action:

> "Plan a 14-day trip to Italy and France for $1,500. We want to stay in 5-star hotels and eat at Michelin star restaurants."

*(The Budget Agent will flag this as impossible, and the QA Reviewer will force the Logistics agent to revise the plan to suggest free activities and hostels instead!)*
