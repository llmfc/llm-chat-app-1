**This file consists of the entire unaltered output for reference.**

 Okay, let's get this ChatGPT clone application fully operational!

Here is the complete, runnable code based on the plan, review, and corrections. Copy and paste these files into the specified project structure, fill in your `.env` file, and run `docker-compose up --build`.

**Project Structure:**

```
chatgpt-clone/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py
│   │   └── models.py
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/
│   ├── public/
│   │   └── vite.svg      # (Default Vite asset)
│   ├── src/
│   │   ├── components/
│   │   │   ├── ChatInput.jsx
│   │   │   ├── ChatMessage.jsx
│   │   │   └── ModelSelector.jsx
│   │   ├── App.jsx
│   │   ├── index.css
│   │   └── main.jsx
│   ├── Dockerfile
│   ├── index.html
│   ├── package.json
│   └── vite.config.js
├── .env.example
├── docker-compose.yml
└── README.md
```

---

**1. Root: `.env.example`**

*   **File Path:** `chatgpt-clone/.env.example`
*   **Action:** Create this file. **Rename it to `.env` and fill in your actual API keys.**

```env
# Rename this file to .env and fill in your API keys and base URLs

# --- OpenAI ---
OPENAI_API_KEY="sk-..."
# OPENAI_BASE_URL="https://api.openai.com/v1" # Optional: Defaults to OpenAI if not set

# --- Groq ---
# Needed for llama3-*-groq models
GROQ_API_KEY="gsk_..."
GROQ_BASE_URL="https://api.groq.com/openai/v1"

# --- Mistral AI ---
# Needed for mistral-* models
MISTRAL_API_KEY="YOUR_MISTRAL_API_KEY"
MISTRAL_BASE_URL="https://api.mistral.ai/v1"

# --- Google Gemini (via compatible endpoint like Together AI or Cloudflare AI Gateway) ---
# Example using Together AI as a compatible endpoint:
# GEMINI_API_KEY="YOUR_TOGETHER_AI_KEY"
# GEMINI_BASE_URL="https://api.together.xyz/v1" # Or your chosen compatible endpoint

# --- Other Llama models (via compatible endpoint like Fireworks etc.) ---
# Example using Fireworks AI:
# FIREWORKS_API_KEY="YOUR_FIREWORKS_API_KEY"
# FIREWORKS_BASE_URL="https://api.fireworks.ai/inference/v1"

# --- Backend Root Path (Optional) ---
# Use if deploying the backend behind a reverse proxy that adds a path prefix (e.g., /api)
# The default is '/api' matching the FastAPI app setup. Set to '/' if no prefix is used.
# ROOT_PATH=/api

# --- Frontend API URL ---
# IMPORTANT: This tells the *frontend* where to find the *backend* API.
# Must be accessible from the user's browser OR from the frontend container (if SSR/proxying).
# Default for local docker-compose setup where browser accesses backend exposed on host port 8000.
VITE_API_BASE_URL=http://localhost:8000/api

# --- Frontend URL (for Backend CORS) ---
# IMPORTANT: This tells the *backend* which frontend origin(s) are allowed to make requests.
# Set this to the URL where your frontend is served from.
# Default for local Vite dev server OR the docker-compose setup (frontend exposed on port 5173).
FRONTEND_URL=http://localhost:5173

# --- Additional CORS Origins (Optional) ---
# Comma-separated list of other frontend URLs allowed to access the backend.
# Example: ADDITIONAL_CORS_ORIGINS=https://my-deployed-frontend.com,https://another-domain.com
# ADDITIONAL_CORS_ORIGINS=
```

---

**2. Root: `docker-compose.yml`**

*   **File Path:** `chatgpt-clone/docker-compose.yml`
*   **Action:** Create this file. It orchestrates the backend and frontend services.

```yaml
version: '3.8'

services:
  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    container_name: chatgpt-clone-backend
    env_file:
      - .env # Load environment variables from .env file in the root
    # Use environment section to override or provide defaults if needed
    # environment:
    #   - ROOT_PATH=/api # Ensure ROOT_PATH matches FastAPI app and Dockerfile CMD
    volumes:
      # Mount backend code for development with hot-reloading (optional)
      # Note: Ensure the CMD in backend/Dockerfile uses '--reload'
      - ./backend/app:/app/app
      # Mount the root .env file directly into the container (alternative to env_file)
      # - ./.env:/.env # If backend/main.py loads from /.env instead of ../../.env
    ports:
      - "8000:8000" # Map host port 8000 to container port 8000
    networks:
      - chat-network
    # command: ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload", "--root-path", "/api"] # Development CMD override

  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    container_name: chatgpt-clone-frontend
    # Pass the API base URL as a build argument AND an environment variable
    # Build arg is used by Vite during build time (import.meta.env)
    # Env var is used by serve at runtime (if needed, or for entrypoint scripts)
    build:
      context: ./frontend
      args:
        VITE_API_BASE_URL: ${VITE_API_BASE_URL:-http://localhost:8000/api} # Default if not set in .env
    environment:
      # Ensure the variable is available at runtime if the container needs it (e.g., entrypoint script)
      # The 'serve' command doesn't directly use this, but good practice.
      - VITE_API_BASE_URL=${VITE_API_BASE_URL:-http://localhost:8000/api}
      # Serve uses PORT env var to determine which port to listen on inside the container
      - PORT=80
    volumes:
      # Mount frontend code for development with hot-reloading (optional)
      # Requires running `npm run dev` inside the container or adjusting Dockerfile CMD
      # - ./frontend/src:/app/src
      # - ./frontend/public:/app/public
      - frontend_node_modules:/app/node_modules # Persist node_modules
    ports:
      - "5173:80" # Map host port 5173 to container port 80 (where 'serve' listens)
    depends_on:
      - backend # Optional: ensures backend starts before frontend attempts connection (useful for health checks)
    networks:
      - chat-network
    # command: ["npm", "run", "dev", "--", "--host"] # Development CMD override (listens on 0.0.0.0)

networks:
  chat-network:
    driver: bridge

volumes:
  frontend_node_modules: # Persist node_modules across container rebuilds (useful for dev)

```

---

**3. Root: `README.md`**

*   **File Path:** `chatgpt-clone/README.md`
*   **Action:** Create this file with setup and usage instructions.

```markdown
# ChatGPT Clone Application

This project implements a basic web application mimicking the functionality of ChatGPT, allowing users to interact with various large language models (LLMs) through a unified interface. It uses FastAPI for the backend and React (Vite) for the frontend, containerized with Docker.

## Features

*   Backend API (FastAPI) to handle requests and stream responses.
*   Support for multiple LLM providers (OpenAI, Groq, Mistral, potentially others via OpenAI-compatible endpoints).
*   Streaming responses using Server-Sent Events (SSE).
*   React frontend with a chat interface.
*   Model selection dropdown.
*   Conversation history stored in `localStorage`.
*   Containerized using Docker and Docker Compose for easy setup.

## Project Structure

```
chatgpt-clone/
├── backend/        # FastAPI backend service
│   ├── app/        # Application code
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/       # React frontend service
│   ├── public/
│   ├── src/        # Application code
│   ├── Dockerfile
│   ├── index.html
│   ├── package.json
│   └── vite.config.js
├── .env.example    # Example environment variables (RENAME TO .env)
├── docker-compose.yml # Docker orchestration
└── README.md       # This file
```

## Prerequisites

*   Docker and Docker Compose installed.
*   API keys for the desired LLM providers (OpenAI, Groq, Mistral, etc.).

## Setup & Running

1.  **Clone the Repository:**
    ```bash
    git clone <your-repo-url> chatgpt-clone
    cd chatgpt-clone
    ```

2.  **Configure Environment Variables:**
    *   Rename `.env.example` to `.env`.
    *   Open the `.env` file and fill in your API keys for the services you want to use (e.g., `OPENAI_API_KEY`, `GROQ_API_KEY`, `MISTRAL_API_KEY`).
    *   Verify `VITE_API_BASE_URL` is correct for your setup (default `http://localhost:8000/api` should work with Docker Compose).
    *   Verify `FRONTEND_URL` is correct for CORS (default `http://localhost:5173` should work with Docker Compose).

3.  **Build and Run Containers:**
    *   From the root `chatgpt-clone/` directory, run:
        ```bash
        docker-compose up --build
        ```
    *   The `--build` flag ensures images are built the first time or when Dockerfiles/code change. You can omit it for subsequent runs if only `.env` changes.
    *   Use `-d` to run in detached mode (background): `docker-compose up --build -d`

4.  **Access the Application:**
    *   Open your web browser and navigate to `http://localhost:5173` (or the port specified for the frontend in `docker-compose.yml`).

5.  **Stopping the Application:**
    *   If running in the foreground, press `Ctrl+C`.
    *   If running in detached mode, use:
        ```bash
        docker-compose down
        ```

## Development Notes

*   **Backend Hot Reloading:** To enable hot reloading for backend development, uncomment the `volumes` mount for `backend/app` in `docker-compose.yml` and ensure the `CMD` in `backend/Dockerfile` uses `--reload`.
*   **Frontend Hot Reloading:** For frontend hot reloading, uncomment the `volumes` mounts for `frontend/src` and `frontend/public` in `docker-compose.yml`, and uncomment/change the `command` in the `frontend` service definition to run `npm run dev`. Access will likely still be via `http://localhost:5173`.
*   **Accessing API Docs:** The backend API documentation (Swagger UI) is available at `http://localhost:8000/api/docs` when the backend container is running.

## Environment Variables (.env)

*   `OPENAI_API_KEY`, `GROQ_API_KEY`, `MISTRAL_API_KEY`, etc.: Your API keys for the respective services. Only models whose corresponding API keys are set will be available in the frontend dropdown.
*   `*_BASE_URL`: Optional base URLs if you need to use a proxy or a non-standard endpoint for a provider. Defaults are provided for major services.
*   `VITE_API_BASE_URL`: The full URL (including `/api` if applicable) that the **frontend** uses to contact the backend API.
*   `FRONTEND_URL`: The origin URL where the **frontend** is served from. Used by the backend for CORS configuration.
*   `ROOT_PATH`: (Backend) Set this if the backend is served behind a proxy that adds a prefix (e.g., `/api`). Default is `/api`.
*   `ADDITIONAL_CORS_ORIGINS`: (Backend) Comma-separated list of additional frontend origins allowed by CORS.

## Important Considerations

*   **Security:** Never commit your `.env` file with actual API keys to version control. Use `.gitignore`. Restrict CORS origins (`FRONTEND_URL`, `ADDITIONAL_CORS_ORIGINS`) in production environments.
*   **Error Handling:** The frontend includes basic error handling for API key issues and stream errors, displaying messages to the user. Backend logs provide more details.
*   **Scalability:** This setup is suitable for development and small-scale use. For production, consider more robust deployment strategies (e.g., Kubernetes, managed container services), database integration for chat history persistence, and proper security hardening.
```

---

**4. Backend: `backend/requirements.txt`**

*   **File Path:** `chatgpt-clone/backend/requirements.txt`
*   **Action:** Ensure this file exists with the correct content.

```txt
fastapi>=0.110.0,<0.111.0
uvicorn[standard]>=0.29.0,<0.30.0
openai>=1.14.3,<2.0.0
python-dotenv>=1.0.1,<2.0.0
sse-starlette>=1.8.2,<2.0.0
pydantic>=2.0.0,<3.0.0
```

---

**5. Backend: `backend/Dockerfile`**

*   **File Path:** `chatgpt-clone/backend/Dockerfile`
*   **Action:** Ensure this file exists with the correct content (including `--root-path`).

```dockerfile
# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /app

# Prevent Python from writing pyc files to disc (optional)
ENV PYTHONDONTWRITEBYTECODE 1
# Ensure Python output is sent straight to terminal (useful for logs)
ENV PYTHONUNBUFFERED 1

# Install system dependencies if needed (e.g., for certain libraries)
# RUN apt-get update && apt-get install -y --no-install-recommends some-package && rm -rf /var/lib/apt/lists/*

# Install pip requirements
COPY requirements.txt .
# Use --no-cache-dir to reduce layer size
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy the application code into the container
# This assumes your FastAPI app structure is inside an 'app' directory
COPY ./app /app/app

# Make port 8000 available to the world outside this container
EXPOSE 8000

# Define environment variable for the API root path, defaulting to /api
# This is used by the CMD directive below.
ENV ROOT_PATH=/api

# Run the application using Uvicorn.
# Use 0.0.0.0 to allow connections from outside the container.
# Use the ROOT_PATH environment variable for the --root-path argument.
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--root-path", "${ROOT_PATH}"]

# For development with hot-reloading (mount volume in docker-compose):
# CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload", "--root-path", "${ROOT_PATH}"]
```

---

**6. Backend: `backend/app/__init__.py`**

*   **File Path:** `chatgpt-clone/backend/app/__init__.py`
*   **Action:** Create this empty file.

```python
# This file makes Python treat the 'app' directory as a package.
```

---

**7. Backend: `backend/app/models.py`**

*   **File Path:** `chatgpt-clone/backend/app/models.py`
*   **Action:** Ensure this file exists with the correct content.

```python
from pydantic import BaseModel
from typing import List, Literal

class Message(BaseModel):
    role: Literal["user", "assistant", "system"]
    content: str

class ChatRequest(BaseModel):
    model: str
    messages: List[Message]
    # Optional fields can be added here (e.g., temperature, max_tokens)
    # Ensure they are handled in the main.py chat_stream endpoint if added.
    # temperature: Optional[float] = None
    # max_tokens: Optional[int] = None

```

---

**8. Backend: `backend/app/main.py`**

*   **File Path:** `chatgpt-clone/backend/app/main.py`
*   **Action:** Ensure this file exists with the finalized, corrected code.

```python
import os
import json
import logging
from typing import AsyncGenerator, Dict, Optional, List

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, RedirectResponse
from sse_starlette.sse import EventSourceResponse
from pydantic import BaseModel
import openai # Import the base library
from openai import AsyncOpenAI, APIError, OpenAIError # Import specific errors
from dotenv import load_dotenv

from .models import ChatRequest, Message # Import models from the same directory

# --- Configuration ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Load environment variables from .env file in the root directory
# Adjust the path if running the script directly outside docker-compose for testing
dotenv_path = os.path.join(os.path.dirname(__file__), '..', '..', '.env')
load_dotenv(dotenv_path=dotenv_path)
logger.info(f"Attempting to load .env file from: {dotenv_path}")

# --- Model Configuration ---
# Maps user-facing model names (keys) to their configuration details (values).
# 'api_key_env': Environment variable name for the API key.
# 'base_url_env': Environment variable name for the API base URL.
# 'default_base_url': Default API base URL if the env var is not set. Can be None.
# 'model_name': The actual model identifier expected by the specific API provider.
MODELS_CONFIG: Dict[str, Dict[str, Optional[str]]] = {
    "gpt-4o": {
        "api_key_env": "OPENAI_API_KEY",
        "base_url_env": "OPENAI_BASE_URL",
        "default_base_url": "https://api.openai.com/v1",
        "model_name": "gpt-4o"
    },
    "gpt-4-turbo": {
        "api_key_env": "OPENAI_API_KEY",
        "base_url_env": "OPENAI_BASE_URL",
        "default_base_url": "https://api.openai.com/v1",
        "model_name": "gpt-4-turbo"
    },
    "gpt-3.5-turbo": {
        "api_key_env": "OPENAI_API_KEY",
        "base_url_env": "OPENAI_BASE_URL",
        "default_base_url": "https://api.openai.com/v1",
        "model_name": "gpt-3.5-turbo"
    },
     "llama3-70b-groq": {
        "api_key_env": "GROQ_API_KEY",
        "base_url_env": "GROQ_BASE_URL",
        "default_base_url": "https://api.groq.com/openai/v1", # Required for Groq
        "model_name": "llama3-70b-8192" # Groq's specific model ID
    },
    "llama3-8b-groq": {
        "api_key_env": "GROQ_API_KEY",
        "base_url_env": "GROQ_BASE_URL",
        "default_base_url": "https://api.groq.com/openai/v1", # Required for Groq
        "model_name": "llama3-8b-8192" # Groq's specific model ID
    },
    "mistral-large": {
        "api_key_env": "MISTRAL_API_KEY",
        "base_url_env": "MISTRAL_BASE_URL",
        "default_base_url": "https://api.mistral.ai/v1", # Required for Mistral
        "model_name": "mistral-large-latest"
    },
    "mistral-small": {
        "api_key_env": "MISTRAL_API_KEY",
        "base_url_env": "MISTRAL_BASE_URL",
        "default_base_url": "https://api.mistral.ai/v1",
        "model_name": "mistral-small-latest"
     },
    # --- Examples for adding other models (ensure keys/URLs are in .env) ---
    # "gemini-pro-together": {
    #     "api_key_env": "GEMINI_API_KEY", # Define GEMINI_API_KEY in .env (e.g., your Together AI key)
    #     "base_url_env": "GEMINI_BASE_URL", # Define GEMINI_BASE_URL in .env (e.g., https://api.together.xyz/v1)
    #     "default_base_url": None, # Force setting via .env
    #     "model_name": "google/gemini-pro" # Model name on the compatible endpoint
    # },
    # "llama3-70b-fireworks": {
    #    "api_key_env": "FIREWORKS_API_KEY", # Define FIREWORKS_API_KEY in .env
    #    "base_url_env": "FIREWORKS_BASE_URL", # Define FIREWORKS_BASE_URL in .env
    #    "default_base_url": "https://api.fireworks.ai/inference/v1",
    #    "model_name": "accounts/fireworks/models/llama-v3-70b-instruct"
    #}
}

# --- Helper Function ---
def get_client_for_model(model_key: str) -> tuple[AsyncOpenAI, str]:
    """
    Retrieves the API configuration for the selected model key, validates required
    environment variables (API key, Base URL), and returns an initialized
    AsyncOpenAI client instance along with the actual model identifier string.

    Args:
        model_key: The user-facing key representing the model in MODELS_CONFIG.

    Returns:
        A tuple containing:
        - An initialized AsyncOpenAI client configured for the model.
        - The actual model identifier string to be used in the API call.

    Raises:
        HTTPException: If the model key is not configured, or if required
                       environment variables (API Key, Base URL) are missing.
    """
    if model_key not in MODELS_CONFIG:
        logger.error(f"Configuration requested for unknown model key: '{model_key}'")
        raise HTTPException(status_code=400, detail=f"Model '{model_key}' is not configured in the backend.")

    config = MODELS_CONFIG[model_key]
    api_key_env = config.get("api_key_env")
    base_url_env = config.get("base_url_env")
    default_base_url = config.get("default_base_url")
    # Use 'model_name' from config, fall back to model_key if not specified
    model_identifier = config.get("model_name") or model_key

    if not api_key_env:
         logger.error(f"Configuration error for '{model_key}': 'api_key_env' is not defined.")
         raise HTTPException(status_code=500, detail=f"Internal configuration error for model '{model_key}': API key environment variable name missing.")

    api_key = os.getenv(api_key_env)
    if not api_key:
        logger.error(f"API Key environment variable '{api_key_env}' not set for model '{model_key}'.")
        raise HTTPException(
            status_code=500,
            detail=f"API key for model '{model_key}' is not configured. Please set the '{api_key_env}' environment variable in the .env file."
        )

    # Determine the base URL: Use env var first, then default, then error if neither exists
    base_url = os.getenv(base_url_env) if base_url_env else None
    if not base_url:
        base_url = default_base_url

    if not base_url: # If still no base URL after checking env var and default
        logger.error(f"Base URL could not be determined for model '{model_key}'. Env var '{base_url_env}' not set and no 'default_base_url' configured.")
        raise HTTPException(
            status_code=500,
            detail=f"API endpoint URL for model '{model_key}' could not be determined. Set '{base_url_env}' in .env or check backend configuration."
        )

    logger.info(f"Configuring client for model '{model_identifier}' (Key: '{model_key}') using Base URL: '{base_url}'")
    try:
        # You can add default httpx client arguments here if needed, e.g., timeout
        # import httpx
        # http_client = httpx.AsyncClient(timeout=60.0)
        # client = AsyncOpenAI(api_key=api_key, base_url=base_url, http_client=http_client)
        client = AsyncOpenAI(api_key=api_key, base_url=base_url)
        return client, model_identifier
    except Exception as e:
        logger.error(f"Failed to initialize AsyncOpenAI client for {model_key}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to create API client for model '{model_key}'. Check configuration and logs.")


# --- FastAPI App Initialization ---
# Determine root path from environment variable, default to "/api"
# This allows running the API behind a reverse proxy at a specific path prefix
api_root_path = os.getenv("ROOT_PATH", "/api")
logger.info(f"Initializing FastAPI app with root_path: '{api_root_path}'")
app = FastAPI(
    title="ChatGPT Clone Backend API",
    version="1.0.0",
    description="API for interacting with various LLMs via a unified interface.",
    root_path=api_root_path
)

# --- CORS Middleware Setup ---
default_frontend_url = "http://localhost:5173" # Default for local dev/docker-compose
frontend_url = os.getenv("FRONTEND_URL", default_frontend_url)

origins = [frontend_url]
if "localhost" in frontend_url or "127.0.0.1" in frontend_url:
    # Automatically add the loopback address if using localhost for dev convenience
    origins.append("http://127.0.0.1:5173") # Common loopback

# Add additional origins from environment variable if provided (comma-separated)
additional_origins = os.getenv("ADDITIONAL_CORS_ORIGINS")
if additional_origins:
    origins.extend([origin.strip() for origin in additional_origins.split(",") if origin.strip()])

# Remove duplicates just in case
origins = list(set(origins))

logger.info(f"Configuring CORS. Allowed Origins: {origins}")

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True, # Allow cookies/auth headers if needed
    allow_methods=["*"],    # Allow all standard methods (GET, POST, etc.)
    allow_headers=["*"],    # Allow all headers
)

# --- API Endpoints ---

# Redirect the application root ("/") to the API documentation ("{root_path}/docs")
@app.get("/", tags=["General"], include_in_schema=False)
async def root_redirect_to_docs():
    """Redirects the root path to the API documentation."""
    return RedirectResponse(url=f'{app.root_path}/docs')

# Health check endpoint within the API root path (e.g., /api/health)
@app.get("/health", tags=["General"])
async def health_check():
    """Provides a simple health check status."""
    logger.debug("Health check endpoint called.")
    return {"status": "ok"}

# Model listing endpoint within the API root path (e.g., /api/models)
@app.get("/models", tags=["Models"])
async def get_available_models():
    """
    Returns a list of model keys for which the required API key
    environment variable is set. This prevents showing models
    that cannot be used.
    """
    verified_models = []
    for model_key, config in MODELS_CONFIG.items():
        api_key_env = config.get("api_key_env")
        if not api_key_env:
            logger.warning(f"Model '{model_key}' skipped: 'api_key_env' not defined in its configuration.")
            continue # Skip if config is incomplete

        if os.getenv(api_key_env):
            verified_models.append(model_key) # Add model if API key env var is set
        else:
            logger.warning(f"Model '{model_key}' skipped: Environment variable '{api_key_env}' is not set.")

    # If no models have keys set after checking, return empty or log prominently
    if not verified_models and MODELS_CONFIG:
         logger.error("CRITICAL: No API keys seem to be set for any configured models. The model list will be empty.")
    elif not MODELS_CONFIG:
        logger.warning("No models are configured in MODELS_CONFIG.")


    logger.info(f"Returning available models (API keys configured): {verified_models}")
    return {"models": verified_models}

# Chat streaming endpoint within the API root path (e.g., /api/chat/stream)
@app.post("/chat/stream", tags=["Chat"])
async def chat_completion_stream(chat_request: ChatRequest, request: Request):
    """
    Handles chat completion requests and streams responses using Server-Sent Events (SSE).

    Accepts a POST request with a JSON body containing:
    - `model`: The key of the model to use (must be configured and have API key set).
    - `messages`: A list of message objects, each with `role` ('user', 'assistant', 'system') and `content`.
    """
    selected_model_key = chat_request.model
    logger.info(f"Received chat stream request for model key: '{selected_model_key}'")

    try:
        # Get the configured client and the actual model identifier string
        client, model_identifier = get_client_for_model(selected_model_key)

    except HTTPException as e:
        # Handle errors during client/config retrieval (e.g., missing key, bad config)
        logger.error(f"Configuration or setup error for model '{selected_model_key}': {e.detail} (Status: {e.status_code})", exc_info=True)
        # Send error details back via SSE (frontend needs to handle this)
        async def error_stream_generator():
            error_payload = json.dumps({"error": {"message": e.detail, "code": e.status_code, "type": "ConfigurationError"}})
            yield f"data: {error_payload}\n\n"
            logger.info(f"Sent configuration error details via SSE for model '{selected_model_key}'.")
        # Use the status code from the HTTPException
        return EventSourceResponse(error_stream_generator(), media_type="text/event-stream", status_code=e.status_code)
    except Exception as e:
        # Catch any other unexpected errors during setup
        logger.error(f"Unexpected error during setup for model '{selected_model_key}': {e}", exc_info=True)
        async def error_stream_generator():
            error_payload = json.dumps({"error": {"message": "An unexpected internal server error occurred during request setup.", "code": 500, "type": "SetupError"}})
            yield f"data: {error_payload}\n\n"
        return EventSourceResponse(error_stream_generator(), media_type="text/event-stream", status_code=500)

    # Define the async generator function for streaming responses
    async def stream_response_generator() -> AsyncGenerator[str, None]:
        stream = None # Ensure stream variable is defined
        try:
            logger.info(f"Initiating chat stream with API. Model: '{model_identifier}', Key: '{selected_model_key}'")
            # Log message count, but be cautious about logging full content in production
            logger.debug(f"Number of messages in request: {len(chat_request.messages)}")
            if chat_request.messages:
                logger.debug(f"Last message role: {chat_request.messages[-1].role}")

            # Format messages for the OpenAI API
            formatted_messages: List[Dict[str, str]] = [
                {"role": msg.role, "content": msg.content} for msg in chat_request.messages
            ]

            # --- Make the API Call ---
            stream = await client.chat.completions.create(
                model=model_identifier,
                messages=formatted_messages,
                stream=True,
                # Optional parameters (can be passed from ChatRequest if added to models.py)
                # temperature=getattr(chat_request, 'temperature', 0.7),
                # max_tokens=getattr(chat_request, 'max_tokens', 1024),
            )
            # -------------------------

            logger.info(f"Stream opened successfully for model '{model_identifier}'. Processing chunks...")
            sent_any_content = False
            async for chunk in stream:
                # Check if