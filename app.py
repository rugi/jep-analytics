import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

# Configuración de la página
st.set_page_config(
    page_title="JEP Analytics Dashboard by RuGI",
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
    """Carga y procesa los datos de JEPs de forma tolerante a columnas faltantes"""
    try:
        # Cargar el CSV con separador coma
        df = pd.read_csv('datos_jeps.csv', sep=';', encoding='utf-8', low_memory=False)

        # Normalizar nombres de columnas
        df.columns = df.columns.str.strip().str.replace(r'\s+', '_', regex=True)

        # ---- Manejo seguro de columnas ----
        # Fechas
        if 'Created' in df.columns:
            df['Created'] = pd.to_datetime(df['Created'], errors='coerce')
        else:
            df['Created'] = pd.NaT

        if 'Updated' in df.columns:
            df['Updated'] = pd.to_datetime(df['Updated'], errors='coerce')
        else:
            df['Updated'] = pd.NaT

        # Año de creación
        df['Year_Created'] = df['Created'].dt.year

        # Duración
        df['Duration_Days'] = (df['Updated'] - df['Created']).dt.days

        # Status
        if 'Status' not in df.columns:
            df['Status'] = 'Unknown'
        else:
            df['Status'] = df['Status'].replace('REVISAR', 'Unknown').fillna('Unknown')

        # Owner
        if 'Owner' not in df.columns:
            df['Owner'] = 'Unknown'
        else:
            df['Owner'] = df['Owner'].replace('REVISAR', 'Unknown').fillna('Unknown')

        # Release
        if 'Release' not in df.columns:
            df['Release'] = 'TBD'
        else:
            df['Release'] = df['Release'].replace('REVISAR', 'TBD').fillna('TBD')

        return df

    except FileNotFoundError:
        st.error("❌ No se encontró el archivo 'datos_jeps.csv'. Asegúrate de tenerlo en el mismo directorio.")
        return None
    except Exception as e:
        st.error(f"❌ Error al cargar los datos: {str(e)}")
        return None

def create_status_chart(df):
    status_counts = df['Status'].value_counts()
    fig = px.pie(
        values=status_counts.values, 
        names=status_counts.index,
        title="🔄 Distribución de Estados de JEPs",
        color_discrete_sequence=px.colors.qualitative.Set3
    )
    fig.update_traces(textposition='inside', textinfo='percent+label')
    return fig

def create_authors_chart(df):
    author_counts = df['Owner'].value_counts().head(10)
    fig = px.bar(
        x=author_counts.values,
        y=author_counts.index,
        orientation='h',
        title="👨‍💻 Top 10 Autores Más Prolíficos",
        color=author_counts.values,
        color_continuous_scale="viridis"
    )
    fig.update_layout(yaxis={'categoryorder': 'total ascending'})
    return fig

def create_timeline_chart(df):
    yearly_counts = df.groupby('Year_Created').size().reset_index(name='Count')
    fig = px.line(
        yearly_counts, 
        x='Year_Created', 
        y='Count',
        title="📈 JEPs Creados por Año",
        markers=True,
        line_shape='spline'
    )
    return fig

def create_release_chart(df):
    df_copy = df.copy()
    df_copy['Release'] = df_copy['Release'].astype(str)
    valid_releases = df_copy[df_copy['Release'].str.match(r'^\d+$', na=False)]
    if not valid_releases.empty:
        release_counts = valid_releases['Release'].value_counts().sort_index()
        fig = px.bar(
            x=release_counts.index,
            y=release_counts.values,
            title="🚀 JEPs por Release de Java",
            color=release_counts.values,
            color_continuous_scale="plasma"
        )
        return fig
    return None

def create_duration_analysis(df):
    if 'Duration_Days' not in df.columns:
        return None

    valid_durations = pd.to_numeric(df['Duration_Days'], errors='coerce')
    valid_durations = valid_durations[valid_durations > 0].dropna()

    if not valid_durations.empty:
        fig = px.histogram(
            valid_durations,
            nbins=30,  # `nbins` en vez de `bins` (más compatible con Plotly)
            title="⏱️ Distribución de Duración de Desarrollo (días)",
            color_discrete_sequence=['#667eea']
        )
        return fig
    return None


def main():
    st.markdown("""
    <div class="main-header">
        <h1>☕ JEP Analytics Dashboard</h1>
        <p>Análisis completo de Java Enhancement Proposals</p>
    </div>
    """, unsafe_allow_html=True)

    df = load_data()
    if df is None:
        st.info("📋 Coloca 'datos_jeps.csv' en el mismo directorio.")
        return

    # Sidebar filtros
    st.sidebar.header("🔍 Filtros")
    estados = ['Todos'] + list(df['Status'].unique())
    estado = st.sidebar.selectbox("Estado", estados)
    años = ['Todos'] + sorted([year for year in df['Year_Created'].unique() if pd.notna(year)])
    año = st.sidebar.selectbox("Año de Creación", años)
    autores = ['Todos'] + list(df['Owner'].unique())
    autor = st.sidebar.selectbox("Autor", autores)

    df_filtrado = df.copy()
    if estado != 'Todos':
        df_filtrado = df_filtrado[df_filtrado['Status'] == estado]
    if año != 'Todos':
        df_filtrado = df_filtrado[df_filtrado['Year_Created'] == año]
    if autor != 'Todos':
        df_filtrado = df_filtrado[df_filtrado['Owner'] == autor]

    # Métricas
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("📊 Total JEPs", len(df_filtrado))
    with col2:
        st.metric("👥 Autores Únicos", df_filtrado['Owner'].nunique())
    with col3:
        df_copy = df_filtrado.copy()
        df_copy['Release'] = df_copy['Release'].astype(str)
        releases_unicos = df_copy[df_copy['Release'].str.match(r'^\d+$', na=False)]['Release'].nunique()
        st.metric("🚀 Releases Afectados", releases_unicos)
    with col4:
        duracion = df_filtrado['Duration_Days'].mean()
        st.metric("⏱️ Duración Promedio", f"{duracion:.0f} días" if pd.notna(duracion) else "N/A")

    # Gráficos
    st.markdown("## 📈 Análisis Visual")
    tab1, tab2, tab3, tab4 = st.tabs(["🔄 Estados", "👨‍💻 Autores", "📅 Timeline", "🚀 Releases"])
    with tab1:
        st.plotly_chart(create_status_chart(df_filtrado), use_container_width=True)
    with tab2:
        st.plotly_chart(create_authors_chart(df_filtrado), use_container_width=True)
    with tab3:
        st.plotly_chart(create_timeline_chart(df_filtrado), use_container_width=True)
    with tab4:
        fig = create_release_chart(df_filtrado)
        st.plotly_chart(fig, use_container_width=True) if fig else st.info("No hay releases válidos.")

    # Análisis detallado
    st.markdown("## 🔍 Análisis Detallado")
    col1, col2 = st.columns(2)
    with col1:
        fig = create_duration_analysis(df_filtrado)
        st.plotly_chart(fig, use_container_width=True) if fig else st.info("No hay duraciones válidas.")
    with col2:
        st.subheader("📊 Estadísticas Rápidas")
        top_authors = df_filtrado['Owner'].value_counts().head(5)
        for author, count in top_authors.items():
            st.write(f"• {author}: {count} JEPs")
        top_status = df_filtrado['Status'].value_counts().head(3)
        for status, count in top_status.items():
            st.write(f"• {status}: {count} JEPs")

    # Tabla
    st.markdown("## 📋 Datos Completos")
    available_cols = df_filtrado.columns.tolist()
    defaults = [c for c in ['Number', 'Title', 'Owner', 'Status', 'Release', 'Created'] if c in available_cols]
    cols = st.multiselect("Selecciona columnas:", options=available_cols, default=defaults or available_cols[:6])
    if cols:
        st.dataframe(df_filtrado[cols], use_container_width=True, height=400)

    # Descargar CSV
    csv = df_filtrado.to_csv(index=False)
    st.download_button(
        label="📥 Descargar datos filtrados como CSV",
        data=csv,
        file_name=f'jeps_filtrados_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv',
        mime='text/csv'
    )

if __name__ == "__main__":
    main()
