from datetime import datetime, timedelta
from jose import jwt
from passlib.context import CryptContext
from motor.motor_asyncio import AsyncIOMotorClient
import os

# JWT Configuration
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-here")
ALGORITHM = "HS256"

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class AuthHandler:
    def __init__(self, db_client):
        self.db = db_client

    async def register_user(self, username: str, password: str, email: str):
        existing_user = await self.db.rulebox_f1.users.find_one({"username": username})
        if existing_user:
            return False, "Username already exists"
        hashed_password = pwd_context.hash(password)
        user = {
            "username": username,
            "password": hashed_password,
            "email": email,
            "created_at": datetime.utcnow()
        }
        await self.db.rulebox_f1.users.insert_one(user)
        return True, "User created successfully"

    async def authenticate_user(self, username: str, password: str):
        user = await self.db.rulebox_f1.users.find_one({"username": username})
        if not user or not pwd_context.verify(password, user["password"]):
            return False, "Invalid credentials"
        token = self.create_token({"username": username})
        return True, token

    def create_token(self, data: dict):
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(days=7)
        to_encode.update({"exp": expire})
        return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    def verify_token(self, token: str):
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            return True, payload["username"]
        except Exception:
            return False, "Invalid token"