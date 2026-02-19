"""
Wolfram Alpha tool integration for LLM function calling.
"""
import os
import logging
from typing import Dict, Any
from wolfram_alpha import fetch_question_with_steps

logger = logging.getLogger(__name__)

# Tool definition for Azure OpenAI function calling
WOLFRAM_ALPHA_TOOL = {
    "type": "function",
    "function": {
        "name": "solve_math_problem",
        "description": "Solve mathematical problems including algebra, calculus, derivatives, integrals, and equations. Returns step-by-step solutions with explanations.",
        "parameters": {
            "type": "object",
            "properties": {
                "problem": {
                    "type": "string",
                    "description": "The mathematical problem to solve. Examples: 'solve x^2 - 5x + 6 = 0', 'derivative of x^3 + 2x^2', 'integrate x^2 dx', 'simplify sqrt(50)'"
                }
            },
            "required": ["problem"]
        }
    }
}


def execute_wolfram_tool(problem: str) -> Dict[str, Any]:
    """
    Execute Wolfram Alpha tool to solve a math problem.
    
    Args:
        problem: Mathematical problem to solve
        
    Returns:
        Dict with solution, steps, and metadata
    """
    try:
        app_id = os.getenv('WOLFRAM_APP_ID', 'WL2J62RLKK')
        
        logger.info(f"Executing Wolfram Alpha for problem: {problem}")
        
        result = fetch_question_with_steps(problem, app_id)
        
        if result.get('error'):
            logger.error(f"Wolfram Alpha error: {result['error']}")
            return {
                "success": False,
                "error": result['error'],
                "problem": problem
            }
        
        # Format the result for the LLM
        steps = result.get('steps') or result.get('how_to_solve', '')
        answer = result.get('answer', '')
        
        logger.info(f"Successfully solved problem with Wolfram Alpha")
        
        return {
            "success": True,
            "problem": problem,
            "answer": answer,
            "steps": steps,
            "input_interpretation": result.get('input_interpretation', ''),
            "solution_summary": f"Problem: {problem}\n\nSolution Steps:\n{steps}\n\nFinal Answer: {answer}" if answer else f"Steps:\n{steps}"
        }
        
    except Exception as e:
        logger.error(f"Error executing Wolfram tool: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "problem": problem
        }


def get_available_tools():
    """Return list of available tools for function calling."""
    return [WOLFRAM_ALPHA_TOOL]
