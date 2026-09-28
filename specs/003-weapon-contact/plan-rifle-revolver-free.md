# Rifle ↔ revólver libre: plan de implementación

> Ejecutar secuencialmente con superpowers:executing-plans, regresión primero y revisión propia.

**Objetivo:** eliminar el corte inicial en ambos sentidos del intercambio libre
rifle/revólver sin alterar selección, munición, acciones reales ni partidas.
**Base:** #51, `17f6086d4ec60c764cd58be62493ae12bd0e2c68`, producto 0.20.14.
**Spec:** [SPEC-003](spec.md), CONTACT-04/05, issue #6.
**Arquitectura:** extender captureSwitch/present existentes. Reutilizar captura
visible, montaje, duración cosmética de 0.90 s, IK y observadores canónicos.
JavaScript/WebGL2 nativos; Node/Python/Playwright sólo para desarrollo.

## Contrato y límites

Given rifle o revólver disponible sin recarga activa ni devolución de pieza,
When se selecciona el otro equipo desde UI o selector congelado,
Then cambian selección/cancelaciones inmediatamente, palmas y las 49 matrices
iniciales permanecen, y un único modelo converge al montaje lógico en 0.90 s.

No habilitar recarga rifle/revólver, otras parejas o equipos pesados por analogía.
No añadir solver, tracker, reloj, geometría, huesos, APIs de caché o dependencias.
Conservar el arreglo canónico de #51 y el productor/particiones de QA de #50.
Arco frontal sólo después de medir esta pareja; tolerancia muestreada −2 mm
inalterada. Palmas/pieza <30 mm por paso preparado de 60 Hz, palmas iniciales
<1e-5 m, matrices <1e-5, targets <12 mm, longitudes invariables.

## Foco de revisión

Selector congelado desde recarga y handoff que aún devuelve la pieza deben
seguir excluidos. Reselección rápida libre preserva la pose mostrada. Disparo
y recarga nuevos siempre prevalecen. Lecturas no mutan gameplay/guardados.
Movimiento conserva memoria de pies y no añade estado persistente al rig.

## Tareas verificables

- [x] Revalidar baseline de cruces y caché. Extender casos de
  `tests/cross-family-handoff.test.cjs`, sin copiar otra matriz de escenarios.
  Observar RED para ambos sentidos libres y las guardas de selector/acciones.
- [x] Extender sólo `src/weapon-handling.js:captureSwitch`, rechazar estado de
  recarga tanto lógico como visible y medir el arco con stock_clearance existente.
  Ejecutar cruces, exclusiones, caché, longitudes, movimiento, prioridad y restore.
- [x] Añadir dos secuencias al catálogo de `tools/qa/sight_contract.py` y al mismo
  observador de `tests/sidearm_sight_browser.py`. Actualizar contratos de selección:
  40 base + 26 cruces = 66 checks, diez intercambios, 61 estados por intercambio.
  Mantener los cinco guards compartidos y 1800 s por productor. Medir duración.
- [ ] Actualizar identidad 0.20.15, build y documentación vigente. Ejecutar suite
  completa Node, Python vigente, build/authoring/export e inmutabilidad.
- [ ] Revisar renderer, capturas, diff y artefactos del HEAD exacto. Crear PR
  acotado; merge sólo con CI verde. Verificar push/Pages separadamente. Retirar
  sólo ramas concluidas, con respaldo recuperable y SHA exacto.

## Evidencia y reversión

Registrar resultados y fallos observados, sin tratar logs parciales como passes.
Revertir esta unidad y su build/versión no migra ni elimina partidas. Las cámaras,
poses y pasos preparados no prueban FPS físicos, CCD, toda la malla ni arte AAA.
#5/#6/#7 siguen abiertos por sus criterios globales. Las notas previas de candidata
se leen junto al cierre verificado del PR.

## Registro de ejecución

Baseline: 11/11. RED de ruta: cinco fallos, incluyendo saltos iniciales
572.577/195.796 mm. Primera extensión: 9/10, rechazada por chaqueta a −4.068 mm
con arco 0.08 m. Ajuste medido a 0.12 m: 10/10, mínimo combinado −0.353 mm.
Se añadieron guardas separadas para pieza pendiente y tercer modelo visible.
Contratos de selección: dos fallos observados antes de agregar las dos nuevas
secuencias; después 20/20 y nueve contratos de workflow aprobados.
Decisión: ambos sentidos libres, no recarga, para cubrir también reversión
sin extender por analogía una devolución de pieza diferente.
