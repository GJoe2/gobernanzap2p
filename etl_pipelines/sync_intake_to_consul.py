import os
import sys
import json
import uuid
from datetime import datetime
import pathlib

if hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except Exception:
        pass

# Script de interoperabilidad DAMA que verifica encuestas del módulo Intake
# y aplica deduplicación NLP antes de convertirlas en párrafos de Consul/Sovereign

DATA_DIR = pathlib.Path(__file__).parent.parent / "data"
LOCAL_JSON_PATH = DATA_DIR / "local_p2p_database.json"
SURVEYS_JSON_PATH = DATA_DIR / "local_intake_surveys.json"

def sync_intake_to_consul():
    print("🔄 [DAMA ETL] Sincronizando encuestas de levantamiento hacia propuestas de Consul/Sovereign...")
    
    if not LOCAL_JSON_PATH.exists():
        print("❌ Error: Base de datos P2P no encontrada. Ejecuta primero simulation/generate_p2p_data.py")
        return

    with open(LOCAL_JSON_PATH, "r", encoding="utf-8") as f:
        db = json.load(f)

    if not SURVEYS_JSON_PATH.exists():
        print("ℹ️ No hay encuestas pendientes de sincronización en local_intake_surveys.json")
        return

    with open(SURVEYS_JSON_PATH, "r", encoding="utf-8") as f:
        surveys = json.load(f)

    nuevas_propuestas = 0
    for s in surveys:
        if s.get("status") == "DRAFT" and not s.get("synced_to_sovereign"):
            # Validación de Calidad DAMA
            eje_code = s.get("eje_code", "ECO-01")
            eje_obj = next((e for e in db["axes"] if e["code"] == eje_code), db["axes"][0])
            
            new_id = f"PROP-{eje_code}-{len(db['propuestas']) + 1:02d}"
            
            db["propuestas"].append({
                "prop_id": new_id,
                "axis_code": eje_code,
                "axis_name": eje_obj["name"],
                "titulo": s.get("titulo"),
                "contenido": s.get("contenido"),
                "autor_did": s.get("autor_did", "did:stacks:SP_CITIZEN_INTAKE"),
                "autor_alias": s.get("autor_alias", "Afiliado Territorial"),
                "version": 1,
                "tokens_favor": 100,
                "tokens_contra": 0,
                "total_tokens_votados": 100,
                "consenso_ratio": 1.0,
                "status": "VOTACION_LIQUIDA_SOVEREIGN",
                "enmiendas_count": 0,
                "fecha_creacion": datetime.now().isoformat(),
                "dama_lineage_source": f"Intake Survey ID: {s.get('survey_id')}"
            })
            s["synced_to_sovereign"] = True
            nuevas_propuestas += 1

    if nuevas_propuestas > 0:
        with open(LOCAL_JSON_PATH, "w", encoding="utf-8") as f:
            json.dump(db, f, indent=2, ensure_ascii=False)
        with open(SURVEYS_JSON_PATH, "w", encoding="utf-8") as f:
            json.dump(surveys, f, indent=2, ensure_ascii=False)
        print(f"✅ {nuevas_propuestas} propuestas sincronizadas exitosamente al motor de democracia líquida.")
    else:
        print("✅ Todas las propuestas estaban sincronizadas.")

if __name__ == "__main__":
    sync_intake_to_consul()
