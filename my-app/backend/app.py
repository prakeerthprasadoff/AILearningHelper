from flask import Flask, request, jsonify
from flask_cors import CORS
from llm_client import AzureLLMClient
from wolfram_tool import get_available_tools, execute_wolfram_tool
import json
import logging
import os
import PyPDF2
from pathlib import Path

from db import (
    init_db,
    get_or_create_user,
    save_chat_turn,
    get_recent_chat_history,
    find_similar_past_question,
    get_mistakes,
    add_mistake as db_add_mistake,
    delete_mistake as db_delete_mistake,
    get_study_plan,
    save_study_plan,
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)  # Enable CORS for React frontend

# Initialize database and Azure LLM client
init_db()
llm_client = AzureLLMClient()

# Set up uploads directory (inside backend folder for Render compatibility)
UPLOADS_DIR = Path(__file__).parent / 'uploads'
UPLOADS_DIR.mkdir(exist_ok=True)
ALLOWED_EXTENSIONS = {'pdf', 'txt', 'md'}

def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def extract_text_from_pdf(filepath):
    """Extract text from PDF file"""
    try:
        text = ""
        with open(filepath, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            for page in reader.pages:
                text += page.extract_text()
        return text
    except Exception as e:
        logger.error(f"Error extracting PDF text: {str(e)}")
        return ""

def read_file_content(filepath):
    """Read content from uploaded file based on extension"""
    ext = filepath.suffix.lower()
    try:
        if ext == '.pdf':
            return extract_text_from_pdf(filepath)
        else:
            with open(filepath, 'r', encoding='utf-8') as f:
                return f.read()
    except Exception as e:
        logger.error(f"Error reading file {filepath}: {str(e)}")
        return ""


@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'service': 'AI Learning Helper Backend'}), 200


@app.route('/api/upload', methods=['POST'])
def upload_file():
    """
    Handle file uploads.
    Expects multipart/form-data with 'file' field.
    Returns JSON: { "filename": str, "size": int, "type": str }
    """
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if not allowed_file(file.filename):
            return jsonify({'error': 'File type not allowed. Only PDF, TXT, and MD files are supported'}), 400
        
        # Save file
        filepath = UPLOADS_DIR / file.filename
        file.save(filepath)
        
        file_size = os.path.getsize(filepath)
        file_type = Path(file.filename).suffix[1:].upper()
        
        logger.info(f"File uploaded: {file.filename} ({file_size} bytes)")
        
        return jsonify({
            'filename': file.filename,
            'size': file_size,
            'type': file_type
        }), 200
        
    except Exception as e:
        logger.error(f"Error uploading file: {str(e)}")
        return jsonify({'error': f'Upload failed: {str(e)}'}), 500


@app.route('/api/uploads', methods=['GET'])
def list_uploads():
    """
    List all uploaded files.
    Returns JSON: { "files": [{"filename": str, "size": int, "type": str}, ...] }
    """
    try:
        files = []
        if UPLOADS_DIR.exists():
            for filepath in UPLOADS_DIR.iterdir():
                if filepath.is_file() and allowed_file(filepath.name):
                    files.append({
                        'filename': filepath.name,
                        'size': filepath.stat().st_size,
                        'type': filepath.suffix[1:].upper()
                    })
        
        return jsonify({'files': files}), 200
        
    except Exception as e:
        logger.error(f"Error listing uploads: {str(e)}")
        return jsonify({'error': f'Failed to list uploads: {str(e)}'}), 500


@app.route('/api/delete-upload/<filename>', methods=['DELETE'])
def delete_upload(filename):
    """
    Delete an uploaded file.
    Expects filename in URL path.
    Returns JSON: { "status": "success" }
    """
    try:
        if not allowed_file(filename):
            return jsonify({'error': 'Invalid file type'}), 400
        
        filepath = UPLOADS_DIR / filename
        
        if not filepath.exists():
            return jsonify({'error': 'File not found'}), 404
        
        if not filepath.is_file():
            return jsonify({'error': 'Not a file'}), 400
        
        filepath.unlink()  # Delete the file
        logger.info(f"File deleted: {filename}")
        
        return jsonify({'status': 'success', 'filename': filename}), 200
        
    except Exception as e:
        logger.error(f"Error deleting file: {str(e)}")
        return jsonify({'error': f'Failed to delete file: {str(e)}'}), 500


@app.route('/api/user/ensure', methods=['POST'])
def user_ensure():
    """
    Get or create user by identifier (e.g. email). Returns { "user_id": int }.
    """
    try:
        data = request.get_json() or {}
        identifier = data.get('identifier', '').strip() or request.headers.get('X-User-Identifier', '')
        if not identifier:
            return jsonify({'error': 'Missing identifier'}), 400
        user_id = get_or_create_user(identifier)
        return jsonify({'user_id': user_id}), 200
    except Exception as e:
        logger.error(str(e))
        return jsonify({'error': str(e)}), 500


@app.route('/api/chat', methods=['POST'])
def chat():
    """
    Handle chat requests from the frontend.
    Expects JSON: {
        "message": "user message",
        "course_name": "course name",
        "conversation_history": [{"role": "user|assistant", "content": "..."}],
        "document_filenames": ["file1.pdf", "file2.txt"],
        "user_identifier": "email or id for personalization (optional)",
        "use_memory": true to use saved history, mistakes, repeated-Q detection (optional, default true)
    }
    Returns JSON: { "response": "AI response", "status": "success", "similar_question": {...} if detected }
    """
    try:
        data = request.get_json()
        
        if not data or 'message' not in data:
            return jsonify({'error': 'Missing message in request'}), 400
        
        user_message = data['message']
        course_name = data.get('course_name', 'your course')
        conversation_history = list(data.get('conversation_history', []))
        document_filenames = data.get('document_filenames', [])
        user_identifier = (data.get('user_identifier') or '').strip()
        use_memory = data.get('use_memory', True)
        
        user_id = None
        if user_identifier:
            try:
                user_id = get_or_create_user(user_identifier)
            except ValueError:
                pass
        
        logger.info(f"Received chat request for course: {course_name}, use_memory=%s", use_memory)
        logger.info(f"User message: {user_message}")
        logger.info(f"Conversation history length: {len(conversation_history)}")
        logger.info(f"Documents requested: {document_filenames}")
        
        # When use_memory and we have user_id, merge in persisted history and add personalization context
        similar_info = None
        mistakes_context = ""
        if use_memory and user_id:
            # Prefer recent DB history for consistency (last 20 turns)
            db_history = get_recent_chat_history(user_id, course_name, limit=20)
            if db_history:
                # Current user message must be last (LLM client does not append it when history is provided)
                conversation_history = db_history + [{"role": "user", "content": user_message}]
            # else: keep frontend-sent conversation_history (it already includes the new message)
            # Detect repeated/similar question and surface for the model
            similar_info = find_similar_past_question(user_id, course_name, user_message)
            # Load mistakes for this course to address weak areas
            mistakes = get_mistakes(user_id, course=course_name)
            if mistakes:
                mistakes_context = "\n".join(
                    f"- Topic: {m.get('topic') or 'General'}; Question: {m['question'][:200]}; Correction/note: {m.get('correction', '')[:200]}"
                    for m in mistakes[:15]
                )
        
        # Load document content if provided
        document_context = ""
        if document_filenames:
            document_texts = []
            for filename in document_filenames:
                filepath = UPLOADS_DIR / filename
                if filepath.exists():
                    content = read_file_content(filepath)
                    if content:
                        document_texts.append(f"--- Document: {filename} ---\n{content}\n")
                        logger.info(f"Loaded document: {filename}")
            
            if document_texts:
                document_context = "\n".join(document_texts)
        
        # Build context-aware system prompt
        system_prompt = f"""You are an AI homework helper for students. 
You are currently helping with {course_name}. 

DO NOT GIVE THE ANSWER. HELP THE STUDENT FIND THE ANSWER ON THEIR OWN. ASK QUESTIONS TO WALK THEM THROUGH.
Your role is to help students through their thought process. For direct questions looking for answers (example: What is x in 3x + 5 = 17?), do not give the straight answer.
Instead, ask questions to the student to walk them through solving the issue or thinking through the problem. If the student has trouble with a topic, you can give them rules or formulas or even sources to help them.
Basically, point the student in the right direction, give them feedback on their thought process, and help them get to the answer on their own.
You are able to confirm and affirm correct answers and thought processes.

Provide clear, educational explanations. Break down complex concepts step by step.
Be encouraging and supportive. Support development of critical thinking; focus on understanding, not just answers.

STRICT—NO WORKING OUT THE PROBLEM FOR THEM (even in explanation):
- You MAY give the formula or rule (e.g. the product rule formula, derivative rules, definitions).
- You must NOT work out the student's problem for them: do not simplify their expression, do not state what each term "simplifies to" or "equals," and do not give the final answer—even as part of an explanation or "walkthrough." The student must do the computation themselves.
- You may ask "What do you get for u'(x)?" or "Apply the rule and tell me your next step" but do not provide that next step or the simplified result yourself. Only confirm or correct after the student shows their work.

DO NOT GIVE THE ANSWER. HELP THE STUDENT FIND THE ANSWER ON THEIR OWN. ASK QUESTIONS TO WALK THEM THROUGH.
You have access to a Wolfram Alpha tool that can solve mathematical problems. Use it only when the student explicitly asks to see a full solution or worked example (e.g. "show me the steps" or "solve this for me"). When the student is practicing (e.g. "I have a product rule problem" or "how do I do this?") do NOT call the tool and do NOT work out the answer—give only the rule/formula and prompt them to try the next step.
At the end of completing a math problem with the tool (only when the student asked for a full solution), you may review the steps with the student.

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
        
        # Add repeated-question / misunderstanding guidance
        if similar_info:
            system_prompt += f"""

REPEATED OR SIMILAR QUESTION: The student has asked something similar before: "{similar_info.get('question', '')[:300]}". 
Address any root misunderstanding; reference the reference materials (if provided) to reinforce the concept. Do not simply repeat the same explanation—probe for what is still unclear and build deeper understanding.
"""
        
        # Add mistakes/weak areas context
        if mistakes_context:
            system_prompt += f"""

AREAS THE STUDENT HAS STRUGGLED WITH (use to tailor explanations and avoid repeating the same confusions):
{mistakes_context}
"""
        
        # Add document context to system prompt if available
        if document_context:
            system_prompt += f"""

REFERENCE MATERIALS PROVIDED BY STUDENT:
{document_context}

Use the above reference materials to provide context-aware answers. You can reference specific materials from the documents when helping the student. When the student asks repeated or related questions, bring in relevant excerpts from these materials to deepen learning.
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
        
        # Persist this turn when we have a user identity and memory is enabled
        if user_id and use_memory:
            try:
                save_chat_turn(user_id, course_name, 'user', user_message)
                save_chat_turn(user_id, course_name, 'assistant', ai_response)
            except Exception as e:
                logger.warning("Failed to save chat history: %s", e)
        
        out = {'response': ai_response, 'status': 'success'}
        if similar_info:
            out['similar_question'] = similar_info
        return jsonify(out), 200
        
    except Exception as e:
        logger.error(f"Error processing chat request: {str(e)}")
        return jsonify({
            'error': 'Failed to process chat request',
            'details': str(e)
        }), 500


@app.route('/api/mistakes', methods=['GET'])
def list_mistakes():
    """List mistakes for the user. Query: user_identifier, optional course."""
    try:
        identifier = request.args.get('user_identifier', '').strip()
        if not identifier:
            return jsonify({'error': 'Missing user_identifier'}), 400
        user_id = get_or_create_user(identifier)
        course = request.args.get('course', '').strip() or None
        items = get_mistakes(user_id, course=course)
        return jsonify({'mistakes': items}), 200
    except Exception as e:
        logger.error(str(e))
        return jsonify({'error': str(e)}), 500


@app.route('/api/mistakes', methods=['POST'])
def create_mistake():
    """Add a mistake. Body: user_identifier, course, question, correction (optional), topic (optional)."""
    try:
        data = request.get_json() or {}
        identifier = (data.get('user_identifier') or '').strip()
        if not identifier:
            return jsonify({'error': 'Missing user_identifier'}), 400
        user_id = get_or_create_user(identifier)
        course = (data.get('course') or '').strip() or 'General'
        question = (data.get('question') or '').strip()
        if not question:
            return jsonify({'error': 'Missing question'}), 400
        correction = (data.get('correction') or '').strip()
        topic = (data.get('topic') or '').strip()
        mid = db_add_mistake(user_id, course, question, correction=correction, topic=topic)
        return jsonify({'id': mid, 'status': 'created'}), 201
    except Exception as e:
        logger.error(str(e))
        return jsonify({'error': str(e)}), 500


@app.route('/api/mistakes/<int:mistake_id>', methods=['DELETE'])
def remove_mistake(mistake_id):
    """Delete a mistake. Query: user_identifier."""
    try:
        identifier = request.args.get('user_identifier', '').strip()
        if not identifier:
            return jsonify({'error': 'Missing user_identifier'}), 400
        user_id = get_or_create_user(identifier)
        ok = db_delete_mistake(mistake_id, user_id)
        if not ok:
            return jsonify({'error': 'Not found'}), 404
        return jsonify({'status': 'deleted'}), 200
    except Exception as e:
        logger.error(str(e))
        return jsonify({'error': str(e)}), 500


@app.route('/api/study-plan', methods=['GET'])
def get_study_plan_route():
    """Get study plan. Query: user_identifier."""
    try:
        identifier = request.args.get('user_identifier', '').strip()
        if not identifier:
            return jsonify({'error': 'Missing user_identifier'}), 400
        user_id = get_or_create_user(identifier)
        result = get_study_plan(user_id)
        if result is None:
            return jsonify({'plan': None, 'updated_at': None}), 200
        return jsonify(result), 200
    except Exception as e:
        logger.error(str(e))
        return jsonify({'error': str(e)}), 500


@app.route('/api/study-plan', methods=['POST'])
def save_study_plan_route():
    """Save study plan. Body: user_identifier, plan (object)."""
    try:
        data = request.get_json() or {}
        identifier = (data.get('user_identifier') or '').strip()
        if not identifier:
            return jsonify({'error': 'Missing user_identifier'}), 400
        user_id = get_or_create_user(identifier)
        plan = data.get('plan')
        if plan is None:
            return jsonify({'error': 'Missing plan'}), 400
        save_study_plan(user_id, plan if isinstance(plan, dict) else {})
        return jsonify({'status': 'saved'}), 200
    except Exception as e:
        logger.error(str(e))
        return jsonify({'error': str(e)}), 500


def _generate_with_llm(prompt: str, document_context: str = "", course_name: str = "your course") -> str:
    """Helper to get a one-shot completion for study guide / practice exam / weekly review."""
    system = f"""You are an educational assistant for {course_name}. 
Generate clear, structured content. Be concise but pedagogically helpful. 
Focus on understanding and critical thinking, not just facts."""
    if document_context:
        system += f"\n\nReference materials the student has provided:\n{document_context}"
    try:
        r = llm_client.get_completion(
            user_message=prompt,
            system_prompt=system,
            conversation_history=[],
            temperature=0.6,
            max_tokens=4000,
        )
        return (r.get('content') or '').strip()
    except Exception as e:
        logger.error("LLM generation failed: %s", e)
        return f"Generation failed: {e}"


@app.route('/api/weekly-review', methods=['POST'])
def weekly_review():
    """Generate weekly review prompts based on weak areas (mistakes). Body: user_identifier, course (optional)."""
    try:
        data = request.get_json() or {}
        identifier = (data.get('user_identifier') or '').strip()
        if not identifier:
            return jsonify({'error': 'Missing user_identifier'}), 400
        user_id = get_or_create_user(identifier)
        course = (data.get('course') or '').strip() or None
        mistakes = get_mistakes(user_id, course=course)
        if not mistakes:
            return jsonify({
                'review_prompts': [],
                'message': 'No recorded mistakes yet. Keep studying and add mistakes to get personalized review prompts.',
            }), 200
        summary = "\n".join(
            f"- {m.get('topic') or 'General'}: {m['question'][:150]} (correction/note: {m.get('correction', '')[:100]})"
            for m in mistakes[:25]
        )
        prompt = f"""Based on the following areas this student has struggled with, generate 5-8 short weekly review prompts or practice questions that would help reinforce understanding. Be specific to their weak areas. Format as a numbered list of prompts or questions.

Student's weak areas:
{summary}"""
        text = _generate_with_llm(prompt, course_name=course or "the course")
        # Simple split into list of prompts
        lines = [s.strip() for s in text.split('\n') if s.strip() and s.strip()[0].isdigit()]
        if not lines:
            lines = [text]
        return jsonify({'review_prompts': lines, 'full_text': text}), 200
    except Exception as e:
        logger.error(str(e))
        return jsonify({'error': str(e)}), 500


@app.route('/api/generate-study-guide', methods=['POST'])
def generate_study_guide():
    """Generate a study guide from course/topic and optional documents. Body: user_identifier, course_name, topic (optional), document_filenames (optional)."""
    try:
        data = request.get_json() or {}
        course_name = (data.get('course_name') or 'your course').strip()
        topic = (data.get('topic') or '').strip()
        document_filenames = data.get('document_filenames') or []
        document_context = ""
        for filename in document_filenames:
            filepath = UPLOADS_DIR / filename
            if filepath.exists():
                content = read_file_content(filepath)
                if content:
                    document_context += f"\n--- {filename} ---\n{content}\n"
        scope = f" for the topic: {topic}" if topic else ""
        prompt = f"""Create a concise study guide for {course_name}{scope}. Include key concepts, definitions, and short practice suggestions. Structure with clear headings. Aim for understanding and critical thinking, not just memorization. Use $...$ for inline math and $$...$$ for display math (limits, fractions, equations)."""
        text = _generate_with_llm(prompt, document_context=document_context, course_name=course_name)
        return jsonify({'study_guide': text, 'course_name': course_name, 'topic': topic or None}), 200
    except Exception as e:
        logger.error(str(e))
        return jsonify({'error': str(e)}), 500


@app.route('/api/generate-practice-exam', methods=['POST'])
def generate_practice_exam():
    """Generate practice exam questions (generalized, not only from PDF). Body: course_name, topic (optional), document_filenames (optional)."""
    try:
        data = request.get_json() or {}
        course_name = (data.get('course_name') or 'your course').strip()
        topic = (data.get('topic') or '').strip()
        document_filenames = data.get('document_filenames') or []
        document_context = ""
        for filename in document_filenames:
            filepath = UPLOADS_DIR / filename
            if filepath.exists():
                content = read_file_content(filepath)
                if content:
                    document_context += f"\n--- {filename} ---\n{content}\n"
        scope = f" focused on: {topic}" if topic else ""
        prompt = f"""Generate a short practice exam (5-8 questions) for {course_name}{scope}. Mix question types: conceptual, short answer, and application. Base questions on the course material; if reference materials are provided below, use them. Do not give answers—only the questions. Format as a numbered list with clear questions. Use $...$ for inline math (e.g. $f(x)$, $x \\\\to 2$) and $$...$$ for display equations (e.g. limits, fractions on their own line)."""
        if document_context:
            prompt += f"\n\nReference materials:\n{document_context}"
        text = _generate_with_llm(prompt, document_context="", course_name=course_name)
        return jsonify({'practice_exam': text, 'course_name': course_name, 'topic': topic or None}), 200
    except Exception as e:
        logger.error(str(e))
        return jsonify({'error': str(e)}), 500


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
