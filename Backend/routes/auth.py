from fastapi import APIRouter, HTTPException
from database import users_collection
from models.user import UserRegister, UserLogin
from utils.security import hash_password, verify_password, create_access_token
import logging

logging.basicConfig(level=logging.INFO)

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)

# ---------------- REGISTER ----------------
@router.post("/register")
def register(user: UserRegister):
    try:
        logging.info(f"Register attempt: {user.email}")

        existing_user = users_collection.find_one({"email": user.email})

        if existing_user:
            raise HTTPException(
                status_code=400,
                detail="Email already registered"
            )

        hashed_password = hash_password(user.password)

        users_collection.insert_one({
            "name": user.name,
            "email": user.email,
            "password": hashed_password
        })

        logging.info(f"User registered successfully: {user.email}")

        return {
            "success": True,
            "message": "User registered successfully"
        }

    except HTTPException:
        raise

    except Exception as e:
        logging.error(str(e))
        raise HTTPException(
            status_code=500,
            detail="Registration failed"
        )


# ---------------- LOGIN ----------------
@router.post("/login")
def login(user: UserLogin):
    try:
        logging.info(f"Login attempt: {user.email}")

        db_user = users_collection.find_one({"email": user.email})

        if not db_user:
            raise HTTPException(
                status_code=401,
                detail="Invalid email or password"
            )

        stored_password = db_user["password"]

        # Handle old plain-text passwords
        if isinstance(stored_password, str) and not stored_password.startswith("$2"):
            if user.password != stored_password:
                raise HTTPException(
                    status_code=401,
                    detail="Invalid email or password"
                )

            # Upgrade plain password to hashed password
            new_hash = hash_password(user.password)

            users_collection.update_one(
                {"email": user.email},
                {"$set": {"password": new_hash}}
            )

        else:
            # Normal hashed password verification
            if not verify_password(user.password, stored_password):
                raise HTTPException(
                    status_code=401,
                    detail="Invalid email or password"
                )

        token = create_access_token({"sub": user.email})

        logging.info(f"Login success: {user.email}")

        return {
            "success": True,
            "access_token": token,
            "token_type": "bearer",
            "user": {
                "name": db_user.get("name", ""),
                "email": db_user.get("email", "")
            }
        }

    except HTTPException:
        raise

    except Exception as e:
        logging.error(str(e))
        raise HTTPException(
            status_code=500,
            detail="Login failed"
        )