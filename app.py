import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

# Configuración de la página
st.set_page_config(
    page_title="JEP Analytics Dashboard",
    page_icon="☕",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilos CSS personalizados
st.markdown("""
<style>
.main-header {
    background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
    padding: 1rem;
    border-radius: 10px;
    color: white;
    margin-bottom: 2rem;
}
.metric-card {
    background: white;
    padding: 1rem;
    border-radius: 8px;
    border-left: 5px solid #667eea;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}
.stMetric {
    background: white;
    padding: 1rem;
    border-radius: 8px;
    border: 1px solid #e0e0e0;
}
</style>
""", unsafe_allow_html=True)

@st.cache_data
def load_data():
    """Carga y procesa los datos de JEPs"""
    try:
        df = pd.read_csv('datos_jeps.csv', sep='\t', encoding='utf-
