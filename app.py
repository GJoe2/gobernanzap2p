"""Unified Streamlit entry point for all GobernanzaP2P applications."""

from pathlib import Path
import runpy

import streamlit as st


ROOT_DIR = Path(__file__).resolve().parent

st.set_page_config(
    page_title="GobernanzaP2P",
    page_icon="🇵🇪",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.title("🇵🇪 GobernanzaP2P")
st.caption("Plataforma unificada: escucha ciudadana, propuestas y analítica P2P")

st.info(
    "Selecciona una pestaña para cambiar de módulo. Los tres módulos comparten "
    "los datos locales del repositorio."
)

intake_tab, proposals_tab, dashboard_tab = st.tabs(
    [
        "🇵🇪 Escucha ciudadana y Perú",
        "📝 Propuestas cívicas",
        "📊 Dashboard P2P",
    ]
)


def run_module(relative_path: str) -> None:
    """Run an existing Streamlit module inside this application.

    The original modules call st.set_page_config() because they were previously
    deployed separately. The unified launcher owns page configuration, so those
    nested calls are temporarily ignored.
    """
    module_path = ROOT_DIR / relative_path
    if not module_path.exists():
        st.error(f"No se encontró el módulo: `{relative_path}`")
        return

    original_set_page_config = st.set_page_config
    st.set_page_config = lambda **kwargs: None
    try:
        runpy.run_path(str(module_path), run_name="__main__")
    except FileNotFoundError as exc:
        st.error(f"Falta un archivo requerido por `{relative_path}`: {exc}")
    except ImportError as exc:
        st.error(f"Falta una dependencia para `{relative_path}`: {exc}")
    except Exception as exc:
        st.exception(exc)
    finally:
        st.set_page_config = original_set_page_config


with intake_tab:
    run_module("peru_intake/app_peru_intake.py")

with proposals_tab:
    run_module("intake_surveys/app_intake.py")

with dashboard_tab:
    run_module("analytics_dashboard/app_dashboard.py")
