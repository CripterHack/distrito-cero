# v0.13 · Movimiento orgánico

## Continuidad y alcance aprobado
Continuar la revisión humana de v0.12 sin sustituir campaña, mundo, ocupantes,
creador ni partidas. Refinar modelado y animación en todos los actores cercanos.
HTML nativo offline, 49 huesos y tres LOD. Referencia artística de la conversación
como objetivo, no promesa de equivalencia AAA ni una textura a pegar en el modelo.

## Diagnóstico
La marcha anterior requiere más extensión que la longitud de las piernas en
parte de su ciclo y mantiene el tobillo plano todo el tiempo. El balanceo del
cuerpo no se compensa en la solución de piernas y las poses de carrera flexionan
poco los codos. La malla de ropa presenta ondulaciones de muestreo en hombros.

## Unidades y criterios
1. Resolver piernas en espacio de modelo después del torso: pie apoyado y suela
   sin penetración, rotación talón/punta y pelvis con alcance seguro. Marcha y
   carrera con fases distintas. Probar ciclos y velocidades completos.
2. Memoria visual por actor, acotada, para apoyos en coordenadas del mundo,
   aceleración y giros. Reset ante teletransporte/cambio de partida. Ninguna
   posición de física ni guardado debe depender del renderer.
3. Brazos contralaterales, respiración torácica suave, cabeza compensada y
   distintos perfiles de dedos para reposo, conducción, carga y alcance.
4. Pulido de hombros/mangas mediante suavizado de superficie con contornos
   preservados. Acabado de tela en coordenadas ligadas al modelo y piel menos
   uniforme. Pruebas de geometría conservadas.
5. Editor: poses sentada y alcance para inspección, transiciones sin saltos y
   cadencia coherente con el juego. Mantener cancelación, comparación y guardados.
6. Regresión completa de lógica, suites de editor/partidas, campaña, render
   continuo y capturas reales pareadas. Separar pruebas controladas de rendimiento.

## Límites
No hay mocap, ropa física, escaneo de manos, ragdoll nuevo o soporte sobre
objetos móviles. Apoyos calculados para el suelo transitable plano. Las
correcciones cinemáticas no garantizan cada autointersección extrema.
