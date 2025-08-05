import google.generativeai as genai
from app.core.config import settings
from typing import List, Dict, Any
import json
import asyncio

class LLMService:
    def __init__(self):
        if not settings.google_api_key:
            raise ValueError("GOOGLE_API_KEY not found in environment variables")
        
        genai.configure(api_key=settings.google_api_key)
        self.model = genai.GenerativeModel('gemini-1.5-flash')
    
    async def generate_response(self, prompt: str, context: str = "") -> str:
        try:
            full_prompt = f"{context}\n\n{prompt}" if context else prompt
            
            # Run the synchronous generate_content in a thread pool
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None, 
                self.model.generate_content, 
                full_prompt
            )
            
            return response.text
        except Exception as e:
            return f"Error generating response: {str(e)}"
    
    async def analyze_legal_case(self, case_text: str) -> Dict[str, Any]:
        prompt = f"""
        Analyze the following legal case using the IRAC method (Issue, Rule, Application, Conclusion).
        Also extract key facts and legal principles.
        
        Case Text: {case_text}
        
        Please provide your analysis in the following JSON format:
        {{
            "issue": "What is the legal question?",
            "rule": "What legal rule applies?",
            "application": "How does the rule apply to the facts?",
            "conclusion": "What is the outcome?",
            "key_facts": ["fact1", "fact2", "fact3"],
            "legal_principles": ["principle1", "principle2"]
        }}
        
        Respond only with valid JSON.
        """
        
        try:
            response = await self.generate_response(prompt)
            # Try to parse JSON response
            # Clean the response to extract JSON
            response_clean = response.strip()
            if response_clean.startswith('```json'):
                response_clean = response_clean[7:-3]
            elif response_clean.startswith('```'):
                response_clean = response_clean[3:-3]
            
            return json.loads(response_clean)
        except json.JSONDecodeError:
            return {
                "issue": "Unable to identify issue - JSON parsing error",
                "rule": "Unable to identify rule - JSON parsing error",
                "application": "Unable to analyze application - JSON parsing error",
                "conclusion": "Unable to determine conclusion - JSON parsing error",
                "key_facts": ["Error parsing response"],
                "legal_principles": ["Error parsing response"]
            }
        except Exception as e:
            return {
                "issue": f"Error: {str(e)}",
                "rule": "Unable to identify rule",
                "application": "Unable to analyze application",
                "conclusion": "Unable to determine conclusion",
                "key_facts": [],
                "legal_principles": []
            }
    
    async def generate_legal_explanation(self, topic: str, question: str, context: List[str] = []) -> str:
        context_str = "\n\n".join(context) if context else ""
        prompt = f"""
        You are a legal education AI assistant. Provide a clear, educational explanation about {topic}.
        
        Question: {question}
        
        Relevant case law and context:
        {context_str}
        
        Please provide a comprehensive but accessible explanation suitable for law students.
        Include relevant legal principles, examples, and practical applications.
        Structure your response with clear headings and bullet points where appropriate.
        """
        
        return await self.generate_response(prompt)

llm_service = LLMService()