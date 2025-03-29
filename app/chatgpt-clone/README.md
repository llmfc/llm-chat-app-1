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


## Prerequisites

*   Docker and Docker Compose installed.
*   API keys for the desired LLM providers (OpenAI, Groq, Mistral, etc.).

## Setup & Running

1.  **Clone the Repository:**
    bash
    git clone <your-repo-url> chatgpt-clone
    cd chatgpt-clone
    

2.  **Configure Environment Variables:**
    *   Rename `.env.example` to `.env`.
    *   Open the `.env` file and fill in your API keys for the services you want to use (e.g., `OPENAI_API_KEY`, `GROQ_API_KEY`, `MISTRAL_API_KEY`).
    *   Verify `VITE_API_BASE_URL` is correct for your setup (default `http://localhost:8000/api` should work with Docker Compose).
    *   Verify `FRONTEND_URL` is correct for CORS (default `http://localhost:5173` should work with Docker Compose).

3.  **Build and Run Containers:**
    *   From the root `chatgpt-clone/` directory, run:
        bash
        docker-compose up --build
        
    *   The `--build` flag ensures images are built the first time or when Dockerfiles/code change. You can omit it for subsequent runs if only `.env` changes.
    *   Use `-d` to run in detached mode (background): `docker-compose up --build -d`

4.  **Access the Application:**
    *   Open your web browser and navigate to `http://localhost:5173` (or the port specified for the frontend in `docker-compose.yml`).

5.  **Stopping the Application:**
    *   If running in the foreground, press `Ctrl+C`.
    *   If running in detached mode, use:
        bash
        docker-compose down
        

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