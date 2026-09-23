# Distrito Cero · instrucciones de continuidad

## Orden de lectura

1. `docs/START-HERE.md`, `docs/project/STATE.md` y `docs/project/HANDOFF.md`.
2. `.specify/memory/constitution.md` y `docs/spec-game-development.md`.
3. La especificación de la tarea y sus `plan.md` / `tasks.md`, cuando existan.
4. Los módulos reales afectados y sus pruebas. No inferir implementación de una captura o de un resumen de chat.

## Versión activa

Consultar `version.json`, `build-info.json` y `docs/project/RELEASES.md`. Producto y esquemas de datos tienen versiones independientes. Antes de publicar ejecutar `python3 build.py --check` y `python3 tests/release_build.test.py`. No reescribir manifiestos históricos al actualizar la versión visual.

## Fuente de verdad

La base importada es v0.19, commit `23f9e9d031c7a0ad270cd74ce0805ea0dfc385da`. El HTML debe ser reconstruible desde `src/` mediante `build.py`. La rama principal se llama **master**. Conservar el orden explícito de fuentes del empaquetador: varias capas extienden y reasignan las clases públicas del namespace `DC`.

`SOURCE-MANIFEST.json`, `qa/v019/release-report.json` y los scripts de auditoría históricos describen entregas anteriores. No actualizarlos para fabricar evidencia nueva. El auditor antiguo deduce su base de la raíz de Git y no debe usarse como auditor universal del repositorio recién importado. Leer `docs/project/QA.md`.

## Flujo de trabajo

Trabajar desde una rama nueva y actualizada, por ejemplo `feat/001-native-qa`, `fix/003-palm-contact` o `docs/quality-gates`. No hacer force-push, borrar ramas ajenas o reescribir el historial sin autorización. Un PR debe tener una especificación/issue, cambios acotados, pruebas, evidencia y reversión. Actualizar `HANDOFF.md` al cerrar cada unidad verificable.

Antes de una modificación de comportamiento: reproducir el problema, escribir una prueba que falle, implementar el mínimo y repetir la regresión afectada. La calidad visual exige capturas y movimiento en el renderer real, no sólo aserciones numéricas. No sustituir pruebas fallidas por umbrales más laxos sin justificar el cambio del requisito.

## Ciclo de vida de ramas y contexto

`master` es la única rama permanente. Mantener ramas sólo para trabajo activo y
crear cada unidad desde el master remoto actualizado. Tras un merge verificado,
retirar la rama con la autorización aplicable y comprobando el SHA exacto. Antes
de retirar ramas sin ascendencia directa, cotejar árboles/patches, PRs y trabajo
único; conservar respaldo recuperable. No borrar ramas protegidas o de PRs abiertos
ni usar un force-push para ocultar divergencias. Los helpers temporales no se
integran al producto y deben retirarse al terminar.

[Registro de limpieza y restauración](docs/project/BRANCH-CLEANUP.md). Leer el
HANDOFF vigente antes de explorar historia. Un plan o un PR antiguo ya integrado
no es una tarea pendiente. No cerrar issues globales ni recrear matrices de QA
para reducir el ruido documental.

## Invariantes

- Runtime nativo sin librerías externas, descargas obligatorias ni telemetría remota. Herramientas de autoría/QA pueden tener dependencias documentadas.
- Mantener el HTML autónomo. Un modo adicional con assets separados requiere ADR y aprobación, no una migración silenciosa de motor.
- Unidades en metros, Y vertical y avance +Z. Esqueleto actual de 49 huesos, DQ y LOD compartidos. Cambiar contratos sólo con versión, migración y pruebas.
- No duplicar campaña, creador, selector, catálogo, ocupantes ni generador. Extender el sistema existente o migrarlo por etapas comprobables.
- Partidas: IDs independientes de nombres, doce espacios sujetos a cuota, validación antes de escribir, exportación, cancelación segura, sin reinicios silenciosos.
- La simulación es propietaria de dinero, salud, munición, misiones y entidades. El renderer no modifica ese estado para corregir una imagen.
- No convertir escenarios preparados ni tiempo de animación controlado en supuesta evidencia de FPS o de una partida completa.
- No atribuir al runtime escaneos, mocap, físicas, expresiones o funciones sólo planificadas.
- No incorporar assets sin procedencia, permiso y huella. No publicar llaves, tokens, URLs firmadas activas, partidas de usuarios ni fuentes tipográficas.

## Comandos mínimos

```sh
python3 build.py
node --test tests/*.test.cjs
python3 tools/export_contact.py
python3 tests/contact_exports.test.py
```

Ejecutar además las pruebas de navegador y geometría afectadas conforme a `docs/project/QA.md`. Los tests de versiones viejas pueden exigir geometrías ya sustituidas: registrar qué se conserva, qué queda histórico y qué especificación reemplaza cada criterio. No declarar que todos los tests Python históricos forman una suite vigente.

## Trabajo autónomo permitido y límites

Se pueden implementar tareas listas con pruebas, documentación y PRs pequeños. No adquirir assets, contratar servicios, desplegar públicamente, cambiar la licencia, modificar permisos del repositorio, eliminar respaldos ni integrar SDKs remotos sin aprobación específica. No iniciar varias modificaciones concurrentes del mismo rig o renderer sin un contrato compartido.

Al terminar, informar commit/PR, archivos cambiados, comandos ejecutados, resultado, límites y siguiente paso concreto. Si faltan herramientas o falla un permiso, conservar un parche reproducible y registrar el bloqueo. No anunciar éxito por haber programado una tarea futura.
