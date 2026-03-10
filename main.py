from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
import models, schemas
from database import engine, SessionLocal

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Permotoran")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/items/", response_model=schemas.MotorResponse)
def tambah_motor(motor: schemas.MotorBase, db: Session = Depends(get_db)):
    motor_baru = models.Motor(**motor.model_dump())
    db.add(motor_baru)
    db.commit()
    db.refresh(motor_baru)
    return motor_baru

@app.get("/items/", response_model=list[schemas.MotorResponse])
def ambil_semua_motor(db: Session = Depends(get_db)):
    return db.query(models.Motor).all()

@app.get("/items/{id}", response_model=schemas.MotorResponse)
def ambil_motor_berdasarkan_id(id: int, db: Session = Depends(get_db)):
    motor_dicari = db.query(models.Motor).filter(models.Motor.idmotor == id).first()
    if motor_dicari is None:
        raise HTTPException(status_code=404, detail="Motor tidak ditemukan")
    return motor_dicari