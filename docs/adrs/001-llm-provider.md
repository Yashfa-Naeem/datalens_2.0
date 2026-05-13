# ADR 001 - LLM Provider Selection

## Context
DataLens requires an LLM for two features: natural language chat with data and executive summary generation. We needed a provider that supports tool-calling/function-calling, is fast, and is free or low cost.

## Options Considered
1. OpenAI GPT-4 - excellent quality but expensive and requires paid plan
2. Google Gemini - free with university subscription but less tool-calling documentation
3. Anthropic Claude - high quality but requires paid API access
4. Groq - free tier available, extremely fast inference, supports tool-calling

## Decision
We chose Groq with llama3-8b-8192 model.

## Trade-offs
- We gain: free API access, very fast response times, good tool-calling support
- We lose: slightly lower quality than GPT-4, smaller context window
- Groq is ideal for a student project with budget constraints and speed requirements
