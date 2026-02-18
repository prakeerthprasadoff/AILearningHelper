from flask import Flask, request, jsonify
from flask_cors import CORS
from llm_client import AzureLLMClient
from wolfram_tool import get_available_tools, execute_wolfram_tool
import json
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
    Expects JSON: { 
        "message": "user message", 
        "course_name": "course name",
        "conversation_history": [{"role": "user|assistant", "content": "..."}]
    }
    Returns JSON: { "response": "AI response" }
    """
    try:
        data = request.get_json()
        
        if not data or 'message' not in data:
            return jsonify({'error': 'Missing message in request'}), 400
        
        user_message = data['message']
        course_name = data.get('course_name', 'your course')
        conversation_history = data.get('conversation_history', [])
        
        logger.info(f"Received chat request for course: {course_name}")
        logger.info(f"User message: {user_message}")
        logger.info(f"Conversation history length: {len(conversation_history)}")
        
        # Build context-aware system prompt
        system_prompt = f"""You are an AI homework helper for students. 
You are currently helping with {course_name}. 

DO NOT GIVE THE ANSWER. HELP THE STUDENT FIND THE ANSWER ON THEIR OWN. ASK QUESTIONS TO WALK THEM THROUGH.
Your role is to help students through their thought process. For direct questions looking for answers (example: What is x in 3x + 5 = 17?), do not give the straight answer.
Instead, ask questions to the student to walk them through solving the issue or thinking through the problem. If the student has trouble with a topic, you can give them rules or formulas or even sources to help them.
Basically, point the student in the right direction, give them feedback on their thought process, and help them get to the answer on their own.
You are able to confirm and affirm correct answers and thought processes.

Provide clear, educational explanations. Break down complex concepts step by step.
Be encouraging and supportive.

DO NOT GIVE THE ANSWER. HELP THE STUDENT FIND THE ANSWER ON THEIR OWN. ASK QUESTIONS TO WALK THEM THROUGH.
You have access to a Wolfram Alpha tool that can solve mathematical problems. When a student asks a math question (algebra, calculus, derivatives, integrals, equations, etc.), use the solve_math_problem function to get step-by-step solutions.
At the end of completing a math problem, or finding the answer, show and review each step with the student so they can see the work process.

IMPORTANT: When including mathematical notation:
- Use $...$ for inline math (e.g., $x^2 + y^2$)
- Use $$...$$ for display/block math equations (e.g., $$\\frac{{d}}{{dx}}(x^n) = nx^{{n-1}}$$)
- DO NOT use \\[ \\] or \\( \\) notation
- Always use double backslashes for LaTeX commands in markdown (e.g., \\frac, \\cdot, \\sum)
- Format all mathematical expressions using proper LaTeX syntax within $ or $$ delimiters

Example of proper formatting:
The derivative of $x^2$ is $2x$.

The product rule states:
$$\\frac{{d}}{{dx}}[u(x) \\cdot v(x)] = u'(x) \\cdot v(x) + u(x) \\cdot v'(x)$$
"""
        
        # Get available tools
        tools = get_available_tools()
        
        # Initial LLM call with tools and conversation history
        response = llm_client.get_completion(
            user_message=user_message,
            system_prompt=system_prompt,
            tools=tools,
            conversation_history=conversation_history
        )
        
        logger.info(f"Initial response finish_reason: {response['finish_reason']}")
        
        # Check if LLM wants to call a tool
        if response['tool_calls']:
            logger.info(f"LLM requested {len(response['tool_calls'])} tool call(s)")
            
            # Build conversation history
            messages = [
                {'role': 'system', 'content': system_prompt},
                {'role': 'user', 'content': user_message},
                {'role': 'assistant', 'content': response.get('content'), 'tool_calls': response['tool_calls']}
            ]
            
            # Execute each tool call
            for tool_call in response['tool_calls']:
                function_name = tool_call['function']['name']
                function_args = json.loads(tool_call['function']['arguments'])
                
                logger.info(f"Executing tool: {function_name} with args: {function_args}")
                
                if function_name == 'solve_math_problem':
                    tool_result = execute_wolfram_tool(function_args['problem'])
                    
                    # Add tool result to conversation
                    messages.append({
                        'role': 'tool',
                        'tool_call_id': tool_call['id'],
                        'name': function_name,
                        'content': json.dumps(tool_result)
                    })
            
            # Get final response from LLM with tool results
            final_response = llm_client.get_completion_with_tool_result(
                messages=messages,
                tools=tools
            )
            
            ai_response = final_response['content']
            logger.info("Generated AI response with tool results")
        else:
            # No tool calls needed, use direct response
            ai_response = response['content']
            logger.info("Generated AI response without tools")
        
        logger.info(f"AI Response text (first 500 chars): {ai_response[:500]}")
        
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
