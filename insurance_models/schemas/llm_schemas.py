import re
from typing import List, Optional
from pydantic import BaseModel, Field, field_validator
from collections import defaultdict

# --- Helper Functions ---
# Esta función no requiere cambios.
def parse_uf_value_from_string(value_str: Optional[str]) -> Optional[float]:
    if value_str is None: return None
    text = str(value_str).strip().lower()
    if any(term in text for term in ["sin copago", "sin deducible", "gratis", "s/d", "sd", "no aplica", "n/a"]) or text == "0": return 0.0
    match = re.search(r'([\d.,]+)', text)
    if not match: return None
    num_part = match.group(1)
    if ',' in num_part: cleaned_num_str = num_part.replace('.', '').replace(',', '.')
    elif '.' in num_part:
        if len(num_part.split('.')[-1]) == 3 and len(num_part) > 4 : cleaned_num_str = num_part.replace('.', '')
        else: cleaned_num_str = num_part
    else: cleaned_num_str = num_part
    try: return float(cleaned_num_str)
    except (ValueError, TypeError): return None

# --- Pydantic Models for LLM Output Validation ---

class PolicyHolderInfo(BaseModel):
    insured_name: Optional[str] = Field(default=None)
    insured_rut: Optional[str] = Field(default=None)

class VehicleInfo(BaseModel):
    make: Optional[str] = Field(default=None)
    model: Optional[str] = Field(default=None)
    year: Optional[int] = Field(default=None)
    
    def is_valid(self) -> bool: 
        return bool(self.make and self.model and self.year)

class WorkshopDetail(BaseModel):
    workshop_type: Optional[str] = Field(default=None)
    conditions_observations: Optional[str] = Field(default=None)


# --- INICIO DE LA SECCIÓN MODIFICADA ---

# --- NUEVO MODELO PARA DEDUCIBLE INTELIGENTE ---
class SmartDeductibleInfo(BaseModel):
    """Representa la información sobre la cobertura de Deducible Inteligente."""
    has_coverage: Optional[bool] = Field(default=False)
    conditions_observations: Optional[str] = Field(default=None)

    @field_validator('has_coverage', mode='before')
    @classmethod
    def validate_has_coverage(cls, v):
        """Asegura que 'has_coverage' sea siempre booleano, convirtiendo None a False."""
        return v if v is not None else False

class NewVehicleReplacementInfo(BaseModel):
    # El campo ahora es opcional para aceptar 'null' del LLM.
    has_coverage: Optional[bool] = Field(default=False)
    conditions_observations: Optional[str] = Field(default=None)

    # Este validador se asegura de que, después de la validación, el campo sea siempre
    # un booleano, convirtiendo 'None' a 'False'.
    @field_validator('has_coverage', mode='before')
    @classmethod
    def validate_has_coverage(cls, v):
        return v if v is not None else False

class ReplacementCarCoverage(BaseModel):
    # El campo ahora es opcional para aceptar 'null' del LLM.
    has_coverage: Optional[bool] = Field(default=False)
    daily_copay_original_str: Optional[str] = Field(default=None)
    days_limit_str: Optional[str] = Field(default=None)
    conditions_observations: Optional[str] = Field(default=None)

    # Validador para convertir 'None' a 'False'
    @field_validator('has_coverage', mode='before')
    @classmethod
    def validate_has_coverage(cls, v):
        return v if v is not None else False
        
# --- FIN DE LA SECCIÓN MODIFICADA ---


class DeductiblePremiumInfo(BaseModel):
    deductible_original_str: Optional[str] = Field(default=None)
    annual_premium_original_str: Optional[str] = Field(default=None)
    rc_coverage_original_str: Optional[str] = Field(default=None, description="Cobertura de Responsabilidad Civil en formato string, ej: '1000'")
    deductible_uf: Optional[float] = Field(default=None, exclude=True)
    annual_premium_uf: Optional[float] = Field(default=None, exclude=True)

    def process_and_convert_values(self):
        self.deductible_uf = parse_uf_value_from_string(self.deductible_original_str)
        self.annual_premium_uf = parse_uf_value_from_string(self.annual_premium_original_str)

class RCPlanAnalysis(BaseModel):
    insurer_name: Optional[str] = Field(default=None)
    plan_name: Optional[str] = Field(default=None)
    
    # --- MODIFICADO: Usar default_factory para crear objetos por defecto ---
    # Si el LLM omite el bloque 'workshop_info', Pydantic creará uno vacío
    # en lugar de lanzar un error.
    workshop_info: Optional[WorkshopDetail] = Field(default_factory=WorkshopDetail)
    replacement_car_info: Optional[ReplacementCarCoverage] = Field(default_factory=ReplacementCarCoverage)
    new_vehicle_replacement_info: Optional[NewVehicleReplacementInfo] = Field(default_factory=NewVehicleReplacementInfo)
    smart_deductible_info: Optional[SmartDeductibleInfo] = Field(default_factory=SmartDeductibleInfo) # <-- NUEVA LÍNEA
    # --- FIN MODIFICADO ---

    deductible_premiums: List[DeductiblePremiumInfo] = Field(default_factory=list)

class InsuranceExtractionOutput(BaseModel):
    error: Optional[str] = Field(default=None)
    document_type: Optional[str] = Field(default=None)
    policy_holder: Optional[PolicyHolderInfo] = Field(default=None)
    vehicle_info: Optional[VehicleInfo] = Field(default=None)
    policy_analyses: List[RCPlanAnalysis] = Field(default_factory=list)

    # Este validador ya no es tan crítico porque los campos son más flexibles,
    # pero se puede mantener si se desea. Se ha comentado para evitar
    # posibles conflictos con la nueva flexibilidad.
    # @model_validator(mode='after')
    # def check_validity(self) -> 'InsuranceExtractionOutput':
    #     if self.error: return self
    #     if not self.vehicle_info or not self.vehicle_info.is_valid(): 
    #         self.error = "Datos del vehículo insuficientes."
    #     return self

    def post_process_data(self):
        """
        Applies business logic to clean and refine the extracted data.
        - Processes and converts UF values.
        - Groups premiums and selects the cheapest.
        - Cleans up RC-only plans.
        """
        # Esta lógica no necesita cambios.
        if self.error:
            return

        INSURER_NORMALIZATION_MAP = {
            'hdi seguros': 'HDI', 'hdi seguros s.a.': 'HDI', 'bci seguros': 'BCI Seguros',
            'mapfre': 'MAPFRE', 'reale chile seguros generales s.a.': 'Reale Seguros',
            'reale seguros': 'Reale Seguros', 'reale': 'Reale Seguros',
            'fid chile seguros generales s.a.': 'FID Seguros', 'fid seguros': 'FID Seguros',
            'zurich chile seguros generales s.a.': 'Zurich',
        }
        
        RC_ONLY_KEYWORDS = ['elemental', 'r. civil', 'responsabilidad civil', '(rc)', 'basic', 'rc)', 'solo rc']

        for plan in self.policy_analyses:
            if plan.insurer_name:
                plan.insurer_name = INSURER_NORMALIZATION_MAP.get(plan.insurer_name.lower(), plan.insurer_name)

            for dp in plan.deductible_premiums:
                dp.process_and_convert_values()

            valid_premiums = [dp for dp in plan.deductible_premiums if dp.annual_premium_uf is not None]
            grouped_premiums = defaultdict(list)
            for dp in valid_premiums:
                grouped_premiums[dp.deductible_uf].append(dp)
            
            plan.deductible_premiums = [
                min(dp_list, key=lambda x: x.annual_premium_uf or float('inf')) 
                for dp_list in grouped_premiums.values() if dp_list
            ]
            
            plan_name_lower = plan.plan_name.lower() if plan.plan_name else ""
            is_rc_only = any(keyword in plan_name_lower for keyword in RC_ONLY_KEYWORDS)

            if is_rc_only:
                plan.workshop_info = None
                if plan.replacement_car_info:
                    plan.replacement_car_info.has_coverage = False
                plan.new_vehicle_replacement_info = None