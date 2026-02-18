"""
Wolfram Alpha Full Results API - Algebra & Calculus Question Generator

Fetches 15 basic algebra and calculus problems with step-by-step solutions from the
Wolfram Alpha API. Output is structured for use with an LLM that explains each step
and the arithmetic to students (rather than just giving answers).

Setup:
  1. Get a free AppID at https://developer.wolframalpha.com/portal/myapps
  2. Set WOLFRAM_APP_ID env var or paste AppID below (env var recommended for GitHub)
  3. pip install requests
  4. For HTTP server (my-app backend): pip install flask flask-cors
"""

import json
import os
import sys
import time
import urllib.parse
from pathlib import Path
from typing import List, Optional

import requests

# Optional: paste AppID here if you prefer (env var takes precedence)
WOLFRAM_APP_ID = ""

# 15 basic algebra and calculus questions (Wolfram Alpha input format)
ALGEBRA_CALCULUS_QUESTIONS = [
    # Algebra - Linear equations
    "solve 2x + 5 = 15",
    "solve 3(x - 4) = 2x + 7",
    "solve 2x/3 + 1 = 5",
    # Algebra - Quadratics
    "solve x^2 - 5x + 6 = 0",
    "solve x^2 - 4 = 0",
    "factor x^2 - 9",
    # Algebra - Simplification
    "expand (x + 3)(x - 2)",
    "simplify (2x^2 + 4x)/(2x)",
    "simplify sqrt(50)",
    # Calculus - Derivatives
    "derivative of x^3 + 2x^2",
    "derivative of sin(x)",
    "derivative of e^(2x)",
    # Calculus - Integrals
    "integrate x^2 dx",
    "integrate sin(x) dx",
    "integrate 1/(1+x^2) dx",
]

# Plain-English step-by-step explanations showing how to solve each problem
# (the arithmetic and reasoning at each step)
HOW_TO_SOLVE = {
    "solve 2x + 5 = 15": """Step 1: Subtract 5 from both sides to isolate the term with x.
   2x + 5 - 5 = 15 - 5
   2x = 10

Step 2: Divide both sides by 2 to solve for x.
   2x ÷ 2 = 10 ÷ 2
   x = 5""",

    "solve 3(x - 4) = 2x + 7": """Step 1: Distribute the 3 on the left side.
   3(x - 4) = 3x - 12
   So: 3x - 12 = 2x + 7

Step 2: Subtract 2x from both sides to get x terms on one side.
   3x - 2x - 12 = 2x - 2x + 7
   x - 12 = 7

Step 3: Add 12 to both sides to solve for x.
   x - 12 + 12 = 7 + 12
   x = 19""",

    "solve 2x/3 + 1 = 5": """Step 1: Subtract 1 from both sides.
   2x/3 + 1 - 1 = 5 - 1
   2x/3 = 4

Step 2: Multiply both sides by 3 to clear the fraction.
   2x/3 × 3 = 4 × 3
   2x = 12

Step 3: Divide both sides by 2 to solve for x.
   2x ÷ 2 = 12 ÷ 2
   x = 6""",

    "solve x^2 - 5x + 6 = 0": """Step 1: Factor the quadratic. We need two numbers that multiply to 6 and add to -5.
   Those are -2 and -3. So: x² - 5x + 6 = (x - 2)(x - 3) = 0

Step 2: Set each factor equal to zero (if a product is 0, one factor must be 0).
   x - 2 = 0  or  x - 3 = 0

Step 3: Solve each equation.
   x = 2  or  x = 3""",

    "solve x^2 - 4 = 0": """Step 1: Add 4 to both sides.
   x² - 4 + 4 = 0 + 4
   x² = 4

Step 2: Take the square root of both sides. Remember: √(x²) = |x|, so x can be positive or negative.
   x = √4  or  x = -√4
   x = 2  or  x = -2""",

    "factor x^2 - 9": """Step 1: Recognize this as a difference of squares: a² - b² = (a + b)(a - b).
   Here, x² - 9 = x² - 3²

Step 2: Apply the formula with a = x and b = 3.
   x² - 9 = (x + 3)(x - 3)""",

    "expand (x + 3)(x - 2)": """Step 1: Use FOIL (First, Outer, Inner, Last) to multiply.
   First:  x × x = x²
   Outer:  x × (-2) = -2x
   Inner:  3 × x = 3x
   Last:   3 × (-2) = -6

Step 2: Combine all terms.
   x² - 2x + 3x - 6

Step 3: Combine like terms (-2x + 3x = x).
   x² + x - 6""",

    "simplify (2x^2 + 4x)/(2x)": """Step 1: Factor the numerator. Both terms have 2x in common.
   2x² + 4x = 2x(x + 2)

Step 2: Rewrite the fraction and cancel the common factor 2x.
   (2x(x + 2)) / (2x) = x + 2

   (We can cancel because 2x ≠ 0 when we simplify.)""",

    "simplify sqrt(50)": """Step 1: Factor 50 into a perfect square times something else.
   50 = 25 × 2 = 5² × 2

Step 2: Use the rule √(a × b) = √a × √b.
   √50 = √(25 × 2) = √25 × √2

Step 3: Simplify √25 = 5.
   √50 = 5√2""",

    "derivative of x^3 + 2x^2": """Step 1: Apply the power rule to each term: d/dx(xⁿ) = n·xⁿ⁻¹
   For x³: the exponent 3 comes down, and we reduce the exponent by 1 → 3x²
   For 2x²: the 2 stays; the exponent 2 comes down, reduce by 1 → 2·2x¹ = 4x

Step 2: Add the results.
   d/dx(x³ + 2x²) = 3x² + 4x""",

    "derivative of sin(x)": """Step 1: Use the derivative rule for sine.
   The derivative of sin(x) with respect to x is cos(x).

   d/dx(sin(x)) = cos(x)

   (This is a standard result from calculus—the rate of change of sine is cosine.)""",

    "derivative of e^(2x)": """Step 1: The derivative of eᵘ is eᵘ times the derivative of u (chain rule).
   Here u = 2x, so du/dx = 2.

Step 2: Apply the chain rule: d/dx(e^(2x)) = e^(2x) × 2 = 2e^(2x)""",

    "integrate x^2 dx": """Step 1: Use the power rule for integrals: ∫xⁿ dx = xⁿ⁺¹/(n+1) + C
   Here n = 2, so we add 1 to the exponent and divide by the new exponent.

Step 2: Apply the rule.
   ∫x² dx = x³/3 + C""",

    "integrate sin(x) dx": """Step 1: Use the standard integral of sine.
   The derivative of -cos(x) is sin(x), so the integral of sin(x) is -cos(x).

   ∫sin(x) dx = -cos(x) + C""",

    "integrate 1/(1+x^2) dx": """Step 1: Recognize this as the derivative of arctan(x).
   The derivative of arctan(x) is 1/(1 + x²), so the integral reverses this.

   ∫1/(1 + x²) dx = arctan(x) + C""",
}

# Pod state for step-by-step solutions (may require Wolfram Alpha Pro for full access)
PODSTATE_STEPS = "Result__Step-by-step+solution"
# Alternative pod states to try if Result doesn't have steps
PODSTATE_ALTERNATIVES = [
    "Result__Show+steps",
    "IndefiniteIntegral__Step-by-step+solution",
    "Derivative__Step-by-step+solution",
]


def query_wolfram(
    question: str,
    app_id: str,
    podstate: Optional[str] = None,
    format: str = "plaintext",
) -> dict:
    """
    Query the Wolfram Alpha Full Results API.
    """
    base_url = "http://api.wolframalpha.com/v2/query"
    params = {
        "appid": app_id,
        "input": question,
        "output": "json",
        "format": format,
    }
    if podstate:
        params["podstate"] = podstate

    response = requests.get(base_url, params=params, timeout=30)
    response.raise_for_status()
    return response.json()


def extract_pods_data(result: dict) -> List[dict]:
    """Extract pod titles and plaintext content from API response."""
    pods = []
    query_result = result.get("queryresult", {})
    if not query_result.get("success"):
        return pods

    for pod in query_result.get("pods", []):
        pod_id = pod.get("id", "")
        pod_title = pod.get("title", "")
        subpods_data = []

        for subpod in pod.get("subpods", []):
            plaintext = subpod.get("plaintext", "").strip()
            if plaintext:
                subpods_data.append(plaintext)

        if subpods_data:
            pods.append(
                {
                    "id": pod_id,
                    "title": pod_title,
                    "content": "\n".join(subpods_data),
                }
            )

    return pods


def fetch_question_with_steps(question: str, app_id: str) -> dict:
    """
    Fetch a question's solution from Wolfram Alpha, attempting step-by-step first.
    Falls back to standard result if steps aren't available (e.g., free tier).
    """
    # Try with step-by-step podstate first
    for podstate in [PODSTATE_STEPS] + PODSTATE_ALTERNATIVES:
        try:
            result = query_wolfram(question, app_id, podstate=podstate)
            query_result = result.get("queryresult", {})

            if not query_result.get("success"):
                error_msg = query_result.get("error", {}).get("msg", "Unknown error")
                continue  # Try next podstate

            pods = extract_pods_data(result)

            # Build structured output for LLM use
            steps_content = ""
            result_content = ""
            input_interpretation = ""

            for pod in pods:
                if "step" in pod["title"].lower() or "step" in pod["id"].lower():
                    steps_content += pod["content"] + "\n\n"
                elif "result" in pod["id"].lower() or "result" in pod["title"].lower():
                    result_content = pod["content"]
                elif "input" in pod["id"].lower():
                    input_interpretation = pod["content"]

            # If we got steps, great; otherwise use whatever we have
            # Use our plain-English "how to solve" when available; otherwise Wolfram's steps
            how_to = HOW_TO_SOLVE.get(question, "")
            wolfram_steps = steps_content.strip() if steps_content else _format_pods_as_steps(pods)
            steps = how_to if how_to else wolfram_steps

            return {
                "question": question,
                "input_interpretation": input_interpretation or question,
                "answer": result_content or (pods[0]["content"] if pods else ""),
                "steps": steps,
                "how_to_solve": how_to,
                "all_pods": [
                    {"title": p["title"], "content": p["content"]}
                    for p in pods
                ],
            }

        except requests.RequestException as e:
            # Network/API error - will retry without podstate below
            pass

    # Fallback: query without podstate to get at least the answer
    try:
        result = query_wolfram(question, app_id, podstate=None)
        pods = extract_pods_data(result)

        result_content = ""
        for pod in pods:
            if "result" in pod["id"].lower():
                result_content = pod["content"]
                break

        how_to = HOW_TO_SOLVE.get(question, "")
        wolfram_steps = _format_pods_as_steps(pods)
        combined_steps = how_to if how_to else wolfram_steps

        return {
            "question": question,
            "input_interpretation": "",
            "answer": result_content,
            "steps": combined_steps,
            "how_to_solve": how_to,
            "all_pods": [
                {"title": p["title"], "content": p["content"]}
                for p in pods
            ],
        }
    except requests.RequestException as e:
        how_to = HOW_TO_SOLVE.get(question, "")
        return {
            "question": question,
            "input_interpretation": "",
            "answer": "",
            "steps": how_to,
            "how_to_solve": how_to,
            "error": str(e),
            "all_pods": [],
        }


def _format_pods_as_steps(pods: List[dict]) -> str:
    """Format pod content as a step-like structure when no explicit steps pod exists."""
    lines = []
    for i, pod in enumerate(pods, 1):
        if pod["content"]:
            lines.append(f"Step {i} ({pod['title']}):\n{pod['content']}")
    return "\n\n".join(lines)


def generate_llm_prompt_context(item: dict) -> str:
    """
    Format a question+solution as context for an LLM that will explain steps
    to students. Includes the plain-English "how to solve" with arithmetic at each step.
    """
    steps = item.get("steps") or item.get("how_to_solve") or item.get("answer", "No steps available.")
    answer = item.get("answer", "")
    lines = [
        "---",
        f"Question: {item['question']}",
        "",
        "How to solve (show each step and the arithmetic to the student):",
        "",
        steps,
        "",
    ]
    if answer and answer not in steps:
        lines.extend([f"Final answer: {answer}", ""])
    return "\n".join(lines)


def _normalize_question(q: str) -> str:
    """Normalize for fuzzy matching (strip, lowercase, collapse spaces)."""
    return " ".join(q.lower().strip().split())


def _lookup_in_cache(question: str, cache: List[dict]) -> Optional[dict]:
    """Find a matching question in the wolfram_questions.json cache."""
    norm = _normalize_question(question)
    for item in cache:
        if _normalize_question(item.get("question", "")) == norm:
            return item
    # Fuzzy: check if question is a substring or vice versa
    for item in cache:
        q = item.get("question", "")
        if norm in _normalize_question(q) or _normalize_question(q) in norm:
            return item
    return None


def _format_chat_response(item: dict) -> str:
    """Format a cached/Wolfram result as chat-friendly text for my-app."""
    steps = item.get("how_to_solve") or item.get("steps") or ""
    answer = item.get("answer", "")
    parts = []
    if steps:
        parts.append(steps)
    if answer and answer not in steps:
        parts.append(f"\nFinal answer: {answer}")
    return "\n".join(parts).strip() if parts else answer or "No result."


def run_server(port: int = 5000):
    """
    Run an HTTP API server compatible with my-app.
    Serves GET /api/query?q=<question> returning JSON suitable for the chat.
    Uses wolfram_questions.json first; falls back to Wolfram API if WOLFRAM_APP_ID set.
    Also handles file uploads at POST /api/upload.
    """
    try:
        from flask import Flask, jsonify, request, send_from_directory  # type: ignore
        from flask_cors import CORS  # type: ignore
        from werkzeug.utils import secure_filename  # type: ignore
    except ImportError:
        print("For server mode, install: pip install flask flask-cors")
        return 1

    app = Flask(__name__)
    CORS(app)

    script_dir = Path(__file__).resolve().parent
    cache_path = script_dir / "wolfram_questions.json"
    cache = []
    if cache_path.exists():
        try:
            with open(cache_path) as f:
                cache = json.load(f)
        except json.JSONDecodeError:
            pass

    app_id = os.environ.get("WOLFRAM_APP_ID") or WOLFRAM_APP_ID

    # File upload configuration
    uploads_dir = script_dir / "uploads"
    uploads_dir.mkdir(exist_ok=True)
    app.config['UPLOAD_FOLDER'] = str(uploads_dir)
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

    # Allowed file extensions
    ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'doc', 'docx', 'ppt', 'pptx', 'xls', 'xlsx'}

    def allowed_file(filename):
        return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

    @app.route("/api/query")
    def api_query():
        q = request.args.get("q", "").strip()
        if not q:
            return jsonify({"text": "Please ask a math question.", "answer": "", "steps": ""}), 400

        # 1. Lookup in cache (wolfram_questions.json)
        item = _lookup_in_cache(q, cache)
        if item:
            text = _format_chat_response(item)
            return jsonify({"text": text, "answer": item.get("answer", ""), "steps": item.get("steps", ""), "how_to_solve": item.get("how_to_solve", "")})

        # 2. Fallback to Wolfram API if app_id available
        if app_id:
            try:
                result = fetch_question_with_steps(q, app_id)
                text = _format_chat_response(result)
                return jsonify({"text": text, "answer": result.get("answer", ""), "steps": result.get("steps", ""), "how_to_solve": result.get("how_to_solve", "")})
            except Exception as e:
                return jsonify({"text": f"Sorry, I couldn't solve that. ({e})", "answer": "", "steps": ""}), 500

        return jsonify({"text": "Question not in cache. Set WOLFRAM_APP_ID to query Wolfram Alpha live.", "answer": "", "steps": ""}), 404

    @app.route("/api/upload", methods=['POST'])
    def upload_file():
        if 'file' not in request.files:
            return jsonify({"error": "No file part"}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({"error": "No selected file"}), 400
        
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            # Add timestamp to avoid conflicts
            timestamp = int(time.time() * 1000)
            name, ext = os.path.splitext(filename)
            unique_filename = f"{name}_{timestamp}{ext}"
            filepath = uploads_dir / unique_filename
            
            file.save(str(filepath))
            
            return jsonify({
                "success": True,
                "filename": unique_filename,
                "originalName": file.filename,
                "size": os.path.getsize(str(filepath))
            }), 200
        
        return jsonify({"error": "File type not allowed"}), 400

    @app.route("/api/files", methods=['GET'])
    def list_files():
        try:
            files = []
            for file_path in uploads_dir.iterdir():
                if file_path.is_file():
                    files.append({
                        "filename": file_path.name,
                        "size": file_path.stat().st_size,
                        "uploadedAt": file_path.stat().st_mtime
                    })
            return jsonify({"files": files}), 200
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    @app.route("/api/files/<filename>", methods=['DELETE'])
    def delete_file(filename):
        try:
            filepath = uploads_dir / secure_filename(filename)
            if filepath.exists() and filepath.is_file():
                filepath.unlink()
                return jsonify({"success": True}), 200
            return jsonify({"error": "File not found"}), 404
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    print(f"Wolfram API server at http://localhost:{port}")
    print("  GET /api/query?q=<question>  -> JSON { text, answer, steps }")
    print("  POST /api/upload -> Upload files")
    print("  GET /api/files -> List uploaded files")
    print("  DELETE /api/files/<filename> -> Delete a file")
    print("  Compatible with my-app chat (use fetch or proxy to this URL)")
    app.run(host="0.0.0.0", port=port, debug=False)
    return 0


def main():
    app_id = os.environ.get("WOLFRAM_APP_ID") or WOLFRAM_APP_ID
    if not app_id:
        print(
            "Error: Set your Wolfram Alpha AppID.\n"
            "  export WOLFRAM_APP_ID=\"your-app-id\"\n"
            "  or paste it in wolfram_alpha.py (WOLFRAM_APP_ID = \"...\")\n"
            "  Get a free AppID at https://developer.wolframalpha.com/portal/myapps"
        )
        return 1

    questions = ALGEBRA_CALCULUS_QUESTIONS
    results = []

    print(f"Fetching {len(questions)} algebra/calculus questions from Wolfram Alpha...\n")

    for i, q in enumerate(questions, 1):
        print(f"[{i}/{len(questions)}] {q}")
        item = fetch_question_with_steps(q, app_id)
        results.append(item)
        # Rate limit: avoid hammering the API
        time.sleep(1)

    # Write JSON (for programmatic use by your LLM pipeline)
    output_json = "wolfram_questions.json"
    with open(output_json, "w") as f:
        json.dump(results, f, indent=2)

    print(f"\nSaved full results to {output_json}")

    # Write prompt-ready text (for pasting into LLM context)
    output_txt = "wolfram_questions_for_llm.txt"
    with open(output_txt, "w") as f:
        f.write(
            "Use the following questions and reference solutions to explain each step "
            "and the arithmetic to students. Do not simply give the final answer.\n\n"
        )
        for item in results:
            f.write(generate_llm_prompt_context(item))

    print(f"Saved LLM prompt context to {output_txt}")

    # Preview - show first few with full step-by-step
    print("\n" + "=" * 60)
    print("PREVIEW: How to solve (first 3 questions)")
    print("=" * 60)
    for i, item in enumerate(results[:3], 1):
        print(generate_llm_prompt_context(item))
    print("\n... (see wolfram_questions.json and wolfram_questions_for_llm.txt for all 15)")

    return 0


if __name__ == "__main__":
    if "--server" in sys.argv or "-s" in sys.argv:
        port = 5000
        try:
            i = sys.argv.index("--port")
            if i + 1 < len(sys.argv):
                port = int(sys.argv[i + 1])
        except (ValueError, IndexError):
            pass
        exit(run_server(port))
    exit(main())
