from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from . import models, crud, database, schemas
import logging
logging.basicConfig(level=logging.INFO)
_logger = logging.getLogger(__name__)
# Create database tables
models.Base.metadata.create_all(bind=database.engine)

app = FastAPI()

# Dependency
def get_db():
    db = database.SessionLocal()
    _logger.info(f"===get_db==db=={db}===========")
    try:
        yield db
    finally:
        db.close()

@app.post("/create/users/", response_model= schemas.UserResponse)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    _logger.info(f"===user=={user}===========")
    _logger.info(f"===db=={db}===========")
    print("hello")
    return crud.create_user(db=db, user=user)

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
