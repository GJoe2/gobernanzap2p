# Catálogo Maestro y Taxonomía Sociodemográfica del Perú (DAMA MDM)
# Normaliza y estandariza las variables sociodemográficas, ámbitos territoriales y preguntas estratégicas.

REGIONES_PERU = [
    "Amazonas", "Áncash", "Apurímac", "Arequipa", "Ayacucho", "Cajamarca",
    "Callao (Provincia Constitucional)", "Cusco", "Huancavelica", "Huánuco",
    "Ica", "Junín", "La Libertad", "Lambayeque", "Lima Metropolitana",
    "Lima Provincias", "Loreto", "Madre de Dios", "Moquegua", "Pasco",
    "Piura", "Puno", "San Martín", "Tacna", "Tumbes", "Ucayali",
    "Diáspora (Peruanos en el Exterior)"
]

AMBITOS_TERRITORIALES = [
    "Urbano",
    "Rural"
]

RANGOS_ETARIOS = [
    "18-25 años (Juventud / Primer Empleo)",
    "26-35 años",
    "36-50 años",
    "51-65 años",
    "65+ años (Adulto Mayor)"
]

SITUACIONES_LABORALES = [
    "Trabajador Independiente / Comerciante / Emprendedor (MYPE / Sector Informal)",
    "Trabajador Dependiente Formal (Planilla sector público o privado)",
    "Agricultor / Ganadero / Productor Rural",
    "Estudiante",
    "Desempleado / Buscando empleo activamente",
    "Labores del hogar / Cuidado no remunerado / Jubilado"
]

NIVELES_EDUCATIVOS = [
    "Primaria",
    "Secundaria",
    "Técnico Superior",
    "Universitario incompleto / completo",
    "Postgrado (Maestría / Doctorado)"
]

EJES_IDEARIO_PERU = {
    "SEG-01": {"nombre": "Seguridad Ciudadana, Reforma Judicial y Anti-Extorsión", "color": "#EF4444"},
    "ECO-02": {"nombre": "Reactivación Económica, Formalización y Apoyo MYPE", "color": "#10B981"},
    "SAL-03": {"nombre": "Salud Pública, Postas Primarias y Medicinas SIS", "color": "#3B82F6"},
    "EDU-04": {"nombre": "Educación Técnica, Digital y Conectada al Empleo", "color": "#F59E0B"},
    "AGR-05": {"nombre": "Desarrollo Agrario, Canales de Riego y Seguridad Alimentaria", "color": "#8B5CF6"},
    "INF-06": {"nombre": "Infraestructura Regional, Agua Potable y Saneamiento", "color": "#06B6D4"}
}

PREGUNTAS_ESTRUCTURADAS = {
    "P1": {
        "pregunta": "1. ¿Aparte de la corrupción, cuál cree que es el MAYOR PROBLEMA que afronta su región o ciudad?",
        "opciones": [
            "Inseguridad ciudadana, delincuencia común, sicariato y extorsión",
            "Falta de agua potable, alcantarillado y servicios básicos domiciliarios",
            "Desempleo, subempleo e informalidad laboral sin protección",
            "Hospitales y postas desabastecidas, sin médicos ni citas oportunas",
            "Pistas, carreteras y puentes en mal estado u obras públicas paralizadas",
            "Abandono de la agricultura, falta de fertilizantes y canales de riego",
            "Contaminación ambiental, minería ilegal o tala indiscriminada",
            "Colegios públicos deteriorados y bajo nivel en la educación escolar",
            "OTRO (Especificar o grabar testimonio en voz)"
        ]
    },
    "P2": {
        "pregunta": "2. ¿Cuál es el MAYOR PROBLEMA que afronta usted o su familia por la situación actual del país?",
        "opciones": [
            "El alto costo de vida y el precio elevado de la canasta básica familiar",
            "Ingresos y sueldos insuficientes o inestabilidad laboral constante",
            "Miedo a ser víctima de robo, extorsión o créditos ilegales ('gota a gota')",
            "Gastos médicos de bolsillo para comprar medicinas o atenderse en clínicas",
            "Deudas excesivas y dificultades para acceder a créditos bancarios justos",
            "Preocupación por la calidad educativa o falta de oportunidades para los hijos",
            "Migración de hijos o familiares al extranjero por falta de futuro"
        ]
    },
    "P3": {
        "pregunta": "3. ¿Cuál cree que debería ser la PRIORIDAD INMEDIATA del próximo Congreso o Gobierno?",
        "opciones": [
            "Lucha implacable contra el crimen organizado, extorsión y depuración judicial/policial",
            "Reactivación económica, créditos blandos y reducción de trabas para MYPEs y Agro",
            "Declarar en emergencia la salud pública, construir y equipar postas primarias en regiones",
            "Shock nacional de inversiones en agua potable y alcantarillado regional",
            "Revolución de educación técnica y digital directamente articulada con el mercado laboral",
            "Destitución y penas severas de cárcel para jueces, fiscales y funcionarios corruptos"
        ]
    }
}
