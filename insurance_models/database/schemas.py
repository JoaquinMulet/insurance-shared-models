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
    Los nombres de los campos ahora coinciden directamente con el modelo `Job` de SQLAlchemy
    para mayor claridad y consistencia. Se eliminan los alias.
    """
    id: int  # <-- El campo se llama 'id', igual que en el modelo Job.
    status: JobStatus
    representative_policy_holder_name: Optional[str] = None
    representative_vehicle_description: Optional[str] = None
    created_at: datetime

    # Configuración de Pydantic para permitir la creación desde un objeto ORM.
    # No se necesitan alias porque los nombres de campo coinciden.
    model_config = ConfigDict(
        from_attributes=True,
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