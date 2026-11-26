# Integración y reversión

El punto de partida es el commit `74c6df7` del PR #74. Para que el último pie llegue adelantado, la simulación y los clips deben compartir la misma fase de marcha y el mismo avance longitudinal. El clip se reproduce una vez. La simulación mantiene el origen del actor disponible para navegación y para otros sistemas del juego. El segundo pie llega a la pose inicial de reposo mientras el primero sostiene el cuerpo.

El cambio se puede revertir recuperando el árbol de v0.20.30 y reconstruyendo con `python3 build.py`. Los ensayos usan partidas y escenas aisladas.
