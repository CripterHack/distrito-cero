# Unidad #23: cancelación de recargas por fase y familia

Base: `3629d1876e160bd32c9e94eec70ce947043e7c66`, PR #22, producto v0.20.1. Alcance parcial de SPEC-003 / #6. Especificación de aceptación en la issue #23.

## Objetivo y arquitectura

Ampliar la cobertura del contrato existente, no crear otro sistema de acciones. Usar las fuentes nativas y el catálogo de `DC.Equipment`, avanzar `equipmentStep` a 1/60 y observar `WeaponHandling.mount`, el serializador y `EquipmentApp.closeArsenal`. La instrumentación de eventos envuelve `emit` sin sustituir su comportamiento.

`cancelEquipment` cancela inputs y conserva la recarga pendiente. `equipWeapon` con otro ID cancela inputs y descarta el temporizador. Confundir estos contratos produciría una prueba incorrecta. `restore` conserva datos persistentes y descarta acciones transitorias. La UI sigue siendo propietaria de cancelar inputs al reanudar.

## Matriz

Diez equipos con recarga: pistola, revólver, subfusil, escopeta, fusil, precisión, lanzador, granada, Gauss y EMP. La enumeración se contrasta con el catálogo para evitar que un filtro vacío o una familia futura quede omitida silenciosamente.

Siete puntos por equipo: inicio, 14%, 30%, 52%, 72%, 90% y 99.9%. Se alcanza cada punto mediante el temporizador real, sin asignar directamente la pose. Es un muestreo explícito de fases e intervalos, no todos los fotogramas o eventos posibles. Incluye reservas abundantes y reservas insuficientes para llenar cargadores grandes.

Cuatro contratos por equipo:

1. Cancelar inputs dos veces no cambia munición o temporizador. Completar transfiere exactamente una vez. Mantener fire bloqueado no dispara ni carga Gauss. Liberar y pulsar nuevamente permite una acción legítima.
2. Cambiar a manos libres, binoculares u otro equipo descarta la recarga. La pieza extraíble vuelve a reposo. No hay transferencias diferidas al regresar al equipo original.
3. Serializar y restaurar conserva munición, sin restaurar recarga, trigger, carga ni pieza separada. Tras la cancelación de inputs de reanudación no aparece una acción antigua.
4. El adaptador del selector restaura sólo la mezcla visual permitida al retornar a play, nunca trigger/carga. El retorno a pause no restaura apuntado. El temporizador no se altera por ejecutar ese adaptador.

490 combinaciones de punto/equipo/ruta, agrupadas en 40 tests, más un test del catálogo y un control negativo. El control negativo elimina deliberadamente el bloqueo en una instancia de prueba del fusil y exige que el oráculo detecte disparo al terminar la recarga. Nunca modifica archivos del runtime.

## Implementación y verificación

- Crear `tests/reload-cancellation.test.cjs` siguiendo el cargador de módulos de `contact-transitions.test.cjs`, sin dependencias nuevas.
- Ejecutar el control negativo y la matriz. Si una aserción revela un defecto del juego, conservar el caso y diagnosticar su causa antes de cambiar producción. No aumentar tolerancias ni modificar contratos para obtener verde.
- Ejecutar `node --test tests/*.test.cjs` y la CI existente del HEAD exacto. Las suites gráficas y HTTP no se eliminan ni sustituyen.
- Revisar cambios y actualizar handoff/estado. Integrar únicamente con checks aplicables aprobados. Registrar los resultados definitivos y SHAs en el PR y la issue, no inventar un commit que se cite a sí mismo.

No se cambia `src/`, `version.json`, `index.html`, `build-info.json`, assets, permisos o publicación cuando la unidad sólo añade pruebas. Revertir el commit de pruebas/documentación es suficiente para rollback.

## Límites de evidencia

El setMode mínimo del test reproduce el contrato del adaptador, no el reloj pausado real, Pointer Lock o eventos físicos del navegador. La restauración es un roundtrip del serializador, no persistencia HTTP ni acceso a partidas del usuario. No mide continuidad temporal de todas las poses, colisiones de superficies, coste GPU o aceptación artística. Los ensayos gráficos y nativos existentes siguen siendo puertas independientes.

PR #22 conserva su verificación previa a merge sobre `87e3dd39b94066ece9003e310e8291966c722e20`. #21 requiere comprobación independiente de publicación. Esta matriz no cierra #5/#6/#7 ni el trabajo pendiente de postura y mira de armas largas.
