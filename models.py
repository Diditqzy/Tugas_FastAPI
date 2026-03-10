from sqlalchemy import Column, Integer, String, Boolean
from database import Base

class Motor(Base):
    __tablename__ = "data_motor"
    idmotor = Column(Integer, primary_key=True, index=True)
    merk = Column(String, index=True)      
    tipe = Column(String)                  
    kapasitas_cc = Column(Integer)         
    siap_dijual = Column(Boolean, default=True)