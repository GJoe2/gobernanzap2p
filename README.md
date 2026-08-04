<div align="center">
  
# ObservaPe
### Observatorio Digital para la Vigilancia Democrática

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![Status: MVP Development](https://img.shields.io/badge/Status-MVP_Development-orange.svg)]()
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)]()

*Una propuesta de ciencia ciudadana y activismo digital participativo para la vigilancia estratégica del gobierno peruano 2026–2031.*

[Qué es](#qué-es-observape) •
[Antecedentes](#antecedentes-y-justificación) •
[Stack Tecnológico](#stack-tecnológico) •
[Cómo Contribuir](#cómo-contribuir) •
[Licencia](#licencia)

---
</div>

## 📖 Resumen Ejecutivo
**ObservaPe** es una plataforma digital ciudadana de código abierto concebida para convertir las promesas del gobierno peruano (2026–2031) en indicadores públicos, auditables y verificables en tiempo real.

La iniciativa parte de una premisa estructural: la brecha entre lo que se promete y lo que se hace no puede depender exclusivamente de la voluntad del Estado que debe ser vigilado. ObservaPe opera con un reloj ciudadano con conteo regresivo de 1826 días y un motor de **Inteligencia Artificial** que cruza fuentes oficiales para emitir **alertas tempranas** a la ciudadanía.

> *"Toda promesa sin métrica es una intención. Toda intención sin seguimiento es retórica. ObservaPe convierte intenciones en contratos ciudadanos."*

## 🌍 Antecedentes y Justificación
El problema de los gobiernos que prometen y no cumplen ha sido enfrentado internacionalmente con tecnología cívica:
* **Taiwán (g0v):** Hackers cívicos tomaron los sistemas del gobierno y los reimplementaron como plataformas abiertas.
* **Estonia:** Arquitectura de confianza técnica y soberanía de datos, sin depender de la voluntad política.
* **Chile (Laboratorio de Gobierno):** Co-creación institucional con evaluación trimestral pública.

En el Perú, el populismo electoral opera sobre promesas sin arquitectura de implementación. El discurso presidencial inaugural incluyó decenas de promesas de digitalización e IA. **ObservaPe** es la respuesta independiente para saber, mes a mes, si se están cumpliendo.

## 🚀 ¿Qué es ObservaPe?
No es una plataforma de quejas, ni un partido político. Es una herramienta de **ciencia ciudadana** que opera bajo 6 componentes funcionales:

1. **Reloj Regresivo (1826 días):** Conteo exacto del tiempo de mandato (28 Julio 2026 - 27 Julio 2031).
2. **Ingesta Automática (Scraping):** Lectura constante del Congreso de la República (proyectos de ley) y el diario oficial El Peruano (normas y resoluciones).
3. **Agente Evaluador de IA:** Un modelo de Inteligencia Artificial lee los datos extraídos diariamente y los contrasta con el catálogo de promesas del gobierno para identificar avances, estancamientos o bloqueos.
4. **Catálogo de Semáforos:** Dashboard público donde cada promesa tiene un estado visible y medible.
5. **Ciudadanía Distribuida:** Cualquier ciudadano puede "adoptar" una promesa para monitorearla y recibir actualizaciones.
6. **Alertas Tempranas:** Notificaciones proactivas cuando una promesa se estanca (ej. > 180 días sin movimiento).

## 💻 Stack Tecnológico (Arquitectura)
La plataforma está diseñada para ser escalable, de bajo costo operativo (*free-tier friendly*) y de alto impacto visual.

*   **Frontend (Plataforma Web):**
    *   `Vite + React`: Renderizado ultrarrápido y desarrollo moderno.
    *   `Tailwind CSS`: Diseño premium, responsivo y enfocado en la experiencia de usuario (UX).
*   **Backend (API & Motor de Alertas):**
    *   `Python (FastAPI)`: Endpoints de alto rendimiento para interactuar con la base de datos y la IA.
*   **Ingesta de Datos (Scraping):**
    *   `Scrapy / BeautifulSoup`: Bots ligeros de recolección de datos públicos (El Peruano, Congreso).
*   **Inteligencia Artificial:**
    *   `LLM (OpenAI / Gemini) + LangChain`: Evaluación semántica de leyes para emitir alertas.
*   **Base de Datos y Autenticación:**
    *   `PostgreSQL (Supabase)`: Almacenamiento relacional/vectorial y autenticación ciudadana sin contraseñas (*Magic Links*).

## 🛠️ Cómo Funciona (Flujo de Datos)
1.  **Extracción:** A las 00:00 hrs, nuestros scripts extraen las nuevas publicaciones de El Peruano y proyectos del Congreso.
2.  **Evaluación:** La IA recibe el texto estructurado y busca correspondencia con el catálogo de 93 promesas originales.
3.  **Veredicto:** Si la IA determina que una ley desbloquea o contradice una promesa, genera un JSON con el veredicto.
4.  **Actualización y Alerta:** La plataforma actualiza el semáforo (Verde, Amarillo, Rojo) y notifica por email a los ciudadanos que "adoptaron" dicha promesa.

## 🤝 Cómo Contribuir
ObservaPe no puede construirse desde una sola organización. Necesitamos:
*   **Desarrolladores (Frontend/Backend):** Para implementar los módulos React o mejorar el scraping en Python.
*   **Ingenieros de Datos / IA:** Para afinar los *prompts* y reducir alucinaciones en la evaluación de leyes.
*   **Periodistas de Datos / Analistas:** Para validar el catálogo de promesas inicial.

### Instrucciones para Desarrollo Local
*(Próximamente: Instrucciones detalladas de despliegue con Docker y Vite).*

1. Clona el repositorio: `git clone https://github.com/tu-org/GobernanzaP2P.git`
2. Instala dependencias del frontend: `cd frontend && npm install`
3. Instala dependencias del backend: `cd backend && pip install -r requirements.txt`

## ⚖️ Licencia
Este proyecto está bajo la Licencia **MIT**. Todo el código es público, auditable y puede ser reutilizado libremente. 
Consulta el archivo [LICENSE](LICENSE) para más detalles.

---
<div align="center">
  <i>Si el gobierno cumple, ObservaPe lo documenta y fortalece su legitimidad. <br>Si no cumple, la ciudadanía tiene los datos para exigirlo.</i>
</div>