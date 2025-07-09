import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D # Para gráficos 3D
import numpy as np # Necesario para operaciones numéricas en los gráficos
from PIL import Image # Para cargar y mostrar imágenes (logos)
from io import BytesIO # Para manejar las imágenes descargadas de la URL
import requests # Para descargar las imágenes de los logos desde Google Drive

# --- Paleta de Colores ---
# Definición de colores en formato RGB (0-1) para Matplotlib
color_primario_1_rgb = (14/255, 69/255, 74/255)   # 0E454A (Oscuro)
color_primario_2_rgb = (31/255, 255/255, 95/255)  # 1FFF5F (Verde vibrante)
color_primario_3_rgb = (255/255, 255/255, 255/255) # FFFFFF (Blanco)

# Colores del logo de Sustrend para complementar
color_sustrend_1_rgb = (0/255, 155/255, 211/255)   # 009BD3 (Azul claro)
color_sustrend_2_rgb = (0/255, 140/255, 207/255)   # 008CCF (Azul medio)
color_sustrend_3_rgb = (0/255, 54/255, 110/255)    # 00366E (Azul oscuro)

# Selección de colores para los gráficos (ajusta a tu gusto)
# Usaré una combinación de los colores primarios y Sustrend para contraste
colors_for_charts = [color_primario_1_rgb, color_primario_2_rgb, color_sustrend_1_rgb, color_sustrend_3_rgb]


# --- Configuración de la página de Streamlit ---
st.set_page_config(layout="wide")

st.title('✨ Visualizador de Impactos - Subproyecto P1.1')
st.subheader('Reducción del fenómeno de “sugaring” en pasas mediante tratamiento por microondas')
st.markdown("""
    Ajusta los parámetros para explorar cómo las proyecciones de impacto ambiental y económico del proyecto
    varían con diferentes escenarios de volumen procesado, precio de exportación y porcentaje de rechazo evitado.
""")

# --- 1. Datos del Proyecto (Línea Base y Proyecciones) ---

# Datos de la ficha técnica
data = {
    "indicador": [
        "GEI evitados por devoluciones internacionales (tCO₂e/año)",
        "Reducción del desperdicio de alimentos (ton/año)",
        "Pérdidas económicas evitadas por lotes rechazados (USD/año)",
        "Ahorros energéticos indirectos (% reducción en consumo energético postcosecha)",
        "Nuevos empleos indirectos (técnicos por planta)"
    ],
    "unidad": ["tCO₂e/año", "ton/año", "USD/año", "%", "técnicos"],
    "rango_perdida_sugaring_min": [None, 5, None, None, None],
    "rango_perdida_sugaring_max": [None, 10, None, None, None],
    "volumen_produccion_ejemplo_ton_año": [None, 1000, 1000, None, None],
    "precio_pasa_ton_usd": [None, None, 2800, None, None],
    "gei_contenedor_retornado_tco2e": [2.4, None, None, None, None],
    "porcentaje_rechazo_evitado_estimado": [10, None, None, None, None],
    "factor_empleo_tecnico_min": [None, None, None, None, 1],
    "factor_empleo_tecnico_max": [None, None, None, None, 3],
    "plantas_procesadoras_ejemplo": [None, None, None, None, 5],
    "personas_a_capacitar_por_plantas": [None, None, None, None, 20]
}

df_diagnostico = pd.DataFrame(data)

# --- 2. Widgets Interactivos para Parámetros (Streamlit) ---
st.sidebar.header('Parámetros de Simulación')

porcentaje_rechazo_evitado = st.sidebar.slider(
    'Porcentaje de Rechazo Evitado (% del volumen exportado):',
    min_value=0.0,
    max_value=20.0,
    value=10.0,
    step=0.5,
    help="Porcentaje del volumen total exportado que se logra salvar del 'sugaring'."
)

volumen_anual_procesado = st.sidebar.slider(
    'Volumen Anual Procesado (ton):',
    min_value=100,
    max_value=5000,
    value=1000,
    step=50,
    help="Volumen total de pasas procesadas anualmente por la industria."
)

precio_pasa = st.sidebar.slider(
    'Precio de Exportación de Pasa (USD/ton):',
    min_value=1000,
    max_value=5000,
    value=2800,
    step=100,
    help="Precio promedio de exportación de la tonelada de pasa."
)

# --- 3. Cálculos de Indicadores ---
# NOTA: Usamos .iloc[-1] para asegurar que tomamos el último valor si hubiera más de uno,
# aunque en este DataFrame solo hay una fila por indicador. Esto hace el acceso más robusto.
gei_evitado = (porcentaje_rechazo_evitado / 100) * (volumen_anual_procesado / 20) * df_diagnostico.loc[0, 'gei_contenedor_retornado_tco2e']

# El rango de desperdicio se convierte en una estimación puntual para la proyección
# Se usa el porcentaje de rechazo evitado del slider para el cálculo del desperdicio evitado
# Aquí se asume una proporción entre min y max del rango original para el cálculo del min proyectado
desperdicio_evitado_factor = porcentaje_rechazo_evitado / df_diagnostico.loc[0, 'porcentaje_rechazo_evitado_estimado']
desperdicio_evitado_min = (df_diagnostico.loc[1, 'rango_perdida_sugaring_min'] / 100) * volumen_anual_procesado * desperdicio_evitado_factor
desperdicio_evitado_max = (df_diagnostico.loc[1, 'rango_perdida_sugaring_max'] / 100) * volumen_anual_procesado * desperdicio_evitado_factor

# Pérdidas económicas evitadas se basan en el desperdicio máximo evitado proyectado
perdidas_economicas = desperdicio_evitado_max * precio_pasa

# Otros indicadores (se mantienen fijos para este ejemplo, pero se podrían parametrizar)
ahorros_energeticos = 10
empleos_indirectos_min = df_diagnostico.loc[4, 'factor_empleo_tecnico_min']
empleos_indirectos_max = df_diagnostico.loc[4, 'factor_empleo_tecnico_max']
# Escalar capacitación según el volumen anual procesado en comparación con el volumen de ejemplo de la ficha
capacitacion_personas = df_diagnostico.loc[4, 'personas_a_capacitar_por_plantas'] * (volumen_anual_procesado / df_diagnostico.loc[1, 'volumen_produccion_ejemplo_ton_año'])


st.header('Resultados Proyectados Anuales:')

# Uso de st.columns para organizar los métricas en una cuadrícula
col1, col2, col3 = st.columns(3)

with col1:
    st.metric(label="✅ **GEI Evitados por Devoluciones**", value=f"{gei_evitado:.2f} tCO₂e")
    st.caption("Reducción de emisiones por evitar el transporte de retorno de lotes rechazados.")
with col2:
    st.metric(label="🗑️ **Reducción del Desperdicio de Alimentos**", value=f"Entre {desperdicio_evitado_min:.0f} y {desperdicio_evitado_max:.0f} ton")
    st.caption(f"Estimación basada en evitar el rechazo por 'sugaring'.")
with col3:
    st.metric(label="💰 **Pérdidas Económicas Evitadas**", value=f"USD {perdidas_economicas:,.0f}")
    st.caption("Ahorros directos al evitar la pérdida de valor de la pasa.")

col4, col5 = st.columns(2) # Una nueva fila para los siguientes dos indicadores

with col4:
    st.metric(label="⚡ **Ahorros Energéticos Indirectos**", value=f"{ahorros_energeticos}%")
    st.caption("Reducción estimada en el consumo energético postcosecha.")
with col5:
    st.metric(label="🧑‍🔬 **Nuevos Empleos Indirectos (por planta)**", value=f"Entre {empleos_indirectos_min} y {empleos_indirectos_max} técnicos")
    st.caption("Estimación de personal técnico requerido para la implementación de la tecnología.")

# Capacitación técnica estimada se muestra fuera de columnas para mayor espacio
st.metric(label="🎓 **Capacitación Técnica Estimada**", value=f"{capacitacion_personas:.0f} personas", help=f"Personas capacitadas, escalado según el volumen anual procesado (ejemplo base: {df_diagnostico.loc[4, 'personas_a_capacitar_por_plantas']} por {df_diagnostico.loc[4, 'plantas_procesadoras_ejemplo']} plantas).")


st.markdown("---")

st.header('📊 Análisis Gráfico de Impactos')

# --- Visualización (Gráficos 3D con Matplotlib) ---
# Se crea una figura más grande para acomodar los gráficos 3D
fig = plt.figure(figsize=(20, 8), facecolor=color_primario_3_rgb) # Fondo blanco para la figura
fig.patch.set_facecolor(color_primario_3_rgb) # Asegura que el fondo de la figura sea blanco

# Calculo de valores de línea base para los gráficos (desde los datos de la ficha)
gei_base_ejemplo = df_diagnostico.loc[0, 'gei_contenedor_retornado_tco2e'] * \
                   (df_diagnostico.loc[0, 'porcentaje_rechazo_evitado_estimado'] / 100) * \
                   (df_diagnostico.loc[1, 'volumen_produccion_ejemplo_ton_año'] / 20)

desperdicio_base_ejemplo = df_diagnostico.loc[1, 'rango_perdida_sugaring_max'] / 100 * \
                           df_diagnostico.loc[1, 'volumen_produccion_ejemplo_ton_año']

perdidas_base_ejemplo = desperdicio_base_ejemplo * df_diagnostico.loc[2, 'precio_pasa_ton_usd']


# Subgráfico 1: GEI Evitados (Barra 3D)
ax1 = fig.add_subplot(1, 3, 1, projection='3d')
ejes_gei = ['Línea Base', 'Proyección']
z_pos = np.array([0, 0])
x_pos = np.arange(len(ejes_gei))
y_pos = np.zeros(len(ejes_gei))
dx = dy = 0.4 # Ancho y profundidad de las barras
dz_gei = np.array([gei_base_ejemplo, gei_evitado]) # Altura de las barras

ax1.bar3d(x_pos, y_pos, z_pos, dx, dy, dz_gei, color=[colors_for_charts[0], colors_for_charts[1]], alpha=0.9)
ax1.set_xticks(x_pos + dx / 2)
ax1.set_xticklabels(ejes_gei, rotation=15)
ax1.set_zlabel('tCO₂e/año', fontsize=10, color=colors_for_charts[0])
ax1.set_title('Emisiones de GEI Evitadas', fontsize=14, color=colors_for_charts[3])
ax1.tick_params(axis='x', colors=colors_for_charts[3])
ax1.tick_params(axis='z', colors=colors_for_charts[0])
ax1.xaxis.pane.fill = False
ax1.yaxis.pane.fill = False
ax1.zaxis.pane.fill = False
ax1.grid(False)
ax1.xaxis.line.set_color(colors_for_charts[0])
ax1.yaxis.line.set_color(colors_for_charts[0])
ax1.zaxis.line.set_color(colors_for_charts[0])

# Subgráfico 2: Desperdicio Evitado (Barra 3D)
ax2 = fig.add_subplot(1, 3, 2, projection='3d')
ejes_desperdicio = ['Línea Base', 'Proyección']
dz_desperdicio = np.array([desperdicio_base_ejemplo, desperdicio_evitado_max])
ax2.bar3d(x_pos, y_pos, z_pos, dx, dy, dz_desperdicio, color=[colors_for_charts[2], colors_for_charts[3]], alpha=0.9)
ax2.set_xticks(x_pos + dx / 2)
ax2.set_xticklabels(ejes_desperdicio, rotation=15)
ax2.set_zlabel('Toneladas/año', fontsize=10, color=colors_for_charts[0])
ax2.set_title('Reducción del Desperdicio de Alimentos', fontsize=14, color=colors_for_charts[3])
ax2.tick_params(axis='x', colors=colors_for_charts[3])
ax2.tick_params(axis='z', colors=colors_for_charts[0])
ax2.xaxis.pane.fill = False
ax2.yaxis.pane.fill = False
ax2.zaxis.pane.fill = False
ax2.grid(False)
ax2.xaxis.line.set_color(colors_for_charts[0])
ax2.yaxis.line.set_color(colors_for_charts[0])
ax2.zaxis.line.set_color(colors_for_charts[0])

# Subgráfico 3: Pérdidas Económicas Evitadas (Barra 3D)
ax3 = fig.add_subplot(1, 3, 3, projection='3d')
ejes_perdidas = ['Línea Base', 'Proyección']
dz_perdidas = np.array([perdidas_base_ejemplo, perdidas_economicas])
ax3.bar3d(x_pos, y_pos, z_pos, dx, dy, dz_perdidas, color=[colors_for_charts[0], colors_for_charts[2]], alpha=0.9)
ax3.set_xticks(x_pos + dx / 2)
ax3.set_xticklabels(ejes_perdidas, rotation=15)
ax3.set_zlabel('USD/año', fontsize=10, color=colors_for_charts[0])
ax3.set_title('Pérdidas Económicas Evitadas', fontsize=14, color=colors_for_charts[3])
ax3.tick_params(axis='x', colors=colors_for_charts[3])
ax3.tick_params(axis='z', colors=colors_for_charts[0])
ax3.xaxis.pane.fill = False
ax3.yaxis.pane.fill = False
ax3.zaxis.pane.fill = False
ax3.grid(False)
ax3.xaxis.line.set_color(colors_for_charts[0])
ax3.yaxis.line.set_color(colors_for_charts[0])
ax3.zaxis.line.set_color(colors_for_charts[0])


plt.tight_layout(rect=[0, 0.05, 1, 0.95]) # Ajusta el layout para evitar solapamientos
st.pyplot(fig) # Muestra la figura de Matplotlib en Streamlit


st.markdown("---")
st.markdown("### Información Adicional:")
st.markdown(f"- **Índice de Circularidad (CTI-WBCSD):** Se estima una mejora del % de circularidad de 0% a ~{porcentaje_rechazo_evitado:.0f}% por la tecnología implementada.")
st.markdown("- **Estado de Avance del Proyecto:** El proyecto cuenta con validación piloto y evidencia experimental en laboratorio. Se recomienda desarrollar fichas de monitoreo en empresas usuarias para registrar el volumen de pasas salvadas.")

st.markdown("---")
# Texto de atribución centrado
st.markdown("<div style='text-align: center;'>Visualizador Creado por el equipo Sustrend SpA en el marco del Proyecto TT GREEN Foods</div>", unsafe_allow_html=True)

# --- Mostrar Logos ---
# Columnas para centrar los logos
col_logos_left, col_logos_center, col_logos_right = st.columns([1, 2, 1])

with col_logos_center:
    # URLs de Google Drive para los logos. Se usa /uc?id= para acceso directo.
    sustrend_logo_url = "https://drive.google.com/uc?id=1vx_znPU2VfdkzeDtl91dlpw_p9mmu4dd"
    ttgreenfoods_logo_url = "https://drive.google.com/uc?id=1uIQZQywjuQJz6Eokkj6dNSpBroJ8tQf8"

    # Intentar descargar y mostrar las imágenes
    try:
        sustrend_response = requests.get(sustrend_logo_url)
        sustrend_response.raise_for_status() # Lanza un error para códigos de estado HTTP incorrectos
        sustrend_image = Image.open(BytesIO(sustrend_response.content))

        ttgreenfoods_response = requests.get(ttgreenfoods_logo_url)
        ttgreenfoods_response.raise_for_status()
        ttgreenfoods_image = Image.open(BytesIO(ttgreenfoods_response.content))

        # Mostrar las imágenes en una fila, ajustando el ancho
        # Se usa una lista de imágenes para mostrar múltiples en una sola llamada st.image
        st.image([sustrend_image, ttgreenfoods_image], width=100) # Ajusta el ancho según necesites
    except requests.exceptions.RequestException as e:
        st.error(f"Error al cargar los logos desde las URLs. Por favor, verifica los enlaces: {e}")
    except Exception as e:
        st.error(f"Error inesperado al procesar las imágenes de los logos: {e}")

st.markdown("<div style='text-align: center; font-size: small; color: gray;'>Viña del Mar, Valparaíso, Chile</div>", unsafe_allow_html=True)

st.sidebar.markdown("---")
st.sidebar.markdown(f"<div style='text-align: center; font-size: smaller; color: gray;'>Versión del Visualizador: 1.2</div>", unsafe_allow_html=True) # Actualizada la versión
st.sidebar.markdown(f"<div style='text-align: center; font-size: x-small; color: lightgray;'>Desarrollado con Streamlit</div>", unsafe_allow_html=True)
