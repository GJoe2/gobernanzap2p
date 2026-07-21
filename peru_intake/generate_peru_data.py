import os
import sys
import json
import uuid
import random
from datetime import datetime, timedelta
import pathlib

# Configurar encoding utf-8 en Windows
if hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

ROOT_DIR = pathlib.Path(__file__).parent.parent
sys.path.append(str(ROOT_DIR))

from peru_intake.peru_demographics import (
    REGIONES_PERU, AMBITOS_TERRITORIALES, RANGOS_ETARIOS,
    SITUACIONES_LABORALES, NIVELES_EDUCATIVOS, PREGUNTAS_ESTRUCTURADAS, EJES_IDEARIO_PERU
)
from peru_intake.nlp_peru_classifier import PeruNLPClassifier

def generate_mock_peru_surveys(num_surveys=160):
    """
    Genera una base de datos simulada y realista de encuestas ciudadanas de todas
    las regiones del Perú con cruces sociodemográficos y testimonios en dialecto peruano.
    """
    print("🚀 Generando 160 encuestas territoriales representativas en las 24 regiones del Perú...")
    
    classifier = PeruNLPClassifier()
    surveys = []

    # Muestras de testimonios realistas en español peruano según la problemática
    testimonios_pool = [
        ("Inseguridad ciudadana, delincuencia común, sicariato y extorsión", 
         "En nuestro distrito ya no se puede abrir el negocio en paz porque te piden cupo o te llaman amenazando. Necesitamos que la policía actúe de verdad y que los jueces no suelten a los delincuentes a las 24 horas."),
        
        ("Falta de agua potable, alcantarillado y servicios básicos domiciliarios",
         "Aquí en el cono norte el agua solo llega por dos horas en la madrugada y a veces viene turbia. Pagamos más a los camiones cisterna que la gente que tiene agua todo el día en San Isidro o Miraflores."),
         
        ("Desempleo, subempleo e informalidad laboral sin protección",
         "Soy comerciante independiente y trabajo doce horas al día, pero las ventas han bajado y todo sube de precio. Si uno se enferma no tiene ni seguro de salud ni CTS para aguantar."),
         
        ("Hospitales y postas desabastecidas, sin médicos ni citas oportunas",
         "Mi mamá tiene diabetes y para conseguir cita en la posta médica nos dan para dentro de tres meses. Cuando vamos al SIS nunca hay pastillas y tenemos que comprar todo en la farmacia privada."),
         
        ("Pistas, carreteras y puentes en mal estado u obras públicas paralizadas",
         "La carretera hacia nuestra provincia está destrozada desde las últimas lluvias del fenómeno del Niño. Los camiones con nuestras hortalizas se demoran el doble en llegar al mercado y la fruta se malograda."),
         
        ("Abandono de la agricultura, falta de fertilizantes y canales de riego",
         "Los fertilizantes están carísimos y el canal de riego comunal está sin revestir desde hace años, se pierde más de la mitad del agua antes de llegar a la chacra. El agro peruano está abandonado."),
         
        ("Contaminación ambiental, minería ilegal o tala indiscriminada",
         "El río donde pescábamos antes ahora baja marrón por los relaves de la minería ilegal y los metales pesados. Necesitamos fiscalización ambiental severa antes de que nuestros hijos se enfermen."),
         
        ("Colegios públicos deteriorados y bajo nivel en la educación escolar",
         "El colegio de mi comunidad tiene las calaminas rotas y no hay computadoras ni internet para los alumnos. ¿Cómo van a competir los jóvenes del interior con los que estudian en colegios privados de la capital?")
    ]

    # Asegurar presencia equitativa en todas las regiones
    for i in range(num_surveys):
        region = REGIONES_PERU[i % len(REGIONES_PERU)]
        
        # Ponderación natural de ámbito según región (en Lima más urbano, en sierra/selva más rural)
        if "Lima" in region or "Callao" in region:
            ambito = random.choices(AMBITOS_TERRITORIALES, weights=[0.88, 0.12])[0]
        elif region in ["Cusco", "Puno", "Ayacucho", "Cajamarca", "Apurímac", "Huancavelica", "Amazonas"]:
            ambito = random.choices(AMBITOS_TERRITORIALES, weights=[0.45, 0.55])[0]
        else:
            ambito = random.choices(AMBITOS_TERRITORIALES, weights=[0.65, 0.35])[0]

        rango_edad = random.choice(RANGOS_ETARIOS)
        genero = random.choices(["Masculino", "Femenino"], weights=[0.50, 0.50])[0]
        educacion = random.choice(NIVELES_EDUCATIVOS)
        
        # Situación laboral pesando informalidad
        sit_laboral = random.choices(
            SITUACIONES_LABORALES,
            weights=[0.48, 0.22, 0.14, 0.06, 0.06, 0.04]
        )[0]

        # Seleccionar problema de P1 y su testimonio par
        problema_p1, testimonio_txt = random.choice(testimonios_pool)
        
        # Opciones de P2 y P3
        problema_p2 = random.choice(PREGUNTAS_ESTRUCTURADAS["P2"]["opciones"])
        prioridad_p3 = random.choice(PREGUNTAS_ESTRUCTURADAS["P3"]["opciones"])

        # Clasificación automática DAMA del Eje basándonos en el testimonio y problema
        eje_code, confianza = classifier.classify_eje(f"{problema_p1} {testimonio_txt}")
        eje_name = EJES_IDEARIO_PERU.get(eje_code, {}).get("nombre", eje_code)

        # Generar fecha en los últimos 15 días
        dias_atras = random.randint(0, 15)
        timestamp = (datetime.now() - timedelta(days=dias_atras)).isoformat()

        survey_record = {
            "survey_id": f"PERU-{uuid.uuid4().hex[:8].upper()}",
            "region": region,
            "ambito_territorial": ambito,
            "rango_edad": rango_edad,
            "genero": genero,
            "nivel_educativo": educacion,
            "situacion_laboral": sit_laboral,
            "p1_problema_region": problema_p1,
            "p2_problema_familiar": problema_p2,
            "p3_prioridad_gobierno": prioridad_p3,
            "testimonio_abierto": testimonio_txt,
            "origen_registro": random.choice(["MODO_CIUDADANO_CELULAR", "MODO_BRIGADISTA_CALLE"]),
            "eje_asignado": eje_code,
            "eje_nombre": eje_name,
            "dama_verified": True,
            "did_verificador": f"did:stacks:PERU_{uuid.uuid4().hex[:6]}",
            "timestamp": timestamp
        }
        surveys.append(survey_record)

    # Guardar en archivo
    data_dir = ROOT_DIR / "peru_intake" / "data"
    data_dir.mkdir(parents=True, exist_ok=True)
    db_path = data_dir / "peru_surveys_database.json"
    
    with open(db_path, "w", encoding="utf-8") as f:
        json.dump(surveys, f, indent=2, ensure_ascii=False)
        
    print(f"✅ Base de datos simulada del Perú creada exitosamente con {len(surveys)} encuestas: {db_path}")
    return surveys

if __name__ == "__main__":
    generate_mock_peru_surveys()
