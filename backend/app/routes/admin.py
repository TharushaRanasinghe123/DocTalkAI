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