# Handoff · siguiente unidad de trabajo

## Base para retomar

Leer STATE y AGENTS. El código de juego vigente sigue siendo v0.19, importado en `23f9e9d031c7a0ad270cd74ce0805ea0dfc385da`. La rama de publicación añade documentación y CI, no un cambio del gameplay. Confirmar el HEAD remoto y los checks antes de crear otra rama.

## Primera tarea recomendada: DC-001

**Objetivo:** convertir las pruebas del laboratorio en un harness de repositorio portable, sin alterar aserciones del juego y sin escribir resultados actuales encima de evidencia histórica.

Leer [spec 001](../../specs/001-reliability/spec.md), [plan](../../specs/001-reliability/plan.md) y [tareas](../../specs/001-reliability/tasks.md). Crear `feat/001-native-qa` desde master actualizado. Preparar un fixture que falle si se admite un JSON viejo como resultado nuevo. Implementar directorio de artefactos por run y selección explícita de navegador/display/origen.

**No empezar por:** remodelar nuevamente el cuello, sustituir WebGL2 por otro motor, borrar baselines, sumar tests antiguos incompatibles o ampliar el mundo.

## Frente artístico paralelo admisible

Preparar DC-005 / spec002: cámaras, luces, matriz de poses y ficha de proporciones. Es una definición del benchmark, no autorización para reemplazar la anatomía aprobada a partir de una única imagen. No tocar simultáneamente el rig y los contactos de otra rama sin contrato.

## Verificación mínima al empezar

```sh
python3 build.py
node --test tests/*.test.cjs
python3 tools/export_contact.py
python3 tests/contact_exports.test.py
```

Comparar salidas con Git y consultar la CI. Los informes viejos no se consideran una nueva ejecución. Los scripts de auditoría antiguos no conocen la raíz nueva del repositorio.

## Al terminar cada unidad

Registrar commit/PR, spec ID, comandos/códigos, SHA del HTML, entorno, evidencia nueva, riesgos restantes y paso siguiente. Actualizar el estado de las tareas sólo cuando haya resultados. Documentar si una validación sigue siendo fixture y no persistencia nativa.
