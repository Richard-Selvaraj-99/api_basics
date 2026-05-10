from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, EmailStr
from sqlalchemy import Column, Integer, String, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session

# -----------------------------
# Database Configuration
# -----------------------------

DATABASE_URL = "sqlite:///./database.db"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}  # Required for SQLite
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# -----------------------------
# SQLAlchemy Model
# -----------------------------

class UserModel(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(80), unique=True, nullable=False)
    email = Column(String(80), unique=True, nullable=False)

# Create tables
Base.metadata.create_all(bind=engine)

# -----------------------------
# Pydantic Schemas
# -----------------------------

class UserBase(BaseModel):
    name: str
    email: EmailStr

class UserCreate(UserBase):
    pass

class UserResponse(UserBase):
    id: int

    class Config:
        orm_mode = True

# -----------------------------
# FastAPI App
# -----------------------------

app = FastAPI()

# -----------------------------
# Dependency
# -----------------------------

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# -----------------------------
# Routes
# -----------------------------

@app.get("/")
def home():
    return {"message": "FastAPI REST API"}

# Get all users
@app.get("/api/users/", response_model=list[UserResponse])
def get_users():
    db: Session = SessionLocal()
    users = db.query(UserModel).all()
    db.close()
    return users

# Create user
@app.post("/api/users/", response_model=UserResponse, status_code=201)
def create_user(user: UserCreate):
    db: Session = SessionLocal()

    existing_user = db.query(UserModel).filter(
        (UserModel.name == user.name) |
        (UserModel.email == user.email)
    ).first()

    if existing_user:
        db.close()
        raise HTTPException(status_code=400, detail="User already exists")

    new_user = UserModel(
        name=user.name,
        email=user.email
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    db.close()
    return new_user

# Get single user
@app.get("/api/users/{id}", response_model=UserResponse)
def get_user(id: int):
    db: Session = SessionLocal()

    user = db.query(UserModel).filter(UserModel.id == id).first()

    db.close()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return user

# Update user
@app.patch("/api/users/{id}", response_model=UserResponse)
def update_user(id: int, updated_user: UserCreate):
    db: Session = SessionLocal()

    user = db.query(UserModel).filter(UserModel.id == id).first()

    if not user:
        db.close()
        raise HTTPException(status_code=404, detail="User not found")

    user.name = updated_user.name
    user.email = updated_user.email

    db.commit()
    db.refresh(user)

    db.close()

    return user

# Delete user
@app.delete("/api/users/{id}")
def delete_user(id: int):
    db: Session = SessionLocal()

    user = db.query(UserModel).filter(UserModel.id == id).first()

    if not user:
        db.close()
        raise HTTPException(status_code=404, detail="User not found")

    db.delete(user)
    db.commit()

    db.close()

    return {"message": f"User with id {id} deleted successfully"}