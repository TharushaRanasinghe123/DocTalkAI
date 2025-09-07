# backend/app/models/conversation.py
from typing import Optional, Dict, List
from app.models.intent_model import IntentType
from pydantic import BaseModel

class ConversationState(BaseModel):
    """Tracks the context of an ongoing conversation within a WebSocket session."""
    current_intent: Optional[IntentType] = None
    collected_entities: Dict = {}  # What the user has provided so far (e.g., {'date': '2024-01-25'})
    missing_requirements: List[str] = []  # What we still need to ask for (e.g., ['patient_name'])

    def reset(self):
        """Reset the state for a new conversation."""
        self.current_intent = None
        self.collected_entities = {}
        self.missing_requirements = []