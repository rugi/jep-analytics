import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import numpy as np

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
        # Intentar cargar el CSV
        df = pd.read_csv('datos_jeps.csv', sep='\t', encoding='utf-8')
        
        # Limpiar nombres de columnas (espacios, caracteres especiales)
        df.columns = df.columns.str.strip().str.replace('\s+', '_', regex=True)
        
        # Limpiar datos y procesar fechas de forma flexible
        # Esto maneja formatos como 2025/3/31, 2025/03/31, etc.
        df['Created'] = pd.to_datetime(df['Created'], errors='coerce')
        df['Updated'] = pd.to_datetime(df['Updated'], errors='coerce')
        
        # Crear columnas derivadas
        df['Year_Created'] = df['Created'].dt.year
        df['Duration_Days'] = (df['Updated'] - df['Created']).dt.days
        
        # Limpiar valores nulos y "REVISAR"
        df['Status'] = df['Status'].replace('REVISAR', 'Unknown')
        df['Owner'] = df['Owner'].replace('REVISAR', 'Unknown')
        df['Release'] = df['Release'].replace('REVISAR', 'TBD')
        
        return df
    except FileNotFoundError:
        st.error("❌ No se encontró el archivo 'datos_jeps.csv'. Asegúrate de tenerlo en el mismo directorio.")
        return None
    except Exception as e:
        st.error(f"❌ Error al cargar los datos: {str(e)}")
        return None

def create_status_chart(df):
    """Gráfico de estado de JEPs"""
    status_counts = df['Status'].value_counts()
    
    fig = px.pie(
        values=status_counts.values, 
        names=status_counts.index,
        title="🔄 Distribución de Estados de JEPs",
        color_discrete_sequence=px.colors.qualitative.Set3
    )
    fig.update_traces(textposition='inside', textinfo='percent+label')
    fig.update_layout(height=400)
    return fig

def create_authors_chart(df):
    """Gráfico de autores más prolíficos"""
    author_counts = df['Owner'].value_counts().head(10)
    
    fig = px.bar(
        x=author_counts.values,
        y=author_counts.index,
        orientation='h',
        title="👨‍💻 Top 10 Autores Más Prolíficos",
        color=author_counts.values,
        color_continuous_scale="viridis"
    )
    fig.update_layout(
        yaxis={'categoryorder': 'total ascending'},
        height=500,
        showlegend=False
    )
    return fig

def create_timeline_chart(df):
    """Gráfico de timeline de JEPs por año"""
    yearly_counts = df.groupby('Year_Created').size().reset_index(name='Count')
    
    fig = px.line(
        yearly_counts, 
        x='Year_Created', 
        y='Count',
        title="📈 JEPs Creados por Año",
        markers=True,
        line_shape='spline'
    )
    fig.update_traces(line_color='#667eea', line_width=3, marker_size=8)
    fig.update_layout(height=400)
    return fig

def create_release_chart(df):
    """Gráfico de JEPs por release"""
    # Convertir Release a string y filtrar releases válidos (números)
    df_copy = df.copy()
    df_copy['Release'] = df_copy['Release'].astype(str)
    valid_releases = df_copy[df_copy['Release'].str.match(r'^\d+$', na=False)]

def create_duration_analysis(df):
    """Análisis de duración de desarrollo"""
    valid_durations = df[df['Duration_Days'] > 0]['Duration_Days']
    
    if not valid_durations.empty:
        fig = px.histogram(
            valid_durations,
            bins=30,
            title="⏱️ Distribución de Duración de Desarrollo (días)",
            color_discrete_sequence=['#667eea']
        )
        fig.update_layout(height=400)
        return fig
    return None

def main():
    # Header principal
    st.markdown("""
    <div class="main-header">
        <h1>☕ JEP Analytics Dashboard</h1>
        <p>Análisis completo de Java Enhancement Proposals</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Cargar datos
    df = load_data()
    
    if df is None:
        st.info("📋 Instrucciones: Coloca el archivo 'datos_jeps.csv' en el mismo directorio que esta aplicación.")
        st.code("""
# Estructura esperada:
app.py
datos_jeps.csv  # ← Tu archivo generado por el parser
requirements.txt
        """)
        return
    
    # Debug: Mostrar nombres de columnas (puedes comentar esto después)
    st.sidebar.write("🔍 Debug - Columnas detectadas:")
    st.sidebar.write(list(df.columns))
    
    # Sidebar con filtros
    st.sidebar.header("🔍 Filtros")
    
    # Filtro por estado
    estados = ['Todos'] + list(df['Status'].unique())
    estado_seleccionado = st.sidebar.selectbox("Estado", estados)
    
    # Filtro por año
    años = ['Todos'] + sorted([year for year in df['Year_Created'].unique() if pd.notna(year)])
    año_seleccionado = st.sidebar.selectbox("Año de Creación", años)
    
    # Filtro por autor
    autores = ['Todos'] + list(df['Owner'].unique())
    autor_seleccionado = st.sidebar.selectbox("Autor", autores)
    
    # Aplicar filtros
    df_filtrado = df.copy()
    
    if estado_seleccionado != 'Todos':
        df_filtrado = df_filtrado[df_filtrado['Status'] == estado_seleccionado]
    
    if año_seleccionado != 'Todos':
        df_filtrado = df_filtrado[df_filtrado['Year_Created'] == año_seleccionado]
        
    if autor_seleccionado != 'Todos':
        df_filtrado = df_filtrado[df_filtrado['Owner'] == autor_seleccionado]
    
    # Métricas principales
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="📊 Total JEPs",
            value=len(df_filtrado),
            delta=f"{len(df_filtrado) - len(df)}" if len(df_filtrado) != len(df) else None
        )
    
    with col2:
        autores_unicos = df_filtrado['Owner'].nunique()
        st.metric(
            label="👥 Autores Únicos",
            value=autores_unicos
        )
    
    with col3:
        # Convertir Release a string primero y filtrar releases válidos
        df_filtrado_copy = df_filtrado.copy()
        df_filtrado_copy['Release'] = df_filtrado_copy['Release'].astype(str)
        releases_unicos = df_filtrado_copy[df_filtrado_copy['Release'].str.match(r'^\d+$', na=False)]
    
    with col4:
        duracion_promedio = df_filtrado['Duration_Days'].mean()
        if pd.notna(duracion_promedio):
            st.metric(
                label="⏱️ Duración Promedio",
                value=f"{duracion_promedio:.0f} días"
            )
        else:
            st.metric(label="⏱️ Duración Promedio", value="N/A")
    
    # Gráficos
    st.markdown("## 📈 Análisis Visual")
    
    tab1, tab2, tab3, tab4 = st.tabs(["🔄 Estados", "👨‍💻 Autores", "📅 Timeline", "🚀 Releases"])
    
    with tab1:
        if len(df_filtrado) > 0:
            fig_status = create_status_chart(df_filtrado)
            st.plotly_chart(fig_status, use_container_width=True)
        else:
            st.info("No hay datos para mostrar con los filtros seleccionados.")
    
    with tab2:
        if len(df_filtrado) > 0:
            fig_authors = create_authors_chart(df_filtrado)
            st.plotly_chart(fig_authors, use_container_width=True)
        else:
            st.info("No hay datos para mostrar con los filtros seleccionados.")
    
    with tab3:
        if len(df_filtrado) > 0 and 'Year_Created' in df_filtrado.columns:
            fig_timeline = create_timeline_chart(df_filtrado)
            st.plotly_chart(fig_timeline, use_container_width=True)
        else:
            st.info("No hay datos de fechas válidas para mostrar.")
    
    with tab4:
        fig_release = create_release_chart(df_filtrado)
        if fig_release:
            st.plotly_chart(fig_release, use_container_width=True)
        else:
            st.info("No hay datos de releases válidos para mostrar.")
    
    # Análisis adicional
    st.markdown("## 🔍 Análisis Detallado")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("⏱️ Análisis de Duración")
        fig_duration = create_duration_analysis(df_filtrado)
        if fig_duration:
            st.plotly_chart(fig_duration, use_container_width=True)
        else:
            st.info("No hay datos de duración válidos.")
    
    with col2:
        st.subheader("📊 Estadísticas Rápidas")
        
        # Top 5 autores
        top_authors = df_filtrado['Owner'].value_counts().head(5)
        if not top_authors.empty:
            st.write("**Top 5 Autores:**")
            for author, count in top_authors.items():
                st.write(f"• {author}: {count} JEPs")
        
        st.write("")
        
        # Estados más comunes
        top_status = df_filtrado['Status'].value_counts().head(3)
        if not top_status.empty:
            st.write("**Estados más comunes:**")
            for status, count in top_status.items():
                st.write(f"• {status}: {count} JEPs")
    
    # Tabla de datos
    st.markdown("## 📋 Datos Completos")
    
    # Configurar columnas a mostrar
    available_columns = df_filtrado.columns.tolist()
    
    # Debug: Mostrar columnas disponibles
    st.write("🔍 **Columnas disponibles en tu CSV:**", available_columns)
    
    # Seleccionar columnas por defecto que existan en el DataFrame
    suggested_defaults = ['Number', 'Title', 'Owner', 'Status', 'Release', 'Created']
    actual_defaults = [col for col in suggested_defaults if col in available_columns]
    
    # Si no hay columnas sugeridas disponibles, usar las primeras 6
    if not actual_defaults:
        actual_defaults = available_columns[:min(6, len(available_columns))]
    
    # Si aún está vacío, usar solo la primera columna
    if not actual_defaults and available_columns:
        actual_defaults = [available_columns[0]]
    
    columns_to_show = st.multiselect(
        "Selecciona columnas a mostrar:",
        options=available_columns,
        default=actual_defaults
    )
    
    if columns_to_show:
        st.dataframe(
            df_filtrado[columns_to_show],
            use_container_width=True,
            height=400
        )
    
    # Botón de descarga
    csv = df_filtrado.to_csv(index=False)
    st.download_button(
        label="📥 Descargar datos filtrados como CSV",
        data=csv,
        file_name=f'jeps_filtrados_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv',
        mime='text/csv'
    )

if __name__ == "__main__":
    main(), na=False)]['Release'].nunique()
        st.metric(
            label="🚀 Releases Afectados",
            value=releases_unicos
        )
    
    with col4:
        duracion_promedio = df_filtrado['Duration_Days'].mean()
        if pd.notna(duracion_promedio):
            st.metric(
                label="⏱️ Duración Promedio",
                value=f"{duracion_promedio:.0f} días"
            )
        else:
            st.metric(label="⏱️ Duración Promedio", value="N/A")
    
    # Gráficos
    st.markdown("## 📈 Análisis Visual")
    
    tab1, tab2, tab3, tab4 = st.tabs(["🔄 Estados", "👨‍💻 Autores", "📅 Timeline", "🚀 Releases"])
    
    with tab1:
        if len(df_filtrado) > 0:
            fig_status = create_status_chart(df_filtrado)
            st.plotly_chart(fig_status, use_container_width=True)
        else:
            st.info("No hay datos para mostrar con los filtros seleccionados.")
    
    with tab2:
        if len(df_filtrado) > 0:
            fig_authors = create_authors_chart(df_filtrado)
            st.plotly_chart(fig_authors, use_container_width=True)
        else:
            st.info("No hay datos para mostrar con los filtros seleccionados.")
    
    with tab3:
        if len(df_filtrado) > 0 and 'Year_Created' in df_filtrado.columns:
            fig_timeline = create_timeline_chart(df_filtrado)
            st.plotly_chart(fig_timeline, use_container_width=True)
        else:
            st.info("No hay datos de fechas válidas para mostrar.")
    
    with tab4:
        fig_release = create_release_chart(df_filtrado)
        if fig_release:
            st.plotly_chart(fig_release, use_container_width=True)
        else:
            st.info("No hay datos de releases válidos para mostrar.")
    
    # Análisis adicional
    st.markdown("## 🔍 Análisis Detallado")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("⏱️ Análisis de Duración")
        fig_duration = create_duration_analysis(df_filtrado)
        if fig_duration:
            st.plotly_chart(fig_duration, use_container_width=True)
        else:
            st.info("No hay datos de duración válidos.")
    
    with col2:
        st.subheader("📊 Estadísticas Rápidas")
        
        # Top 5 autores
        top_authors = df_filtrado['Owner'].value_counts().head(5)
        if not top_authors.empty:
            st.write("**Top 5 Autores:**")
            for author, count in top_authors.items():
                st.write(f"• {author}: {count} JEPs")
        
        st.write("")
        
        # Estados más comunes
        top_status = df_filtrado['Status'].value_counts().head(3)
        if not top_status.empty:
            st.write("**Estados más comunes:**")
            for status, count in top_status.items():
                st.write(f"• {status}: {count} JEPs")
    
    # Tabla de datos
    st.markdown("## 📋 Datos Completos")
    
    # Configurar columnas a mostrar
    columns_to_show = st.multiselect(
        "Selecciona columnas a mostrar:",
        options=df_filtrado.columns.tolist(),
        default=['Number', 'Title', 'Owner', 'Status', 'Release', 'Created']
    )
    
    if columns_to_show:
        st.dataframe(
            df_filtrado[columns_to_show],
            use_container_width=True,
            height=400
        )
    
    # Botón de descarga
    csv = df_filtrado.to_csv(index=False)
    st.download_button(
        label="📥 Descargar datos filtrados como CSV",
        data=csv,
        file_name=f'jeps_filtrados_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv',
        mime='text/csv'
    )

if __name__ == "__main__":
    main(), na=False)]
    
    if not valid_releases.empty:
        release_counts = valid_releases['Release'].value_counts().sort_index()
        
        fig = px.bar(
            x=release_counts.index,
            y=release_counts.values,
            title="🚀 JEPs por Release de Java",
            color=release_counts.values,
            color_continuous_scale="plasma"
        )
        fig.update_layout(height=400, showlegend=False)
        return fig
    return None

def create_duration_analysis(df):
    """Análisis de duración de desarrollo"""
    valid_durations = df[df['Duration_Days'] > 0]['Duration_Days']
    
    if not valid_durations.empty:
        fig = px.histogram(
            valid_durations,
            bins=30,
            title="⏱️ Distribución de Duración de Desarrollo (días)",
            color_discrete_sequence=['#667eea']
        )
        fig.update_layout(height=400)
        return fig
    return None

def main():
    # Header principal
    st.markdown("""
    <div class="main-header">
        <h1>☕ JEP Analytics Dashboard</h1>
        <p>Análisis completo de Java Enhancement Proposals</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Cargar datos
    df = load_data()
    
    if df is None:
        st.info("📋 Instrucciones: Coloca el archivo 'datos_jeps.csv' en el mismo directorio que esta aplicación.")
        st.code("""
# Estructura esperada:
app.py
datos_jeps.csv  # ← Tu archivo generado por el parser
requirements.txt
        """)
        return
    
    # Sidebar con filtros
    st.sidebar.header("🔍 Filtros")
    
    # Filtro por estado
    estados = ['Todos'] + list(df['Status'].unique())
    estado_seleccionado = st.sidebar.selectbox("Estado", estados)
    
    # Filtro por año
    años = ['Todos'] + sorted([year for year in df['Year_Created'].unique() if pd.notna(year)])
    año_seleccionado = st.sidebar.selectbox("Año de Creación", años)
    
    # Filtro por autor
    autores = ['Todos'] + list(df['Owner'].unique())
    autor_seleccionado = st.sidebar.selectbox("Autor", autores)
    
    # Aplicar filtros
    df_filtrado = df.copy()
    
    if estado_seleccionado != 'Todos':
        df_filtrado = df_filtrado[df_filtrado['Status'] == estado_seleccionado]
    
    if año_seleccionado != 'Todos':
        df_filtrado = df_filtrado[df_filtrado['Year_Created'] == año_seleccionado]
        
    if autor_seleccionado != 'Todos':
        df_filtrado = df_filtrado[df_filtrado['Owner'] == autor_seleccionado]
    
    # Métricas principales
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="📊 Total JEPs",
            value=len(df_filtrado),
            delta=f"{len(df_filtrado) - len(df)}" if len(df_filtrado) != len(df) else None
        )
    
    with col2:
        autores_unicos = df_filtrado['Owner'].nunique()
        st.metric(
            label="👥 Autores Únicos",
            value=autores_unicos
        )
    
    with col3:
        # Convertir Release a string primero y filtrar releases válidos
        df_filtrado_copy = df_filtrado.copy()
        df_filtrado_copy['Release'] = df_filtrado_copy['Release'].astype(str)
        releases_unicos = df_filtrado_copy[df_filtrado_copy['Release'].str.match(r'^\d+$', na=False)]
    
    with col4:
        duracion_promedio = df_filtrado['Duration_Days'].mean()
        if pd.notna(duracion_promedio):
            st.metric(
                label="⏱️ Duración Promedio",
                value=f"{duracion_promedio:.0f} días"
            )
        else:
            st.metric(label="⏱️ Duración Promedio", value="N/A")
    
    # Gráficos
    st.markdown("## 📈 Análisis Visual")
    
    tab1, tab2, tab3, tab4 = st.tabs(["🔄 Estados", "👨‍💻 Autores", "📅 Timeline", "🚀 Releases"])
    
    with tab1:
        if len(df_filtrado) > 0:
            fig_status = create_status_chart(df_filtrado)
            st.plotly_chart(fig_status, use_container_width=True)
        else:
            st.info("No hay datos para mostrar con los filtros seleccionados.")
    
    with tab2:
        if len(df_filtrado) > 0:
            fig_authors = create_authors_chart(df_filtrado)
            st.plotly_chart(fig_authors, use_container_width=True)
        else:
            st.info("No hay datos para mostrar con los filtros seleccionados.")
    
    with tab3:
        if len(df_filtrado) > 0 and 'Year_Created' in df_filtrado.columns:
            fig_timeline = create_timeline_chart(df_filtrado)
            st.plotly_chart(fig_timeline, use_container_width=True)
        else:
            st.info("No hay datos de fechas válidas para mostrar.")
    
    with tab4:
        fig_release = create_release_chart(df_filtrado)
        if fig_release:
            st.plotly_chart(fig_release, use_container_width=True)
        else:
            st.info("No hay datos de releases válidos para mostrar.")
    
    # Análisis adicional
    st.markdown("## 🔍 Análisis Detallado")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("⏱️ Análisis de Duración")
        fig_duration = create_duration_analysis(df_filtrado)
        if fig_duration:
            st.plotly_chart(fig_duration, use_container_width=True)
        else:
            st.info("No hay datos de duración válidos.")
    
    with col2:
        st.subheader("📊 Estadísticas Rápidas")
        
        # Top 5 autores
        top_authors = df_filtrado['Owner'].value_counts().head(5)
        if not top_authors.empty:
            st.write("**Top 5 Autores:**")
            for author, count in top_authors.items():
                st.write(f"• {author}: {count} JEPs")
        
        st.write("")
        
        # Estados más comunes
        top_status = df_filtrado['Status'].value_counts().head(3)
        if not top_status.empty:
            st.write("**Estados más comunes:**")
            for status, count in top_status.items():
                st.write(f"• {status}: {count} JEPs")
    
    # Tabla de datos
    st.markdown("## 📋 Datos Completos")
    
    # Configurar columnas a mostrar
    columns_to_show = st.multiselect(
        "Selecciona columnas a mostrar:",
        options=df_filtrado.columns.tolist(),
        default=['Number', 'Title', 'Owner', 'Status', 'Release', 'Created']
    )
    
    if columns_to_show:
        st.dataframe(
            df_filtrado[columns_to_show],
            use_container_width=True,
            height=400
        )
    
    # Botón de descarga
    csv = df_filtrado.to_csv(index=False)
    st.download_button(
        label="📥 Descargar datos filtrados como CSV",
        data=csv,
        file_name=f'jeps_filtrados_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv',
        mime='text/csv'
    )

if __name__ == "__main__":
    main(), na=False)]['Release'].nunique()
        st.metric(
            label="🚀 Releases Afectados",
            value=releases_unicos
        )
    
    with col4:
        duracion_promedio = df_filtrado['Duration_Days'].mean()
        if pd.notna(duracion_promedio):
            st.metric(
                label="⏱️ Duración Promedio",
                value=f"{duracion_promedio:.0f} días"
            )
        else:
            st.metric(label="⏱️ Duración Promedio", value="N/A")
    
    # Gráficos
    st.markdown("## 📈 Análisis Visual")
    
    tab1, tab2, tab3, tab4 = st.tabs(["🔄 Estados", "👨‍💻 Autores", "📅 Timeline", "🚀 Releases"])
    
    with tab1:
        if len(df_filtrado) > 0:
            fig_status = create_status_chart(df_filtrado)
            st.plotly_chart(fig_status, use_container_width=True)
        else:
            st.info("No hay datos para mostrar con los filtros seleccionados.")
    
    with tab2:
        if len(df_filtrado) > 0:
            fig_authors = create_authors_chart(df_filtrado)
            st.plotly_chart(fig_authors, use_container_width=True)
        else:
            st.info("No hay datos para mostrar con los filtros seleccionados.")
    
    with tab3:
        if len(df_filtrado) > 0 and 'Year_Created' in df_filtrado.columns:
            fig_timeline = create_timeline_chart(df_filtrado)
            st.plotly_chart(fig_timeline, use_container_width=True)
        else:
            st.info("No hay datos de fechas válidas para mostrar.")
    
    with tab4:
        fig_release = create_release_chart(df_filtrado)
        if fig_release:
            st.plotly_chart(fig_release, use_container_width=True)
        else:
            st.info("No hay datos de releases válidos para mostrar.")
    
    # Análisis adicional
    st.markdown("## 🔍 Análisis Detallado")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("⏱️ Análisis de Duración")
        fig_duration = create_duration_analysis(df_filtrado)
        if fig_duration:
            st.plotly_chart(fig_duration, use_container_width=True)
        else:
            st.info("No hay datos de duración válidos.")
    
    with col2:
        st.subheader("📊 Estadísticas Rápidas")
        
        # Top 5 autores
        top_authors = df_filtrado['Owner'].value_counts().head(5)
        if not top_authors.empty:
            st.write("**Top 5 Autores:**")
            for author, count in top_authors.items():
                st.write(f"• {author}: {count} JEPs")
        
        st.write("")
        
        # Estados más comunes
        top_status = df_filtrado['Status'].value_counts().head(3)
        if not top_status.empty:
            st.write("**Estados más comunes:**")
            for status, count in top_status.items():
                st.write(f"• {status}: {count} JEPs")
    
    # Tabla de datos
    st.markdown("## 📋 Datos Completos")
    
    # Configurar columnas a mostrar
    columns_to_show = st.multiselect(
        "Selecciona columnas a mostrar:",
        options=df_filtrado.columns.tolist(),
        default=['Number', 'Title', 'Owner', 'Status', 'Release', 'Created']
    )
    
    if columns_to_show:
        st.dataframe(
            df_filtrado[columns_to_show],
            use_container_width=True,
            height=400
        )
    
    # Botón de descarga
    csv = df_filtrado.to_csv(index=False)
    st.download_button(
        label="📥 Descargar datos filtrados como CSV",
        data=csv,
        file_name=f'jeps_filtrados_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv',
        mime='text/csv'
    )

if __name__ == "__main__":
    main()
