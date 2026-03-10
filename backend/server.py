from fastapi import FastAPI, APIRouter, HTTPException, Depends, status, UploadFile, File, Form
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.responses import FileResponse
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
from pydantic import BaseModel, Field, EmailStr
from typing import List, Optional
from bson import ObjectId
import os
import logging
from pathlib import Path
import uuid
import shutil

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT settings
SECRET_KEY = os.environ.get("SECRET_KEY", "your-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7  # 7 days

# Invite code for team registration (optional - set to enable invite-only registration)
INVITE_CODE = os.environ.get("INVITE_CODE", None)  # Set in .env to enable

# Security
security = HTTPBearer()

# Create the main app without a prefix
app = FastAPI()

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Uploads directory
UPLOAD_DIR = ROOT_DIR / "uploads"
UPLOAD_DIR.mkdir(exist_ok=True)


# ============= MODELS =============

class PyObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid ObjectId")
        return ObjectId(v)

    @classmethod
    def __get_pydantic_json_schema__(cls, _schema_generator):
        return {'type': 'string'}


class UserRole(str):
    ADMIN = "admin"
    TEAM_MEMBER = "team_member"


class Department(str):
    MARKETING = "Marketing"
    ADS = "Ads"
    INVENTORY = "Inventory"
    DISPATCH = "Dispatch"
    WEBSITE = "Website"
    CUSTOMER_SUPPORT = "Customer Support"
    ACCOUNTS = "Accounts"
    DESIGN = "Design"


class TaskStatus(str):
    PENDING = "Pending"
    IN_PROGRESS = "In Progress"
    WAITING = "Waiting"
    COMPLETED = "Completed"


class TaskPriority(str):
    HIGH = "High"
    MEDIUM = "Medium"
    LOW = "Low"


# User Models
class UserCreate(BaseModel):
    email: EmailStr
    password: str
    name: str


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class User(BaseModel):
    id: str = Field(alias="_id")
    email: EmailStr
    name: str
    role: str
    createdAt: datetime

    class Config:
        populate_by_name = True


class Token(BaseModel):
    access_token: str
    token_type: str
    user: User


# Task Models
class TaskCreate(BaseModel):
    title: str
    description: str
    assignedTo: str  # user id
    deadline: datetime
    priority: str  # High, Medium, Low
    department: str
    status: str = "Pending"


class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    assignedTo: Optional[str] = None
    deadline: Optional[datetime] = None
    priority: Optional[str] = None
    department: Optional[str] = None
    status: Optional[str] = None


class Task(BaseModel):
    id: str = Field(alias="_id")
    title: str
    description: str
    assignedTo: str
    assignedToName: Optional[str] = None
    assignedBy: str
    assignedByName: Optional[str] = None
    deadline: datetime
    priority: str
    department: str
    status: str
    createdAt: datetime
    updatedAt: datetime

    class Config:
        populate_by_name = True


# Comment Models
class CommentCreate(BaseModel):
    text: str


class Comment(BaseModel):
    id: str = Field(alias="_id")
    taskId: str
    userId: str
    userName: str
    text: str
    createdAt: datetime

    class Config:
        populate_by_name = True


# Attachment Models
class Attachment(BaseModel):
    id: str = Field(alias="_id")
    taskId: str
    fileName: str
    filePath: str
    fileType: str
    uploadedBy: str
    uploadedByName: str
    createdAt: datetime

    class Config:
        populate_by_name = True


# ============= AUTH UTILITIES =============

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        token = credentials.credentials
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    user = await db.users.find_one({"_id": ObjectId(user_id)})
    if user is None:
        raise credentials_exception
    
    user["_id"] = str(user["_id"])
    return User(**user)


async def get_current_admin(current_user: User = Depends(get_current_user)):
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    return current_user


# ============= AUTH ROUTES =============

@api_router.post("/auth/register", response_model=Token)
async def register(user_data: UserCreate):
    # Check if user already exists
    existing_user = await db.users.find_one({"email": user_data.email})
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Check invite code if enabled
    user_count = await db.users.count_documents({})
    if user_count > 0 and INVITE_CODE:
        # After first user, require invite code if set
        invite = user_data.dict().get("invite_code")
        if invite != INVITE_CODE:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Invalid invite code"
            )
    
    # Check if this is the first user (will be admin)
    role = UserRole.ADMIN if user_count == 0 else UserRole.TEAM_MEMBER
    
    # Create user
    hashed_password = get_password_hash(user_data.password)
    user_doc = {
        "_id": ObjectId(),
        "email": user_data.email,
        "password": hashed_password,
        "name": user_data.name,
        "role": role,
        "createdAt": datetime.utcnow()
    }
    
    await db.users.insert_one(user_doc)
    
    # Create access token
    access_token = create_access_token(data={"sub": str(user_doc["_id"])})
    
    user_doc["_id"] = str(user_doc["_id"])
    del user_doc["password"]
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": User(**user_doc)
    }


@api_router.post("/auth/login", response_model=Token)
async def login(user_data: UserLogin):
    # Find user
    user = await db.users.find_one({"email": user_data.email})
    if not user or not verify_password(user_data.password, user["password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    
    # Create access token
    access_token = create_access_token(data={"sub": str(user["_id"])})
    
    user["_id"] = str(user["_id"])
    del user["password"]
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": User(**user)
    }


@api_router.get("/auth/me", response_model=User)
async def get_me(current_user: User = Depends(get_current_user)):
    return current_user


# ============= USER ROUTES =============

@api_router.get("/users", response_model=List[User])
async def get_users(current_user: User = Depends(get_current_user)):
    users = await db.users.find().to_list(1000)
    return [User(**{**user, "_id": str(user["_id"])}) for user in users]


# ============= TASK ROUTES =============

@api_router.post("/tasks", response_model=Task)
async def create_task(task_data: TaskCreate, current_user: User = Depends(get_current_user)):
    # Get assigned user details
    assigned_user = await db.users.find_one({"_id": ObjectId(task_data.assignedTo)})
    if not assigned_user:
        raise HTTPException(status_code=404, detail="Assigned user not found")
    
    task_doc = {
        "_id": ObjectId(),
        "title": task_data.title,
        "description": task_data.description,
        "assignedTo": task_data.assignedTo,
        "assignedToName": assigned_user["name"],
        "assignedBy": current_user.id,
        "assignedByName": current_user.name,
        "deadline": task_data.deadline,
        "priority": task_data.priority,
        "department": task_data.department,
        "status": task_data.status,
        "createdAt": datetime.utcnow(),
        "updatedAt": datetime.utcnow()
    }
    
    await db.tasks.insert_one(task_doc)
    task_doc["_id"] = str(task_doc["_id"])
    
    return Task(**task_doc)


@api_router.get("/tasks", response_model=List[Task])
async def get_tasks(
    priority: Optional[str] = None,
    department: Optional[str] = None,
    assignedTo: Optional[str] = None,
    status: Optional[str] = None,
    current_user: User = Depends(get_current_user)
):
    # Build filter
    filter_dict = {}
    if priority:
        filter_dict["priority"] = priority
    if department:
        filter_dict["department"] = department
    if assignedTo:
        filter_dict["assignedTo"] = assignedTo
    if status:
        filter_dict["status"] = status
    
    # Admin sees all tasks, team members see only their assigned tasks or tasks they created
    if current_user.role != UserRole.ADMIN:
        filter_dict["$or"] = [
            {"assignedTo": current_user.id},
            {"assignedBy": current_user.id}
        ]
    
    tasks = await db.tasks.find(filter_dict).to_list(1000)
    return [Task(**{**task, "_id": str(task["_id"])}) for task in tasks]


@api_router.get("/tasks/{task_id}", response_model=Task)
async def get_task(task_id: str, current_user: User = Depends(get_current_user)):
    if not ObjectId.is_valid(task_id):
        raise HTTPException(status_code=400, detail="Invalid task ID")
    
    task = await db.tasks.find_one({"_id": ObjectId(task_id)})
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    task["_id"] = str(task["_id"])
    return Task(**task)


@api_router.put("/tasks/{task_id}", response_model=Task)
async def update_task(
    task_id: str,
    task_data: TaskUpdate,
    current_user: User = Depends(get_current_user)
):
    if not ObjectId.is_valid(task_id):
        raise HTTPException(status_code=400, detail="Invalid task ID")
    
    task = await db.tasks.find_one({"_id": ObjectId(task_id)})
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    # Build update document
    update_dict = {"updatedAt": datetime.utcnow()}
    if task_data.title is not None:
        update_dict["title"] = task_data.title
    if task_data.description is not None:
        update_dict["description"] = task_data.description
    if task_data.assignedTo is not None:
        assigned_user = await db.users.find_one({"_id": ObjectId(task_data.assignedTo)})
        if not assigned_user:
            raise HTTPException(status_code=404, detail="Assigned user not found")
        update_dict["assignedTo"] = task_data.assignedTo
        update_dict["assignedToName"] = assigned_user["name"]
    if task_data.deadline is not None:
        update_dict["deadline"] = task_data.deadline
    if task_data.priority is not None:
        update_dict["priority"] = task_data.priority
    if task_data.department is not None:
        update_dict["department"] = task_data.department
    if task_data.status is not None:
        update_dict["status"] = task_data.status
    
    await db.tasks.update_one(
        {"_id": ObjectId(task_id)},
        {"$set": update_dict}
    )
    
    updated_task = await db.tasks.find_one({"_id": ObjectId(task_id)})
    updated_task["_id"] = str(updated_task["_id"])
    
    return Task(**updated_task)


@api_router.delete("/tasks/{task_id}")
async def delete_task(
    task_id: str,
    current_user: User = Depends(get_current_admin)
):
    if not ObjectId.is_valid(task_id):
        raise HTTPException(status_code=400, detail="Invalid task ID")
    
    result = await db.tasks.delete_one({"_id": ObjectId(task_id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Task not found")
    
    # Also delete related comments and attachments
    await db.comments.delete_many({"taskId": task_id})
    await db.attachments.delete_many({"taskId": task_id})
    
    return {"message": "Task deleted successfully"}


# ============= COMMENT ROUTES =============

@api_router.post("/tasks/{task_id}/comments", response_model=Comment)
async def create_comment(
    task_id: str,
    comment_data: CommentCreate,
    current_user: User = Depends(get_current_user)
):
    if not ObjectId.is_valid(task_id):
        raise HTTPException(status_code=400, detail="Invalid task ID")
    
    task = await db.tasks.find_one({"_id": ObjectId(task_id)})
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    comment_doc = {
        "_id": ObjectId(),
        "taskId": task_id,
        "userId": current_user.id,
        "userName": current_user.name,
        "text": comment_data.text,
        "createdAt": datetime.utcnow()
    }
    
    await db.comments.insert_one(comment_doc)
    comment_doc["_id"] = str(comment_doc["_id"])
    
    return Comment(**comment_doc)


@api_router.get("/tasks/{task_id}/comments", response_model=List[Comment])
async def get_comments(
    task_id: str,
    current_user: User = Depends(get_current_user)
):
    comments = await db.comments.find({"taskId": task_id}).sort("createdAt", 1).to_list(1000)
    return [Comment(**{**comment, "_id": str(comment["_id"])}) for comment in comments]


# ============= ATTACHMENT ROUTES =============

@api_router.post("/tasks/{task_id}/attachments", response_model=Attachment)
async def upload_attachment(
    task_id: str,
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user)
):
    if not ObjectId.is_valid(task_id):
        raise HTTPException(status_code=400, detail="Invalid task ID")
    
    task = await db.tasks.find_one({"_id": ObjectId(task_id)})
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    # Generate unique filename
    file_extension = file.filename.split(".")[-1] if "." in file.filename else ""
    unique_filename = f"{uuid.uuid4()}.{file_extension}"
    file_path = UPLOAD_DIR / unique_filename
    
    # Save file - read content first then write
    try:
        content = await file.read()
        with open(file_path, "wb") as buffer:
            buffer.write(content)
    except Exception as e:
        logger.error(f"Error saving file: {e}")
        raise HTTPException(status_code=500, detail="Failed to save file")
    
    attachment_doc = {
        "_id": ObjectId(),
        "taskId": task_id,
        "fileName": file.filename,
        "filePath": str(file_path),
        "fileType": file.content_type or "application/octet-stream",
        "uploadedBy": current_user.id,
        "uploadedByName": current_user.name,
        "createdAt": datetime.utcnow()
    }
    
    await db.attachments.insert_one(attachment_doc)
    attachment_doc["_id"] = str(attachment_doc["_id"])
    
    return Attachment(**attachment_doc)


@api_router.get("/tasks/{task_id}/attachments", response_model=List[Attachment])
async def get_attachments(
    task_id: str,
    current_user: User = Depends(get_current_user)
):
    attachments = await db.attachments.find({"taskId": task_id}).sort("createdAt", 1).to_list(1000)
    return [Attachment(**{**attachment, "_id": str(attachment["_id"])}) for attachment in attachments]


@api_router.get("/attachments/{attachment_id}/download")
async def download_attachment(
    attachment_id: str,
    current_user: User = Depends(get_current_user)
):
    if not ObjectId.is_valid(attachment_id):
        raise HTTPException(status_code=400, detail="Invalid attachment ID")
    
    attachment = await db.attachments.find_one({"_id": ObjectId(attachment_id)})
    if not attachment:
        raise HTTPException(status_code=404, detail="Attachment not found")
    
    file_path = Path(attachment["filePath"])
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found")
    
    return FileResponse(
        path=file_path,
        filename=attachment["fileName"],
        media_type=attachment["fileType"]
    )


# ============= HEALTH CHECK =============

@api_router.get("/")
async def root():
    return {"message": "Task Management API", "status": "running"}


@api_router.get("/health")
async def health_check():
    return {"status": "healthy"}


# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()
