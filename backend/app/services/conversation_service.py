# backend/app/services/conversation_service.py
from typing import Dict, List, Tuple
from app.models.conversation import ConversationState
from app.models.intent_model import IntentType, IntentResponse
from app.services.openai_service import openai_service  # Import to access REQUIREMENTS_MAP

class ConversationService:
    
    async def process_intent(self, intent_response: IntentResponse, current_state: ConversationState) -> Tuple[str, ConversationState]:
        """
        The CORE LOGIC: Checks if we have enough info to act, or if we need to ask the user for more.
        Returns: (response_text: str, updated_state: ConversationState)
        """
        # Get the list of valid entity combinations for this intent
        valid_combinations = openai_service.REQUIREMENTS_MAP.get(intent_response.intent, [])
        
        # If this is a new intent, reset the state and figure out what we need
        if current_state.current_intent != intent_response.intent:
            current_state.current_intent = intent_response.intent
            # Start with the entities GPT just extracted
            current_state.collected_entities = intent_response.entities
            current_state.missing_requirements = []  # We'll calculate this below
        else:
            # We are in the middle of a conversation for the same intent
            # The user's new transcript is the answer to our last question
            if current_state.missing_requirements:
                next_entity = current_state.missing_requirements[0]
                # Assume the user's entire response is the value for the entity we asked for
                if intent_response.entities:
                    current_state.collected_entities.update(intent_response.entities)
                # We've collected it, so remove it from the missing list
                current_state.missing_requirements.pop(0)

        # Check if ANY of the valid combinations are fully satisfied by our collected_entities
        is_requirement_met = False
        for combination in valid_combinations:
            # Check if every entity in this combination is present and not null/empty
            if all(current_state.collected_entities.get(entity) for entity in combination):
                is_requirement_met = True
                break  # We found one valid combination, that's enough!

        if is_requirement_met:
            # WE HAVE EVERYTHING! Now we can proceed to database actions.
            response_text = self._generate_confirmation_message(intent_response.intent, current_state.collected_entities)
            # Reset state after successful completion
            current_state.reset()
        else:
            # WE STILL NEED MORE INFO. Figure out the SMARTEST question to ask.
            next_entity_to_ask = self._find_next_required_entity(valid_combinations, current_state.collected_entities)
            if next_entity_to_ask:
                response_text = self._generate_clarification_question(next_entity_to_ask, intent_response.intent)
                current_state.missing_requirements = [next_entity_to_ask]  # Now we are waiting for this
            else:
                # Fallback: shouldn't happen often, but if we can't figure out what to ask.
                response_text = "I need more information to help you with that. Could you please provide more details?"
                current_state.missing_requirements = []

        return response_text, current_state

    def _find_next_required_entity(self, valid_combinations, collected_entities):
        """
        Smart logic to find the most important entity to ask for next.
        This is a simple implementation - you can make it more complex.
        """
        # Flatten all required entities across all combinations
        all_required_entities = set()
        for combination in valid_combinations:
            all_required_entities.update(combination)
        
        # Find which required entities we are still missing
        missing_entities = [entity for entity in all_required_entities if not collected_entities.get(entity)]
        
        # Just return the first missing entity as a simple strategy.
        # A more advanced strategy would prioritize entities that appear in the most combinations.
        return missing_entities[0] if missing_entities else None

    def _generate_clarification_question(self, missing_entity: str, intent: IntentType) -> str:
        """Generates a natural language question to ask for missing information."""
        questions = {
            "patient_name": "Sure, may I please have your full name?",
            "date": "What date are you referring to?",
            "time": "What time do you have in mind?",
            "doctor_name": "Which doctor would you like to see?",
            "new_date": "What is the new date you'd like to reschedule to?",
            "new_time": "What is the new time you'd prefer?",
            "appointment_id": "Could you please provide your appointment ID or reference number?",
        }
        return questions.get(missing_entity, "Could you please provide that information?")

    def _generate_confirmation_message(self, intent: IntentType, entities: Dict) -> str:
        """Generates a confirmation message before acting (will later trigger DB)."""
        # Check which combination was satisfied
        valid_combinations = openai_service.REQUIREMENTS_MAP.get(intent, [])
        used_combination = None
        for combination in valid_combinations:
            if all(entities.get(entity) for entity in combination):
                used_combination = combination
                break

        if intent == IntentType.CANCEL_APPOINTMENT:
            if used_combination == ["appointment_id"]:
                return f"Okay, I will cancel appointment {entities['appointment_id']}."
            else:  # must be ["patient_name", "date"]
                return f"Okay, I will cancel the appointment for {entities['patient_name']} on {entities['date']}."

        elif intent == IntentType.BOOK_APPOINTMENT:
            return f"Great! I'll book an appointment for {entities['patient_name']} with {entities['doctor_name']} on {entities['date']} at {entities['time']}."

        elif intent == IntentType.RESCHEDULE_APPOINTMENT:
            if used_combination == ["appointment_id", "new_date", "new_time"]:
                return f"Okay, I will reschedule appointment {entities['appointment_id']} to {entities['new_date']} at {entities['new_time']}."
            else:  # must be ["patient_name", "date", "new_date", "new_time"]
                return f"Okay, I will reschedule the appointment for {entities['patient_name']} from {entities['date']} to {entities['new_date']} at {entities['new_time']}."

        return "Okay, I'll proceed with that."


# Create global instance - THIS IS WHAT THE TEST IS TRYING TO IMPORT
conversation_service = ConversationService()