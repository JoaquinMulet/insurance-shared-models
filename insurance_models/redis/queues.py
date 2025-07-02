from pydantic import BaseModel

# Define queue names as constants to avoid typos
OCR_QUEUE = "ocr_queue"
LLM_QUEUE = "llm_queue"
ASSEMBLY_QUEUE = "assembly_queue"

# Pydantic models for message payloads
# Using integers for IDs now

class OcrQueueMessage(BaseModel):
    job_file_id: int

class LlmQueueMessage(BaseModel):
    job_file_id: int

class AssemblyQueueMessage(BaseModel):
    # CORRECCIÓN: 'ints' cambiado a 'int'
    job_id: int