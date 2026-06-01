import streamlit as st
import pandas as pd
import plotly.express as px
import os
import numpy as np
import plotly.graph_objects as go

# 1. Configuración de la página
st.set_page_config(
    page_title="Tablero de Datos Interactivo",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Nombre del archivo local (debe estar en la misma carpeta del script)
ARCHIVO_EXCEL = "World Energy Balances Highlights 2025.xlsx"

# 2. Función para cargar datos directamente desde el archivo local
@st.cache_data
def cargar_datos_locales(ruta_archivo):
    if not os.path.exists(ruta_archivo):
        st.error(f"❌ No se encontró el archivo '{ruta_archivo}' en el directorio actual.")
        return None
    
    try:
        # Intentamos leer la pestaña 'Nuestra Selección'
        df = pd.read_excel(ruta_archivo, sheet_name='Nuestra Selección')
    except ValueError:
        try:
            # Intento alternativo sin acento
            df = pd.read_excel(ruta_archivo, sheet_name='Nuestra seleccion')
        except ValueError:
            st.error("❌ No se encontró la pestaña 'Nuestra Selección' en el archivo Excel.")
            return None
    return df

@st.cache_data
def cargar_datos():
    # Usamos os.path para asegurar que encuentre el archivo en la misma carpeta que app.py
    ruta_archivo = os.path.join(os.path.dirname(__file__), 'datos_energia.csv')
    
    if os.path.exists(ruta_archivo):
        return pd.read_csv(ruta_archivo)
    elif os.path.exists('datos_energia.csv'): # Alternativa por si ejecutas directamente desde la consola
        return pd.read_csv('datos_energia.csv')
    else:
        return None

# Carga automática al iniciar la app
df_original = cargar_datos_locales(ARCHIVO_EXCEL)
datos_energia = cargar_datos()

# 4. Cuerpo Principal de la Aplicación
st.title("📊 TPI - Análisis del Panorama Energético Mundial")
st.markdown("---")

# Estructura de pestañas (Definida de manera global para que todo el script tenga acceso)
tabs = st.tabs(["📌 Introducción", "📈 Análisis Exploratorio", "📋 Conclusión"])

# --- PESTAÑA 1: INTRODUCCIÓN ---
with tabs[0]:
    st.subheader("Contexto del Proyecto")
    st.write("""
    Este dataset reúne información sobre la producción, consumo y transformación 
    de energía en distintos países, con datos desde **1971 hasta 2024**,
    organizados por tipo de fuente energética.\n
    Nos basamos en el reporte "World Energy Balances Highlights 2025" de la **Agencia Internacional de Energía (IEA)**.
    """)

     # Tarjetas de métricas clave (KPIs) basándose en los filtros aplicados arriba
    col1, col2, col3 = st.columns(3)
    col1.metric(label="Total de Filas", value=6832)
    col2.metric(label="Total de Columnas", value=60)
    col3.metric(label="Años Evaluados", value=54)

    st.markdown("---")
    
    # Si el archivo Excel se leyó correctamente, renderizamos los filtros y la tabla AQUÍ adentro
    if df_original is not None:
        st.markdown("### ⚙️ Filtros de Control de Datos")
        
        # Mapeo dinámico de columnas por si difieren las mayúsculas/acentos
        col_categoria = 'Categoría' if 'Categoría' in df_original.columns else df_original.columns[1]
        col_año = 'Año' if 'Año' in df_original.columns else df_original.columns[0]
        col_valor = 'Valor' if 'Valor' in df_original.columns else df_original.columns[2]
        
        # Identificar la columna de País de forma dinámica
        if 'Pais' in df_original.columns:
            col_pais = 'Pais'
        elif 'País' in df_original.columns:
            col_pais = 'País'
        elif 'Country' in df_original.columns:
            col_pais = 'Country'
        else:
            col_pais = df_original.columns[3]

        # Identificar la columna de Flujo de forma dinámica
        if 'Flujo' in df_original.columns:
            col_flujo = 'Flujo'
        elif 'flujo' in df_original.columns:
            col_flujo = 'flujo'
        elif 'Flow' in df_original.columns:
            col_flujo = 'Flow'
        else:
            col_flujo = next((c for c in df_original.columns if 'flujo' in c.lower() or 'flow' in c.lower()), df_original.columns[4])

        # Creamos los contenedores de filtros en columnas para que se vea ordenado en el cuerpo principal
        f_col1, f_col2, f_col3 = st.columns(3)

        with f_col1:
            paises_disponibles = sorted(df_original[col_pais].dropna().unique())
            pais_seleccionado = st.multiselect(
                "Selecciona los países:",
                options=paises_disponibles,
                default=paises_disponibles
            )

        with f_col2:
            categorias_disponibles = df_original[col_categoria].unique()
            categoria_seleccionada = st.multiselect(
                "Selecciona las secciones/categorías:",
                options=categorias_disponibles,
                default=categorias_disponibles
            )

        with f_col3:
            flujos_disponibles = df_original[col_flujo].dropna().unique()
            flujo_seleccionado = st.multiselect(
                "Selecciona los flujos de energía:",
                options=flujos_disponibles,
                default=flujos_disponibles
            )

        # --- Filtrar el dataframe según las TRES selecciones ---
        df_filtrado = df_original[
            (df_original[col_categoria].isin(categoria_seleccionada)) & 
            (df_original[col_pais].isin(pais_seleccionado)) &
            (df_original[col_flujo].isin(flujo_seleccionado))
        ]
        
        

        st.subheader("Explorador de Datos")
        st.write("Tabla Interactiva con los Datos del Dataset Original.")
        st.dataframe(df_filtrado, use_container_width=True)
    else:
        st.warning("⚠️ Los filtros y el explorador no están disponibles porque el archivo Excel no se cargó correctamente.")

# --- PESTAÑA 2: ANÁLISIS EXPLORATORIO ---
with tabs[1]:
    st.subheader("Problemáticas Principales:")
    st.subheader("¿Cómo ha evolucionado la producción de energía nuclear a nivel mundial a lo largo del tiempo?:")
    
    if datos_energia is not None and not datos_energia.empty:
        df_world_nuclear = datos_energia[
            (datos_energia['Pais'].str.contains('Mundo', case=False, na=False)) &
            (datos_energia['Producto'] == 'Nuclear') &
            (datos_energia['Flujo'] == 'Produccion de energia (GWh)')
        ]

        years_to_plot = [col for col in datos_energia.columns if str(col).isdigit() and str(col) != '2024']

        if not df_world_nuclear.empty:
            nuclear_world_vals = df_world_nuclear[years_to_plot].apply(pd.to_numeric, errors='coerce').fillna(0).sum()

            st.markdown("### Gráfico Interactivo")
            df_grafico = pd.DataFrame({
                'Año': years_to_plot,
                'Producción (GWh)': nuclear_world_vals.values
            }).set_index('Año')
            
            st.scatter_chart(df_grafico)

        st.write("---")
        st.subheader("¿Qué países presentan los mayores niveles de producción de energía?:")

        df_production = datos_energia[datos_energia['Flujo'] == 'Produccion de energia (GWh)'].copy()
        year_columns = [col for col in df_production.columns if str(col).isdigit()]

        for col in year_columns:
            df_production[col] = pd.to_numeric(df_production[col], errors='coerce').fillna(0)

        production_by_country = df_production.groupby('Pais')[year_columns].sum().sum(axis=1)

        df_highest_production = production_by_country.sort_values(ascending=False).reset_index()
        df_highest_production.columns = ['Pais', 'Produccion Total (GWh)']

        aggregated_entities = [
            'Mundo', 'IEA and Accession/Association countries', 'OCDE Total', 
            'IEA Total', 'No-OCDE Total', 'No-OCDE Asia (incluye China)', 
            'No-OCDE Europa y Eurasia', 'No-OCDE Americas', 'Medio Oriente'
        ]

        df_highest_production_filtered = df_highest_production[~df_highest_production['Pais'].isin(aggregated_entities)]

        st.write("Países con los mayores niveles de producción de energía (Producción Total en GWh)")
        st.dataframe(df_highest_production_filtered.head(10), use_container_width=True)

        fig_production = px.bar(
            df_highest_production_filtered.head(10),
            x='Pais',
            y='Produccion Total (GWh)',
            color='Pais',
            title='Top 10 Países con los Mayores Niveles de Producción de Energía (GWh)',
            labels={'Pais': 'País', 'Produccion Total (GWh)': 'Producción Total (GWh)'},
            color_discrete_sequence=px.colors.sequential.Viridis
        )

        fig_production.update_layout(
            showlegend=False,
            xaxis_tickangle=-45,
            margin=dict(l=20, r=20, t=50, b=100)
        )

        st.plotly_chart(fig_production, use_container_width=True)
        
    elif datos_energia is not None and datos_energia.empty:
        st.warning("El archivo 'datos_energia.csv' está vacío.")
    else:
        st.error("No se encontró el archivo 'datos_energia.csv'. Asegúrate de que esté en la misma carpeta que este script.")

# --- PESTAÑA 3: CONCLUSIÓN ---
with tabs[2]:
    if datos_energia is not None and not datos_energia.empty:
        years_analysis = [col for col in datos_energia.columns if str(col).isdigit() and str(col) != '2024']

        fossil_global = datos_energia[(datos_energia['Pais'] == 'Mundo') & (datos_energia['Producto'] == 'Combustibles fosiles') & (datos_energia['Flujo'] == 'Produccion de energia (GWh)')][years_analysis].apply(pd.to_numeric).values.flatten()
        renov_global = datos_energia[(datos_energia['Pais'] == 'Mundo') & (datos_energia['Producto'] == 'Recursos renovables') & (datos_energia['Flujo'] == 'Produccion de energia (GWh)')][years_analysis].apply(pd.to_numeric).values.flatten()
        nuclear_global = datos_energia[(datos_energia['Pais'] == 'Mundo') & (datos_energia['Producto'] == 'Nuclear') & (datos_energia['Flujo'] == 'Produccion de energia (GWh)')][years_analysis].apply(pd.to_numeric).values.flatten()

        sostenible_global = renov_global + nuclear_global

        st.subheader("Proyección Metas Acuerdo de París")

        years_num = np.array([float(y) for y in years_analysis])
        
        coef_sos = np.polyfit(years_num, sostenible_global, 1)
        coef_fos = np.polyfit(years_num, fossil_global, 1)

        future_years = np.arange(int(min(years_num)), 2046)
        trend_sos = np.polyval(coef_sos, future_years)
        trend_fos = np.polyval(coef_fos, future_years)

        target_years = [2030, 2045]
        p_sos = np.polyval(coef_sos, target_years)
        p_fos = np.polyval(coef_fos, target_years)

        fig = go.Figure()

        fig.add_trace(go.Scatter(x=years_num, y=fossil_global, mode='lines', name='Histórico Fósil', line=dict(color='gray', width=2), opacity=0.5))
        fig.add_trace(go.Scatter(x=years_num, y=sostenible_global, mode='lines', name='Histórico Sostenible', line=dict(color='green', width=2), opacity=0.5))
        fig.add_trace(go.Scatter(x=future_years, y=trend_fos, mode='lines', name='Tendencia Fósil', line=dict(color='black', dash='dash')))
        fig.add_trace(go.Scatter(x=future_years, y=trend_sos, mode='lines', name='Tendencia Sostenible', line=dict(color='green', dash='dash')))

        fig.add_trace(go.Scatter(x=target_years, y=p_sos, mode='markers+text', name='Hitos Sostenibles', text=[f"{v:,.0f} GWh" for v in p_sos], textposition="top center", marker=dict(color='darkgreen', size=10)))
        fig.add_trace(go.Scatter(x=target_years, y=p_fos, mode='markers+text', name='Hitos Fósiles', text=[f"{v:,.0f} GWh" for v in p_fos], textposition="bottom center", marker=dict(color='black', size=10)))

        fig.update_layout(
            title='Trayectoria Energética Global hacia 2030 y 2045 (Interactivo)',
            xaxis_title='Año',
            yaxis_title='Producción (GWh)',
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            margin=dict(l=0, r=0, t=80, b=0),
            hovermode="x unified"
        )

        fig.add_vrect(x0=2030, x1=2045, fillcolor="yellow", opacity=0.1, layer="below", line_width=0, annotation_text="Acuerdo de París", annotation_position="top left")

        st.plotly_chart(fig, use_container_width=True)

        st.info("💡 **Análisis de la Brecha:**")
        c1, c2 = st.columns(2)
        for i, year in enumerate(target_years):
            diff = p_fos[i] - p_sos[i]
            with c1 if i == 0 else c2:
                st.metric(f"Brecha Fósil vs Sostenible ({year})", f"{diff:,.0f} GWh", delta_color="inverse")

    st.markdown("---")
    st.subheader("Reflexiones finales")
    st.write("Este trabajo nos ayudó a comprender:")    

    st.markdown("""
    > ➔ **Panorama energético mundial:** Entender cómo se distribuye el consumo y la producción global.
    >
    > ➔ **Cambios importantes en el tiempo:** Analizar las transiciones históricas y cómo evolucionaron las matrices energéticas.
    >
    > ➔ **Analizar información real:** Trabajar directamente con datos oficiales y limpios para evitar sesgos.
    >
    > ➔ **Futuro de la energía:** Proyectar las trends del Acuerdo de París y medir la brecha real que nos falta cubrir.
    """)
