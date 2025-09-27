# Jep-analytics.
🚀 JEP Analytics Dashboard
Dashboard interactivo para analizar Java Enhancement Proposals usando Streamlit.

Creado como complemento para la charla: "3 JEPs que debes de conocer".

✨ Características

📊 Tablas interactivas ordenables, filtrables y paginables

📈 Gráficos dinámicos con Plotly

🔍 Filtros avanzados por estado, año y autor

📱 Responsive design funciona en móvil y desktop

📥 Descarga de datos filtrados

⚡ Análisis en tiempo real

📁 Estructura del Proyecto
```
jep-analytics/
├── app.py              # Dashboard principal
├── requirements.txt    # Dependencias Python
├── datos_jeps.csv     # Tu CSV generado por el parser Java
└── README.md          # Este archivo
```

🛠️ Setup Local

0. Python 3.13 

1. Instalar dependencias

```bash
pip install -r requirements.txt
```

2. Copiar tu CSV
Coloca tu archivo datos_jeps.csv (generado por el parser Java) en el mismo directorio que app.py.

3. Ejecutar localmente

```bash
streamlit run app.py
```

Se abrirá automáticamente en: http://localhost:8501
