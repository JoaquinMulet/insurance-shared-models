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
    
    # Aquí está el cambio: le decimos a Pydantic que el campo 'job_id'
    # debe poblarse desde el atributo 'id' del objeto fuente.
    job_id: int = Field(alias='id')
    
    status: JobStatus
    
    # Para estos campos, el nombre coincide entre el modelo y el schema,
    # así que no necesitan alias. Pydantic los mapeará automáticamente.
    # Solo que en el modelo SQLAlchemy se llaman 'representative_policy_holder_name'
    # y 'representative_vehicle_description'. ¡Hay que aliasarlos también!
    policy_holder_name: Optional[str] = Field(default=None, alias='representative_policy_holder_name')
    vehicle_description: Optional[str] = Field(default=None, alias='representative_vehicle_description')

    created_at: datetime

    model_config = ConfigDict(
        from_attributes=True,
        # MUY IMPORTANTE: Hay que permitir que se usen alias.
        populate_by_name=True,
    )


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

class LlmQueueMessage(BaseModel):
    """Mensaje para encolar un resultado de OCR para procesamiento con LLM."""
    job_file_id: int

class AssemblyQueueMessage(BaseModel):
    """Mensaje para encolar un trabajo para el ensamblaje final de resultados."""
    job_id: int