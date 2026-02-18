from flask import Flask, request, jsonify
from flask_cors import CORS
from llm_client import AzureLLMClient
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)  # Enable CORS for React frontend

# Initialize Azure LLM client
llm_client = AzureLLMClient()


@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'service': 'AI Learning Helper Backend'}), 200


@app.route('/api/chat', methods=['POST'])
def chat():
    """
    Handle chat requests from the frontend.
    Expects JSON: { "message": "user message", "course_name": "course name" }
    Returns JSON: { "response": "AI response" }
    """
    try:
        data = request.get_json()
        
        if not data or 'message' not in data:
            return jsonify({'error': 'Missing message in request'}), 400
        
        user_message = data['message']
        course_name = data.get('course_name', 'your course')
        
        logger.info(f"Received chat request for course: {course_name}")
        logger.info(f"User message: {user_message}")
        
        # Build context-aware system prompt
        system_prompt = f"""You are an AI homework helper for students. 
You are currently helping with {course_name}. 
Provide clear, educational explanations. Break down complex concepts step by step.
Be encouraging and supportive."""
        
        # Get response from Azure LLM
        ai_response = llm_client.get_completion(
            user_message=user_message,
            system_prompt=system_prompt
        )
        
        logger.info(f"Generated AI response successfully")
        
        return jsonify({
            'response': ai_response,
            'status': 'success'
        }), 200
        
    except Exception as e:
        logger.error(f"Error processing chat request: {str(e)}")
        return jsonify({
            'error': 'Failed to process chat request',
            'details': str(e)
        }), 500


@app.route('/api/chat/stream', methods=['POST'])
def chat_stream():
    """
    Handle streaming chat requests (for future enhancement).
    """
    try:
        data = request.get_json()
        
        if not data or 'message' not in data:
            return jsonify({'error': 'Missing message in request'}), 400
        
        user_message = data['message']
        course_name = data.get('course_name', 'your course')
        
        system_prompt = f"""You are an AI homework helper for students. 
You are currently helping with {course_name}. 
Provide clear, educational explanations. Break down complex concepts step by step.
Be encouraging and supportive."""
        
        # Get streaming response from Azure LLM
        response_stream = llm_client.get_streaming_completion(
            user_message=user_message,
            system_prompt=system_prompt
        )
        
        def generate():
            for chunk in response_stream:
                yield f"data: {chunk}\n\n"
        
        return app.response_class(generate(), mimetype='text/event-stream')
        
    except Exception as e:
        logger.error(f"Error processing streaming chat request: {str(e)}")
        return jsonify({
            'error': 'Failed to process streaming chat request',
            'details': str(e)
        }), 500


if __name__ == '__main__':
    logger.info("Starting AI Learning Helper Backend Server...")
    app.run(host='0.0.0.0', port=5001, debug=True)
