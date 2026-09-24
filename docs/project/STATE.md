# Estado real del proyecto

## Versión activa del árbol: v0.20.9 · Coherencia

Canal **prototype**, fecha 2026-09-24. Identidad exacta en
[version.json](../../version.json) y [build-info.json](../../build-info.json).
Este árbol es una candidata hasta que su PR registre integración y publicación.
La base remota es `3d6722e4e20b706c6a821b1866cf62c1f133784f`, producto 0.20.8.

## Unidad actual: salida de recarga hacia otra familia

PR #44 integrado en esa base. Su Verify posterior 35965293807 y Pages
35965293263 terminaron success. La limpieza previa conservó sólo master.
No repetir el cambio libre entre familias aceptado en 0.20.8.

La candidata amplía la presentación al cambio desde una recarga activa entre
rifle, SMG, escopeta y sniper. Conserva la cancelación lógica inmediata, la pose
inicial y la transformación de la pieza extraíble visible. La salida cosmética
usa 0.60 s por su mayor recorrido; el cambio libre conserva 0.40 s.
[RELOAD-HANDOFF](RELOAD-HANDOFF.md) define el contrato, la causa, las regresiones,
la cobertura gráfica y las limitaciones. Las ejecuciones finales y la revisión
se registran en el PR de esta unidad, sin anticipar resultados de CI.

No cambia geometría, anclas originales, longitudes de huesos, física, cámara,
reglas de munición ni formatos de partidas. No añade funda, IK o reloj paralelos.
La mano de apoyo es libre durante la entrega, no un contacto digital rígido.
La pieza se asienta antes de reemplazar el único objeto mostrado. No equivale
a aprobar artísticamente todo el gesto de reinserción ni una colisión completa.

La suite gráfica existente añade dos casos de recarga y seis comprobaciones,
sin retirar sus 16 controles anteriores. El presupuesto por suite WebGL de CI
pasa de 600 a 900 s para esa cobertura adicional, no los umbrales geométricos.
Los workflows de persistencia y exportación humana conservan su alcance.

## Backlog vigente

| Issue | Pendiente real |
| :--- | :--- |
| #5 · Personaje patrón | Aceptación artística/procedencia global y materiales/UV. Matriz y exportaciones ya existen. |
| #6 · Contactos y recargas | Verificar/integrar esta salida de recarga. Después, equipos sin dock, interrupciones por acción, acciones/anatomías/locomoción combinadas y coste por actor/LOD. |
| #7 · Vertical slice | Escena/recorrido íntegro, playtests humanos y medición en equipo de referencia. |

Los observadores muestrean superficies contra volúmenes. No acreditan CCD,
colisión de toda la malla, separación positiva universal o FPS de GPU física.
No cerrar criterios globales por el éxito de una unidad acotada ni fabricar
participantes, hardware o aceptación artística.

## Integraciones que no deben repetirse

#44 (3d6722e): entrega cosmética libre entre familias, 0.20.8. #43 (be26fa0):
preparación desde ready=0. #42 (c27282f): guardia/recarga de equipo preparado.
#40 (8695273): apoyo dinámico. #41 (02e3a14): limpieza y continuidad.
#30/#34–#39: rifle, benchmark, familias, exportación/raíces/tangentes y marcha.
[EQUIPMENT-HANDOFF](EQUIPMENT-HANDOFF.md) conserva el alcance anterior;
[estado anterior completo](https://github.com/CripterHack/distrito-cero/blob/3d6722e4e20b706c6a821b1866cf62c1f133784f/docs/project/STATE.md)
conserva sus evidencias y límites. Las issues resueltas conservan su alcance.

La [política de ramas](BRANCH-CLEANUP.md) exige master como única rama permanente.
Mantener sólo trabajo activo y retirar ramas concluidas tras revisión y respaldo.
Los helpers no se integran al árbol ni a la ascendencia del producto. No se
modifican permisos del repositorio, licencia ni dependencias del juego.

Campaña, creador, catálogo, equipamiento, vehículos, policía, daños y regiones
permanecen. [Handoff](HANDOFF.md), [QA](QA.md), [recursos](ASSETS.md).
