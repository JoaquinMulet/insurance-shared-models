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

# ========================================================================
# --- INICIO DE LA MODIFICACIÓN ---
# ========================================================================
class JobDashboardItem(BaseModel):
    """
    Representa la forma de un solo trabajo tal como se expone en la API.
    Actúa como una capa de traducción entre el modelo de BD y el cliente.
    """
    
    # Define el campo público 'job_id' y lo mapea al campo 'id' del modelo ORM.
    job_id: int = Field(alias='id')
    
    status: JobStatus
    
    # Define el campo público 'policy_holder_name' y lo mapea al campo
    # 'representative_policy_holder_name' del modelo ORM.
    policy_holder_name: Optional[str] = Field(default=None, alias='representative_policy_holder_name')
    
    # Define 'vehicle_description' y lo mapea a 'representative_vehicle_description'.
    vehicle_description: Optional[str] = Field(default=None, alias='representative_vehicle_description')

    created_at: datetime

    # Configuración centralizada para el comportamiento del modelo:
    model_config = ConfigDict(
        from_attributes=True,  # Permite crear instancias desde objetos ORM (SQLAlchemy).
        populate_by_name=True, # Permite usar los alias al leer/poblar el modelo.
    )

# ========================================================================
# --- FIN DE LA MODIFICACIÓN ---
# ========================================================================


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
    El tipo de `jobs` es JobDashboardItem. FastAPI/Pydantic se
    encargarán de la serialización correcta usando los alias.
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