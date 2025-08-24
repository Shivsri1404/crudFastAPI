from fastapi import FastAPI, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from . import models, crud, database, schemas
import logging
logging.basicConfig(level=logging.INFO)
_logger = logging.getLogger(__name__)
import os, shutil

# Create database tables
models.Base.metadata.create_all(bind=database.engine)

app = FastAPI()
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Dependency
def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/create/users/", response_model= schemas.UserResponse)
def create_user(name: str= Form(...), email: str= Form(...), file: UploadFile = File(None), db: Session = Depends(get_db)):
    user_image_path = None
    if file:
        file_location = os.path.join(UPLOAD_DIR, file.filename)
        with open(file_location, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        user_image_path = file_location
    try:
        return crud.create_user(db=db, user= schemas.UserCreate(name=name, email=email), user_image_path=user_image_path)
    except IntegrityError:
        db.rollback()  # important: reset transaction state
        raise HTTPException(
            status_code=400,
            detail=f"Email '{email}' is already registered."
        )

@app.get("/get/users/", response_model=list[schemas.UserResponse])
def read_users(offset: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    return crud.get_users(db, offset=offset, limit=limit)

@app.get("/get/users/{user_id}", response_model=schemas.UserResponse)
def read_user(user_id: int, db: Session = Depends(get_db)):
    db_user = crud.get_user(db, user_id=user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user

@app.put("/update/users/{user_id}", response_model=schemas.UserResponse)
def update_user(user_id: int, user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = crud.update_user(db, user_id, user)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user

@app.delete("/delete/users/{user_id}")
def delete_user(user_id: int, db: Session = Depends(get_db)):
    db_user = crud.delete_user(db, user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    return {"message": "User deleted"}
