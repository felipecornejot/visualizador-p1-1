import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image
from io import BytesIO
import requests

# --- Paleta de Colores ---
# Definición de colores en formato RGB (0-1) para Matplotlib
color_primario_1_rgb = (14/255, 69/255, 74/255)   # 0E454A (Oscuro)
color_primario_2_rgb = (31/255, 255/255, 95/255)  # 1FFF5F (Verde vibrante)
color_primario_3_rgb = (255/255, 255/255, 255/255) # FFFFFF (Blanco)

# Colores del logo de Sustrend para complementar
color_sustrend_1_rgb = (0/255, 155/255, 211/255)   # 009BD3 (Azul claro)
color_sustrend_2_rgb = (0/255, 140/255, 207/255)   # 008CCF (Azul medio)
color_sustrend_3_rgb = (0/255, 54/255, 110/255)    # 00366E (Azul oscuro)

# Selección de colores para los gráficos
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
gei_evitado = (porcentaje_rechazo_evitado / 100) * (volumen_anual_procesado / 20) * df_diagnostico.loc[0, 'gei_contenedor_retornado_tco2e']

desperdicio_evitado_factor = porcentaje_rechazo_evitado / df_diagnostico.loc[0, 'porcentaje_rechazo_evitado_estimado']
desperdicio_evitado_min = (df_diagnostico.loc[1, 'rango_perdida_sugaring_min'] / 100) * volumen_anual_procesado * desperdicio_evitado_factor
desperdicio_evitado_max = (df_diagnostico.loc[1, 'rango_perdida_sugaring_max'] / 100) * volumen_anual_procesado * desperdicio_evitado_factor

perdidas_economicas = desperdicio_evitado_max * precio_pasa

ahorros_energeticos = 10
empleos_indirectos_min = df_diagnostico.loc[4, 'factor_empleo_tecnico_min']
empleos_indirectos_max = df_diagnostico.loc[4, 'factor_empleo_tecnico_max']
capacitacion_personas = df_diagnostico.loc[4, 'personas_a_capacitar_por_plantas'] * (volumen_anual_procesado / df_diagnostico.loc[1, 'volumen_produccion_ejemplo_ton_año'])


st.header('Resultados Proyectados Anuales:')

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

col4, col5 = st.columns(2)

with col4:
    st.metric(label="⚡ **Ahorros Energéticos Indirectos**", value=f"{ahorros_energeticos}%")
    st.caption("Reducción estimada en el consumo energético postcosecha.")
with col5:
    st.metric(label="🧑‍🔬 **Nuevos Empleos Indirectos (por planta)**", value=f"Entre {empleos_indirectos_min} y {empleos_indirectos_max} técnicos")
    st.caption("Estimación de personal técnico requerido para la implementación de la tecnología.")

st.metric(label="🎓 **Capacitación Técnica Estimada**", value=f"{capacitacion_personas:.0f} personas", help=f"Personas capacitadas, escalado según el volumen anual procesado (ejemplo base: {df_diagnostico.loc[4, 'personas_a_capacitar_por_plantas']} por {df_diagnostico.loc[4, 'plantas_procesadoras_ejemplo']} plantas).")


st.markdown("---")

st.header('📊 Análisis Gráfico de Impactos')

# --- Visualización (Gráficos 2D con Matplotlib) ---
# Cálculo de valores de línea base para los gráficos (desde los datos de la ficha)
gei_base_ejemplo = df_diagnostico.loc[0, 'gei_contenedor_retornado_tco2e'] * \
                   (df_diagnostico.loc[0, 'porcentaje_rechazo_evitado_estimado'] / 100) * \
                   (df_diagnostico.loc[1, 'volumen_produccion_ejemplo_ton_año'] / 20)

desperdicio_base_ejemplo = df_diagnostico.loc[1, 'rango_perdida_sugaring_max'] / 100 * \
                           df_diagnostico.loc[1, 'volumen_produccion_ejemplo_ton_año']

perdidas_base_ejemplo = desperdicio_base_ejemplo * df_diagnostico.loc[2, 'precio_pasa_ton_usd']

# Creamos una figura con 3 subplots (2D)
fig, (ax1, ax2, ax3) = plt.subplots(1, 3, figsize=(20, 7), facecolor=color_primario_3_rgb)
fig.patch.set_facecolor(color_primario_3_rgb)

# Definición de etiquetas y valores para los gráficos de barras 2D
labels = ['Línea Base', 'Proyección']
bar_width = 0.6
x = np.arange(len(labels))

# --- Gráfico 1: GEI Evitados ---
gei_values = [gei_base_ejemplo, gei_evitado]
bars1 = ax1.bar(x, gei_values, width=bar_width, color=[colors_for_charts[0], colors_for_charts[1]])
ax1.set_ylabel('tCO₂e/año', fontsize=12, color=colors_for_charts[3])
ax1.set_title('Emisiones de GEI Evitadas', fontsize=14, color=colors_for_charts[3])
ax1.set_xticks(x)
ax1.set_xticklabels(labels, rotation=15, color=colors_for_charts[0])
ax1.yaxis.set_tick_params(colors=colors_for_charts[0]) # Color de los números del eje Y
ax1.spines['top'].set_visible(False)
ax1.spines['right'].set_visible(False)
ax1.tick_params(axis='x', length=0) # Elimina los ticks del eje X
ax1.set_ylim(bottom=0) # Asegura que el eje Y comience en 0 para GEI
for bar in bars1:
    yval = bar.get_height()
    ax1.text(bar.get_x() + bar.get_width()/2, yval + 0.05 * yval, round(yval, 2), ha='center', va='bottom', color=colors_for_charts[0])


# --- Gráfico 2: Desperdicio Evitado ---
desperdicio_values = [desperdicio_base_ejemplo, desperdicio_evitado_max]
bars2 = ax2.bar(x, desperdicio_values, width=bar_width, color=[colors_for_charts[2], colors_for_charts[3]])
ax2.set_ylabel('Toneladas/año', fontsize=12, color=colors_for_charts[0])
ax2.set_title('Reducción del Desperdicio de Alimentos', fontsize=14, color=colors_for_charts[3])
ax2.set_xticks(x)
ax2.set_xticklabels(labels, rotation=15, color=colors_for_charts[0])
ax2.yaxis.set_tick_params(colors=colors_for_charts[0])
ax2.spines['top'].set_visible(False)
ax2.spines['right'].set_visible(False)
ax2.tick_params(axis='x', length=0)
ax2.set_ylim(bottom=0) # Asegura que el eje Y comience en 0 para Desperdicio
for bar in bars2:
    yval = bar.get_height()
    ax2.text(bar.get_x() + bar.get_width()/2, yval + 0.05 * yval, round(yval, 0), ha='center', va='bottom', color=colors_for_charts[0])


# --- Gráfico 3: Pérdidas Económicas Evitadas ---
perdidas_values = [perdidas_base_ejemplo, perdidas_economicas]
bars3 = ax3.bar(x, perdidas_values, width=bar_width, color=[colors_for_charts[1], colors_for_charts[0]])
ax3.set_ylabel('USD/año', fontsize=12, color=colors_for_charts[3])
ax3.set_title('Pérdidas Económicas Evitadas', fontsize=14, color=colors_for_charts[3])
ax3.set_xticks(x)
ax3.set_xticklabels(labels, rotation=15, color=colors_for_charts[0])
ax3.yaxis.set_tick_params(colors=colors_for_charts[0])
ax3.spines['top'].set_visible(False)
ax3.spines['right'].set_visible(False)
ax3.tick_params(axis='x', length=0)
ax3.set_ylim(bottom=0) # Asegura que el eje Y comience en 0 para Pérdidas Económicas
for bar in bars3:
    yval = bar.get_height()
    ax3.text(bar.get_x() + bar.get_width()/2, yval + 0.05 * yval, f"{int(yval):,}", ha='center', va='bottom', color=colors_for_charts[0])


plt.tight_layout(rect=[0, 0.05, 1, 0.95]) # Ajusta el layout
st.pyplot(fig) # Muestra la figura completa de Matplotlib en Streamlit

# --- Funcionalidad de descarga de cada gráfico ---
st.markdown("---")
st.subheader("Descargar Gráficos Individualmente")

# Función auxiliar para generar el botón de descarga
def download_button(fig, filename_prefix, key):
    buf = BytesIO()
    fig.savefig(buf, format="png", bbox_inches="tight", dpi=300)
    st.download_button(
        label=f"Descargar {filename_prefix}.png",
        data=buf.getvalue(),
        file_name=f"{filename_prefix}.png",
        mime="image/png",
        key=key
    )

# Crear figuras individuales para cada gráfico para poder descargarlas
# Figura 1: GEI Evitados
fig_gei, ax_gei = plt.subplots(figsize=(8, 6), facecolor=color_primario_3_rgb)
ax_gei.bar(x, gei_values, width=bar_width, color=[colors_for_charts[0], colors_for_charts[1]])
ax_gei.set_ylabel('tCO₂e/año', fontsize=12, color=colors_for_charts[3])
ax_gei.set_title('Emisiones de GEI Evitadas', fontsize=14, color=colors_for_charts[3])
ax_gei.set_xticks(x)
ax_gei.set_xticklabels(labels, rotation=15, color=colors_for_charts[0])
ax_gei.yaxis.set_tick_params(colors=colors_for_charts[0])
ax_gei.spines['top'].set_visible(False)
ax_gei.spines['right'].set_visible(False)
ax_gei.tick_params(axis='x', length=0)
ax_gei.set_ylim(bottom=0)
for bar in ax_gei.patches:
    yval = bar.get_height()
    ax_gei.text(bar.get_x() + bar.get_width()/2, yval + 0.05 * yval, round(yval, 2), ha='center', va='bottom', color=colors_for_charts[0])
plt.tight_layout()
download_button(fig_gei, "GEI_Evitados", "download_gei")
plt.close(fig_gei) # Importante cerrar la figura para liberar memoria

# Figura 2: Desperdicio Evitado
fig_desperdicio, ax_desperdicio = plt.subplots(figsize=(8, 6), facecolor=color_primario_3_rgb)
ax_desperdicio.bar(x, desperdicio_values, width=bar_width, color=[colors_for_charts[2], colors_for_charts[3]])
ax_desperdicio.set_ylabel('Toneladas/año', fontsize=12, color=colors_for_charts[0])
ax_desperdicio.set_title('Reducción del Desperdicio de Alimentos', fontsize=14, color=colors_for_charts[3])
ax_desperdicio.set_xticks(x)
ax_desperdicio.set_xticklabels(labels, rotation=15, color=colors_for_charts[0])
ax_desperdicio.yaxis.set_tick_params(colors=colors_for_charts[0])
ax_desperdicio.spines['top'].set_visible(False)
ax_desperdicio.spines['right'].set_visible(False)
ax_desperdicio.tick_params(axis='x', length=0)
ax_desperdicio.set_ylim(bottom=0)
for bar in ax_desperdicio.patches:
    yval = bar.get_height()
    ax_desperdicio.text(bar.get_x() + bar.get_width()/2, yval + 0.05 * yval, round(yval, 0), ha='center', va='bottom', color=colors_for_charts[0])
plt.tight_layout()
download_button(fig_desperdicio, "Desperdicio_Evitado", "download_desperdicio")
plt.close(fig_desperdicio)

# Figura 3: Pérdidas Económicas Evitadas
fig_perdidas, ax_perdidas = plt.subplots(figsize=(8, 6), facecolor=color_primario_3_rgb)
ax_perdidas.bar(x, perdidas_values, width=bar_width, color=[colors_for_charts[1], colors_for_charts[0]])
ax_perdidas.set_ylabel('USD/año', fontsize=12, color=colors_for_charts[3])
ax_perdidas.set_title('Pérdidas Económicas Evitadas', fontsize=14, color=colors_for_charts[3])
ax_perdidas.set_xticks(x)
ax_perdidas.set_xticklabels(labels, rotation=15, color=colors_for_charts[0])
ax_perdidas.yaxis.set_tick_params(colors=colors_for_charts[0])
ax_perdidas.spines['top'].set_visible(False)
ax_perdidas.spines['right'].set_visible(False)
ax_perdidas.tick_params(axis='x', length=0)
ax_perdidas.set_ylim(bottom=0)
for bar in ax_perdidas.patches:
    yval = bar.get_height()
    ax_perdidas.text(bar.get_x() + bar.get_width()/2, yval + 0.05 * yval, f"{int(yval):,}", ha='center', va='bottom', color=colors_for_charts[0])
plt.tight_layout()
download_button(fig_perdidas, "Perdidas_Economicas_Evitadas", "download_perdidas")
plt.close(fig_perdidas)


st.markdown("---")
st.markdown("### Información Adicional:")
st.markdown(f"- **Índice de Circularidad (CTI-WBCSD):** Se estima una mejora del % de circularidad de 0% a ~{porcentaje_rechazo_evitado:.0f}% por la tecnología implementada.")
st.markdown("- **Estado de Avance del Proyecto:** El proyecto cuenta con validación piloto y evidencia experimental en laboratorio. Se recomienda desarrollar fichas de monitoreo en empresas usuarias para registrar el volumen de pasas salvadas.")

st.markdown("---")
# Texto de atribución centrado
st.markdown("<div style='text-align: center;'>Visualizador Creado por el equipo Sustrend SpA en el marco del Proyecto TT GREEN Foods</div>", unsafe_allow_html=True)

# --- Mostrar Logos ---
col_logos_left, col_logos_center, col_logos_right = st.columns([1, 2, 1])

with col_logos_center:
    sustrend_logo_url = "https://drive.google.com/uc?id=1vx_znPU2VfdkzeDtl91dlpw_p9mmu4dd"
    ttgreenfoods_logo_url = "https://drive.google.com/uc?id=1uIQZQywjuQJz6Eokkj6dNSpBroJ8tQf8"

    try:
        sustrend_response = requests.get(sustrend_logo_url)
        sustrend_response.raise_for_status()
        sustrend_image = Image.open(BytesIO(sustrend_response.content))

        ttgreenfoods_response = requests.get(ttgreenfoods_logo_url)
        ttgreenfoods_response.raise_for_status()
        ttgreenfoods_image = Image.open(BytesIO(ttgreenfoods_response.content))

        st.image([sustrend_image, ttgreenfoods_image], width=100)
    except requests.exceptions.RequestException as e:
        st.error(f"Error al cargar los logos desde las URLs. Por favor, verifica los enlaces: {e}")
    except Exception as e:
        st.error(f"Error inesperado al procesar las imágenes de los logos: {e}")

st.markdown("<div style='text-align: center; font-size: small; color: gray;'>Viña del Mar, Valparaíso, Chile</div>", unsafe_allow_html=True)

st.sidebar.markdown("---")
st.sidebar.markdown(f"<div style='text-align: center; font-size: smaller; color: gray;'>Versión del Visualizador: 1.3</div>", unsafe_allow_html=True)
st.sidebar.markdown(f"<div style='text-align: center; font-size: x-small; color: lightgray;'>Desarrollado con Streamlit</div>", unsafe_allow_html=True)
