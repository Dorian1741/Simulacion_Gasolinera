import simpy
import numpy as np
import pandas as pd
from config.settings import RANDOM_SEED, TIEMPO_SIMULACION
from models.gasolinera import Gasolinera
from models.simulador import Simulador
from visualization.dashboard import generar_dashboard

def main():
    print("Inicializando entorno de simulación modular...")
    np.random.seed(RANDOM_SEED) #usar semillas de generacion de pseudoaleatorios como en minecraft
    
    # Iniciar Entorno y Clases
    env = simpy.Environment()
    estacion = Gasolinera(env)
    simulador = Simulador(env, estacion)
    
    # Lanzar la simulación
    print(f"⏳ Ejecutando simulación por {TIEMPO_SIMULACION} minutos...")
    env.process(simulador.generar_llegadas())
    env.run(until=TIEMPO_SIMULACION)
    
    print(f"✅ Simulación completada. Procesando métricas...")
    
    # Consolidar datos
    df_resultados = pd.DataFrame(simulador.datos_vehiculos)
    df_resultados.to_csv('resultados_simulacion.csv', index=False)
    print("📊 Datos exportados exitosamente a 'resultados_simulacion.csv'. Generando Dashboard...")
    
    # Mostrar Gráficos
    generar_dashboard(df_resultados)

if __name__ == "__main__":
    main()