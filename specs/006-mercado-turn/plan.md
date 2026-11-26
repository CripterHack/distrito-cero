# Integración y reversión

El punto de partida es la v0.20.29 del PR #73, commit `6c96c61`. La malla de Higgsfield, su rig y las pistas de marcha, reposo y carrera sirven de referencia. La animación de media vuelta mueve las caderas y alterna los pies. El origen del actor se mantiene en la acera.

La simulación controla la fase y la orientación lógica. El renderizador dibuja el modelo desde la orientación de entrada mientras reproduce el giro de las caderas. Al terminar entrega el movimiento al reposo o a la carrera en la nueva dirección. La misma fase sirve para las dos mallas y se conserva cuando el personaje deja de simularse por distancia.

La unidad se puede revertir recuperando el árbol del commit anterior y reconstruyendo con `python3 build.py`. El formato de las partidas sigue admitiendo los guardados anteriores.
