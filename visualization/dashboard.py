import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

def generar_dashboard(df: pd.DataFrame):
    #Genera una visualización de las métricas obtenidas
    # Verificar si el DataFrame está vacío para evitar errores
    if df.empty:
        print("⚠️ No hay datos para mostrar en el Dashboard.")
        return

    sns.set_theme(style="whitegrid")
    fig = plt.figure(figsize=(15, 9))
    fig.suptitle('Dashboard Analítico - Operaciones en Gasolinera', fontsize=16, fontweight='bold')

    # 1. Historial de Espera
    ax1 = plt.subplot(2, 2, 1)
    sns.histplot(df['Tiempo_Espera_Fila'], bins=30, kde=True, color='crimson', ax=ax1)
    ax1.set_title('Distribución de Tiempos de Espera en Fila')
    ax1.set_xlabel('Minutos')
    ax1.set_ylabel('Frecuencia')

    # 2. Evolucion en el tiempou
    ax2 = plt.subplot(2, 2, 2)
    sns.scatterplot(x='Hora_Llegada', y='Tiempo_Espera_Fila', data=df, alpha=0.5, color='darkblue', ax=ax2)
    
    # hacer la linea de tendencia si hay suficientes datos
    if len(df) > 5:
        sns.lineplot(
            x=df['Hora_Llegada'], 
            y=df['Tiempo_Espera_Fila'].rolling(5).mean(), 
            color='orange', 
            label='Tendencia', 
            ax=ax2
        )
    ax2.set_title('Evolución del Tiempo de Espera a lo largo del día')
    ax2.set_xlabel('Minuto de Simulación')

    # 3. Densidades comparadas
    ax3 = plt.subplot(2, 2, 3)
    sns.kdeplot(df['Tiempo_Servicio_Real'], fill=True, label='T. Servicio Real', color='green', ax=ax3)
    sns.kdeplot(df['Tiempo_Total_Sistema'], fill=True, label='T. Total en Sistema', color='purple', ax=ax3)
    ax3.set_title('T. Servicio vs T. Total')
    ax3.set_xlabel('Minutos')
    ax3.legend()

    # 4. Panel de KPIs
    ax4 = plt.subplot(2, 2, 4)
    ax4.axis('off')
    kpis = (
        f"MÉTRICAS GLOBALES (KPIs)\n\n"
        f"Vehículos Atendidos:     {len(df)}\n"
        f"T. Promedio Espera:      {df['Tiempo_Espera_Fila'].mean():.2f} min\n"
        f"T. Máximo Espera:        {df['Tiempo_Espera_Fila'].max():.2f} min\n"
        f"T. Promedio en Sistema:  {df['Tiempo_Total_Sistema'].mean():.2f} min\n"
        f"T. Promedio Servicio:    {df['Tiempo_Servicio_Real'].mean():.2f} min"
    )
    ax4.text(0.1, 0.4, kpis, fontsize=13, family='monospace', 
             bbox=dict(facecolor='#f4f4f4', edgecolor='black', boxstyle='round,pad=1'))

    plt.tight_layout()
    plt.subplots_adjust(top=0.9)
    plt.show()