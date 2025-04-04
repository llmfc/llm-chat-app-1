# llm-chat-app-1

## About
This code was generated by [CodeCraftAI](https://codecraft.name)

**User requests:**
I want you to create me ChatGPT-like application. There's a prompt and user can talk to backend. User can choose between various LLMs (such as Gemini, OpenAI models, Claude, Llama - every model that exists). Once user's prompt is sent to backend, backend should pass that prompt to model and stream response back to user. Make sure to contain context (if user asks about topic X, backend responds, user probably wants to continue talking about same thing). Also, enable user to start new chat (clear context). For communication user python-openai package and focus on OpenAI compatible models.

I want clear design with chat in focus, you can keep user's requests and responses it receives in browser's local storage. Also, emphasize to user the privacy is first, there's no KYC and that it's FREE.

Make sure to include deployment files as well.

Style it a bit! I want nice CSS, to be almost exactly like ChatGPT. I know you're an artist, do something :D
Also let customer select exact models: GPT 3.5, GPT 4.0, O1, LLama, Mistral, Gemini Flash 2.0, Gemini Pro 1.5 ...
- I like red color

Check OUTPUT.md for the complete unaltered output.

## Project Plan
```


**Clarified Request:** Build a web application mimicking ChatGPT, featuring a React frontend and Python/FastAPI backend.

**Key Requirements:**

*   **Frontend (React):** Chat interface, displays user/LLM messages, model selection dropdown (GPT-3.5 Turbo, GPT-4, GPT-4o, Llama models via compatible API, Mistral models via compatible API, Gemini models via compatible API), "New Chat" button, mimics ChatGPT CSS, stores chat history in Local Storage, emphasizes "Privacy First, No KYC, FREE".
*   **Backend (Python/FastAPI):** API endpoint receives prompt/model/context, uses `openai` library with OpenAI-compatible API endpoints, manages API keys/base URLs via environment variables, streams responses via Server-Sent Events (SSE), provides `/api/models` endpoint.
*   **LLM Handling:** Assume access to OpenAI-compatible APIs for all listed models (e.g., OpenAI, Groq, Mistral API, etc.). Backend routes requests based on model selection.
*   **Deployment:** Provide Dockerfiles (frontend/backend) and `docker-compose.yml`.

**Constraint:** The user running the application backend will bear the API costs for the selected LLMs.

**Project Plan: ChatGPT-Clone Web Application**

**Goal:** Develop a functional ChatGPT-like web application with a React frontend and Python/FastAPI backend, supporting multiple LLMs via compatible APIs, focusing on user privacy and free usage (API costs borne by the deployer).

**Phase 1: Backend Setup & Core API (FastAPI)**

1.  **Task:** Initialize FastAPI Project
    *   **Action:** Set up project structure (`backend/`), install dependencies (`requirements.txt`: FastAPI, Uvicorn, OpenAI, python-dotenv, sse-starlette).
    *   **Consideration:** Choose Python version (e.g., 3.11).
2.  **Task:** Implement Model Configuration & API Key Management
    *   **Action:** Define `MODELS_CONFIG` dictionary in `main.py`. Implement logic to load API keys and base URLs from environment variables (`.env` file) using `python-dotenv`. Create `.env.example`.
    *   **Consideration:** Securely handle API keys. Clearly document required environment variables.
3.  **Task:** Create Core Chat Streaming Endpoint (`/api/chat/stream`)
    *   **Action:** Define Pydantic models for request (`ChatRequest`, `Message`). Implement the endpoint using FastAPI. Use `sse-starlette` for Server-Sent Events (SSE).
    *   **Consideration:** Correctly handle SSE formatting (`data: ...\n\n`). Implement basic error handling for API calls.
4.  **Task:** Implement LLM Interaction Logic
    *   **Action:** Use the `openai` library's `AsyncOpenAI` client. Dynamically set `api_key` and `base_url` based on selected model from `MODELS_CONFIG`. Implement streaming request (`stream=True`).
    *   **Consideration:** Handle context management by passing the message history. Ensure proper `async/await` usage. Manage client instantiation/closing.
5.  **Task:** Create Models Endpoint (`/api/models`)
    *   **Action:** Implement an endpoint that returns the keys (user-facing names) from `MODELS_CONFIG`.
6.  **Task:** CORS Configuration & Basic Endpoints
    *   **Action:** Configure `CORSMiddleware` to allow requests from the frontend development server. Add basic `/` and `/health` endpoints.
7.  **Task:** Backend Dockerization
    *   **Action:** Create `backend/Dockerfile` to containerize the FastAPI application.

**Phase 2: Frontend Development (React)**

1.  **Task:** Initialize React Project (Vite)
    *   **Action:** Set up project structure (`frontend/`) using Vite with the React template. Install necessary dependencies.
    *   **Consideration:** Choose Node.js version. Set up basic project structure (`src/`, `components/`).
2.  **Task:** Build UI Components
    *   **Action:** Create components: `ChatMessage.jsx` (display user/assistant messages), `ChatInput.jsx` (textarea, submit button), `ModelSelector.jsx` (dropdown).
    *   **Consideration:** Plan component props and state management (e.g., using `useState`, `useEffect`).
3.  **Task:** Implement Core App Layout (`App.jsx`)
    *   **Action:** Assemble components into the main layout. Add header with title and privacy notices. Add a main chat window area and the input area.
    *   **Consideration:** Use CSS for layout (Flexbox/Grid).
4.  **Task:** Implement Chat State Management
    *   **Action:** Manage conversation history (array of message objects) in `App.jsx` state. Implement "New Chat" functionality (clearing history).
    *   **Consideration:** Decide on message object structure (`{ role: 'user'/'assistant', content: '...' }`).
5.  **Task:** Implement API Communication & Streaming
    *   **Action:** Fetch available models from `/api/models` on load. Handle form submission: send prompt, selected model, and history to `/api/chat/stream`. Use `EventSource` API to receive SSE stream. Update chat history with streamed response chunks.
    *   **Consideration:** Handle loading state while waiting for response. Manage `EventSource` connection/closing. Parse SSE data. Display errors received from the backend.
6.  **Task:** Implement Local Storage Persistence
    *   **Action:** Use `useEffect` to load chat history from Local Storage on mount and save it whenever it changes.
    *   **Consideration:** Handle potential Local Storage errors. Choose a suitable key name.
7.  **Task:** Styling (CSS)
    *   **Action:** Apply CSS (`index.css` or component-specific CSS) to mimic ChatGPT's appearance (colors, fonts, layout, message bubbles).
    *   **Consideration:** Aim for responsiveness. Use CSS variables for theming (optional).
8.  **Task:** Frontend Dockerization
    *   **Action:** Create `frontend/Dockerfile` (multi-stage build recommended) to build and serve the static React app (e.g., using Nginx or a static server).

**Phase 3: Integration & Deployment**

1.  **Task:** Docker Compose Setup
    *   **Action:** Create `docker-compose.yml` to define and run frontend and backend services together for local development/testing. Configure ports and environment variable loading from the `.env` file.
    *   **Consideration:** Ensure services can communicate (network configuration). Map necessary ports.
2.  **Task:** Testing & Refinement
    *   **Action:** Test end-to-end functionality: model selection, chat streaming, context, new chat, persistence, error handling across different models. Refine UI/UX based on testing.
    *   **Consideration:** Test with actual API keys for configured models. Check browser compatibility.
3.  **Task:** Documentation
    *   **Action:** Create `README.md` with setup instructions, required environment variables (`.env.example`), how to run using Docker Compose, and notes on API key costs.

**Technical Considerations & Reminders:**

*   **API Costs:** Emphasize in `README.md` that deploying this backend incurs API costs based on the selected LLM and usage. The "FREE" aspect applies only to the *end-user* interacting with the deployed application.
*   **Error Handling:** Implement robust error handling on both frontend (displaying errors to user) and backend (logging errors, sending informative error messages via SSE).
*   **API Compatibility:** Verify that the chosen third-party API endpoints are indeed compatible with the OpenAI library's chat completion structure and streaming format. Adjust backend logic if necessary.
*   **Security:** Do not commit API keys directly into code. Use environment variables exclusively. Ensure backend CORS is configured correctly for security.
*   **Scalability:** This initial setup is suitable for single-user or low-traffic scenarios. Scaling requires further infrastructure (e.g., load balancing, managed database instead of local storage, potentially WebSocket for more complex state).
*   **Environment Variables:** Ensure all necessary API keys and Base URLs (e.g., `OPENAI_API_KEY`, `GROQ_API_KEY`, `GROQ_BASE_URL`, `MISTRAL_API_KEY`, `MISTRAL_BASE_URL`) are defined in the `.env` file for local development and set in the deployment environment.
```
