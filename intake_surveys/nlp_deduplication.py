import re
from difflib import SequenceMatcher

class DAMANLPDeduplicator:
    """
    Motor de Calidad y Deduplicación Semántica DAMA-DMBOK.
    Compara las nuevas propuestas ciudadanas en bruto contra los incisos
    ya existentes o en redacción en Consul/Sovereign para evitar redundancias
    y mantener la integridad del catálogo de datos cívicos.
    """
    def __init__(self, threshold=0.78):
        self.threshold = threshold

    def _clean_text(self, text):
        if not text:
            return ""
        # Minúsculas y eliminar puntuación básica para normalización semántica
        text = text.lower()
        text = re.sub(r'[^\w\s]', '', text)
        return text.strip()

    def _token_overlap(self, text1, text2):
        words1 = set(self._clean_text(text1).split())
        words2 = set(self._clean_text(text2).split())
        if not words1 or not words2:
            return 0.0
        # Índice de Jaccard simplificado
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        return len(intersection) / len(union)

    def _sequence_similarity(self, text1, text2):
        t1 = self._clean_text(text1)
        t2 = self._clean_text(text2)
        return SequenceMatcher(None, t1, t2).ratio()

    def check_similarity(self, new_title, new_content, existing_proposals):
        """
        Calcula similitud híbrida (Jaccard + SequenceMatcher) entre la nueva propuesta
        y la lista de propuestas existentes.
        Retorna una lista de dicts con las coincidencias superadas el threshold.
        """
        matches = []
        new_combined = f"{new_title} {new_content}"

        for prop in existing_proposals:
            exist_combined = f"{prop.get('titulo', '')} {prop.get('contenido', '')}"
            seq_sim = self._sequence_similarity(new_combined, exist_combined)
            token_sim = self._token_overlap(new_combined, exist_combined)
            
            # Ponderación híbrida
            score = round((seq_sim * 0.6) + (token_sim * 0.4), 3)

            if score >= self.threshold or self._sequence_similarity(self._clean_text(new_title), self._clean_text(prop.get('titulo', ''))) >= 0.75:
                matches.append({
                    "prop_id": prop.get("prop_id", "DRAFT"),
                    "titulo": prop.get("titulo", "Sin Título"),
                    "axis_code": prop.get("axis_code", ""),
                    "similarity_score": score,
                    "status": prop.get("status", "BORRADOR")
                })

        # Ordenar por mayor similitud
        matches.sort(key=lambda x: x["similarity_score"], reverse=True)
        return matches
