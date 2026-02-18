# AI Learning Helper

An AI-powered homework helper application with React frontend and Python Flask backend, using Azure OpenAI for intelligent responses.

## Project Structure

```
my-app/
├── backend/              # Python Flask backend
│   ├── app.py           # Main Flask application
│   ├── llm_client.py    # Azure OpenAI client
│   └── requirements.txt # Python dependencies
├── src/                 # React frontend source
│   ├── components/      # React components
│   ├── pages/          # Page components
│   └── config.js       # Frontend configuration
├── .env                # Environment variables (not in git)
└── start-backend.sh    # Backend startup script
```

## Setup Instructions

### Prerequisites
- Node.js (v18 or higher)
- Python 3.8 or higher
- Azure OpenAI API credentials

### 1. Environment Variables

Create a `.env` file in the root directory with your Azure credentials:

```env
AZURE_API_KEY=your_azure_api_key
AZURE_MODEL_ENDPOINT=your_azure_endpoint
```

### 2. Install Frontend Dependencies

```bash
npm install
```

### 3. Install Backend Dependencies

```bash
cd backend
pip install -r requirements.txt
```

Or use the startup script (recommended):

```bash
chmod +x start-backend.sh
./start-backend.sh
```

## Running the Application

### Start Backend Server

**Option 1: Using the startup script (recommended)**
```bash
./start-backend.sh
```

**Option 2: Manual start**
```bash
cd backend
python app.py
```

The backend server will run on `http://localhost:5000`

### Start Frontend Development Server

In a separate terminal:

```bash
npm run dev
```

The frontend will run on `http://localhost:5173` (or another port if 5173 is busy)

## Features

- **AI Chat Interface**: Students can ask questions about their coursework
- **Course-Specific Context**: AI responses are tailored to the specific course
- **Azure OpenAI Integration**: Powered by GPT-4 for intelligent, educational responses
- **Real-time Responses**: Get immediate feedback on homework questions
- **User Authentication**: Secure login system for students

## API Endpoints

### `GET /api/health`
Health check endpoint

### `POST /api/chat`
Send a message and receive AI response

**Request Body:**
```json
{
  "message": "What is photosynthesis?",
  "course_name": "Biology 101"
}
```

**Response:**
```json
{
  "response": "Photosynthesis is...",
  "status": "success"
}
```

## Development

- Frontend: React with Vite, TailwindCSS
- Backend: Python Flask with Azure OpenAI
- CORS enabled for local development

## Troubleshooting

**Backend not connecting:**
- Ensure the backend server is running on port 5000
- Check that `.env` file contains correct Azure credentials
- Verify no firewall blocking localhost:5000

**Frontend not receiving responses:**
- Check browser console for CORS errors
- Ensure `VITE_API_BASE_URL` matches backend URL
- Verify backend server is running and healthy (`GET /api/health`)

---

## React + Vite Template Info

This template provides a minimal setup to get React working in Vite with HMR and some ESLint rules.

Currently, two official plugins are available:

- [@vitejs/plugin-react](https://github.com/vitejs/vite-plugin-react/blob/main/packages/plugin-react) uses [Babel](https://babeljs.io/) (or [oxc](https://oxc.rs) when used in [rolldown-vite](https://vite.dev/guide/rolldown)) for Fast Refresh
- [@vitejs/plugin-react-swc](https://github.com/vitejs/vite-plugin-react/blob/main/packages/plugin-react-swc) uses [SWC](https://swc.rs/) for Fast Refresh
