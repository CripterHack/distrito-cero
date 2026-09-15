# Verificación de Distrito Cero v0.3

Fecha: 8 de septiembre de 2026.

## Resultados

| Grupo | Evidencia | Resultado |
| --- | --- | --- |
| Lógica general y regresión policial | `qa/v03/unit-report.txt` | 70 pruebas, 0 fallidas |
| Sintaxis | `node --check src/*.js` por archivo | Siete fuentes JS verificadas |
| Navegador, regresión del juego | `qa/browser-report.json` | 52 comprobaciones correctas |
| Navegador, interacción policial y tacto | `qa/v03/police-browser-report.json` | 72 comprobaciones correctas |
| Render continuo general | `qa/continuous-render-report.json` | Entrada, movimiento y render real, sin sustitución |
| Render continuo durante contacto policial | `qa/v03/police-continuous-report.json` | Maniobra real, sin sustituir simulación, render o almacenamiento |
| Solicitudes externas del juego | Ambos informes de navegador | 0 |

## Regresión reproducida antes de la corrección

La primera batería policial, sobre v0.2, falló en 21 de 24 casos. `qa/v03/police-red.txt` conserva esa ejecución. Reprodujo reducción artificial de velocidad durante roces, penalización por alcance policial, captura a pie en movimiento y captura sin visibilidad. Los casos correspondientes a las interacciones nuevas también fallaban al no existir esas funciones todavía.

Tras la implementación pasan esos casos, los 38 casos previos y ocho comprobaciones policiales adicionales. No se presentan todos los casos iniciales como fallos de funcionalidad anterior: varios son requisitos nuevos.

## Cobertura de integración

La batería general verifica entrada en la ciudad, movimiento, conducción, frenado y salida, pausa, mapa, GPS, diálogo, seis etapas narrativas, un desenlace, encargos, guardar y continuar, modo foto y controles táctiles. Los dos desenlaces y la validación de partidas también se prueban en lógica.

La batería policial coloca vehículos en situaciones controladas, pero ejecuta la simulación real y usa eventos reales de teclado, ratón y tacto. Verifica reversa tras contacto frontal, aceleración tras alcance, carrera a pie, captura estando detenido, rendición completa y cancelada, reanudación del movimiento, pausa, pérdida de visibilidad y recuperación del contacto. El botón de rendición y cinco controles principales tienen comprobaciones de posición y recepción de eventos en 390 × 844 y 844 × 390.

La escena de dos patrullas en extremos opuestos y la variación de pasos de 30, 60 y 120 Hz están cubiertas en lógica. Son situaciones de prueba, no una garantía de escapar de cualquier bloqueo posible.

## Entorno y límites

Chromium 144 en Linux, Xvfb y WebGL2 por software con SwiftShader. Fue necesario iniciar Xvfb para que el contexto WebGL2 se creara en este entorno. No se modificaron las políticas de navegación del navegador.

El HTML se carga con `page.set_content` porque la navegación está restringida. Las dos baterías amplias usan almacenamiento en memoria **solo en el código de prueba**. No se incorpora al HTML distribuido. Se comprueba serialización, escritura y restauración del contrato, no persistencia nativa al cerrar y reabrir un navegador físico.

En las baterías amplias se suspende exclusivamente el renderizador entre fotogramas de captura para que SwiftShader no altere las esperas de interacción. La simulación y la interfaz siguen ejecutándose. Cada captura invoca el renderizador WebGL original y comprueba `gl.getError()`. Los dos scripts de render continuo no sustituyen render, simulación ni almacenamiento y sirven como comprobación independiente.

No se ha probado Safari, un iPhone físico, mandos, extensiones ni sesiones prolongadas en distintos equipos. Las pruebas automatizadas no son una certificación completa de accesibilidad, una campaña recorrida manualmente calle por calle ni un benchmark de rendimiento de una GPU física.

## Capturas actuales

`qa/v03/11-police-breakaway.png` muestra la maniobra después de un contacto.

`qa/v03/12-police-capture.png` muestra el medidor de captura y rendición.

`qa/v03/13-police-search.png` y `14-police-search-map.png` muestran la búsqueda y el último contacto.

`qa/v03/15-police-mobile-390.png` y `15-police-mobile-844.png` muestran el HUD policial en ambos formatos móviles.

`qa/v03/16-police-live.png` muestra una escena del ensayo con render continuo.

## Reproducir

```bash
python build.py
node --test tests/*.test.cjs
xvfb-run -a python tests/browser_qa.py
xvfb-run -a python tests/police_browser.py
xvfb-run -a python tests/continuous_render.py
xvfb-run -a python tests/police_continuous.py
```

Python estándar y Node integrado bastan para empaquetar y ejecutar la lógica. Las herramientas de navegador son dependencias exclusivamente de desarrollo. Para jugar basta el HTML y un navegador con WebGL2.
