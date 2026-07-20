import os
import sys
import json
import uuid
import random
from datetime import datetime, timedelta
import pathlib

if hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except Exception:
        pass

# Intentar importar pymongo (si está disponible y MongoDB corriendo)
try:
    import pymongo
    MONGO_AVAILABLE = True
except ImportError:
    MONGO_AVAILABLE = False

DATA_DIR = pathlib.Path(__file__).parent.parent / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)
LOCAL_JSON_PATH = DATA_DIR / "local_p2p_database.json"

def generate_did(idx):
    return f"did:stacks:SP{uuid.uuid5(uuid.NAMESPACE_DNS, str(idx)).hex[:16].upper()}"

def generate_mock_ecosystem():
    print("🚀 Generando datos simulados de Gobernanza P2P, Democracia Líquida y DAMA-DMBOK...")
    
    # 1. Ejes Ideológicos
    axes = [
        {"code": "ECO-01", "name": "Economía, Trabajo y Productividad", "token": "TOKEN_ECO", "color": "#10B981"},
        {"code": "EDU-02", "name": "Educación, Ciencia e IA Pública", "token": "TOKEN_EDU", "color": "#3B82F6"},
        {"code": "SAL-03", "name": "Salud Integral y Bienestar", "token": "TOKEN_SAL", "color": "#F59E0B"},
        {"code": "REF-04", "name": "Reforma Política y Gobernanza P2P", "token": "TOKEN_REF", "color": "#8B5CF6"},
        {"code": "AMB-05", "name": "Ambiente y Transición Ecológica", "token": "TOKEN_AMB", "color": "#EC4899"}
    ]

    territorios = [
        "Distrito Capital - Centro", "Distrito Capital - Norte", "Zona Metropolitana Occidente",
        "Región Sur - Agrícola", "Región Costera / Puerto", "Polo Tecnológico e Industrial", "Diáspora / Exterior"
    ]

    # 2. Afiliados / Militantes (Golden Records DAMA MDM)
    nombres_base = [
        ("Dr. Carlos Mendoza", "DELEGADO_TEMATICO", "ECO-01", "Economista y ex-consultor público"),
        ("Dra. Elena Ramos", "DELEGADO_TEMATICO", "AMB-05", "Bióloga marina y activista ambiental"),
        ("Ing. Sofía Vargas", "DELEGADO_TEMATICO", "EDU-02", "Especialista en IA Cívica y ciberseguridad"),
        ("Lic. Marcos Peña", "DELEGADO_TEMATICO", "REF-04", "Abogado constitucionalista y experto en DAOs"),
        ("Dra. Valeria Gómez", "DELEGADO_TEMATICO", "SAL-03", "Médica sanitarista y epidemióloga"),
        ("Andrés Benítez", "MILITANTE_VERIFICADO", None, "Líder estudiantil universitario"),
        ("Camila Soto", "MILITANTE_VERIFICADO", None, "Emprendedora tecnológica cooperativa"),
        ("Javier Morales", "SIMPATIZANTE", None, "Trabajador autónomo y vecino comunitario"),
        ("Lucía Fernández", "MILITANTE_VERIFICADO", None, "Docente de escuela técnica pública"),
        ("Rodrigo Silva", "SIMPATIZANTE", None, "Investigador en energías renovables")
    ]

    afiliados = []
    for i in range(1, 65):
        did = generate_did(i)
        if i <= len(nombres_base):
            alias, rol, eje_exp, bio = nombres_base[i-1]
        else:
            alias = f"Militante Cívico #{i}"
            rol = random.choices(["SIMPATIZANTE", "MILITANTE_VERIFICADO"], weights=[0.4, 0.6])[0]
            eje_exp = None
            bio = "Participante orgánico de la red P2P territorial."

        balances = {e["code"]: 100 for e in axes}
        
        afiliados.append({
            "did_id": did,
            "alias_civico": alias,
            "rol_partidario": rol,
            "eje_especialidad": eje_exp,
            "bio": bio,
            "territorio": random.choice(territorios),
            "balances_tokens": balances,
            "sybil_verified": True if rol != "SIMPATIZANTE" else random.choice([True, False]),
            "fecha_ingreso": (datetime.now() - timedelta(days=random.randint(10, 300))).isoformat()
        })

    # 3. Delegaciones Líquidas (Sovereign P2P Graph)
    delegaciones = []
    delegados_por_eje = {
        "ECO-01": afiliados[0]["did_id"],
        "AMB-05": afiliados[1]["did_id"],
        "EDU-02": afiliados[2]["did_id"],
        "REF-04": afiliados[3]["did_id"],
        "SAL-03": afiliados[4]["did_id"]
    }

    # Crear red de confianza delegativa
    for a in afiliados[5:]:
        # Cada militante decide si delega o vota directo en cada eje
        for eje_code, del_did in delegados_por_eje.items():
            if random.random() < 0.65: # 65% probabilidad de delegar al referente técnico
                delegaciones.append({
                    "tx_id": str(uuid.uuid4()),
                    "timestamp": (datetime.now() - timedelta(days=random.randint(1, 15))).isoformat(),
                    "sender_did": a["did_id"],
                    "sender_alias": a["alias_civico"],
                    "target_did": del_did,
                    "target_alias": next(item["alias_civico"] for item in afiliados if item["did_id"] == del_did),
                    "axis_code": eje_code,
                    "tokens_delegated": 100,
                    "status": "ACTIVE_DELEGATION"
                })

    # 4. Propuestas e Incisos del Ideario (Consul Collaborative Legislation + Sovereign Votes)
    propuestas_data = [
        ("ECO-01", "Renta Básica de Innovación y Cooperativismo Digital", 
         "Establecer un fondo soberano regional alimentado por regalías energéticas e impositivas a grandes corporaciones tecnológicas, destinado a financiar cooperativas de software de código abierto y emprendimientos juveniles."),
        ("ECO-01", "Reforma Fiscal Verde y Simplificación Tributaria",
         "Eliminar impuestos distorsivos al pequeño comerciante y aplicar tasas progresivas y trazables en blockchain a la especulación financiera y huella de carbono industrial."),
        ("EDU-02", "Soberanía Tecnológica y Código Abierto en el Estado",
         "Obligatoriedad de que el 100% del software adquirido o desarrollado para la administración pública sea de código libre y auditable por la ciudadanía (estilo LaSuite.coop / Sovereign)."),
        ("EDU-02", "Plan Nacional de Alfabetización en IA Cívica",
         "Incorporar programación en Python y ética de Inteligencia Artificial como materia curricular obligatoria desde la escuela secundaria pública."),
        ("SAL-03", "Historia Clínica Universal Descentralizada y Privada (DID)",
         "Crear un protocolo nacional de salud donde cada paciente sea dueño criptográfico de su historia clínica mediante credenciales verificables, eliminando la burocracia entre hospitales."),
        ("SAL-03", "Plan Integral de Salud Mental Comunitaria en Barrios",
         "Apertura de centros territoriales de escucha y atención comunitaria interdisciplinaria en todos los distritos urbanos con financiamiento participativo prioritario."),
        ("REF-04", "Presupuesto Participativo Mandatorio sobre el 15% Municipal",
         "Por ley constitucional, los municipios deberán someter el 15% de su presupuesto de inversión pública a votación directa y delegativa digital de los vecinos vía plataformas abiertas."),
        ("REF-04", "Revocatoria de Mandato Ágil mediante Firmas Digitales Verificadas",
         "Habilitar el proceso de referéndum revocatorio para cargos electivos intermedios cuando el 20% del padrón verificado en el sistema P2P lo solicite digitalmente."),
        ("AMB-05", "Protección Total de Humedales y Cuencas Hídricas",
         "Prohibición absoluta y penalización severa a la deforestación y cambio de uso de suelo en zonas adyacentes a cuencas hídricas y humedales urbanos y rurales."),
        ("AMB-05", "Transición Solar Distribuida con Generación Comunitaria",
         "Incentivos fiscales para que barrios y consorcios instalen granjas solares compartidas, vendiendo el excedente limpio a la red eléctrica pública.")
    ]

    propuestas = []
    transacciones_voto = []

    for idx, (eje, titulo, contenido) in enumerate(propuestas_data, 1):
        prop_id = f"PROP-{eje}-{idx:02d}"
        autor = random.choice(afiliados[5:15])
        
        # Calcular votos directos y por delegación líquida
        votos_a_favor = 0
        votos_en_contra = 0
        tokens_a_favor = 0
        tokens_en_contra = 0
        
        # Voto de los delegados temáticos primero
        delegado_eje_did = delegados_por_eje[eje]
        voto_delegado = random.choices(["FAVOR", "CONTRA"], weights=[0.8, 0.2])[0]
        
        # Sumar tokens directos del delegado + todos los que le delegaron y no sobreescribieron
        tokens_delegados_recibidos = sum(d["tokens_delegated"] for d in delegaciones if d["target_did"] == delegado_eje_did and d["axis_code"] == eje)
        tokens_totales_delegado = 100 + int(tokens_delegados_recibidos * random.uniform(0.7, 0.95)) # Un % no sobreescribe
        
        if voto_delegado == "FAVOR":
            votos_a_favor += 1
            tokens_a_favor += tokens_totales_delegado
        else:
            votos_en_contra += 1
            tokens_en_contra += tokens_totales_delegado

        transacciones_voto.append({
            "tx_id": str(uuid.uuid4()),
            "timestamp": datetime.now().isoformat(),
            "proposal_id": prop_id,
            "voter_did": delegado_eje_did,
            "voter_alias": next(item["alias_civico"] for item in afiliados if item["did_id"] == delegado_eje_did),
            "axis_code": eje,
            "tokens_weight": tokens_totales_delegado,
            "direction": voto_delegado,
            "is_delegated_bundle": True
        })

        # Votos directos independientes
        for a in afiliados[10:35]:
            dir_voto = random.choices(["FAVOR", "CONTRA"], weights=[0.75, 0.25])[0]
            if dir_voto == "FAVOR":
                votos_a_favor += 1
                tokens_a_favor += 100
            else:
                votos_en_contra += 1
                tokens_en_contra += 100
                
            transacciones_voto.append({
                "tx_id": str(uuid.uuid4()),
                "timestamp": (datetime.now() - timedelta(hours=random.randint(1, 48))).isoformat(),
                "proposal_id": prop_id,
                "voter_did": a["did_id"],
                "voter_alias": a["alias_civico"],
                "axis_code": eje,
                "tokens_weight": 100,
                "direction": dir_voto,
                "is_delegated_bundle": False
            })

        total_tokens = tokens_a_favor + tokens_en_contra
        consenso_ratio = round(tokens_a_favor / total_tokens, 3) if total_tokens > 0 else 0

        status = "APROBADO_IDEARIO_FINAL" if consenso_ratio >= 0.66 else ("VOTACION_LIQUIDA_SOVEREIGN" if consenso_ratio >= 0.50 else "EN_REVISION_ENMIENDAS")

        propuestas.append({
            "prop_id": prop_id,
            "axis_code": eje,
            "axis_name": next(x["name"] for x in axes if x["code"] == eje),
            "titulo": titulo,
            "contenido": contenido,
            "autor_did": autor["did_id"],
            "autor_alias": autor["alias_civico"],
            "version": 1,
            "tokens_favor": tokens_a_favor,
            "tokens_contra": tokens_en_contra,
            "total_tokens_votados": total_tokens,
            "consenso_ratio": consenso_ratio,
            "status": status,
            "enmiendas_count": random.randint(1, 6),
            "fecha_creacion": (datetime.now() - timedelta(days=random.randint(3, 20))).isoformat()
        })

    # 5. Deliberación IA (Polis AI Deliberation Clusters)
    polis_clusters = [
        {
            "cluster_id": 1,
            "name": "Facción Innovación & Cooperativismo Digital",
            "size_percent": 42.5,
            "color": "#3B82F6",
            "pos_x": -0.65,
            "pos_y": 0.45,
            "key_traits": ["Soberanía digital", "Cooperativas de software", "Renta básica P2P"]
        },
        {
            "cluster_id": 2,
            "name": "Facción Ecologista & Descentralización Territorial",
            "size_percent": 38.0,
            "color": "#10B981",
            "pos_x": 0.55,
            "pos_y": 0.50,
            "key_traits": ["Presupuesto participativo 15%", "Protección humedales", "Energía solar de barrio"]
        },
        {
            "cluster_id": 3,
            "name": "Facción Institucionalista y Reforma Constitucional",
            "size_percent": 19.5,
            "color": "#8B5CF6",
            "pos_x": 0.10,
            "pos_y": -0.70,
            "key_traits": ["Auditoría DAMA-DMBOK", "Revocatoria de mandato por DID", "Transparencia fiscal"]
        }
    ]

    consensus_bridges = [
        {
            "statement": "El software del Estado y el ideario deben regirse por código abierto auditable y democracia líquida revocable.",
            "approval_cluster_1": 96.2,
            "approval_cluster_2": 94.0,
            "approval_cluster_3": 89.5,
            "overall_consensus": 94.1,
            "is_bridge": True
        },
        {
            "statement": "Todo municipio debe someter al menos el 15% de su inversión a votación directa y delegada en plataformas P2P.",
            "approval_cluster_1": 88.0,
            "approval_cluster_2": 97.5,
            "approval_cluster_3": 82.0,
            "overall_consensus": 90.3,
            "is_bridge": True
        },
        {
            "statement": "Los balances de tokens de voto deben ser inmutables pero disociados de la identidad civil para proteger el voto secreto.",
            "approval_cluster_1": 91.0,
            "approval_cluster_2": 85.0,
            "approval_cluster_3": 95.0,
            "overall_consensus": 90.1,
            "is_bridge": True
        }
    ]

    # Guardar en archivo local JSON como Single Source of Truth robusto y portable
    database_dump = {
        "metadata": {
            "created_at": datetime.now().isoformat(),
            "dama_compliance": "DAMA-DMBOK v2 Level 4 (Managed & Audited)",
            "total_afiliados": len(afiliados),
            "total_propuestas": len(propuestas),
            "total_delegaciones": len(delegaciones),
            "total_transacciones_voto": len(transacciones_voto)
        },
        "axes": axes,
        "afiliados": afiliados,
        "delegaciones": delegaciones,
        "propuestas": propuestas,
        "transacciones_voto": transacciones_voto,
        "polis_clusters": polis_clusters,
        "consensus_bridges": consensus_bridges
    }

    with open(LOCAL_JSON_PATH, "w", encoding="utf-8") as f:
        json.dump(database_dump, f, indent=2, ensure_ascii=False)

    print(f"✅ Base de datos simulada creada exitosamente en: {LOCAL_JSON_PATH}")
    
    # Intentar cargar en MongoDB local si está corriendo
    if MONGO_AVAILABLE:
        try:
            client = pymongo.MongoClient("mongodb://localhost:27017/", serverSelectionTimeoutMS=1500)
            client.server_info() # Check connection
            db = client["sovereign_db"]
            db.afiliados.drop()
            db.delegaciones.drop()
            db.propuestas.drop()
            db.transacciones_voto.drop()
            db.polis_clusters.drop()
            
            db.afiliados.insert_many(afiliados)
            db.delegaciones.insert_many(delegaciones)
            db.propuestas.insert_many(propuestas)
            db.transacciones_voto.insert_many(transacciones_voto)
            db.polis_clusters.insert_many(polis_clusters)
            print("🚀 Sincronizado correctamente con servidor MongoDB en localhost:27017/sovereign_db!")
        except Exception as e:
            print(f"ℹ️ MongoDB local no activo aún ({e}). Las aplicaciones utilizarán el adaptador local JSON portable sin interrupciones.")

    return database_dump

if __name__ == "__main__":
    generate_mock_ecosystem()
