# AI Learning Helper

An AI-powered homework assistant application with file upload capabilities.

## Features

- **Course Management**: Organize your classes and learning materials
- **AI Chat**: Ask questions about your course material and get AI-powered responses
- **File Upload**: Upload notes, slides, and assignments for future AI analysis
- **Wolfram Alpha Integration**: Get step-by-step solutions to math problems

## Setup

### Backend Server

1. Install Python dependencies:
```bash
pip install flask flask-cors requests
```

2. Start the Flask server:
```bash
python3 wolfram_alpha.py --server
```

The server will run on `http://localhost:5000` and provides the following endpoints:
- `GET /api/query?q=<question>` - Query Wolfram Alpha for math solutions
- `POST /api/upload` - Upload files (max 16MB)
- `GET /api/files` - List uploaded files
- `DELETE /api/files/<filename>` - Delete a file

### Frontend Application

1. Navigate to the my-app directory:
```bash
cd my-app
```

2. Install dependencies:
```bash
npm install
```

3. Start the development server:
```bash
npm run dev
```

The app will run on `http://localhost:5173`

## File Upload

The application supports uploading the following file types:
- Documents: `.txt`, `.pdf`, `.doc`, `.docx`, `.ppt`, `.pptx`, `.xls`, `.xlsx`
- Images: `.png`, `.jpg`, `.jpeg`, `.gif`

Files are stored in the `uploads/` directory on the server and can be deleted from the UI.

## Demo Credentials

- Email: `demo@myapp.com`
- Password: `abcd`

## Development

### Linting
```bash
cd my-app
npm run lint
```

### Building for Production
```bash
cd my-app
npm run build
```
