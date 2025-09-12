# backend/app/services/openai_service.py
import os
import json
import logging
from openai import AsyncOpenAI
from dotenv import load_dotenv
from typing import Dict, Any, Optional, List
from app.models.intent_model import IntentResponse, IntentType
from datetime import datetime

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class OpenAIService:
    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY not set in environment variables")
        
        self.client = AsyncOpenAI(api_key=self.api_key)
        self.model = "gpt-4o-mini"
        self.conversation_history: Dict[str, List[Dict]] = {}  # session_id -> message history

    async def analyze_intent(self, transcript: str, session_id: str = "default") -> IntentResponse:
        """
        Analyze transcript with conversation context and extract intent/entities
        """
        try:
            # Get or create conversation history
            if session_id not in self.conversation_history:
                self.conversation_history[session_id] = [
                    {"role": "system", "content": self._get_system_prompt()}
                ]
            
            # Add user message to history
            self.conversation_history[session_id].append({
                "role": "user", 
                "content": f"Patient message: {transcript}"
            })
            
            # Call OpenAI with full conversation context
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=self.conversation_history[session_id],
                temperature=0.1,
                max_tokens=500,
                response_format={"type": "json_object"}
            )
            
            # Parse the response
            result = json.loads(response.choices[0].message.content)
            print(f"📊 Raw OpenAI response: {result}")

            # Add AI response to history
            self.conversation_history[session_id].append({
                "role": "assistant", 
                "content": json.dumps(result)
            })

            # Keep history manageable (last 10 messages)
            if len(self.conversation_history[session_id]) > 12:  # system + 10 turns
                self.conversation_history[session_id] = [
                    self.conversation_history[session_id][0]  # Keep system prompt
                ] + self.conversation_history[session_id][-10:]  # Keep last 10 messages

            # Convert to IntentResponse
            intent_response = self._parse_intent_response(result, transcript)
            print(f"🎯 Final IntentResponse: {intent_response.dict()}")
        
            return intent_response
        
        except Exception as e:
            logger.error(f"Error in OpenAI intent analysis: {e}")
            return IntentResponse(
                intent=IntentType.UNKNOWN,
                entities={},
                confidence=0.0,
                raw_transcript=transcript,
                processed_response="Sorry, I couldn't process that request."
            )
    
    def _get_system_prompt(self) -> str:
        """System prompt for the AI assistant with conversation awareness"""
        today_date = datetime.now().strftime("%Y-%m-%d")
        return f"""
    You are a medical appointment assistant for a GP clinic. You are having a conversation with a patient.

    **CONVERSATION RESPONSIBILITIES:**
    1. Understand the patient's intent in the context of our conversation
    2. Extract relevant entities intelligently
    3. Provide appropriate responses that move the conversation forward
    4. Remember what information we've already discussed

    **SMART ENTITY EXTRACTION:**
    - patient_name: Extract ONLY the name (e.g., "my name is John" → "John", "call me Sarah" → "Sarah")
    - doctor_name: Extract doctor name with title (e.g., "I want to see Dr. Smith" → "Dr. Smith")
    - appointment_id: Extract numbers/letters (e.g., "my ID is 123-ABC" → "123-ABC")
    - date: Convert to YYYY-MM-DD format (today: {today_date})
    - time: Convert to HH:MM format
    - new_date: Extract when rescheduling (e.g., "change to next Tuesday" → "YYYY-MM-DD")
    - new_time: Extract when rescheduling (e.g., "move to 2 PM" → "14:00")

    **QUERY APPOINTMENT FUNCTIONALITY:**
    - If patient asks about existing appointment details: intent=query_appointment
    - Extract appointment_id or patient_name for lookup
    - Examples: 
      "What's my appointment time?" → query_appointment
      "When is my booking with ID 123456?" → query_appointment, appointment_id=123456
      "Tell me about my appointment" → query_appointment
      "What are my appointment details?" → query_appointment

    **RESPONSE FORMAT:**
    Respond with JSON in this exact format:
    {{
        "intent": "book_appointment|reschedule_appointment|cancel_appointment|query_appointment|query_availability|greeting|thanks|unknown",
        "entities": {{
            "doctor_name": "extracted value or null",
            "doctor_specialization": "extracted value or null", 
            "date": "YYYY-MM-DD or null",
            "time": "HH:MM or null", 
            "reason": "extracted value or null",
            "patient_name": "extracted value or null",
            "appointment_id": "extracted value or null"
        }},
        "confidence": 0.0-1.0,
        "processed_response": "Natural language response that moves conversation forward"
    }}

    **CONVERSATION EXAMPLES:**
    - If patient says "my name is John" after you asked for name: intent=book_appointment, patient_name=John
    - If patient says "thanks": intent=thanks, processed_response="You're welcome!"
    - If patient provides incomplete info: ask for missing pieces naturally

    **RESCHEDULING VALIDATION:**
    - If patient provides appointment ID for rescheduling, acknowledge it
    - But don't assume rescheduling is possible until we check status
    - If appointment is cancelled, respond appropriately: "This appointment is cancelled and cannot be rescheduled"
    """
    
    def _parse_intent_response(self, result: Dict[str, Any], transcript: str) -> IntentResponse:
        """Parse OpenAI response into IntentResponse model"""
        try:
            # Map string intent to IntentType enum
            intent_str = result.get("intent", "unknown").lower()
            intent_type = IntentType.UNKNOWN
            
            intent_mapping = {
                "book_appointment": IntentType.BOOK_APPOINTMENT,
                "reschedule_appointment": IntentType.RESCHEDULE_APPOINTMENT,
                "cancel_appointment": IntentType.CANCEL_APPOINTMENT,
                "query_appointment": IntentType.QUERY_APPOINTMENT,
                "query_availability": IntentType.QUERY_AVAILABILITY,
                "greeting": IntentType.GREETING,
                "thanks": IntentType.THANKS
            }
            
            intent_type = intent_mapping.get(intent_str, IntentType.UNKNOWN)
            
            # Clean entities - remove None values
            entities = result.get("entities", {})
            cleaned_entities = {k: v for k, v in entities.items() if v is not None}
            
            return IntentResponse(
                intent=intent_type,
                entities=cleaned_entities,  # Only non-null entities
                confidence=result.get("confidence", 0.0),
                raw_transcript=transcript,
                processed_response=result.get("processed_response", "I understand.")
            )
            
        except Exception as e:
            logger.error(f"Error parsing intent response: {e}")
            return IntentResponse(
                intent=IntentType.UNKNOWN,
                entities={},
                confidence=0.0,
                raw_transcript=transcript,
                processed_response="Sorry, I encountered an error processing your request."
            )
    
    def clear_conversation_history(self, session_id: str):
        """Clear conversation history for a session"""
        if session_id in self.conversation_history:
            del self.conversation_history[session_id]

# Create global instance
openai_service = OpenAIService()