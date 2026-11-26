# Integración y reversión

La simulación asigna la ruta al puesto existente `ped:38`. La distancia recorrida determina la fase de zancada. El renderizador usa los materiales de este personaje y las transformaciones de los 49 huesos del GLB; la paleta lineal reproduce sus pesos de autoría. El reparto modular comparte la infraestructura de dibujo y usa su propia deformación con cuaterniones duales. La sombra se proyecta sobre la acera a 0,145 m. Las mallas, poses y texturas viajan dentro del HTML y se reconstruyen después de perder el contexto WebGL.

La reversión consiste en recuperar el árbol de la candidata v0.20.28 y reconstruir el HTML. El esquema de partida sigue siendo el mismo.
