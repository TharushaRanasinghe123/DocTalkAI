import datetime
from fastapi import APIRouter, HTTPException, Query
from app.services.mongodb_service import mongodb_service
from app.models.appointment import AppointmentCreate, AppointmentResponse
from bson import ObjectId


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

# @router.get("/appointments/{appointment_id}", response_model=dict)
# async def get_appointment(appointment_id: str):
#     """Get a specific appointment"""
#     appointment = await mongodb_service.get_appointment(appointment_id)
#     if appointment:
#         return {"appointment": appointment}
#     raise HTTPException(status_code=404, detail="Appointment not found")

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

# @router.post("/appointments/{appointment_id}/reschedule", response_model=dict)
# async def reschedule_appointment(appointment_id: str, date: str, time: str = None):
#     """Reschedule an appointment"""
#     success = await mongodb_service.reschedule_appointment(appointment_id, date, time)
#     if success:
#         return {"message": "Appointment rescheduled successfully"}
#     raise HTTPException(status_code=404, detail="Appointment not found or reschedule failed")

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

# Get appointments for a specific doctor with filtering
@router.get("/doctors/{doctor_id}/appointments")
async def get_doctor_appointments(
    doctor_id: str,
    appointment_date: str = Query(None, description="Date in YYYY-MM-DD format"),
    status: str = Query(None, description="Filter by status (scheduled, completed, cancelled)")
):
    """
    Get appointments for a specific doctor with optional date and status filtering
    """
    try:
        # First get the doctor's name from their ID
        doctor = await mongodb_service.db.users.find_one(
            {"_id": ObjectId(doctor_id), "role": "doctor"}
        )
        
        if not doctor:
            raise HTTPException(status_code=404, detail="Doctor not found")
        
        doctor_name = doctor.get("name")
        if not doctor_name:
            raise HTTPException(status_code=404, detail="Doctor name not found")
        
        # Build query using doctor's name (since appointments have doctorName field)
        query = {"doctorName": doctor_name}
        
        if appointment_date:
            query["date"] = appointment_date
            
        if status:
            query["status"] = status
        
        # Get appointments from MongoDB
        appointments = []
        async for appointment in mongodb_service.db.appointments.find(query):
            # Convert ObjectId to string and format the response
            appointment["id"] = str(appointment["_id"])
            del appointment["_id"]
            
            # Convert datetime objects to ISO format for JSON serialization
            for key, value in appointment.items():
                if isinstance(value, datetime.datetime):
                    appointment[key] = value.isoformat()
                    
            appointments.append(appointment)
            
        return {"appointments": appointments}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch appointments: {str(e)}")
    

# Update appointment status (simplified version)
@router.put("/appointments/{appointment_id}/status")
async def update_appointment_status(
    appointment_id: str,
    status_data: dict  # Expecting {"status": "new_status"}
):
    """
    Update appointment status (scheduled, completed, cancelled)
    """
    try:
        # Simplified status system
        valid_statuses = ["completed", "cancelled", "booked"]
        new_status = status_data.get("status")
        
        if new_status not in valid_statuses:
            raise HTTPException(
                status_code=400, 
                detail=f"Invalid status value. Must be one of: {valid_statuses}"
            )
        
        # Update appointment in MongoDB
        result = await mongodb_service.db.appointments.update_one(
            {"appointment_id": appointment_id},
            {"$set": {
                "status": new_status,
                "updatedAt": datetime.datetime.utcnow()
            }}
        )
        
        if result.modified_count == 0:
            raise HTTPException(status_code=404, detail="Appointment not found")
            
        return {
            "message": f"Appointment status updated to {new_status}",
            "appointment_id": appointment_id,
            "new_status": new_status
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update appointment: {str(e)}")