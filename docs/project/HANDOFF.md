# Continuación vigente · candidata 0.20.13, rifle ↔ pistola

## Base integrada

Master `613c16495d79e009587c56593ebe9c5a48591406`, producto 0.20.12,
PR #48 integrado. Su verificación de push `36159916035` aprobó; sus resultados
no se atribuyen a esta candidata. La retirada anterior guardó el historial en
`pr48-backup-36160316608`. No repetir #42–#48.

## Unidad actual

[CROSS-FAMILY-HANDOFF](CROSS-FAMILY-HANDOFF.md) y el
[plan](../../specs/003-weapon-contact/plan-cross-family-handoff.md) definen el
primer cruce rifle ↔ pistola, libre y desde recarga. Se reutiliza la captura de
la pose realmente presentada, el montaje y la devolución cosmética del cargador.
La coordinación de tronco/cabeza y el amount de los dedos también se conservan.
Duración 0.90 s; arco frontal de 0.12 m sólo en esta ruta, heredable al reseleccionar.
No se cambia gameplay, piezas, huesos, cámara, disponibilidad o persistencia.

Regresiones: 64 casos dirigidos de pose/fase más selector congelado, reversión,
restore, acciones reales, marcha y exclusiones. Un test adicional reutiliza el
observador de culata sobre 152 poses de superficies seleccionadas. Sight añade
cuatro secuencias al mismo bucle de teclas/renderer: 58 checks en total.
Comprobar el PR exacto para resultados completos y capturas; este documento no
acredita por sí solo integración ni aceptación artística.

## Pendientes reales

Antes del merge: aprobar suites/artefactos del HEAD y revisión propia. Después
de integrar esta unidad, no volver a tratar rifle ↔ pistola como ruta ausente.
Los demás cruces (incluido rifle ↔ revólver), herramientas y equipos pesados
siguen pendientes. Elegir un caso reproducible antes de ampliar captureSwitch.
No generalizar el arco de 0.12 m a parejas no medidas ni añadir otro solver.

Disparo/nueva recarga deben seguir prevaleciendo de inmediato: la continuidad
cosmética de esos cortes no queda aprobada por demostrar la prioridad lógica.
#6 conserva revisión global, giros/acciones/anatomías combinadas y coste por
actor/LOD. #5 mantiene arte/procedencia/materiales/UV; #7 recorrido, cinco
participantes propuestos y equipo físico de referencia. No fabricar evidencia.

## Verificación y ramas

```sh
python3 build.py --check
node --test tests/*.test.cjs
python3 tests/release_build.test.py
python3 tests/ci_workflow.test.py
python3 tests/qa_selection.test.py
xvfb-run -a python3 -m tools.qa.run --suite sight --headed --timeout 1800 --output artifacts/cross-family-check
```

Ejecutar además [QA](QA.md), revisar capturas/artefactos del HEAD y comprobar
master/Pages separadamente. [BRANCH-CLEANUP](BRANCH-CLEANUP.md): sólo master es
permanente; conservar trabajo activo y retirar lo concluido con respaldo y SHA
exacto. Los helpers no pertenecen al árbol ni a la ascendencia del producto.
Revertir la unidad sin migrar ni borrar partidas. Revisión propia, no independiente.
