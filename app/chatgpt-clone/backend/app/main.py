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
            yield f"data: {error_payload}\
\
"
            logger.info(f"Sent configuration error details via SSE for model '{selected_model_key}'.")
        # Use the status code from the HTTPException
        return EventSourceResponse(error_stream_generator(), media_type="text/event-stream", status_code=e.status_code)
    except Exception as e:
        # Catch any other unexpected errors during setup
        logger.error(f"Unexpected error during setup for model '{selected_model_key}': {e}", exc_info=True)
        async def error_stream_generator():
            error_payload = json.dumps({"error": {"message": "An unexpected internal server error occurred during request setup.", "code": 500, "type": "SetupError"}})
            yield f"data: