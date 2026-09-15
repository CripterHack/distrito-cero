# Distrito Cero v0.5 · Verificación

Fecha: 9 de septiembre de 2026. Base: v0.4. Entrega: HTML autónomo y fuentes con modelos nativos opcionales en GLB.

## Resultados ejecutados sobre v0.5

| Grupo | Resultado | Evidencia |
| :--- | :--- | :--- |
| Lógica y regresión | 104 de 104 pruebas | `qa/v05/logic.txt` |
| Personaje, sombreadores, árbol, foto e interfaces móviles | 72 de 72 comprobaciones | `qa/v05/realism-browser.json` |
| Renderer y simulación continuos | 14 de 14 comprobaciones | `qa/v05/continuous-realism-report.json` |
| Campaña y controles heredados ejecutados en la versión nueva | 52 de 52 comprobaciones | `qa/v05/legacy/browser-report.json` |
| Estructura, buffers, pesos y animaciones de los dos GLB nativos | 2 de 2 pruebas | `qa/v05/native-export-tests.txt` |

Total de comprobaciones de navegador: **138**. No se sumaron informes históricos de v0.4. En estas tres ejecuciones finales no hubo errores JavaScript/WebGL registrados ni solicitudes de recursos externos.

Los GLB también se leyeron mediante `trimesh`, como parser independiente: 11 mallas y 36,210 triángulos únicos del personaje; 8 mallas compartidas y 6,018 triángulos únicos del kit de coche (la escena reutiliza las ruedas). Las cajas envolventes son finitas y de escala métrica. Esto no verifica la reproducción de animación en un editor externo. Evidencia: `qa/v05/independent-glb-parse.json`.

## Qué se comprobó

La lógica incluye los 96 tests originales y ocho nuevos de la paleta de huesos y las mallas: identidad en reposo, transformaciones finitas para distintas poses, cambios reales entre caminar y sujetar, rechazo de pesos/normales/índices de hueso inválidos, geometría determinista con presupuesto, orientación del cristal derecho y curvatura del techo.

La integración renderizó fotogramas WebGL reales de reposo, andar, correr, agacharse, saltar, sujetar, coche limpio/dañado y árbol en pie/caído. Comprobó que los datos de huesos se usan tanto en la pasada de sombra como en color. Se revisaron manualmente capturas del juego, incluidas primer plano, coche, marcha, follaje y modo foto móvil. La revisión visual identifica un resultado más detallado pero aún estilizado, no un resultado hiperrealista.

La prueba continua no reemplazó el renderer, el almacenamiento ni los métodos de simulación. Se utilizó el teclado real del navegador para retroceder y girar durante contacto policial, acelerar contra una luminaria, caminar y saltar. La lámpara se rompió y dejó de iluminar, el coche recibió daño frontal, el jugador pudo escapar del contacto, el personaje animó su paleta y aterrizó. Se prepararon posiciones iniciales para que las situaciones fueran repetibles.

La prueba heredada volvió a recorrer campaña, movimiento, conducción, mapa, pausa, respaldo JSON e interfaces táctiles. No es una prueba de todas las combinaciones emergentes de mundo abierto ni valida todos los desenlaces imaginables.

## Entorno y alcance

Chromium instalado en el contenedor, Xvfb y ANGLE SwiftShader. La primera ejecución headless no obtuvo contexto WebGL2, por lo que las comprobaciones finales utilizaron Chromium con ventana bajo Xvfb. La simulación continua se ejecutó en calidad económica a 640 × 400. La captura final de esa suite fue a 1000 × 650 en calidad equilibrada. No se infiere rendimiento de hardware ni se promete un FPS.

La suite de fotogramas usa una instancia aislada de almacenamiento en memoria, carga el HTML con `set_content` y congela renderer/cámara entre fotogramas reales para controlar el tiempo de la escena. Los eventos de teclado y táctiles se envían al DOM, y la lógica de simulación no se sustituye. La suite continua compensa este alcance con el bucle real activo.

Vistas móviles comprobadas: 390 × 844 y 844 × 390. Son viewports y eventos táctiles emulados, no teléfonos físicos. Safari, Firefox, iPhone físico, GPU real, permisos de descargas reales y persistencia nativa `file://` no fueron probados. Por eso se mantiene la instrucción de exportar/importar partida al cambiar de HTML.

## Incidencias y límites registrados

1. Se corrigió una normal de cristal lateral orientada hacia dentro, el techo inicialmente plano, la proporción excesiva de cabeza/hombros y la uniformidad de emisión en ventanas. Las capturas finales corresponden a las correcciones.
2. Una ejecución temprana del nuevo test de integración agotó el tiempo durante la captura del árbol. La cámara seguía amortiguándose mientras se revisaban poses y algunos encuadres se alejaban. Se aisló la cámara, se ajustó la calidad de esa prueba y se ejecutó de nuevo la suite completa: 72 comprobaciones finales. No se contabilizó el pase incompleto.
3. La prueba continua termina únicamente el proceso Chromium que ella misma inició para evitar el bloqueo de cierre observado en SwiftShader. Las comprobaciones y la captura se completan antes de terminar ese proceso.
4. Las escenas de autoría de Higgsfield finalizaron y tienen revisiones exactas. La descarga de sus nuevos GLB al contenedor no se completó, así que el runtime usa reconstrucción nativa documentada. No hay bytes de una transferencia truncada en los recursos. La revisión visual que sustenta esta entrega es la del renderer local. La revisión completa de las imágenes remotas de autoría no se completó en el cliente.
5. No se ejecutó el validador oficial Khronos sobre los GLB nativos. Se comprobaron estructura de GLB, rangos de buffers, recuentos, índices, normales unitarias, suma de pesos, rango de huesos, tiempos crecientes, cuaterniones unitarios, bucles cerrados y lectura con `trimesh`. No se afirma compatibilidad certificada con todos los importadores.

## Lo que no cambia

Se comprobó mediante comparación binaria con el commit base que `core.js`, `world.js`, `police.js`, `simulation.js`, `dynamics.js`, `interactions.js` y `character-motion.js` permanecen intactos. No se modificaron los costes, reglas policiales, misiones o persistencia. El nuevo poseador y renderer consumen ese estado sin convertirse en fuente de verdad de la simulación.

## Reproducir

```bash
python build.py
node --test tests/*.test.cjs
python tests/native_exports.test.py
DISPLAY=:99 python tests/realism_browser.py
DISPLAY=:99 python tests/continuous_realism.py
DISPLAY=:99 python tests/legacy_v05.py
```

Playwright, Chromium y un display son herramientas de prueba, nunca requisitos del juego. Para regenerar los GLB se usa `python tools/export_native_glb.py`; NumPy/SciPy y Node son dependencias sólo de construcción. No hay bibliotecas externas de runtime.
