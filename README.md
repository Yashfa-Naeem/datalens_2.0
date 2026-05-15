# DataLens - Analytics Dashboard
DataLens is a web application that allows users to upload any CSV file and automatically generate an interactive analytics dashboard with AI-powered chat and executive summaries.
## Team Members
- Yashfa Naeem - Backend (FastAPI, SQLite, Data Profiling, API Endpoints)
- Friend 1 - Frontend (React, Recharts, Dashboard UI)
- Friend 2 - LLM Integration (Groq Chat, Executive Summary)
## Dataset
2015 US Flight Delays and Cancellations (5.8M rows)
## Prerequisites
- Python 3.11+
- Node 18+
- uv (Python package manager)
- npm
- Groq API key (free at console.groq.com)
## Setup Instructions
1. Clone the repository
git clone https://github.com/Yashfa-Naeem/datalens_2.0.git
cd datalens_2.0
2. Get a Groq API key
Go to https://console.groq.com, sign up free, create API key
3. Install backend dependencies
cd backend
uv install
4. Install frontend dependencies
cd frontend
npm install
## Running the App
Start backend (Terminal 1):
cd backend
set GROQ_API_KEY=your_key_here
uv run uvicorn app.main:app --reload --port 8000
Start frontend (Terminal 2):
cd frontend
npm run dev
Open http://localhost:5173 in your browser.
## Features
- Upload any CSV file up to 50MB
- Auto-generated charts based on data columns
- Global filters across all visualizations
- AI chat with your data in plain English
- Executive summary with AI generated insights
- Data persists in SQLite
## Running Tests
Backend: cd backend && uv run pytest
Frontend: cd frontend && npm run test
## Troubleshooting
- Backend wont start: Make sure GROQ_API_KEY is set
- Charts not showing: Make sure backend is running on port 8000
- CSV upload fails: File must be under 50MB and valid CSV
- Module not found: Run uv install in backend and npm install in frontend