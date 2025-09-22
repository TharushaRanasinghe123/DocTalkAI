from fastapi import APIRouter, HTTPException, status
from bson import ObjectId
from app.models.user import UserCreate, UserLogin, UserOut, UserRole
from app.services.mongodb_service import mongodb_service
from app.utils.auth import get_password_hash, verify_password, create_access_token
import datetime

router = APIRouter(tags=["Authentication"])

@router.post("/signup", response_model=UserOut, status_code=status.HTTP_201_CREATED)
async def sign_up(user_data: UserCreate):
    # Check if user already exists
    existing_user = await mongodb_service.find_user_by_email(user_data.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Hash password
    hashed_password = get_password_hash(user_data.password)
    
    # Create user document
    user_dict = {
        "email": user_data.email,
        "name": user_data.name,
        "phone": user_data.phone,
        "hashed_password": hashed_password,
        "role": user_data.role,
        "force_password_change": False,
        "created_at": datetime.datetime.utcnow()
    }
    
    # Insert into database
    user_id = await mongodb_service.create_user(user_dict)
    
    # Get the created user
    created_user = await mongodb_service.find_user_by_id(user_id)

    # Convert to response model
    return {
        "id": str(created_user["_id"]),
        "email": created_user["email"],
        "name": created_user["name"],
        "phone": created_user.get("phone"),
        "role": created_user["role"]
    }

@router.post("/login")
async def login(login_data: UserLogin):
    # Find user
    user = await mongodb_service.find_user_by_email(login_data.email)
    if not user or not verify_password(login_data.password, user["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Check if doctor needs to change password
    if user["role"] == UserRole.DOCTOR and user.get("force_password_change", False):
        return {
            "message": "Password change required",
            "force_password_change": True,
            "user_id": str(user["_id"])
        }
    
    # Create access token
    access_token = create_access_token(
        data={"sub": user["email"], "role": user["role"]}
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "role": user["role"],
        "user_id": str(user["_id"]),
        "force_password_change": False,
        "name": user.get("name", "Doctor"),  # Add this line
        "email": user["email"]
    }

@router.post("/change-password")
async def change_password(change_data: dict):
    """Change password for users with force_password_change"""
    try:
        user_id = change_data.get("user_id")
        new_password = change_data.get("new_password")
        
        if not user_id or not new_password:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User ID and new password are required"
            )
        
        # Find user and update password
        user = await mongodb_service.find_user_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        hashed_password = get_password_hash(new_password)
        
        # Update password and remove force_password_change flag
        await mongodb_service.users_collection.update_one(
            {"_id": ObjectId(user_id)},
            {"$set": {
                "hashed_password": hashed_password,
                "force_password_change": False
            }}
        )
        
        return {"message": "Password changed successfully"}
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to change password: {str(e)}"
        )
# Add this to your main.py to include the auth routes