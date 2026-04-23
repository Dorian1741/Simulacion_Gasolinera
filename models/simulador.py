import simpy
import numpy as np
from typing import List, Dict
from models.gasolinera import Gasolinera
from config.settings import (
    PROBABILIDAD_PAGO_TARJETA, 
    TIEMPO_EXTRA_TARJETA
)

class Simulador:
    """Controla la lógica estocástica del flujo vehicular."""
    
    def __init__(self, env: simpy.Environment, gasolinera: Gasolinera, tiempo_entre_llegadas=1.5):
        self.env = env
        self.gasolinera = gasolinera
        self.tiempo_entre_llegadas = tiempo_entre_llegadas
        self.datos_vehiculos: List[Dict] = []
        self.vehiculos_atendidos = 0
        self.vehiculos_perdidos = 0  #contador para los que ven la fila larga y se van
        self.tiempo_ocupado_total =0 #contador para el tiempo que se ocupan los surtidores

    def flujo_vehiculo(self, nombre: str):
        """Ciclo de vida de un vehículo (Entidad) dentro del sistema (Nodos)."""
        hora_llegada = self.env.now

       # Si la fila es de 5 autos o más, el cliente decide irse.
        if len(self.gasolinera.surtidores.queue) >= 10:
            self.vehiculos_perdidos += 1
            return  # Sale de la simulación sin entrar a la gasolinera

        # 1. Hacer fila para un surtidor (Recurso 1)
        with self.gasolinera.surtidores.request() as req_surtidor:
            yield req_surtidor
            hora_accede_surtidor = self.env.now
            
            # 2. Esperar a que un trabajador esté libre (Recurso 2)
            with self.gasolinera.trabajadores.request() as req_trabajador:
                yield req_trabajador
                hora_inicio_servicio = self.env.now
                
                # Ejecutar tiempo de tanqueo base
                yield self.gasolinera.atender_vehiculo()
                
                # 3. Lógica Estocástica de Pagos
                if np.random.rand() < PROBABILIDAD_PAGO_TARJETA:
                    # El pago con tarjeta demora más tiempo
                    yield self.env.timeout(TIEMPO_EXTRA_TARJETA)
        
        # 4. El vehículo libera los recursos y sale del sistema
        hora_salida = self.env.now
        Tiempo_Servicio = hora_salida - hora_inicio_servicio
        self.tiempo_ocupado_total += Tiempo_Servicio
        # 5. Registro de Métricas (Data Logging)
        self.datos_vehiculos.append({
            'ID_Vehiculo': nombre,
            'Hora_Llegada': round(hora_llegada, 2),
            'Hora_Inicio_Servicio': round(hora_inicio_servicio, 2),
            'Hora_Salida': round(hora_salida, 2),
            'Tiempo_Espera_Fila': round(hora_inicio_servicio - hora_llegada, 2),
            'Tiempo_Servicio_Real': round(hora_salida - hora_inicio_servicio, 2),
            'Tiempo_Total_Sistema': round(hora_salida - hora_llegada, 2)
        })
        self.vehiculos_atendidos += 1

    def generar_llegadas(self):
        """Generador de procesos dinámico (Uniforme o Exponencial)."""
        i = 1
        while True:
            # Comprobamos si nos enviaron un rango (tupla o lista) desde app.py
            if isinstance(self.tiempo_entre_llegadas, (tuple, list)):
                tiempo_minimo = self.tiempo_entre_llegadas[0]
                tiempo_maximo = self.tiempo_entre_llegadas[1]
                # Usamos Distribución Uniforme para el rango
                tiempo_llegada_aleatorio = np.random.uniform(low=tiempo_minimo, high=tiempo_maximo)
            else:
                # Si es un solo número (Configuración Base), usamos Distribución Exponencial
                tiempo_llegada_aleatorio = np.random.exponential(scale=self.tiempo_entre_llegadas)
            
            yield self.env.timeout(tiempo_llegada_aleatorio)
            
            # Crea un nuevo vehículo y lo inyecta en el sistema
            self.env.process(self.flujo_vehiculo(f'Veh_{i}'))
            i += 1