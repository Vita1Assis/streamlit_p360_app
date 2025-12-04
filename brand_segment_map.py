# Mapeamento de Marca para Segmento (baseado na análise anterior)
BRAND_SEGMENT_MAP = {
    "Apple": "Tecnologia",
    "Samsung":"Tecnologia",
    "Apple": "Smartphones",
    "Samsung":"Smartphones",
    "Bartira": "Móveis"
    }
BRANDS = sorted(list(set(BRAND_SEGMENT_MAP.keys())))
BRANDS.insert(0, "Tudo")  # Adiciona opção "Tudo"

SEGMENTS = sorted(list(set(BRAND_SEGMENT_MAP.values())))
SEGMENTS.insert(0, "Tudo") # Adiciona a opção "Tudo" no início
