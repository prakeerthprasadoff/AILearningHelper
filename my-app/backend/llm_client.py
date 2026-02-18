import os
import requests
import json
import logging
from typing import Optional, Generator, List, Dict, Any
from dotenv import load_dotenv

logger = logging.getLogger(__name__)

# Load environment variables from .env file
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '..', '.env'))


class AzureLLMClient:
    """Client for interacting with Azure OpenAI deployment"""
    
    def __init__(self):
        """Initialize the Azure LLM client with credentials from environment variables"""
        self.api_key = os.getenv('AZURE_API_KEY')
        self.endpoint = os.getenv('AZURE_MODEL_ENDPOINT')
        
        if not self.api_key:
            raise ValueError("AZURE_API_KEY not found in environment variables")
        if not self.endpoint:
            raise ValueError("AZURE_MODEL_ENDPOINT not found in environment variables")
        
        self.headers = {
            'Content-Type': 'application/json',
            'api-key': self.api_key
        }
        
        logger.info("Azure LLM Client initialized successfully")
    
    def get_completion(
        self,
        user_message: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 1000,
        tools: Optional[List[Dict[str, Any]]] = None,
        conversation_history: Optional[List[Dict[str, str]]] = None
    ) -> Dict[str, Any]:
        """
        Get a completion from Azure OpenAI with optional function calling support.
        
        Args:
            user_message: The user's input message
            system_prompt: Optional system prompt to set context
            temperature: Controls randomness (0-1)
            max_tokens: Maximum tokens in response
            tools: Optional list of tool definitions for function calling
            conversation_history: Optional conversation history (list of {role, content})
            
        Returns:
            Dict with 'content' (str), 'tool_calls' (list), and 'finish_reason' (str)
        """
        try:
            messages = []
            
            if system_prompt:
                messages.append({
                    'role': 'system',
                    'content': system_prompt
                })
            
            # Add conversation history if provided
            if conversation_history:
                messages.extend(conversation_history)
            else:
                # Fall back to just adding the current user message
                messages.append({
                    'role': 'user',
                    'content': user_message
                })
            
            payload = {
                'messages': messages,
                'temperature': temperature,
                'max_tokens': max_tokens,
                'top_p': 0.95,
                'frequency_penalty': 0,
                'presence_penalty': 0
            }
            
            # Add tools if provided
            if tools:
                payload['tools'] = tools
                payload['tool_choice'] = 'auto'
            
            logger.info(f"Sending request to Azure OpenAI endpoint")
            
            response = requests.post(
                self.endpoint,
                headers=self.headers,
                json=payload,
                timeout=60
            )
            
            response.raise_for_status()
            
            result = response.json()
            
            if 'choices' in result and len(result['choices']) > 0:
                choice = result['choices'][0]
                message = choice['message']
                
                return {
                    'content': message.get('content', ''),
                    'tool_calls': message.get('tool_calls', []),
                    'finish_reason': choice.get('finish_reason', 'stop')
                }
            else:
                logger.error("Unexpected response format from Azure OpenAI")
                return {
                    'content': "I apologize, but I encountered an issue generating a response. Please try again.",
                    'tool_calls': [],
                    'finish_reason': 'error'
                }
                
        except requests.exceptions.Timeout:
            logger.error("Request to Azure OpenAI timed out")
            return {
                'content': "I apologize, but the request timed out. Please try again.",
                'tool_calls': [],
                'finish_reason': 'error'
            }
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Request error: {str(e)}")
            return {
                'content': f"I apologize, but I encountered an error: {str(e)}",
                'tool_calls': [],
                'finish_reason': 'error'
            }
            
        except Exception as e:
            logger.error(f"Unexpected error in get_completion: {str(e)}")
            return {
                'content': "I apologize, but I encountered an unexpected error. Please try again.",
                'tool_calls': [],
                'finish_reason': 'error'
            }
    
    def get_completion_with_tool_result(
        self,
        messages: List[Dict[str, Any]],
        tools: Optional[List[Dict[str, Any]]] = None,
        temperature: float = 0.7,
        max_tokens: int = 1000
    ) -> Dict[str, Any]:
        """
        Continue a conversation with tool results.
        
        Args:
            messages: Full conversation history including tool results
            tools: Optional list of tool definitions
            temperature: Controls randomness
            max_tokens: Maximum tokens in response
            
        Returns:
            Dict with 'content', 'tool_calls', and 'finish_reason'
        """
        try:
            payload = {
                'messages': messages,
                'temperature': temperature,
                'max_tokens': max_tokens,
                'top_p': 0.95,
                'frequency_penalty': 0,
                'presence_penalty': 0
            }
            
            if tools:
                payload['tools'] = tools
                payload['tool_choice'] = 'auto'
            
            response = requests.post(
                self.endpoint,
                headers=self.headers,
                json=payload,
                timeout=60
            )
            
            response.raise_for_status()
            result = response.json()
            
            if 'choices' in result and len(result['choices']) > 0:
                choice = result['choices'][0]
                message = choice['message']
                
                return {
                    'content': message.get('content', ''),
                    'tool_calls': message.get('tool_calls', []),
                    'finish_reason': choice.get('finish_reason', 'stop')
                }
            else:
                return {
                    'content': "Error processing response.",
                    'tool_calls': [],
                    'finish_reason': 'error'
                }
                
        except Exception as e:
            logger.error(f"Error in get_completion_with_tool_result: {str(e)}")
            return {
                'content': f"Error: {str(e)}",
                'tool_calls': [],
                'finish_reason': 'error'
            }
    
    def get_streaming_completion(
        self,
        user_message: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 1000
    ) -> Generator[str, None, None]:
        """
        Get a streaming completion from Azure OpenAI.
        
        Args:
            user_message: The user's input message
            system_prompt: Optional system prompt to set context
            temperature: Controls randomness (0-1)
            max_tokens: Maximum tokens in response
            
        Yields:
            Chunks of the AI's response text
        """
        try:
            messages = []
            
            if system_prompt:
                messages.append({
                    'role': 'system',
                    'content': system_prompt
                })
            
            messages.append({
                'role': 'user',
                'content': user_message
            })
            
            payload = {
                'messages': messages,
                'temperature': temperature,
                'max_tokens': max_tokens,
                'top_p': 0.95,
                'frequency_penalty': 0,
                'presence_penalty': 0,
                'stream': True
            }
            
            logger.info(f"Sending streaming request to Azure OpenAI endpoint")
            
            response = requests.post(
                self.endpoint,
                headers=self.headers,
                json=payload,
                stream=True,
                timeout=60
            )
            
            response.raise_for_status()
            
            for line in response.iter_lines():
                if line:
                    line_text = line.decode('utf-8')
                    if line_text.startswith('data: '):
                        data_str = line_text[6:]
                        if data_str.strip() == '[DONE]':
                            break
                        try:
                            data = json.loads(data_str)
                            if 'choices' in data and len(data['choices']) > 0:
                                delta = data['choices'][0].get('delta', {})
                                content = delta.get('content', '')
                                if content:
                                    yield content
                        except json.JSONDecodeError:
                            continue
                            
        except Exception as e:
            logger.error(f"Error in streaming completion: {str(e)}")
            yield f"Error: {str(e)}"
