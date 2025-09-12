# app/models/conversation_state.py
from pydantic import BaseModel
from typing import Dict, List, Optional
from app.models.intent_model import IntentType

class ConversationState(BaseModel):
    # A unique identifier for this conversation (e.g., WebSocket connection ID)
    session_id: str
    # What the user is currently trying to do (e.g., book_appointment)
    current_intent: Optional[IntentType] = None
    # The details the user has already provided
    # Example: {"patient_name": "Tausha", "doctor_name": "Kavin"}
    collected_entities: Dict[str, str] = {}
    # The details we still NEED to ask for
    # Example: If REQUIREMENTS_MAP says we need 4 things and user gave 2, this will be ["date", "time"]
    missing_requirements: List[str] = []
    # Flag to check if we have everything needed to talk to the database
    is_fulfilled: bool = False

    def reset(self):
        """Resets the conversation state to a clean slate."""
        self.current_intent = None
        self.collected_entities = {}
        self.missing_requirements = []
        self.is_fulfilled = False