{\rtf1\ansi\ansicpg1252\cocoartf2513
\cocoatextscaling0\cocoaplatform0{\fonttbl\f0\fswiss\fcharset0 Helvetica;\f1\fnil\fcharset0 AppleColorEmoji;}
{\colortbl;\red255\green255\blue255;}
{\*\expandedcolortbl;;}
\margl1440\margr1440\vieww10800\viewh8400\viewkind0
\pard\tx566\tx1133\tx1700\tx2267\tx2834\tx3401\tx3968\tx4535\tx5102\tx5669\tx6236\tx6803\pardirnatural\partightenfactor0

\f0\fs24 \cf0 import streamlit as st\
import pandas as pd\
import matplotlib.pyplot as plt\
\
# --- Configuraci\'f3n de la p\'e1gina de Streamlit ---\
st.set_page_config(layout="wide")\
\
st.title('
\f1 \uc0\u55357 \u56520 
\f0  Visualizador de Impactos - Subproyecto P1.1')\
st.subheader('Reducci\'f3n del fen\'f3meno de \'93sugaring\'94 en pasas mediante tratamiento por microondas')\
st.markdown("""\
    Ajusta los par\'e1metros para explorar c\'f3mo las proyecciones de impacto ambiental y econ\'f3mico del proyecto\
    var\'edan con diferentes escenarios de volumen procesado, precio de exportaci\'f3n y porcentaje de rechazo evitado.\
""")\
\
# --- 1. Datos del Proyecto (L\'ednea Base y Proyecciones) ---\
\
# Datos de la ficha t\'e9cnica\
data = \{\
    "indicador": [\
        "GEI evitados por devoluciones internacionales (tCO\uc0\u8322 e/a\'f1o)",\
        "Reducci\'f3n del desperdicio de alimentos (ton/a\'f1o)",\
        "P\'e9rdidas econ\'f3micas evitadas por lotes rechazados (USD/a\'f1o)",\
        "Ahorros energ\'e9ticos indirectos (% reducci\'f3n en consumo energ\'e9tico postcosecha)",\
        "Nuevos empleos indirectos (t\'e9cnicos por planta)"\
    ],\
    "unidad": ["tCO\uc0\u8322 e/a\'f1o", "ton/a\'f1o", "USD/a\'f1o", "%", "t\'e9cnicos"],\
    "rango_perdida_sugaring_min": [None, 5, None, None, None], # % del total exportado\
    "rango_perdida_sugaring_max": [None, 10, None, None, None], # % del total exportado\
    "volumen_produccion_ejemplo_ton_a\'f1o": [None, 1000, 1000, None, None], # para el ejemplo de la ficha\
    "precio_pasa_ton_usd": [None, None, 2800, None, None],\
    "gei_contenedor_retornado_tco2e": [2.4, None, None, None, None],\
    "porcentaje_rechazo_evitado_estimado": [10, None, None, None, None], # % del volumen exportado\
    "factor_empleo_tecnico_min": [None, None, None, None, 1],\
    "factor_empleo_tecnico_max": [None, None, None, None, 3],\
    "plantas_procesadoras_ejemplo": [None, None, None, None, 5],\
    "personas_a_capacitar_por_plantas": [None, None, None, None, 20]\
\}\
\
df_diagnostico = pd.DataFrame(data)\
\
# --- 2. Widgets Interactivos para Par\'e1metros (Streamlit) ---\
st.sidebar.header('Par\'e1metros de Simulaci\'f3n')\
\
porcentaje_rechazo_evitado = st.sidebar.slider(\
    'Porcentaje de Rechazo Evitado (% del volumen exportado):',\
    min_value=0.0,\
    max_value=20.0,\
    value=10.0,\
    step=0.5,\
    help="Porcentaje del volumen total exportado que se logra salvar del 'sugaring'."\
)\
\
volumen_anual_procesado = st.sidebar.slider(\
    'Volumen Anual Procesado (ton):',\
    min_value=100,\
    max_value=5000,\
    value=1000,\
    step=50,\
    help="Volumen total de pasas procesadas anualmente por la industria."\
)\
\
precio_pasa = st.sidebar.slider(\
    'Precio de Exportaci\'f3n de Pasa (USD/ton):',\
    min_value=1000,\
    max_value=5000,\
    value=2800,\
    step=100,\
    help="Precio promedio de exportaci\'f3n de la tonelada de pasa."\
)\
\
# --- 3. C\'e1lculos y Visualizaci\'f3n (Streamlit) ---\
\
# C\'e1lculos din\'e1micos basados en los sliders\
# (Volumen total / 20 ton por contenedor) * GEI por contenedor\
gei_evitado = (porcentaje_rechazo_evitado / 100) * (volumen_anual_procesado / 20) * df_diagnostico.loc[0, 'gei_contenedor_retornado_tco2e']\
\
# El rango de desperdicio se convierte en una estimaci\'f3n puntual para la proyecci\'f3n\
# Se usa el porcentaje de rechazo evitado del slider para el c\'e1lculo del desperdicio evitado\
desperdicio_evitado_min = (porcentaje_rechazo_evitado / 100) * volumen_anual_procesado * (df_diagnostico.loc[1, 'rango_perdida_sugaring_min'] / df_diagnostico.loc[1, 'rango_perdida_sugaring_max']) # Ajuste proporcional al slider\
desperdicio_evitado_max = (porcentaje_rechazo_evitado / 100) * volumen_anual_procesado\
\
\
# P\'e9rdidas econ\'f3micas evitadas se basan en el desperdicio evitado proyectado por el slider\
perdidas_economicas = desperdicio_evitado_max * precio_pasa\
\
# Otros indicadores (no son directamente impactados por los sliders para este ejemplo simple)\
ahorros_energeticos = 10 # % reducci\'f3n fija por ahora\
empleos_indirectos_min = df_diagnostico.loc[4, 'factor_empleo_tecnico_min']\
empleos_indirectos_max = df_diagnostico.loc[4, 'factor_empleo_tecnico_max']\
capacitacion_personas = df_diagnostico.loc[4, 'personas_a_capacitar_por_plantas'] * (volumen_anual_procesado / df_diagnostico.loc[1, 'volumen_produccion_ejemplo_ton_a\'f1o']) # Escala con el volumen\
\
st.header('Resultados Proyectados Anuales:')\
\
col1, col2, col3 = st.columns(3)\
\
with col1:\
    st.metric(label="
\f1 \uc0\u9989 
\f0  **GEI Evitados por Devoluciones**", value=f"\{gei_evitado:.2f\} tCO\uc0\u8322 e")\
    st.caption("Reducci\'f3n de emisiones por evitar el transporte de retorno de lotes rechazados.")\
with col2:\
    st.metric(label="
\f1 \uc0\u55357 \u56785 \u65039 
\f0  **Reducci\'f3n del Desperdicio de Alimentos**", value=f"\{desperdicio_evitado_max:.0f\} ton")\
    st.caption(f"Estimaci\'f3n basada en evitar el rechazo por 'sugaring'.")\
with col3:\
    st.metric(label="
\f1 \uc0\u55357 \u56496 
\f0  **P\'e9rdidas Econ\'f3micas Evitadas**", value=f"USD \{perdidas_economicas:,.0f\}")\
    st.caption("Ahorros directos al evitar la p\'e9rdida de valor de la pasa.")\
\
col4, col5, col6 = st.columns(3)\
\
with col4:\
    st.metric(label="
\f1 \uc0\u9889 
\f0  **Ahorros Energ\'e9ticos Indirectos**", value=f"\{ahorros_energeticos\}%")\
    st.caption("Reducci\'f3n estimada en el consumo energ\'e9tico postcosecha.")\
with col5:\
    st.metric(label="
\f1 \uc0\u55358 \u56785 \u8205 \u55357 \u56620 
\f0  **Nuevos Empleos Indirectos (por planta)**", value=f"Entre \{empleos_indirectos_min\} y \{empleos_indirectos_max\} t\'e9cnicos")\
    st.caption("Estimaci\'f3n de personal t\'e9cnico requerido para la implementaci\'f3n de la tecnolog\'eda.")\
with col6:\
    st.metric(label="
\f1 \uc0\u55356 \u57235 
\f0  **Capacitaci\'f3n T\'e9cnica Estimada**", value=f"\{capacitacion_personas:.0f\} personas")\
    st.caption(f"Personas capacitadas, escalado seg\'fan el volumen anual procesado.")\
\
st.markdown("---")\
\
st.header('An\'e1lisis Gr\'e1fico de Impactos')\
\
# --- Visualizaci\'f3n (Gr\'e1ficos con Matplotlib y Streamlit) ---\
fig, axes = plt.subplots(1, 3, figsize=(20, 7))\
fig.suptitle('Proyecciones de Impacto - Subproyecto P1.1', fontsize=16)\
\
# Gr\'e1fico 1: GEI Evitados\
# Calculado del ejemplo de la ficha para la l\'ednea base\
gei_base_ejemplo = (df_diagnostico.loc[0, 'porcentaje_rechazo_evitado_estimado'] / 100) * \\\
                   (df_diagnostico.loc[1, 'volumen_produccion_ejemplo_ton_a\'f1o'] / 20) * \\\
                   df_diagnostico.loc[0, 'gei_contenedor_retornado_tco2e']\
\
ejes_gei = ['L\'ednea Base (Ejemplo Ficha)', 'Proyecci\'f3n Actual']\
valores_gei = [gei_base_ejemplo, gei_evitado]\
axes[0].bar(ejes_gei, valores_gei, color=['lightcoral', 'skyblue'])\
axes[0].set_title('Emisiones de GEI Evitadas (tCO\uc0\u8322 e/a\'f1o)')\
axes[0].set_ylabel('tCO\uc0\u8322 e/a\'f1o')\
for i, v in enumerate(valores_gei):\
    axes[0].text(i, v + 0.5, f"\{v:.2f\}", ha='center', va='bottom')\
\
# Gr\'e1fico 2: Desperdicio Evitado\
# Ejemplo de ficha para l\'ednea base (usando el m\'e1ximo del rango de p\'e9rdida)\
desperdicio_base_ejemplo = df_diagnostico.loc[1, 'rango_perdida_sugaring_max'] / 100 * \\\
                           df_diagnostico.loc[1, 'volumen_produccion_ejemplo_ton_a\'f1o']\
\
ejes_desperdicio = ['L\'ednea Base (Ejemplo Ficha)', 'Proyecci\'f3n']\
valores_desperdicio = [desperdicio_base_ejemplo, desperdicio_evitado_max]\
axes[1].bar(ejes_desperdicio, valores_desperdicio, color=['lightcoral', 'lightgreen'])\
axes[1].set_title('Reducci\'f3n del Desperdicio de Alimentos (ton/a\'f1o)')\
axes[1].set_ylabel('Toneladas/a\'f1o')\
for i, v in enumerate(valores_desperdicio):\
    axes[1].text(i, v + 0.5, f"\{v:.0f\}", ha='center', va='bottom')\
\
# Gr\'e1fico 3: P\'e9rdidas Econ\'f3micas Evitadas\
# Ejemplo de ficha para l\'ednea base (usando el desperdicio base y precio de la ficha)\
perdidas_base_ejemplo = desperdicio_base_ejemplo * df_diagnostico.loc[2, 'precio_pasa_ton_usd']\
\
ejes_perdidas = ['L\'ednea Base (Ejemplo Ficha)', 'Proyecci\'f3n Actual']\
valores_perdidas = [perdidas_base_ejemplo, perdidas_economicas]\
axes[2].bar(ejes_perdidas, valores_perdidas, color=['lightcoral', 'skyblue'])\
axes[2].set_title('P\'e9rdidas Econ\'f3micas Evitadas (USD/a\'f1o)')\
axes[2].set_ylabel('USD/a\'f1o')\
for i, v in enumerate(valores_perdidas):\
    axes[2].text(i, v + 500, f"$\{v:,.0f\}", ha='center', va='bottom')\
\
plt.tight_layout(rect=[0, 0.03, 1, 0.95])\
st.pyplot(fig) # Muestra la figura de Matplotlib en Streamlit\
\
st.markdown("---")\
st.markdown("### Informaci\'f3n Adicional:")\
st.markdown(f"- **\'cdndice de Circularidad (CTI-WBCSD):** Se estima una mejora del % de circularidad de 0% a ~\{porcentaje_rechazo_evitado:.0f\}% por la tecnolog\'eda implementada.")\
st.markdown("- **Estado de Avance del Proyecto:** El proyecto cuenta con validaci\'f3n piloto y evidencia experimental en laboratorio. Se recomienda desarrollar fichas de monitoreo en empresas usuarias para registrar el volumen de pasas salvadas.")}