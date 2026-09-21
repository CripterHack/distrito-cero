# #29 · Coordinación del rifle neutral

## Estado actualizado · v0.20.2

Corrección implementada sobre `0f01f574ef23817afd407e0cf2ed90fc7bd49540`, dentro del PR #30. Resultado local completo: 500/500 Node, 90 checks gráficos canónicos y build reproducible. El PR determina CI remota, revisión e integración finales. No heredar aprobaciones del HEAD anterior.

## Contrato revisado de manera explícita

[ADR 0003](../../docs/adr/0003-rifle-surface-dock.md) sustituye el desplazamiento de `upperArmR` por el triángulo 8898 de chaqueta y el punto más cercano en la cara posterior de culata. Conserva la distancia antigua en el informe, todos los umbrales y la comparación histórica. Dos cuboides cosméticos del rifle cambian de silueta, no los agarres/miras/cargador ni el modelo humano. Esto reemplaza la restricción provisional de geometría inmutable del primer plan, no se presenta como si ese contrato nunca hubiera cambiado.

## Ejecución

- [x] Reproducir el fallo ocular original y la referencia de prenda ausente.
- [x] Conservar los diez controles de rechazo sobre superficie real y las variantes anteriores descartadas.
- [x] Coordinar cabeza, torso, clavículas y montaje único, con alcance de ambas manos y anatomía intactos.
- [x] Ajustar la silueta de la culata y verificar sus proxies contra triángulos dibujados.
- [x] Suavizar el ciclo nativo de elevación, recarga y bajada. No demorar reglas o contabilización de disparos.
- [x] Pasar la aceptación original y 18 combinaciones centrales sin elevar tolerancias.
- [x] Regenerar HTML/GLB, actualizar identidad 0.20.2 y revisar capturas canónicas sin sustituciones de módulos.
- [ ] Registrar en #30 el éxito de CI completa del HEAD exacto, la revisión y el merge autorizado.
- [ ] Comprobar por separado CI de master y Pages después del merge.

Los dos últimos pasos no se marcan como hechos anticipadamente. Sus registros de ejecución quedan en el PR para no confundir evidencia de otra rama o de un intento previo.

## Evidencia, límites y reversión

[Mediciones y reproducción](../../docs/project/RIFLE-COORDINATION.md). Mantener #5/#6/#7 abiertas. La evaluación es propia, no artística independiente. El muestreo de vértices no equivale a colisión completa. No hay rendimiento físico acreditado ni validación de todas las anatomías.

Las recetas A/B y C siguen descartadas y documentadas en [stock-surface-rejection](stock-surface-rejection.md), revisiones anteriores del PR y el historial de este plan. Los runs fallidos de los HEAD `f2dc994`, `a106263` y `0f01f57` no se reetiquetan. Revertir las fuentes con sus salidas generadas, sin migración ni borrado de partidas.
