# Distrito Cero · Diseño de la primera versión

Aventura criminal original de conducción y exploración, ambientada en una ciudad ficticia de noche. No utiliza material de GTA ni librerías en tiempo de ejecución.

## Alcance
Una ciudad 3D procedural transitable, personaje en tercera persona, coches conducibles, tráfico, peatones reactivos, persecución policial, seis etapas narrativas, trabajos secundarios repetibles, escondites, talleres, mapa, guardado y controles táctiles. Estética cinematográfica, no promesa de fotorealismo AAA. Violencia no gráfica, sin instrucciones delictivas aplicables al mundo real.

## Dirección
Distrito Cero es una ciudad costera endeudada con el consorcio Vértice. El jugador es un conductor que acepta un traslado aparentemente rutinario y termina con un archivo que vincula a la empresa y a sus contactos policiales. Puede cerrar la historia o seguir recorriendo la ciudad.

## Arquitectura
JavaScript clásico modular por archivos, namespace DC, sin importaciones de red. El build concatena las fuentes en un HTML autónomo que se puede abrir como archivo local. WebGL2 renderiza mallas e instancias propias. HTML/CSS maneja HUD, menús y accesibilidad. Canvas 2D dibuja el mapa. Web Audio sintetiza efectos y paisaje sonoro tras interacción del usuario.

Simulación a pasos fijos de 1/60 s, unidades en metros, Y vertical, avance +Z, cámara independiente. Los sistemas de ciudad, simulación, render, audio e interfaz no comparten propiedad del estado. Partida versionada en localStorage, con exportación manual como respaldo. No hay servidores, analítica ni solicitudes externas.

## Verificación
Pruebas unitarias de geometría, rutas, conducción, persecución, misiones y recuperación de guardados. Navegador Chromium real para inicio, marcha a pie, entrada al coche, movimiento, pausa, diálogos, mapa, guardar/cargar y viewport móvil. Capturas obligatorias para evaluar el WebGL y la interfaz. No se afirmará validación en dispositivos no probados.
