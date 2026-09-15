# Distrito Cero v0.17 · Arsenal

## Alcance
Continuación de Rasgos v0.16 en el mismo HTML y motor nativos. Incorporar un selector de equipamiento usable por ratón, teclado y táctil. Catálogo de catorce opciones: manos libres, bastón, hoja, pistola, revólver, subfusil, escopeta, fusil, precisión, lanzador, granada, Gauss, EMP y binoculares. Todos disponibles para experimentar, con munición limitada y reabastecimiento explícito en puntos seguros. Parámetros puramente ficticios para juego, no simulación ni diseño de armas reales.

## Diseño elegido
Extender los sistemas de simulación y representación, no crear otro juego/visor ni reemplazar el personaje. Catálogo y rayos 3D puros en `equipment.js`, temporizadores/impactos/persistencia en `equipment-simulation.js`, geometrías en `equipment-geometry.js`, poses/cámara en `equipment-renderer.js` y DOM/entradas en `equipment-ui.js`. Guardado compatible: nueva sección opcional equipment, valores iniciales para partidas antiguas y validación antes de mutar estado. No tocar el esquema del catálogo de partidas.

## Contrato
* TAB abre el arsenal sin desplazar el foco del navegador durante juego. Cerrar confirma sólo la selección explícita.
* Ratón izquierdo o J usa el equipo, botón derecho sostenido o Z activa apuntado. Mirar mediante arrastre derecho en modo armado. L recarga, B alterna binoculares, rueda cambia su zoom, H marca destino observado. R conserva rendición y T radio.
* Movimiento original, uso de objetos y acceso a coche prevalecen. Equipamiento se recoge visualmente mientras se conduce, carga objetos o accede. No se dispara desde el coche en esta versión.
* Rayos 3D ordenados por distancia. Edificios opacos detienen disparos y medición. Comprobar también recorrido desde boca del arma para no disparar a través de esquinas. Gauss atraviesa un máximo de tres objetivos blandos/vehículos, nunca edificios.
* Gauss: mantener para cargar y soltar para disparar. Cambio de equipo, pausa, pérdida de foco o interacción cancelan carga sin disparo. Cargar no consume celdas hasta disparar.
* EMP: pulso localizado que interrumpe temporalmente propulsión, sirenas y luminarias visibles. Conserva daño y alerta. Coches en marcha frenan gradualmente, no desaparecen ni cambian de propietario.
* Lanzador y granada usan proyectiles, colisión barrida, explosión de radio finito y oclusión por edificios. Daño a vehículos/objetos, respuesta no gráfica de personajes y riesgo propio.
* Binoculares: 2x/4x/8x/12x, vista óptica, distancia y GPS sólo de lo visible. Sin munición ni daño.
* Reacciones NPC no gráficas y temporales, sin nuevo sistema de combate armado policial. Sin promesa de física balística realista ni hiperrealismo.

## Secuencia verificable
1. Congelar base y ejecutar regresión Node.
2. Tests fallidos: catálogo, munición/carga, geometría rayos, efectos, guardado compatible.
3. Implementar simulación y verificar regresiones.
4. Integrar modelos, poses con objetivos de manos y cámara óptica sin modificar mallas humanas.
5. Integrar selector accesible y controles, recuperación tras cancelar entradas.
6. Pruebas de navegador reales, disparos/EMP/zoom/partidas, móvil y bucle continuo.
7. Revisar capturas, corregir defectos, documentar alcance y empaquetar con hashes.

## Presupuestos
Hasta 24 proyectiles, 96 efectos activos compartidos entre trazos/pulsos/explosiones y 32 marcadores de impacto temporales. Recursos de armas compartidos. Texturas humanas y geometría de v0.16 sin cambios. Valores y temporizadores validados y acotados. Estado de munición/selección se guarda por partida. No se guardan rayos, partículas ni proyectiles en vuelo.
