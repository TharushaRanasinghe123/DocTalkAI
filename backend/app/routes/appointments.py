from fastapi import APIRouter, HTTPException
from app.services.mongodb_service import mongodb_service
from app.models.appointment import AppointmentCreate, AppointmentResponse

router = APIRouter()

@router.post("/appointments", response_model=dict)
async def create_appointment(appointment: AppointmentCreate):
    """Create a new appointment"""
    appointment_id = await mongodb_service.insert_appointment(appointment.dict())
    if appointment_id:
        return {"message": "Appointment created successfully", "appointment_id": appointment_id}
    raise HTTPException(status_code=500, detail="Failed to create appointment")

@router.get("/appointments", response_model=dict)
async def get_all_appointments():
    """Get all appointments"""
    appointments = await mongodb_service.get_all_appointments()
    return {"appointments": appointments, "count": len(appointments)}

@router.get("/appointments/{appointment_id}", response_model=dict)
async def get_appointment(appointment_id: str):
    """Get a specific appointment"""
    appointment = await mongodb_service.get_appointment(appointment_id)
    if appointment:
        return {"appointment": appointment}
    raise HTTPException(status_code=404, detail="Appointment not found")

@router.post("/appointments/{appointment_id}/cancel", response_model=dict)
async def cancel_appointment(appointment_id: str):
    """Cancel an appointment"""
    success = await mongodb_service.cancel_appointment(appointment_id)
    if success:
        return {"message": "Appointment cancelled successfully"}
    raise HTTPException(status_code=404, detail="Appointment not found or already cancelled")

@router.post("/appointments/{appointment_id}/reschedule", response_model=dict)
async def reschedule_appointment(appointment_id: str, date: str, time: str = None):
    """Reschedule an appointment"""
    success = await mongodb_service.reschedule_appointment(appointment_id, date, time)
    if success:
        return {"message": "Appointment rescheduled successfully"}
    raise HTTPException(status_code=404, detail="Appointment not found or reschedule failed")

@router.get("/appointments/{appointment_id}/details", response_model=dict)
async def get_appointment_details(appointment_id: str):
    """Get appointment details including date and time"""
    appointment = await mongodb_service.get_appointment_by_id(appointment_id)
    if appointment:
        return {
            "message": "Appointment details",
            "appointment": appointment
        }
    raise HTTPException(status_code=404, detail="Appointment not found")

@router.post("/appointments/{appointment_id}/reschedule", response_model=dict)
async def reschedule_appointment(appointment_id: str, date: str, time: str = None):
    """Reschedule an appointment"""
    success = await mongodb_service.reschedule_appointment(appointment_id, date, time)
    if success:
        return {"message": "Appointment rescheduled successfully"}
    raise HTTPException(status_code=404, detail="Appointment not found or reschedule failed")

@router.get("/appointments/{appointment_id}", response_model=dict)
async def get_appointment(appointment_id: str):
    """Get a specific appointment's details"""
    appointment = await mongodb_service.get_appointment_by_id(appointment_id)
    if appointment:
        return {
            "message": "Appointment details",
            "appointment": appointment
        }
    raise HTTPException(status_code=404, detail="Appointment not found")