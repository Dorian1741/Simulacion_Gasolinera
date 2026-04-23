# ==========================================
# CONFIGURACIÓN GENERAL DEL SISTEMA
# ==========================================
RANDOM_SEED = 42
TIEMPO_SIMULACION = 60 * 12  # 12 horas en minutos (720 min)

# ==========================================
# RECURSOS (Infraestructura y Personal)
# ==========================================
NUM_SURTIDORES = 4
NUM_TRABAJADORES = 2

# ==========================================
# VARIABLES ESTOCÁSTICAS (Teoría de Colas)
# ==========================================
# Tasa de Llegadas (Lambda - λ): Promedio de vehículos por minuto.
# Según los estudios de demanda en hora pico, digamos 1 vehículo cada 1.2 minutos.
TIEMPO_ENTRE_LLEGADAS = 1.2  

# Tiempos de Servicio (Mu - μ): Depende del tipo de tanqueo y pago.
# Usaremos una distribución Normal para modelar este comportamiento empírico.
TIEMPO_SERVICIO_MEDIA = 3.5  # Minutos promedio en tanquear y pagar
TIEMPO_SERVICIO_STD = 1.2    # Desviación estándar (variabilidad humana)

# Penalización por tipo de pago (Simulando retrasos por tarjetas o facturación)
PROBABILIDAD_PAGO_TARJETA = 0.40  # 40% pagan con tarjeta
TIEMPO_EXTRA_TARJETA = 1.5        # Minutos extra por procesar la tarjeta