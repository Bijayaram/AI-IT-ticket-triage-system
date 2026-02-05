"""
Gemini-based response generation.
IMPORTANT: Gemini is ONLY used for generating draft replies (NOT for embeddings or classification).
"""
import google.generativeai as genai
import os
import json
import logging
from typing import Dict, Any, List, Optional
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)


class GeminiReplyGenerator:
    """
    Generate draft replies using Gemini API.
    Returns STRICT JSON format for structured responses.
    """
    
    DEFAULT_MODEL = "gemini-2.5-flash"
    
    def __init__(self, api_key: Optional[str] = None, model_name: Optional[str] = None):
        """
        Initialize Gemini reply generator.
        
        Args:
            api_key: Gemini API key (default: from GEMINI_API_KEY env var)
            model_name: Model name (default: gemini-2.0-flash-exp)
        """
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY not found in environment variables")
        
        self.model_name = model_name or self.DEFAULT_MODEL
        
        # Configure Gemini
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel(self.model_name)
        
        logger.info(f"✓ Gemini reply generator initialized: {self.model_name}")
    
    def generate_reply(
        self,
        subject: str,
        body: str,
        predicted_queue: str,
        is_critical: bool,
        similar_tickets: Optional[List[Dict[str, Any]]] = None,
        max_retries: int = 3
    ) -> Dict[str, Any]:
        """
        Generate a draft reply for a ticket.
        
        Args:
            subject: Ticket subject
            body: Ticket body
            predicted_queue: Predicted department/queue
            is_critical: Whether ticket is critical
            similar_tickets: List of similar historical tickets (RAG context)
            max_retries: Maximum retry attempts
            
        Returns:
            Dictionary with:
            {
                "success": bool,
                "language": str,
                "subject": str,
                "body": str,
                "confidence": float (0-1),
                "needs_human_approval": bool,
                "suggested_tags": List[str],
                "error": Optional[str]
            }
        """
        # Build prompt with RAG context
        prompt = self._build_prompt(subject, body, predicted_queue, is_critical, similar_tickets)
        
        # Try generation with retries
        for attempt in range(max_retries):
            try:
                response = self.model.generate_content(
                    prompt,
                    generation_config={
                        "temperature": 0.3,
                        "top_p": 0.95,
                        "max_output_tokens": 2048,
                    }
                )
                
                # Parse JSON response
                result = self._parse_response(response.text)
                
                # Apply business rules
                result = self._apply_business_rules(result, is_critical)
                
                result["success"] = True
                return result
                
            except json.JSONDecodeError as e:
                logger.warning(f"JSON parse error (attempt {attempt+1}/{max_retries}): {e}")
                if attempt == max_retries - 1:
                    return self._error_response("Failed to parse Gemini response as JSON")
            
            except Exception as e:
                logger.error(f"Gemini generation error (attempt {attempt+1}/{max_retries}): {e}")
                if attempt == max_retries - 1:
                    return self._error_response(str(e))
        
        return self._error_response("Max retries exceeded")
    
    def _build_prompt(
        self,
        subject: str,
        body: str,
        predicted_queue: str,
        is_critical: bool,
        similar_tickets: Optional[List[Dict[str, Any]]]
    ) -> str:
        """Build prompt with RAG context"""
        
        prompt = f"""You are an expert IT support assistant. Generate a professional draft reply for the following IT support ticket.

TICKET INFORMATION:
Subject: {subject}
Body: {body}
Department: {predicted_queue}
Priority: {"HIGH (CRITICAL)" if is_critical else "Normal"}

"""
        
        # Add similar tickets as RAG context
        if similar_tickets and len(similar_tickets) > 0:
            prompt += "SIMILAR HISTORICAL TICKETS (for reference):\n\n"
            for i, ticket in enumerate(similar_tickets[:3], 1):
                prompt += f"Example {i}:\n"
                prompt += f"Subject: {ticket.get('subject', 'N/A')}\n"
                prompt += f"Issue: {ticket.get('body', 'N/A')[:200]}...\n"
                prompt += f"Resolution: {ticket.get('answer', 'N/A')[:200]}...\n"
                prompt += f"Queue: {ticket.get('queue', 'N/A')}\n\n"
        
        prompt += """
INSTRUCTIONS:
1. Draft a professional, helpful reply suitable for corporate IT support
2. Detect the language of the ticket and respond in the SAME language
3. If information is missing, ask 1-2 specific clarifying questions
4. Do NOT hallucinate policies or make up information
5. Use the similar tickets above as reference for tone and approach (if provided)
6. Be concise but thorough

OUTPUT FORMAT (STRICT JSON ONLY):
Return ONLY a valid JSON object (no markdown, no explanation) with this exact structure:
{
  "language": "en|de|es|fr|etc",
  "subject": "Reply subject line",
  "body": "Full reply body text",
  "confidence": 0.0-1.0,
  "needs_human_approval": true|false,
  "suggested_tags": ["tag1", "tag2", "tag3"]
}

IMPORTANT: Return ONLY the JSON object, nothing else.
"""
        
        return prompt
    
    def _parse_response(self, response_text: str) -> Dict[str, Any]:
        """Parse and validate Gemini response"""
        
        # Clean response (remove markdown if present)
        response_text = response_text.strip()
        if response_text.startswith("```json"):
            response_text = response_text[7:]
        if response_text.startswith("```"):
            response_text = response_text[3:]
        if response_text.endswith("```"):
            response_text = response_text[:-3]
        response_text = response_text.strip()
        
        # Parse JSON
        result = json.loads(response_text)
        
        # Validate required fields
        required_fields = ["language", "subject", "body", "confidence", "needs_human_approval"]
        for field in required_fields:
            if field not in result:
                raise ValueError(f"Missing required field: {field}")
        
        # Ensure suggested_tags is a list
        if "suggested_tags" not in result:
            result["suggested_tags"] = []
        
        # Validate confidence range
        result["confidence"] = max(0.0, min(1.0, float(result["confidence"])))
        
        return result
    
    def _apply_business_rules(self, result: Dict[str, Any], is_critical: bool) -> Dict[str, Any]:
        """
        Apply business rules to override Gemini decisions.
        
        Business rules:
        1. If ticket is critical => needs_human_approval MUST be true
        2. If confidence < threshold => route to human approval
        """
        confidence_threshold = float(os.getenv("CONFIDENCE_THRESHOLD", "0.7"))
        
        # Rule 1: Critical tickets ALWAYS need approval
        if is_critical:
            result["needs_human_approval"] = True
        
        # Rule 2: Low confidence needs approval
        if result["confidence"] < confidence_threshold:
            result["needs_human_approval"] = True
        
        return result
    
    def _error_response(self, error_msg: str) -> Dict[str, Any]:
        """Generate error response (routes to human)"""
        return {
            "success": False,
            "language": "en",
            "subject": "Error generating reply",
            "body": "An error occurred while generating the response. This ticket requires human attention.",
            "confidence": 0.0,
            "needs_human_approval": True,
            "suggested_tags": ["error", "needs_review"],
            "error": error_msg
        }


# Global generator instance
_generator = None


def get_generator(api_key: Optional[str] = None) -> GeminiReplyGenerator:
    """
    Get global generator instance (singleton pattern).
    
    Args:
        api_key: Gemini API key (optional)
        
    Returns:
        GeminiReplyGenerator instance
    """
    global _generator
    if _generator is None:
        _generator = GeminiReplyGenerator(api_key=api_key)
    return _generator
