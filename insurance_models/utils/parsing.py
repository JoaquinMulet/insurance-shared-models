import re

def parse_uf_value(value_str: str | None) -> float | None:
    """
    Parsea un string que contiene un valor (posiblemente en UF) a un float.

    Esta función es la "fuente de la verdad" para convertir valores monetarios
    o de unidades en todo el sistema. Maneja:
    - Términos textuales para el valor cero (ej: "Sin Deducible", "Gratis", "No Aplica").
    - Separadores de miles chilenos (puntos).
    - Separadores decimales (comas y puntos).
    - Extrae solo la parte numérica de un string más largo (ej: "UF 5.5").

    Args:
        value_str: El string a parsear.

    Returns:
        Un float si la conversión es exitosa, 0.0 para términos de gratuidad,
        o None si no se puede parsear.
    """
    if value_str is None:
        return None
    
    text = str(value_str).strip().lower()
    
    # 1. Comprobar términos textuales para el valor cero.
    if any(term in text for term in ["sin deducible", "sin copago", "gratis", "no aplica", "n/a", "s/d"]):
        return 0.0
        
    # 2. Extraer la parte numérica del string.
    match = re.search(r'([\d.,]+)', text)
    if not match:
        return None
        
    num_part = match.group(1)
    
    # 3. Limpiar el número para manejar el formato chileno (punto como miles, coma como decimal).
    cleaned_num_str = ""
    if ',' in num_part and '.' in num_part:
        # Asume formato como "1.234,56" -> "1234.56"
        cleaned_num_str = num_part.replace('.', '').replace(',', '.')
    elif ',' in num_part:
        # Asume formato como "1234,56" -> "1234.56"
        cleaned_num_str = num_part.replace(',', '.')
    elif '.' in num_part:
        # Lógica para distinguir entre separador de miles y decimal.
        # Si hay más de un punto (ej: 1.234.567) o si el último grupo tiene 3 dígitos
        # y el número es largo (ej: 1.234), se asume que son separadores de miles.
        parts = num_part.split('.')
        if len(parts) > 2 or (len(parts) == 2 and len(parts[1]) == 3 and len(num_part) > 4):
            cleaned_num_str = num_part.replace('.', '')
        else:
            cleaned_num_str = num_part
    else:
        cleaned_num_str = num_part

    # 4. Intentar la conversión final a float.
    try:
        return float(cleaned_num_str)
    except (ValueError, TypeError):
        return None