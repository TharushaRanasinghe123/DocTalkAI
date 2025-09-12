# app/services/conversation_service.py
from typing import Tuple
from app.models.conversation_state import ConversationState
from app.models.intent_model import IntentResponse, IntentType
from app.services.openai_service import openai_service # Import the REQUIREMENTS_MAP

class ConversationService:
    # This will store active conversations in memory (for now)
    def __init__(self):
        self.active_conversations: Dict[str, ConversationState] = {}

    async def process_intent(self, intent_response: IntentResponse, session_id: str) -> Tuple[str, bool]:
        """
        The CORE LOGIC.
        Takes the user's intent and the current session, and decides what to do next.
        Returns: (response_text, should_speak)
        """
            # 0. Handle the case where this is an answer to a previous question
        current_state = self.active_conversations.get(session_id, ConversationState(session_id=session_id))
        
        # FIX: If this is an unknown intent BUT we have an active conversation, treat it as an answer
        if (intent_response.intent == IntentType.UNKNOWN and 
            current_state.current_intent and 
            current_state.missing_requirements):
            
            print(f"🔍 Treating unknown intent as response to previous question: {intent_response.raw_transcript}")
            # Assume this is answering our last question
            intent_response.intent = current_state.current_intent
            
            # Try to extract entities from what might be the answer
            if current_state.missing_requirements:
                next_requirement = current_state.missing_requirements[0]
                # For appointment IDs, we can try to extract numbers from the raw transcript
                if next_requirement == "appointment_id":
                    # Simple extraction: look for numbers in the transcript
                    import re
                    numbers = re.findall(r'\d+', intent_response.raw_transcript)
                    if numbers:
                        intent_response.entities["appointment_id"] = " ".join(numbers)
                        print(f"✅ Extracted appointment_id from numbers: {intent_response.entities['appointment_id']}")
                else:
                    # For other requirements, use the raw transcript as the value
                    intent_response.entities[next_requirement] = intent_response.raw_transcript
                    print(f"📝 Using raw transcript for {next_requirement}: {intent_response.raw_transcript}")
        
        # 1. Get or create the conversation state for this session
        current_state = self.active_conversations.get(session_id, ConversationState(session_id=session_id))

        # 2. Check if this is a new intent or a response to a previous question
        if current_state.current_intent != intent_response.intent:
            # It's a NEW INTENT! Reset and start fresh.
            current_state.reset()
            current_state.current_intent = intent_response.intent
            # Start with the entities OpenAI just extracted
            current_state.collected_entities = intent_response.entities
            # Figure out what we're missing
            required_slots = openai_service.REQUIREMENTS_MAP.get(intent_response.intent, [])
            current_state.missing_requirements = [
                slot for slot in required_slots 
                if not intent_response.entities.get(slot) # Check if the slot is missing
            ]

        else:
            # It's the SAME INTENT. The user is probably answering our last question.
            if current_state.missing_requirements:
                next_slot = current_state.missing_requirements[0]
                
                # NEW FIXED CODE: Use extracted entity if available, otherwise use raw transcript
                if next_slot in intent_response.entities:
                    # YES! OpenAI found the exact entity we were looking for
                    slot_value = intent_response.entities[next_slot]
                    print(f"✅ Extracted {next_slot}: {slot_value}")
                else:
                    # OpenAI didn't find it, so use the raw transcript as a fallback
                    slot_value = intent_response.raw_transcript
                    print(f"⚠️  Using raw transcript for {next_slot}: {slot_value}")
                
                current_state.collected_entities[next_slot] = slot_value
                current_state.missing_requirements.pop(0)  # Remove from missing list

            # CRITICAL: Check if user provided OTHER entities we need
            for slot, value in intent_response.entities.items():
                if slot in current_state.missing_requirements:  # Don't double-process
                    print(f"🎁 Bonus extracted {slot}: {value}")
                    current_state.collected_entities[slot] = value
                    if slot in current_state.missing_requirements:
                        current_state.missing_requirements.remove(slot)

        # 3. Save the updated state
        self.active_conversations[session_id] = current_state

        # 4. Check: Do we have everything we need?
        if not current_state.missing_requirements:
            # YES! We are ready to talk to the database.
            current_state.is_fulfilled = True
            # For now, just confirm. Later, this will trigger a DB insert.
            response_text = self._generate_confirmation_message(current_state)
            # Reset after fulfilling
            current_state.reset()
            return response_text, True
        else:
            # NO. We need to ask for the next piece of information.
            next_slot = current_state.missing_requirements[0]
            response_text = self._generate_question(next_slot, intent_response.intent)
            return response_text, True

    def _generate_question(self, missing_slot: str, intent: IntentType) -> str:
        """Generates a natural language question to ask for missing information."""
        questions = {
            "patient_name": "Sure, may I please have your full name?",
            "date": "What date would you like to book for?",
            "time": "What time works best for you?",
            "doctor_name": "Which doctor would you like to see?",
            "appointment_id": "Could you please provide your appointment ID?",
            "new_date": "What is the new date you'd prefer?",
            "new_time": "What is the new time you'd prefer?",
        }
        return questions.get(missing_slot, "Could you please provide that information?")

    def _generate_confirmation_message(self, state: ConversationState) -> str:
        """Generates a confirmation message with the collected info."""
        # Build a simple confirmation message from the collected entities
        details = ", ".join([f"{k}: {v}" for k, v in state.collected_entities.items()])
        return f"Great! I will process your request for: {details}."

# Create a global instance
conversation_service = ConversationService()