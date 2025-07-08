import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# --- Configuración de la página de Streamlit ---
st.set_page_config(layout="wide")

st.title('📈 Visualizador de Impactos - Subproyecto P1.1')
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
    "rango_perdida_sugaring_min": [None, 5, None, None, None], # % del total exportado
    "rango_perdida_sugaring_max": [None, 10, None, None, None], # % del total exportado
    "volumen_produccion_ejemplo_ton_año": [None, 1000, 1000, None, None], # para el ejemplo de la ficha
    "precio_pasa_ton_usd": [None, None, 2800, None, None],
    "gei_contenedor_retornado_tco2e": [2.4, None, None, None, None],
    "porcentaje_rechazo_evitado_estimado": [10, None, None, None, None], # % del volumen exportado
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

# --- 3. Cálculos y Visualización (Streamlit) ---

# Cálculos dinámicos basados en los sliders
# (Volumen total / 20 ton por contenedor) * GEI por contenedor
gei_evitado = (porcentaje_rechazo_evitado / 100) * (volumen_anual_procesado / 20) * df_diagnostico.loc[0, 'gei_contenedor_retornado_tco2e']

# El rango de desperdicio se convierte en una estimación puntual para la proyección
# Se usa el porcentaje de rechazo evitado del slider para el cálculo del desperdicio evitado
desperdicio_evitado_min = (porcentaje_rechazo_evitado / 100) * volumen_anual_procesado * (df_diagnostico.loc[1, 'rango_perdida_sugaring_min'] / df_diagnostico.loc[1, 'rango_perdida_sugaring_max']) # Ajuste proporcional al slider
desperdicio_evitado_max = (porcentaje_rechazo_evitado / 100) * volumen_anual_procesado


# Pérdidas económicas evitadas se basan en el desperdicio evitado proyectado por el slider
perdidas_economicas = desperdicio_evitado_max * precio_pasa

# Otros indicadores (no son directamente impactados por los sliders para este ejemplo simple)
ahorros_energeticos = 10 # % reducción fija por ahora
empleos_indirectos_min = df_diagnostico.loc[4, 'factor_empleo_tecnico_min']
empleos_indirectos_max = df_diagnostico.loc[4, 'factor_empleo_tecnico_max']
capacitacion_personas = df_diagnostico.loc[4, 'personas_a_capacitar_por_plantas'] * (volumen_anual_procesado / df_diagnostico.loc[1, 'volumen_produccion_ejemplo_ton_año']) # Escala con el volumen

st.header('Resultados Proyectados Anuales:')

col1, col2, col3 = st.columns(3)

with col1:
    st.metric(label="✅ **GEI Evitados por Devoluciones**", value=f"{gei_evitado:.2f} tCO₂e")
    st.caption("Reducción de emisiones por evitar el transporte de retorno de lotes rechazados.")
with col2:
    st.metric(label="🗑️ **Reducción del Desperdicio de Alimentos**", value=f"{desperdicio_evitado_max:.0f} ton")
    st.caption(f"Estimación basada en evitar el rechazo por 'sugaring'.")
with col3:
    st.metric(label="💰 **Pérdidas Económicas Evitadas**", value=f"USD {perdidas_economicas:,.0f}")
    st.caption("Ahorros directos al evitar la pérdida de valor de la pasa.")

col4, col5, col6 = st.columns(3)

with col4:
    st.metric(label="⚡ **Ahorros Energéticos Indirectos**", value=f"{ahorros_energeticos}%")
    st.caption("Reducción estimada en el consumo energético postcosecha.")
with col5:
    st.metric(label="🧑‍🔬 **Nuevos Empleos Indirectos (por planta)**", value=f"Entre {empleos_indirectos_min} y {empleos_indirectos_max} técnicos")
    st.caption("Estimación de personal técnico requerido para la implementación de la tecnología.")
with col6:
    st.metric(label="🎓 **Capacitación Técnica Estimada**", value=f"{capacitacion_personas:.0f} personas")
    st.caption(f"Personas capacitadas, escalado según el volumen anual procesado.")

st.markdown("---")

st.header('Análisis Gráfico de Impactos')

# --- Visualización (Gráficos con Matplotlib y Streamlit) ---
fig, axes = plt.subplots(1, 3, figsize=(20, 7))
fig.suptitle('Proyecciones de Impacto - Subproyecto P1.1', fontsize=16)

# Gráfico 1: GEI Evitados
# Calculado del ejemplo de la ficha para la línea base
gei_base_ejemplo = (df_diagnostico.loc[0, 'porcentaje_rechazo_evitado_estimado'] / 100) * \
                   (df_diagnostico.loc[1, 'volumen_produccion_ejemplo_ton_año'] / 20) * \
                   df_diagnostico.loc[0, 'gei_contenedor_retornado_tco2e']

ejes_gei = ['Línea Base (Ejemplo Ficha)', 'Proyección Actual']
valores_gei = [gei_base_ejemplo, gei_evitado]
axes[0].bar(ejes_gei, valores_gei, color=['lightcoral', 'skyblue'])
axes[0].set_title('Emisiones de GEI Evitadas (tCO₂e/año)')
axes[0].set_ylabel('tCO₂e/año')
for i, v in enumerate(valores_gei):
    axes[0].text(i, v + 0.5, f"{v:.2f}", ha='center', va='bottom')

# Gráfico 2: Desperdicio Evitado
# Ejemplo de ficha para línea base (usando el máximo del rango de pérdida)
desperdicio_base_ejemplo = df_diagnostico.loc[1, 'rango_perdida_sugaring_max'] / 100 * \
                           df_diagnostico.loc[1, 'volumen_produccion_ejemplo_ton_año']

ejes_desperdicio = ['Línea Base (Ejemplo Ficha)', 'Proyección']
valores_desperdicio = [desperdicio_base_ejemplo, desperdicio_evitado_max]
axes[1].bar(ejes_desperdicio, valores_desperdicio, color=['lightcoral', 'lightgreen'])
axes[1].set_title('Reducción del Desperdicio de Alimentos (ton/año)')
axes[1].set_ylabel('Toneladas/año')
for i, v in enumerate(valores_desperdicio):
    axes[1].text(i, v + 0.5, f"{v:.0f}", ha='center', va='bottom')

# Gráfico 3: Pérdidas Económicas Evitadas
# Ejemplo de ficha para línea base (usando el desperdicio base y precio de la ficha)
perdidas_base_ejemplo = desperdicio_base_ejemplo * df_diagnostico.loc[2, 'precio_pasa_ton_usd']

ejes_perdidas = ['Línea Base (Ejemplo Ficha)', 'Proyección Actual']
valores_perdidas = [perdidas_base_ejemplo, perdidas_economicas]
axes[2].bar(ejes_perdidas, valores_perdidas, color=['lightcoral', 'skyblue'])
axes[2].set_title('Pérdidas Económicas Evitadas (USD/año)')
axes[2].set_ylabel('USD/año')
for i, v in enumerate(valores_perdidas):
    axes[2].text(i, v + 500, f"${v:,.0f}", ha='center', va='bottom')

plt.tight_layout(rect=[0, 0.03, 1, 0.95])
st.pyplot(fig) # Muestra la figura de Matplotlib en Streamlit

st.markdown("---")
st.markdown("### Información Adicional:")
st.markdown(f"- **Índice de Circularidad (CTI-WBCSD):** Se estima una mejora del % de circularidad de 0% a ~{porcentaje_rechazo_evitado:.0f}% por la tecnología implementada.")
st.markdown("- **Estado de Avance del Proyecto:** El proyecto cuenta con validación piloto y evidencia experimental en laboratorio. Se recomienda desarrollar fichas de monitoreo en empresas usuarias para registrar el volumen de pasas salvadas.")
