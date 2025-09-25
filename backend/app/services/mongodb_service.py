import os
from typing import Optional
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
from bson import ObjectId
from datetime import datetime
import random
import string

load_dotenv()

class MongoDBService:
    def __init__(self):
        self.uri = os.getenv("MONGODB_URI")
        self.db_name = "doctalk_db"
        self.client = None
        self.db = None
        self.users_collection = None
    
    async def connect(self):
        """Connect to MongoDB Atlas"""
        try:
            self.client = AsyncIOMotorClient(self.uri)
            # Test connection
            await self.client.admin.command('ping')
            self.db = self.client[self.db_name]
            self.users_collection = self.db['users']
            print("✅ Connected to MongoDB Atlas successfully!")
            return True
        except Exception as e:
            print(f"❌ MongoDB connection failed: {e}")
            return False
        
        
    async def insert_appointment(self, appointment_data: dict):
        """Insert a new appointment and return just the appointment ID string"""
        try:
            appointment_id = ''.join(random.choices(string.digits, k=6))
            # Add timestamps
            appointment_data.update({
                "appointment_id": appointment_id,
                "status": "booked",
                "createdAt": datetime.utcnow(),
                "updatedAt": datetime.utcnow()
            })
            
            # Insert and return just the ID string
            await self.db.appointments.insert_one(appointment_data)
            return appointment_id  # Return only the ID as string
            
        except Exception as e:
            print(f"❌ Failed to insert appointment: {e}")
            return None
        
    async def get_appointment(self, appointment_id: str):
        """Get a single appointment by ID"""
        try:
            appointment = await self.db.appointments.find_one({"appointment_id": appointment_id})
            if appointment:
                appointment["id"] = str(appointment["_id"])
                del appointment["_id"]

                # Convert any other ObjectId fields
                for key, value in appointment.items():
                    if isinstance(value, ObjectId):
                        appointment[key] = str(value)
                    elif isinstance(value, datetime):
                        appointment[key] = value.isoformat()
                return appointment
            return None
        except Exception as e:
            print(f"❌ Failed to get appointment: {e}")
            return None

    async def get_all_appointments(self):
        """Get all appointments"""
        try:
            appointments = []
            async for appointment in self.db.appointments.find():
                appointment["id"] = str(appointment["_id"])
                del appointment["_id"]  # Remove the ObjectId field
            
                # Also convert any other ObjectId fields if they exist
                for key, value in appointment.items():
                    if isinstance(value, ObjectId):
                        appointment[key] = str(value)
                appointments.append(appointment)
            return appointments
        except Exception as e:
            print(f"❌ Failed to get appointments: {e}")
            return []

    async def cancel_appointment(self, appointment_id: str) -> bool:
        """Cancel an appointment by ID"""
        try:
            result = await self.db.appointments.update_one(
                {"appointment_id": appointment_id},
                {"$set": {"status": "cancelled", "updatedAt": datetime.utcnow()}}
            )
            return result.modified_count > 0
        except Exception as e:
            print(f"❌ Failed to cancel appointment by ID: {e}")
            return False

    async def cancel_appointment_by_details(self, patient_name: str, date: str, time: str = None) -> bool:
        """Cancel an appointment by patient details"""
        try:
            # Build query
            query = {
                "patient_name": patient_name,
                "date": date,
                "status": "booked"  # Only cancel booked appointments
            }
            if time:
                query["time"] = time
                
            # Find the appointment
            appointment = await self.db.appointments.find_one(query)
            if not appointment:
                print(f"❌ No appointment found for {patient_name} on {date}")
                return False
                
            # Cancel it
            result = await self.db.appointments.update_one(
                {"_id": appointment["_id"]},
                {"$set": {"status": "cancelled", "updatedAt": datetime.utcnow()}}
            )
            return result.modified_count > 0
            
        except Exception as e:
            print(f"❌ Failed to cancel appointment by details: {e}")
            return False

    async def find_appointment_by_details(self, patient_name: str, date: str, time: str = None) -> dict:
        """Find appointment by patient details"""
        try:
            query = {
                "patient_name": patient_name,
                "date": date,
                "status": "booked"
            }
            if time:
                query["time"] = time
                
            appointment = await self.db.appointments.find_one(query)
            if appointment:
                appointment["_id"] = str(appointment["_id"])  # Convert ObjectId to string
            return appointment
            
        except Exception as e:
            print(f"❌ Failed to find appointment: {e}")
            return None
        

    async def reschedule_appointment(self, appointment_id: str, date: str, time: str = None) -> bool:
        """Reschedule an appointment by ID"""
        try:
             # First check if appointment exists and is booked
            status = await self.get_appointment_status(appointment_id)
            
            if status is None:
                print(f"❌ Appointment not found: {appointment_id}")
                return False
                
            if status == "cancelled":
                print(f"❌ Cannot reschedule cancelled appointment: {appointment_id}")
                return False
                
            if status != "booked":
                print(f"❌ Invalid appointment status: {status} for {appointment_id}")
                return False
        
            update_data = {
                "date": date,
                "updatedAt": datetime.utcnow()
            }
            
            if time:
                update_data["time"] = time
                
            result = await self.db.appointments.update_one(
                {"appointment_id": appointment_id, "status": "booked"},
                {"$set": update_data}
            )

            print(f"📊 MongoDB update result: {result.modified_count} modified")

            return result.modified_count > 0

        except Exception as e:
            print(f"❌ Failed to reschedule appointment: {e}")
            return False
        
    async def get_appointment_status(self, appointment_id: str) -> Optional[str]:
        """Get appointment status (booked/cancelled) or None if not found"""
        try:
            appointment = await self.db.appointments.find_one(
                {"appointment_id": appointment_id},
                {"status": 1}  # Only return status field
            )
            return appointment.get("status") if appointment else None
        except Exception as e:
            print(f"❌ Failed to get appointment status: {e}")
            return None
        
    async def get_appointment_by_id(self, appointment_id: str) -> Optional[dict]:
        """Get complete appointment details by ID"""
        try:
            appointment = await self.db.appointments.find_one({"appointment_id": appointment_id})
            if appointment:
                # Convert ObjectId to string and format the response
                appointment["_id"] = str(appointment["_id"])
                
                # Convert datetime objects to ISO format for JSON serialization
                for key, value in appointment.items():
                    if isinstance(value, datetime):
                        appointment[key] = value.isoformat()
                        
                return appointment
            return None
        except Exception as e:
            print(f"❌ Failed to get appointment: {e}")
            return None
    
    # USER MANAGEMENT METHODS
    async def create_user(self, user_data: dict):
        """Create a new user"""
        try:
            result = await self.users_collection.insert_one(user_data)
            return result.inserted_id
        except Exception as e:
            print(f"❌ Failed to create user: {e}")
            return None

    async def find_user_by_email(self, email: str):
        """Find a user by email"""
        try:
            user = await self.users_collection.find_one({"email": email})
            return user
        except Exception as e:
            print(f"❌ Failed to find user: {e}")
            return None

    async def find_user_by_id(self, user_id: str):
        """Find a user by ID"""
        try:
            user = await self.users_collection.find_one({"_id": ObjectId(user_id)})
            return user
        except Exception as e:
            print(f"❌ Failed to find user: {e}")
            return None
    
    async def get_available_doctors(self):
        """Get list of available doctors"""
        try:
            doctors = []
            async for doctor in self.users_collection.find({"role": "doctor"}):
                doctors.append({
                    "name": doctor.get("name"),
                    "specialization": doctor.get("specialization", "General")
                })
            return doctors
        except Exception as e:
            print(f"Error fetching doctors: {e}")
            return []

# Global instance
mongodb_service = MongoDBService()
