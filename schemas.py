from pydantic import BaseModel, ConfigDict

class MotorBase(BaseModel):
    merk: str
    tipe: str
    kapasitas_cc: int
    siap_dijual: bool = True
class MotorResponse(MotorBase):
    idmotor: int
    class Config:
      orm_mode = True