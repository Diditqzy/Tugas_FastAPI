from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from passlib.context import CryptContext
import jwt
from jwt.exceptions import InvalidTokenError
from datetime import datetime, timedelta, timezone

import models, schemas
from database import engine, SessionLocal

# Buat tabel di database jika belum ada
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Permotoran")

# --- KONFIGURASI KEAMANAN (JWT & Password Hashing) ---
# Di dunia nyata/production, SECRET_KEY ini harus ditaruh di environment variables (.env)
SECRET_KEY = "rahasia_negara_jangan_dibocorin_ya_bos"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- FUNGSI HELPER AUTH & RBAC ---
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# Dependency untuk mengambil User yang sedang login (Verifikasi Token)
def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Token tidak valid atau sudah kedaluwarsa",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except InvalidTokenError:
        raise credentials_exception
    
    user = db.query(models.User).filter(models.User.username == username).first()
    if user is None:
        raise credentials_exception
    return user

# Dependency RBAC: Hanya membolehkan User dengan role "admin"
def get_current_admin_user(current_user: models.User = Depends(get_current_user)):
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access Denied! Fitur ini hanya untuk Admin.",
        )
    return current_user


# --- ENDPOINT AUTHENTICATION (Register & Login) ---

@app.post("/register", response_model=schemas.UserResponse)
def register_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    # Cek apakah username sudah dipakai
    db_user = db.query(models.User).filter(models.User.username == user.username).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Username sudah terdaftar")
    
    hashed_password = get_password_hash(user.password)
    db_user = models.User(username=user.username, hashed_password=hashed_password, role=user.role)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@app.post("/login", response_model=schemas.Token)
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.username == form_data.username).first()
    # Verifikasi username dan password
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Username atau password salah",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Jika lolos, buatkan token JWT
    access_token = create_access_token(data={"sub": user.username, "role": user.role})
    return {"access_token": access_token, "token_type": "bearer"}


# --- ENDPOINT CRUD OPERASIONAL ---

# Read All (Boleh diakses siapa saja)
@app.get("/items/", response_model=list[schemas.MotorResponse])
def ambil_semua_motor(db: Session = Depends(get_db)):
    return db.query(models.Motor).all()

# Read Per-ID (Boleh diakses siapa saja)
@app.get("/items/{id}", response_model=schemas.MotorResponse)
def ambil_motor_berdasarkan_id(id: int, db: Session = Depends(get_db)):
    motor_dicari = db.query(models.Motor).filter(models.Motor.idmotor == id).first()
    if motor_dicari is None:
        raise HTTPException(status_code=404, detail="Motor tidak ditemukan")
    return motor_dicari

# Create (Harus login: ada dependency get_current_user)
@app.post("/items/", response_model=schemas.MotorResponse)
def tambah_motor(motor: schemas.MotorBase, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    motor_baru = models.Motor(**motor.model_dump())
    db.add(motor_baru)
    db.commit()
    db.refresh(motor_baru)
    return motor_baru

# Update (Harus login: ada dependency get_current_user)
@app.put("/items/{id}", response_model=schemas.MotorResponse)
def update_motor(id: int, motor: schemas.MotorBase, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    motor_db = db.query(models.Motor).filter(models.Motor.idmotor == id).first()
    if not motor_db:
        raise HTTPException(status_code=404, detail="Motor tidak ditemukan")
    
    motor_db.merk = motor.merk
    motor_db.tipe = motor.tipe
    motor_db.kapasitas_cc = motor.kapasitas_cc
    motor_db.siap_dijual = motor.siap_dijual
    
    db.commit()
    db.refresh(motor_db)
    return motor_db

# Delete (RBAC: HANYA ADMIN YANG BOLEH HAPUS. Dependency: get_current_admin_user)
@app.delete("/items/{id}")
def hapus_motor(id: int, db: Session = Depends(get_db), admin_user: models.User = Depends(get_current_admin_user)):
    motor_db = db.query(models.Motor).filter(models.Motor.idmotor == id).first()
    if not motor_db:
        raise HTTPException(status_code=404, detail="Motor tidak ditemukan")
    
    db.delete(motor_db)
    db.commit()
    return {"message": "Motor berhasil dihapus"}