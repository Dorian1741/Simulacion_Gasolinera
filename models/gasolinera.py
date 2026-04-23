import simpy
import numpy as np
from config.settings import NUM_SURTIDORES, NUM_TRABAJADORES, TIEMPO_SERVICIO_MEDIA, TIEMPO_SERVICIO_STD

class Gasolinera:
    """Representa los recursos físicos y humanos de la estación."""
    def __init__(self, env: simpy.Environment):
        self.env = env
        self.surtidores = simpy.Resource(env, capacity=NUM_SURTIDORES)
        self.trabajadores = simpy.Resource(env, capacity=NUM_TRABAJADORES)

    def atender_vehiculo(self) -> simpy.events.Timeout:
        """Simula el tiempo de tanqueo y pago."""
        tiempo_servicio = max(1.0, np.random.normal(loc=TIEMPO_SERVICIO_MEDIA, scale=TIEMPO_SERVICIO_STD))
        return self.env.timeout(tiempo_servicio)