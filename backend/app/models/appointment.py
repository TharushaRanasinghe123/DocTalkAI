from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class AppointmentCreate(BaseModel):
    patientName: str
    doctorName: str
    date: str
    time: str
    reason: Optional[str] = None

class AppointmentResponse(BaseModel):
    id: str
    patientName: str
    doctorName: str
    date: str
    time: str
    reason: Optional[str] = None
    status: str
    createdAt: datetime
    updatedAt: datetime