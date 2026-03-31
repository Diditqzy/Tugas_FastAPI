from pydantic import BaseModel, ConfigDict

# --- Schemas Motor ---
class MotorBase(BaseModel):
    merk: str
    tipe: str
    kapasitas_cc: int
    siap_dijual: bool = True

class MotorResponse(MotorBase):
    idmotor: int
    model_config = ConfigDict(from_attributes=True)

# --- TAMBAHAN BARU: Schemas User & Auth ---
class UserCreate(BaseModel):
    username: str
    password: str
    role: str = "user" # Default saat register adalah user biasa

class UserResponse(BaseModel):
    id: int
    username: str
    role: str
    model_config = ConfigDict(from_attributes=True)

class Token(BaseModel):
    access_token: str
    token_type: str