# insurance-shared-models/insurance_models/database/schemas.py

from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional, Any, Dict
from datetime import datetime
from .models import JobStatus

# --- Schemas para la creación de Jobs ---

class JobCreateRequest(BaseModel):
    filenames: List[str] = Field(..., min_items=1, max_items=5, description="Lista de nombres de archivo a subir.")

class JobCreateResponse(BaseModel):
    job_id: int
    upload_urls: Dict[str, str]


# --- Schemas para la visualización de Jobs (Dashboard y Detalle) ---

class JobDashboardItem(BaseModel):
    """Representa un único trabajo en la lista del dashboard."""
    job_id: int
    status: JobStatus
    policy_holder_name: Optional[str] = None
    vehicle_description: Optional[str] = None
    created_at: datetime

    # --- CAMBIO IMPORTANTE ---
    # Esto permite que Pydantic cree una instancia de este schema
    # directamente desde un objeto de modelo SQLAlchemy (ej: el modelo Job).
    # Es el equivalente a 'orm_mode = True' en Pydantic v1.
    model_config = ConfigDict(from_attributes=True)


class JobDashboardResponse(BaseModel):
    """
    Schema original para la lista de trabajos.
    Lo mantenemos por si se usa en otro lugar, pero el endpoint principal
    usará la versión paginada.
    """
    jobs: List[JobDashboardItem]


# --- ESQUEMA NUEVO PARA PAGINACIÓN ---
class PaginatedJobDashboardResponse(BaseModel):
    """
    Nueva respuesta para el dashboard que incluye metadatos de paginación.
    """
    jobs: List[JobDashboardItem]
    total_jobs: int
    total_pages: int
    current_page: int
    limit: int


class JobDetailResponse(BaseModel):
    """Representa la vista detallada de un trabajo con sus resultados."""
    status: JobStatus
    result: Optional[Dict[str, Any]] = None


# --- Schemas para la comunicación interna (Redis Queues) ---

class OcrQueueMessage(BaseModel):
    """Mensaje para encolar un archivo para procesamiento OCR."""
    job_file_id: int

class LlmQueueMessage(Base_Model_):
    """Mensaje para encolar un resultado de OCR para procesamiento con LLM."""
    job_file_id: int
    ocr_result: str

class AssemblyQueueMessage(BaseModel):
    """Mensaje para encolar un trabajo para el ensamblaje final de resultados."""
    job_id: int