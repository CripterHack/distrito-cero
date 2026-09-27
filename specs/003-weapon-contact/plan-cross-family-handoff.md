# Primer cruce rifle ↔ pistola: plan y registro

**Base:** master `613c16495d79e009587c56593ebe9c5a48591406`, producto 0.20.12.
**Spec:** [SPEC-003](spec.md), CONTACT-04/05, issue #6.
**Ejecución:** superpowers:executing-plans, secuencial, revisión propia.
**Objetivo:** conservar la pose realmente mostrada al cambiar rifle ↔ pistola,
libre o desde recarga, sin retrasar la selección o las acciones reales.

## Diseño y límites

Extender captureSwitch/present del módulo existente, nunca un segundo solver,
tracker o reloj. La captura cosmética conserva coordinación y dedos. El cargador
antiguo regresa a su asiento antes de mostrar un único modelo nuevo. La duración
es 0.90 s. La mano de apoyo queda libre durante la devolución cosmética.
Mantener disponibilidad, munición, trigger, longitudes, memoria de pies, cámara,
partidas y origen lógico de disparo. Otras parejas no se habilitan por analogía.

## Tareas y registro

- [x] Reproducir dos direcciones libres/en recarga en los helpers existentes.
  Cuatro regresiones fallaron contra master antes de modificar runtime.
- [x] Preservar la coordinación corporal de la pose visible. La prueba ampliada
  de las 49 matrices detectó tres fallos adicionales de pulgar; mezclar amount
  junto a los ángulos corrige el origen de esa discontinuidad.
- [x] Medir superficies seleccionadas con stock_clearance existente. Primera
  versión rechazada por −8.024 mm de chaqueta. Decisión: sumar 4 cm al mismo
  arco frontal sólo para rifle/pistola, heredable al reseleccionar, sin ampliar
  el límite de −2 mm. Siete regresiones dirigidas aprueban; mínimo −0.353 mm.
- [x] Ampliar sight sin duplicar escena/observador ni omitir los 40 checks.
  Añadir cuatro secuencias, 18 checks. El contrato de selección falló con
  40 != 58 antes de actualizar el registro; vuelve a aprobar (13 tests).
- [ ] Compilar identidad 0.20.13; verificar Node/Python completos, autoría,
  exportaciones y renderer. Conservar por separado intentos interrumpidos.
- [ ] Revisar diff/capturas/artefactos del HEAD y publicar PR acotado.
- [ ] Merge únicamente con CI verde; verificar master/Pages después y retirar
  ramas concluidas con respaldo, comparación de SHA y sin trabajo ajeno.

## Archivos e invariantes de aceptación

Runtime: src/weapon-handling.js. Regresiones: tests/cross-family-handoff.test.cjs,
exclusiones explícitas en equipment-handoff/sidearm-handoff. Renderer:
tests/sidearm_sight_browser.py; cardinalidad: tools/qa/run.py y qa_selection.
Identidad: version.json, build-info.json, index.html e índices/documentación.

Palmas iniciales <1e-5 m; matrices <1e-5; palmas/pieza <30 mm por paso preparado
de 60 Hz; targets <12 mm; longitud invariante. Recarga cancelada sin transferencia,
un solo modelo, pieza asentada antes del intercambio y restore sin cosméticos.
Las acciones reales pueden cortar presentación de inmediato: no atribuirles
suavidad visual por aprobar su prioridad lógica. Superficies muestreadas != toda
la malla; no CCD, aceptación artística, participantes o hardware inventados.
