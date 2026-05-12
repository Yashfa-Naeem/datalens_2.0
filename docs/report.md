## Maria's Contribution

### Features Built
- **ChatPanel.jsx** — LLM chat interface allowing users to ask natural 
language questions about the dataset. Connects to the backend `/api/chat` 
endpoint which uses Groq API with tool-calling to return data-grounded answers.

- **ExecutiveSummary.jsx** — AI-generated executive summary component. 
Users click "Generate Summary" and the app calls `/api/summary` which uses 
Groq to analyze the dataset and return business analyst style insights.

### Integration
Both components were integrated into Dashboard.jsx and styled to match 
the existing dark theme of the application.