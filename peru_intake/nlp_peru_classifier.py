import re
from difflib import SequenceMatcher

class PeruNLPClassifier:
    """
    Clasificador Semántico y Deduplicador DAMA-DMBOK v2 para el Perú.
    1. Clasifica automáticamente respuestas abiertas o notas de voz transcritas
       hacia uno de los 6 Ejes del Ideario Partidario.
    2. Calcula similitud semántica contra encuestas previas en la misma región
       para evitar duplicación y detectar focos de consenso ciudadano.
    """
    def __init__(self, deduplication_threshold=0.74):
        self.threshold = deduplication_threshold
        
        # Diccionario de palabras clave peruanas para asignación automática de Ejes
        self.eje_keywords = {
            "SEG-01": [
                "robo", "inseguridad", "delincuencia", "sicariato", "extorsion", "extorsiones",
                "cupo", "gota a gota", "policia", "jueces", "fiscales", "carcel", "seguridad",
                "crimen", "bandas", "delincuentes", "asaltos", "cámaras", "penal"
            ],
            "ECO-02": [
                "empleo", "chamba", "sueldo", "ingresos", "canasta", "precios", "plata", "dinero",
                "mype", "emprendedor", "comerciante", "informal", "formalizacion", "creditos",
                "banco", "deuda", "impuestos", "sunat", "trabajo", "pobreza", "economía"
            ],
            "SAL-03": [
                "posta", "postas", "hospital", "hospitales", "medicos", "medico", "doctor",
                "citas", "medicina", "medicinas", "sis", "essalud", "salud", "enfermo",
                "ambulancia", "emergencia", "atencion", "camas"
            ],
            "EDU-04": [
                "colegio", "colegios", "escuela", "escuelas", "educacion", "profesores", "maestros",
                "universidad", "instituto", "hijos", "futuro", "becas", "internet", "aulas", "tecnico"
            ],
            "AGR-05": [
                "agro", "agricultura", "campesino", "campo", "siembra", "cosecha", "riego",
                "fertilizantes", "urea", "ganado", "ganaderia", "chacra", "productores",
                "sequia", "heladas", "agrario"
            ],
            "INF-06": [
                "agua", "desague", "alcantarillado", "pistas", "carreteras", "puentes", "obras",
                "luz", "electricidad", "internet", "basura", "contaminacion", "mineria ilegal",
                "rio", "desbordes", "fenomeno del nino", "infraestructura", "servicios"
            ]
        }

    def _clean_text(self, text):
        if not text:
            return ""
        text = text.lower()
        # Eliminar tildes comunes para robustez del matching
        text = text.replace("á", "a").replace("é", "e").replace("í", "i").replace("ó", "o").replace("ú", "u")
        text = re.sub(r'[^\w\s]', '', text)
        return text.strip()

    def classify_eje(self, text):
        """
        Asigna el código de Eje temático más probable a partir de un texto en español peruano.
        Retorna (eje_code, confianza_estimada).
        """
        cleaned = self._clean_text(text)
        if not cleaned:
            return "ECO-02", 0.5  # Eje por defecto

        words = set(cleaned.split())
        scores = {}

        for eje_code, kw_list in self.eje_keywords.items():
            count = 0
            for kw in kw_list:
                kw_clean = self._clean_text(kw)
                if kw_clean in words or any(kw_clean in w for w in words):
                    count += 1
            scores[eje_code] = count

        best_eje = max(scores, key=scores.get)
        max_score = scores[best_eje]

        if max_score == 0:
            return "ECO-02", 0.51  # Si no detecta palabra clave específica, cae en Economía
        else:
            confianza = min(0.98, round(0.60 + (max_score * 0.12), 2))
            return best_eje, confianza

    def find_duplicate_or_similar(self, new_text, existing_surveys, region=None):
        """
        Busca si ya existe una problemática o propuesta semánticamente muy similar en la misma región
        o a nivel nacional, cumpliendo con la deduplicación DAMA.
        """
        matches = []
        new_clean = self._clean_text(new_text)
        if not new_clean or len(new_clean) < 10:
            return matches

        for item in existing_surveys:
            # Priorizar búsqueda dentro de la misma región si se especifica
            if region and item.get("region") != region and region != "TODAS":
                continue

            exist_text = item.get("p1_problema_region", "") + " " + item.get("testimonio_abierto", "")
            exist_clean = self._clean_text(exist_text)
            
            if not exist_clean:
                continue

            seq_ratio = SequenceMatcher(None, new_clean, exist_clean).ratio()
            
            # Intersección de palabras
            w_new = set(new_clean.split())
            w_exist = set(exist_clean.split())
            jaccard = len(w_new.intersection(w_exist)) / len(w_new.union(w_exist)) if w_new and w_exist else 0.0

            score = round((seq_ratio * 0.65) + (jaccard * 0.35), 3)

            if score >= self.threshold:
                matches.append({
                    "survey_id": item.get("survey_id", "DRAFT"),
                    "region": item.get("region", "Perú"),
                    "problema": item.get("p1_problema_region", ""),
                    "testimonio": item.get("testimonio_abierto", "Sin testimonio adicional"),
                    "eje_code": item.get("eje_asignado", "SEG-01"),
                    "similarity_score": score
                })

        matches.sort(key=lambda x: x["similarity_score"], reverse=True)
        return matches[:3]
