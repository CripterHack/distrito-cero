# v0.18 · Manejo y contacto

Continuar el HTML v0.17, sin cambiar el inventario, catálogo, perfiles o partidas.

## Diagnóstico
Las manos resuelven posición pero no orientación. La muñeca copia el antebrazo.
La mano de apoyo se retira con un seno genérico sin coincidir con un cargador.
El arma tiene un origen global desacoplado de la respiración y de los gestos de manos.
El selector combina fondo casi opaco, panel opaco y desenfoque fuerte.

## Implementación
1. Pruebas nuevas que fallen: orientación de muñeca, alcance, agarres diferenciados,
   continuidad de recarga y retorno, muelle de retroceso y persistencia inalterada.
2. Módulo `weapon-handling.js`: perfiles de utilería, contactos orientados, pose baja,
   apuntado, retroceso amortiguado y secuencias coordinadas por familia.
3. Extender IK de brazos con orientación terminal y torsión limitada de antebrazo.
   Mantener el camino antiguo para contactos de coche y acciones sin orientación.
4. Separar piezas móviles de cargadores en geometría, dibujarlas desde el mismo
   montaje que determina las manos, y fijar el instante de origen de disparo.
5. Selector realmente translúcido con el juego debajo, congelación de la vista,
   pausa, foco encerrado, clics aislados, retorno a jugar y tamaños móviles.
6. Pruebas completas de lógica y navegador, capturas de detalle y regresión de
   biblioteca, campaña, Gauss, EMP, óptica y bucle real.

## Límites
Posturas y recargas de videojuego, no instrucción ni réplica mecánica real.
No hay colisión física individual de falanges. No se añade combate autónomo NPC.
Conservar los modelos humanos, once peinados y los 49 huesos existentes.
