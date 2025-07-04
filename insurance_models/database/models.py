from sqlalchemy import (
    Column, String, Integer, DateTime, Boolean, Text,
    DECIMAL, Enum, ForeignKey, BigInteger
)
from sqlalchemy.orm import relationship, declarative_base
from sqlalchemy.dialects.postgresql import JSONB
from datetime import datetime
import enum

Base = declarative_base()

# --- Enums ---

class JobStatus(enum.Enum):
    PENDING_UPLOAD = "PENDING_UPLOAD"
    OCR_IN_PROGRESS = "OCR_IN_PROGRESS"
    OCR_COMPLETED = "OCR_COMPLETED"
    OCR_FAILED = "OCR_FAILED"
    LLM_PROCESSING = "LLM_PROCESSING"
    LLM_COMPLETED = "LLM_COMPLETED"
    LLM_FAILED = "LLM_FAILED"
    ASSEMBLING = "ASSEMBLING"  # Renombrado de ASSEMBLY_IN_PROGRESS para consistencia
    ASSEMBLY_FAILED = "ASSEMBLY_FAILED"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"
    PENDING = "PENDING"

class WorkshopType(enum.Enum):
    LIBRE_ELECCION = "LIBRE_ELECCION"
    TALLER_MARCA = "TALLER_MARCA"
    TALLER_MULTIMARCA = "TALLER_MULTIMARCA"
    NO_APLICA = "NO_APLICA"

class LogLevel(enum.Enum):
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"

# --- Main Tables ---

class User(Base):
    __tablename__ = "users"
    id = Column(String, primary_key=True, comment="Clerk User ID")
    email = Column(String(255), unique=True, nullable=False, index=True)
    name = Column(String(255))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    jobs = relationship("Job", back_populates="user", cascade="all, delete-orphan")

class Job(Base):
    __tablename__ = "jobs"
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    status = Column(Enum(JobStatus), default=JobStatus.PENDING_UPLOAD, index=True)
    representative_policy_holder_name = Column(String(500), comment="Nombre representativo para mostrar en UI")
    representative_vehicle_description = Column(String(200), comment="Descripción del vehículo para mostrar en UI")
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", back_populates="jobs")
    files = relationship("JobFile", back_populates="job", cascade="all, delete-orphan")
    results = relationship("JobResult", back_populates="job", cascade="all, delete-orphan", uselist=False)
    logs = relationship("ProcessingLog", back_populates="job", cascade="all, delete-orphan")
    
    # Estas relaciones se mantienen, pero su llenado ya no es parte del flujo crítico.
    policy_holders = relationship("PolicyHolder", back_populates="job", cascade="all, delete-orphan")
    vehicles = relationship("Vehicle", back_populates="job", cascade="all, delete-orphan")
    insurance_plans = relationship("InsurancePlan", back_populates="job", cascade="all, delete-orphan")

class JobFile(Base):
    __tablename__ = "job_files"
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    job_id = Column(BigInteger, ForeignKey("jobs.id"), nullable=False, index=True)
    filename = Column(String(500), nullable=False)
    r2_object_key = Column(String(1000), nullable=False)
    status = Column(Enum(JobStatus), default=JobStatus.PENDING_UPLOAD, index=True)

    job = relationship("Job", back_populates="files")
    ocr_results = relationship("OcrResult", back_populates="file", cascade="all, delete-orphan", uselist=False)
    
    # --- CAMBIO CLAVE: Relación con la nueva tabla LlmResult ---
    llm_result = relationship("LlmResult", back_populates="file", cascade="all, delete-orphan", uselist=False)

class Insurer(Base):
    __tablename__ = "insurers"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(200), unique=True, nullable=False)

    insurance_plans = relationship("InsurancePlan", back_populates="insurer")

# --- NUEVA TABLA PARA ALMACENAR LA SALIDA EN BRUTO DEL LLM ---
class LlmResult(Base):
    __tablename__ = "llm_results"
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    job_file_id = Column(BigInteger, ForeignKey("job_files.id"), nullable=False, unique=True, index=True)
    raw_llm_data = Column(JSONB, nullable=False, comment="La salida JSON cruda del modelo LLM, sin procesar.")
    created_at = Column(DateTime, default=datetime.utcnow)

    file = relationship("JobFile", back_populates="llm_result")


class OcrResult(Base):
    __tablename__ = "ocr_results"
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    job_file_id = Column(BigInteger, ForeignKey("job_files.id"), nullable=False, unique=True)
    text_content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    file = relationship("JobFile", back_populates="ocr_results")

# --- Las siguientes tablas ahora son secundarias al flujo principal ---
# --- Se mantienen por si se quieren usar para análisis posteriores o features adicionales ---

class PolicyHolder(Base):
    __tablename__ = "policy_holders"
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    job_id = Column(BigInteger, ForeignKey("jobs.id"), nullable=False, index=True)
    name = Column(String(500))
    rut = Column(String(20))

    job = relationship("Job", back_populates="policy_holders")

class Vehicle(Base):
    __tablename__ = "vehicles"
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    job_id = Column(BigInteger, ForeignKey("jobs.id"), nullable=False, index=True)
    make = Column(String(100))
    model = Column(String(100))
    year = Column(Integer)

    job = relationship("Job", back_populates="vehicles")
    
    def to_dict(self):
        return {"make": self.make, "model": self.model, "year": self.year}

class InsurancePlan(Base):
    __tablename__ = "insurance_plans"
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    job_id = Column(BigInteger, ForeignKey("jobs.id"), nullable=False, index=True)
    insurer_id = Column(Integer, ForeignKey("insurers.id"), nullable=True)
    plan_name = Column(String(255))

    job = relationship("Job", back_populates="insurance_plans")
    insurer = relationship("Insurer", back_populates="insurance_plans")
    deductible_premiums = relationship("DeductiblePremium", back_populates="plan", cascade="all, delete-orphan")
    workshop_coverage = relationship("WorkshopCoverage", back_populates="plan", uselist=False, cascade="all, delete-orphan")
    replacement_car_coverage = relationship("ReplacementCarCoverage", back_populates="plan", uselist=False, cascade="all, delete-orphan")
    new_vehicle_replacement_coverage = relationship("NewVehicleReplacementCoverage", back_populates="plan", uselist=False, cascade="all, delete-orphan")

class DeductiblePremium(Base):
    __tablename__ = "deductible_premiums"
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    insurance_plan_id = Column(BigInteger, ForeignKey("insurance_plans.id"), nullable=False, index=True)
    deductible_uf = Column(String)
    annual_premium_uf = Column(String)
    rc_coverage_uf = Column(String)
    parsed_deductible = Column(DECIMAL(10, 2))
    parsed_premium = Column(DECIMAL(10, 2))

    plan = relationship("InsurancePlan", back_populates="deductible_premiums")

class WorkshopCoverage(Base):
    __tablename__ = "workshop_coverages"
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    insurance_plan_id = Column(BigInteger, ForeignKey("insurance_plans.id"), nullable=False, unique=True)
    workshop_type = Column(String)
    conditions = Column(Text)
    
    plan = relationship("InsurancePlan", back_populates="workshop_coverage")

    def to_dict(self):
        return {"workshop_type": self.workshop_type, "conditions": self.conditions}

class ReplacementCarCoverage(Base):
    __tablename__ = "replacement_car_coverages"
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    insurance_plan_id = Column(BigInteger, ForeignKey("insurance_plans.id"), nullable=False, unique=True)
    has_coverage = Column(Boolean, default=False)
    days_limit = Column(String)
    copay_details = Column(String)
    conditions = Column(Text)

    plan = relationship("InsurancePlan", back_populates="replacement_car_coverage")
    
    def to_dict(self):
        return {"has_coverage": self.has_coverage, "days_limit": self.days_limit, "copay_details": self.copay_details, "conditions": self.conditions}

class NewVehicleReplacementCoverage(Base):
    __tablename__ = "new_vehicle_replacement_coverages"
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    insurance_plan_id = Column(BigInteger, ForeignKey("insurance_plans.id"), nullable=False, unique=True)
    has_coverage = Column(Boolean, default=False)
    conditions = Column(Text)

    plan = relationship("InsurancePlan", back_populates="new_vehicle_replacement_coverage")
    
    def to_dict(self):
        return {"has_coverage": self.has_coverage, "conditions": self.conditions}

class JobResult(Base):
    __tablename__ = "job_results"
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    job_id = Column(BigInteger, ForeignKey("jobs.id"), nullable=False, unique=True)
    consolidated_data = Column(JSONB)
    created_at = Column(DateTime, default=datetime.utcnow)

    job = relationship("Job", back_populates="results")

class ProcessingLog(Base):
    __tablename__ = "processing_logs"
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    job_id = Column(BigInteger, ForeignKey("jobs.id"), nullable=False, index=True)
    service_name = Column(String(100), index=True)
    message = Column(Text)
    level = Column(Enum(LogLevel), default=LogLevel.INFO)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)

    job = relationship("Job", back_populates="logs")