# backend/app/models/intent_model.py
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from enum import Enum

class IntentType(str, Enum):
    BOOK_APPOINTMENT = "book_appointment"
    RESCHEDULE_APPOINTMENT = "reschedule_appointment"
    CANCEL_APPOINTMENT = "cancel_appointment"
    QUERY_APPOINTMENT = "query_appointment"
    QUERY_AVAILABILITY = "query_availability"
    GREETING = "greeting"
    THANKS = "thanks"
    UNKNOWN = "unknown"

class IntentRequest(BaseModel):
    text: str

class IntentResponse(BaseModel):
    intent: IntentType
    entities: Dict[str, Any]
    confidence: float = Field(..., ge=0.0, le=1.0)
    raw_transcript: str
    processed_response: Optional[str] = None

# Example entity structure
class AppointmentEntities(BaseModel):
    doctor_name: Optional[str] = None
    doctor_specialization: Optional[str] = None
    date: Optional[str] = None
    time: Optional[str] = None
    reason: Optional[str] = None
    patient_name: Optional[str] = None
    appointment_id: Optional[str] = None