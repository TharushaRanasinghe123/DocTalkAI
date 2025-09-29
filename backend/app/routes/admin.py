from fastapi import APIRouter, HTTPException, status, Depends
from app.models.user import UserCreateByAdmin
from app.services.mongodb_service import mongodb_service
from app.utils.auth import get_password_hash
import datetime
from datetime import datetime

router = APIRouter(tags=["Admin"])

@router.post("/admin/doctors")
async def add_doctor(doctor_data: UserCreateByAdmin):
    """Admin endpoint to add new doctors"""
    try:
        # Check if user already exists
        existing_user = await mongodb_service.find_user_by_email(doctor_data.email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        # Hash the password
        hashed_password = get_password_hash(doctor_data.password)
        
        # Create doctor user document
        doctor_dict = {
            "email": doctor_data.email,
            "name": doctor_data.name,
            "hashed_password": hashed_password,
            "role": "doctor",
            "specialization": doctor_data.specialization,
            "force_password_change": True,  # Doctor must change password on first login
            "created_at": datetime.datetime.utcnow()
        }
        
        # Insert into database
        doctor_id = await mongodb_service.create_user(doctor_dict)
        
        return {
            "message": "Doctor added successfully",
            "doctor_id": str(doctor_id),
            "email": doctor_data.email,
            "temporary_password": doctor_data.password  # In real app, don't return this!
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to add doctor: {str(e)}"
        )
    
@router.get("/admin/stats")
async def get_admin_stats():
    """Get statistics for admin dashboard"""
    try:
        # Get total patients
        total_patients = await mongodb_service.db.users.count_documents({"role": "patient"})
        
        # Get total doctors
        total_doctors = await mongodb_service.db.users.count_documents({"role": "doctor"})
        
        # Get today's appointments
        today = datetime.now().strftime("%Y-%m-%d")
        today_appointments = await mongodb_service.db.appointments.count_documents({
            "date": today,
            "status": {"$in": ["booked", "scheduled"]}
        })
        
        # Get monthly revenue (placeholder)
        monthly_revenue = 12845
        
        return {
            "total_patients": total_patients,
            "total_doctors": total_doctors,
            "today_appointments": today_appointments,
            "monthly_revenue": f"${monthly_revenue:,}"
        }
        
    except Exception as e:
        print(f"Error fetching stats: {e}")
        return {
            "total_patients": 0,
            "total_doctors": 0,
            "today_appointments": 0,
            "monthly_revenue": "$0"
        }
    
# Add to app/routes/admin.py
@router.get("/admin/doctors")
async def get_all_doctors():
    """Get all doctors with filtering options"""
    try:
        doctors = []
        async for doctor in mongodb_service.db.users.find({"role": "doctor"}):
            doctors.append({
                "id": str(doctor["_id"]),
                "name": doctor.get("name", ""),
                "email": doctor.get("email", ""),
                "specialization": doctor.get("specialization", "General"),
                "created_at": doctor.get("created_at", ""),
                "force_password_change": doctor.get("force_password_change", False)
            })
        
        return {"doctors": doctors}
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch doctors: {str(e)}"
        )
    
@router.get("/admin/patients")
async def get_all_patients():
    """Get all patients with their details"""
    try:
        patients = []
        async for patient in mongodb_service.db.users.find({"role": "patient"}):
            # Get patient's appointments count
            appointment_count = await mongodb_service.db.appointments.count_documents({
                "patient_name": patient.get("name", "")
            })
            
            # Get latest appointment
            latest_appointment = await mongodb_service.db.appointments.find_one({
                "patient_name": patient.get("name", "")
            }, sort=[("date", -1)])
            
            patients.append({
                "id": str(patient["_id"]),
                "name": patient.get("name", ""),
                "email": patient.get("email", ""),
                "phone": patient.get("phone", ""),
                "created_at": patient.get("created_at", ""),
                "appointment_count": appointment_count,
                "latest_appointment": latest_appointment.get("date") if latest_appointment else "No appointments",
                "status": "Active"  # You can add more status logic here
            })
        
        return {"patients": patients}
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch patients: {str(e)}"
        )

@router.get("/admin/patients/{patient_id}/appointments")
async def get_patient_appointments(patient_id: str):
    """Get all appointments for a specific patient"""
    try:
        from bson import ObjectId
        
        # Get patient details
        patient = await mongodb_service.db.users.find_one({
            "_id": ObjectId(patient_id),
            "role": "patient"
        })
        
        if not patient:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Patient not found"
            )
        
        # Get patient's appointments
        appointments = []
        async for appointment in mongodb_service.db.appointments.find({
            "patient_name": patient.get("name", "")
        }).sort("date", -1):
            appointments.append({
                "id": str(appointment.get("_id", "")),
                "appointment_id": appointment.get("appointment_id", ""),
                "doctor_name": appointment.get("doctor_name", ""),
                "date": appointment.get("date", ""),
                "time": appointment.get("time", ""),
                "status": appointment.get("status", ""),
                "reason": appointment.get("reason", "")
            })
        
        return {
            "patient": {
                "name": patient.get("name", ""),
                "email": patient.get("email", ""),
                "phone": patient.get("phone", "")
            },
            "appointments": appointments
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch patient appointments: {str(e)}"
        )

@router.get("/admin/appointments")
async def get_all_appointments():
    """Get all appointments for admin view"""
    try:
        appointments = []
        async for appointment in mongodb_service.db.appointments.find().sort("date", -1):
            appointments.append({
                "id": str(appointment.get("_id", "")),
                "appointment_id": appointment.get("appointment_id", ""),
                "patient_name": appointment.get("patient_name", ""),
                "doctor_name": appointment.get("doctor_name", ""),
                "date": appointment.get("date", ""),
                "time": appointment.get("time", ""),
                "status": appointment.get("status", ""),
                "reason": appointment.get("reason", ""),
                "created_at": appointment.get("created_at", "")
            })
        
        return {"appointments": appointments}
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch appointments: {str(e)}"
        )