from pydantic import BaseModel, Field, EmailStr
from typing import List, Optional, Dict, Any
from datetime import datetime
from .models import JobStatus

# --- User Schemas ---
class UserBase(BaseModel):
    email: EmailStr
    name: Optional[str] = None

class UserCreate(UserBase):
    id: str # Clerk User ID

class User(UserBase):
    id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# --- Job Schemas for API ---

# NUEVO: Esquema para un solo item en la lista del dashboard
class JobDashboardItem(BaseModel):
    job_id: int
    status: JobStatus
    policy_holder_name: Optional[str] = Field(None, description="Nombre del asegurado principal del trabajo")
    vehicle_description: Optional[str] = Field(None, description="Descripción del vehículo principal del trabajo")
    created_at: datetime

    class Config:
        from_attributes = True

# NUEVO: Esquema para la respuesta completa del dashboard
class JobDashboardResponse(BaseModel):
    jobs: List[JobDashboardItem]

# NUEVO: Esquema para la respuesta de detalle del job
class JobDetailResponse(BaseModel):
    status: JobStatus
    result: Optional[Dict[str, Any]] = Field(None, description="El objeto JSON consolidado si el trabajo está completo")