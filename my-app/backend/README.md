# AI Learning Helper - Backend

Python Flask backend for handling Azure OpenAI LLM requests.

## Setup

1. **Install Python dependencies:**
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

2. **Environment variables:**
   The backend reads credentials from the `.env` file in the parent directory (`my-app/.env`).
   Ensure these variables are set:
   - `AZURE_API_KEY`
   - `AZURE_MODEL_ENDPOINT`

3. **Run the backend server:**
   ```bash
   python app.py
   ```
   The server will start on `http://localhost:5000`

## API Endpoints

### `GET /api/health`
Health check endpoint to verify the server is running.

**Response:**
```json
{
  "status": "healthy",
  "service": "AI Learning Helper Backend"
}
```

### `POST /api/chat`
Send a chat message and receive an AI response.

**Request:**
```json
{
  "message": "What is photosynthesis?",
  "course_name": "Biology 101"
}
```

**Response:**
```json
{
  "response": "Photosynthesis is the process...",
  "status": "success"
}
```

### `POST /api/chat/stream`
Send a chat message and receive a streaming AI response (for future use).

## Architecture

- `app.py` - Flask application with API routes
- `llm_client.py` - Azure OpenAI client for making LLM calls
- `requirements.txt` - Python dependencies

## Development

The backend uses:
- **Flask** for the web server
- **Flask-CORS** to allow requests from the React frontend
- **python-dotenv** to load environment variables
- **requests** for HTTP calls to Azure OpenAI API
