# Handoff · 0.20.3 / exportación humana en revisión

## Punto exacto para retomar

Master `4c615090d7395bda048bee0d1ee2070702833808` contiene el PR #35. La coordinación de SMG, escopeta y sniper ya se integró; no repetir el arreglo del rifle #29 ni el del benchmark #33. Verify 35843734280 y benchmark 35843734295 aprobaron antes del merge. La CI del push y Pages se comprueban por separado.

El trabajo actual está en PR #36, rama `feat/005-current-human-export`, continuación de #5 / CHAR-06. Leer [CURRENT-HUMAN-EXPORT](CURRENT-HUMAN-EXPORT.md) y [plan](../../specs/002-character-benchmark/plan-current-export.md). Se genera un GLB de autoría actual sin sustituir los históricos ni modificar el juego.

El primer validador oficial, run 35846902847, falló con 13 nodos hoja inválidos y 15,921 advertencias. Dos regresiones reprodujeron children vacío y 15,906 índices no nulos con peso cero. La normalización corrige sólo la salida portable. Nueve tests Python comprueban el aislamiento, el formato y la preservación de todos los demás buffers. La CI del nuevo HEAD y el reporte Khronos completo deben revisarse antes de integrar #36. Una prueba unitaria no acredita esa validación.

El manifiesto registra fuentes y versiones reales de herramientas. Una comparación entre plataformas produjo diferencias en muestras de animación; no afirmar identidad binaria entre toolchains distintos. La regresión compara contra los bytes exactos de la receta de la misma ejecución. DQ/LBS, materiales/tangentes y jerarquía siguen con límites de portabilidad explícitos. No se concede una licencia nueva al contenido propio.

## Lo comprobado en PR #35

519 Node y 98 Python en la reconstrucción remota exacta. Artefactos del HEAD b7362fb: 205 checks WebGL, 80 HTTP nativos y 36 de benchmark, todos aprobados y con digests cotejados. Se revisaron las 48 capturas longarms, incluidas 20 vistas estáticas y 28 muestras de ciclo. La regresión local adicional aprobó 220 checks de arsenal, catálogo, campaña y continuidad. Estos fixtures no constituyen una vertical slice sin teletransportes ni rendimiento de GPU física.

[ADR 0004](../adr/0004-longarm-family-docks.md) documenta la migración cosmética y la referencia de prenda por familia. [Plan](../../specs/003-weapon-contact/plan-longarm-families.md). Se conservan rifle, anatomía, manos, reglas, partidas y workflows normales. La rama auxiliar retiró su workflow en bedd63d; nunca entró al producto. El primer intento gráfico perdió contexto y permanece fallido, separado de la repetición aislada aprobada.

## Criterios todavía pendientes

#5 requiere revisión artística registrada de proporciones/materiales/variantes y procedencia editable. #6 conserva la revisión global de superficies y acciones, vídeo y coste por actor/LOD. #7 requiere implementar y verificar la escena/recorrido íntegro, alternativas, playtest humano y presupuesto sobre equipo físico identificado. No cerrar esos alcances por el número de tests ni fabricar participantes, vídeos o FPS.

## Integración e historia

Ramas por unidad, pruebas aplicables completas, revisión del diff y artefactos del HEAD exacto, merge autorizado sólo con sus gates aprobados. Comprobar el push a master y Pages por separado. No forzar push, borrar datos del sitio o reescribir evidencia histórica.

[Estado](STATE.md), [QA](QA.md), [rifle #29](RIFLE-COORDINATION.md), [benchmark #33](BENCHMARK-AIM.md), [cancelación](../../specs/003-weapon-contact/plan-reload-cancellation.md), [HTTP nativo](../../specs/003-weapon-contact/plan-native-reload.md), [auditor #27](../../specs/003-weapon-contact/plan-longarm-audit.md), [variantes rechazadas](../../specs/003-weapon-contact/stock-surface-rejection.md), [gates CI](CI-GATES.md). El [handoff anterior completo](https://github.com/CripterHack/distrito-cero/blob/4c615090d7395bda048bee0d1ee2070702833808/docs/project/HANDOFF.md) conserva sus entradas históricas sin repetir instrucciones obsoletas como trabajo actual.

Git del laboratorio no resuelve GitHub. Las copias locales son snapshots y pueden conservar commit=null. Publicar sólo sobre padres remotos reales con contenido verificado. Revisión propia, no independiente.
