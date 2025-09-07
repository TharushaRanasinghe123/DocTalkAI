# backend/app/services/openai_service.py
import os
import json
import logging
from openai import AsyncOpenAI
from dotenv import load_dotenv
from typing import Dict, Any, Optional
from app.models.intent_model import IntentResponse, IntentType
from datetime import datetime


# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class OpenAIService:

    REQUIREMENTS_MAP = {
        IntentType.BOOK_APPOINTMENT: [
            ["patient_name", "doctor_name", "date", "time"] # Only one way to book: need all details.
        ],
        IntentType.RESCHEDULE_APPOINTMENT: [
            ["appointment_id", "new_date", "new_time"],         # Option 1: Use the appointment ID
            ["patient_name", "date", "new_date", "new_time"]    # Option 2: Use name + old date
        ],
        IntentType.CANCEL_APPOINTMENT: [
            ["appointment_id"],                 # Option 1: Easiest! Just the ID.
            ["patient_name", "date"]            # Option 2: Use name + date.
        ],
        IntentType.QUERY_AVAILABILITY: [
            ["doctor_name", "date"]             # Need to know who and when to check.
        ]
        # GREETING, THANKS, UNKNOWN require no specific entities
    }

    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY not set in environment variables")
        
        self.client = AsyncOpenAI(api_key=self.api_key)
        self.model = "gpt-4o-mini"  # Using GPT-4o-mini as specified
    
    async def analyze_intent(self, transcript: str) -> IntentResponse:
        """
        Analyze transcript to extract intent and entities using GPT-4o-mini
        """
        try:
            # Create the prompt for intent analysis
            prompt = self._create_intent_prompt(transcript)
            
            # Call OpenAI API
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": self._get_system_prompt()
                    },
                    {
                        "role": "user", 
                        "content": prompt
                    }
                ],
                temperature=0.1,
                max_tokens=500,
                response_format={"type": "json_object"}
            )
            
            # Parse the response
            result = json.loads(response.choices[0].message.content)
            print(f"📊 Raw OpenAI response: {result}")

            # Convert to IntentResponse
            intent_response = self._parse_intent_response(result, transcript)
            print(f"🎯 Final IntentResponse: {intent_response.dict()}")
        
            return intent_response
        
        except Exception as e:
            logger.error(f"Error in OpenAI intent analysis: {e}")
            # Return default response on error
            return IntentResponse(
                intent=IntentType.UNKNOWN,
                entities={},
                confidence=0.0,
                raw_transcript=transcript,
                processed_response="Sorry, I couldn't process that request."
            )
    
    def _create_intent_prompt(self, transcript: str) -> str:
        """Create the prompt for intent analysis"""
        return f"""
        Analyze this patient message and extract the intent and relevant details:

        Message: "{transcript}"

        Respond with JSON only in this exact format:
        {{
            "intent": "book_appointment|reschedule_appointment|cancel_appointment|query_availability|greeting|thanks|unknown",
            "entities": {{
                "doctor_name": "string or null",
                "doctor_specialization": "string or null", 
                "date": "string or null",
                "time": "string or null", 
                "reason": "string or null",
                "patient_name": "string or null",
                "appointment_id": "string or null"
            }},
            "confidence": 0.95,
            "processed_response": "A natural language response to the patient"
        }}
        """
    
    def _get_system_prompt(self) -> str:
        """System prompt for the AI assistant"""
        today_date = datetime.now().strftime("%Y-%m-%d")
        return f"""
        You are a medical appointment assistant for a GP clinic. Analyze patient messages to understand their intent and extract relevant information.

        Common intents:
        - book_appointment: Patient wants to schedule a new appointment
        - reschedule_appointment: Patient wants to change an existing appointment
        - cancel_appointment: Patient wants to cancel an appointment
        - query_availability: Patient is asking about available slots
        - greeting: Simple hello/good morning/etc.
        - thanks: Patient is thanking or ending conversation
        - unknown: Cannot determine intent

        **CRITICAL INSTRUCTION FOR DATES:**
        - Convert all relative dates (like "today", "tomorrow", "next Monday") into absolute dates in YYYY-MM-DD format.
        - Today's date is {today_date}. Use this as a reference for conversion.
        - Example: If today is {today_date} and patient says "tomorrow", output "2024-09-05".
        - If no specific date is mentioned, use null.

        Extract entities like doctor names, dates, times, reasons for visit, etc.
        Be accurate and return confidence scores appropriately.
        """
    
    def _parse_intent_response(self, result: Dict[str, Any], transcript: str) -> IntentResponse:
        """Parse OpenAI response into IntentResponse model"""
        try:
            # Map string intent to IntentType enum
            intent_str = result.get("intent", "unknown").lower()
            intent_type = IntentType.UNKNOWN
            
            if intent_str == "book_appointment":
                intent_type = IntentType.BOOK_APPOINTMENT
            elif intent_str == "reschedule_appointment":
                intent_type = IntentType.RESCHEDULE_APPOINTMENT
            elif intent_str == "cancel_appointment":
                intent_type = IntentType.CANCEL_APPOINTMENT
            elif intent_str == "query_availability":
                intent_type = IntentType.QUERY_AVAILABILITY
            elif intent_str == "greeting":
                intent_type = IntentType.GREETING
            elif intent_str == "thanks":
                intent_type = IntentType.THANKS
            
            return IntentResponse(
                intent=intent_type,
                entities=result.get("entities", {}),
                confidence=result.get("confidence", 0.0),
                raw_transcript=transcript,
                processed_response=result.get("processed_response")
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

# Create global instance
openai_service = OpenAIService()