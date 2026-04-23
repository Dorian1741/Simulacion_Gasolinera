import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import simpy
import numpy as np
import os
from datetime import datetime

# Importamos tu configuración y modelos
# verifica el settings en fa
from config.settings import RANDOM_SEED, TIEMPO_SIMULACION, TIEMPO_ENTRE_LLEGADAS
from models.gasolinera import Gasolinera
from models.simulador import Simulador

st.set_page_config(page_title="Simulación Gasolinera", page_icon="⛽", layout="wide")

# ==========================================
# CONFIGURACIÓN DE AFLUENCIA POR DÍA
# ==========================================
AFLUENCIA_POR_DIA = {
    "carnaval (tiempo de fiestas)": TIEMPO_ENTRE_LLEGADAS,
    "Lunes a Jueves (Normal)": (1,3),
    "Viernes (Alto)": 0.8,
    "Sábado (Muy Alto)": 0.60,
    "Domingo (Bajo)": (3,5)
}

# ==========================================
# BARRA LATERAL (SIDEBAR) INTERACTIVA
# ==========================================
st.sidebar.image("https://cdn-icons-png.flaticon.com/512/4433/4433058.png", width=100)
st.sidebar.title("⚙️ Parámetros")
st.sidebar.markdown("Modifica los valores y vuelve a ejecutar para ver distintos escenarios.")

# Selector principal de escenario
dia_seleccionado = st.sidebar.selectbox(
    "Selecciona el escenario a simular:",
    options=list(AFLUENCIA_POR_DIA.keys())
)

# ---Extraemos el tiempo del día seleccionado ---
tiempo_llegada_dia = AFLUENCIA_POR_DIA[dia_seleccionado]
st.sidebar.write(f"⏱️ **Frecuencia:** 1 auto cada {tiempo_llegada_dia} min aprox.")
st.sidebar.divider()

# MODO ALEATORIO
aleatorio = st.sidebar.checkbox("🎲 Modo aleatorio", value= True)
nueva_semilla = st.sidebar.number_input("Semilla Aleatoria (Seed)", value=RANDOM_SEED, step=1, disabled=aleatorio)
nuevo_tiempo = st.sidebar.slider("Tiempo de Simulación (min)", min_value=60, max_value=720, value=TIEMPO_SIMULACION, step=60)

st.sidebar.divider()
st.sidebar.info("💡 Cambia la 'Semilla Aleatoria' a cualquier otro número (ej. 15, 99, 1024) para generar un día de operaciones completamente diferente.")

# ==========================================
# PANEL PRINCIPAL
# ==========================================
st.title("⛽ Simulador Interactivo de Gasolinera")
st.markdown("Esta interfaz permite visualizar los resultados del modelo de colas estocástico.")

if st.button("▶️ Ejecutar Simulación", type="primary"):
    
    with st.spinner('Procesando llegadas y tiempos de servicio...'):
        if aleatorio:
            np.random.seed(None)
        else:      
            np.random.seed(nueva_semilla)
        
        env = simpy.Environment()
        estacion = Gasolinera(env)
        
        # tiempo de llegada dinámico al simulador ---
        simulador = Simulador(env, estacion, tiempo_entre_llegadas=tiempo_llegada_dia)
        
        env.process(simulador.generar_llegadas())
        env.run(until=nuevo_tiempo)
        
        df = pd.DataFrame(simulador.datos_vehiculos)
        
        # Guardado automático en PC
        #investigar el algoritmo completo xd
        carpeta_resultados = "resultados"
        os.makedirs(carpeta_resultados, exist_ok=True)
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")#no entendi esto pero en reddit decian que funciona y funciono
        nombre_archivo = f"simulacion_{timestamp}.csv"
        ruta_completa = os.path.join(carpeta_resultados, nombre_archivo)
        df.to_csv(ruta_completa, index=False)
    
    st.success(f"✅ Simulación completada. Se atendieron {len(df)} vehículos en {nuevo_tiempo} minutos.")
    
    st.subheader("📈 Indicadores Clave de Rendimiento (KPIs)")
    
    # 1. Cálculo de Utilización (Nivel de uso de los surtidores)
    # Fórmula: (Suma de tiempos de servicio) / (Cantidad de surtidores * Tiempo total simulado)
    num_surtidores = 4  
    utilizacion = (simulador.tiempo_ocupado_total / (num_surtidores * nuevo_tiempo)) * 100
    
    # 2. 5 columnas para que quepan todos los indicadores
    col1, col2, col3, col4, col5 = st.columns(5)
    
    col1.metric(label="Total Vehículos", value=len(df))
    col2.metric(label="Espera Promedio", value=f"{df['Tiempo_Espera_Fila'].mean():.2f} min")
    col3.metric(label="Utilización", value=f"{utilizacion:.1f}%") # <--- Aquí está el % de uso
    col4.metric(label="Clientes Perdidos", value=simulador.vehiculos_perdidos)
    col5.metric(label="Espera Máxima", value=f"{df['Tiempo_Espera_Fila'].max():.2f} min")

    st.divider()

    st.subheader("📊 Análisis Visual del Rendimiento")
    fig, axes = plt.subplots(1, 2, figsize=(16, 5))
    
    sns.histplot(df['Tiempo_Espera_Fila'], bins=30, kde=True, color='crimson', ax=axes[0])
    axes[0].set_title('Distribución de Tiempos de Espera')
    axes[0].set_xlabel('Minutos')
    axes[0].set_ylabel('Cantidad de Vehículos')
    
    sns.scatterplot(x='Hora_Llegada', y='Tiempo_Espera_Fila', data=df, alpha=0.5, color='darkblue', ax=axes[1])
    if len(df) > 10:
        sns.lineplot(x=df['Hora_Llegada'], y=df['Tiempo_Espera_Fila'].rolling(10).mean(), color='orange', label='Tendencia Móvil', ax=axes[1])
    axes[1].set_title('Evolución del Tiempo de Espera')
    axes[1].set_xlabel('Minuto de Simulación')
    
    st.pyplot(fig)

    st.divider()
    
    # Mostrar tabla completa y botón de descarga ---
    st.subheader("📋 Registro de Eventos Completo")
    
    # Botón para descargar el CSV directamente desde el navegador
    csv_bytes = df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="⬇️ Descargar Datos en Excel (CSV)",
        data=csv_bytes,
        file_name=nombre_archivo,
        mime='text/csv',
    )
    
    # Mostrar los vehículos en la web
    st.dataframe(df, use_container_width=True)