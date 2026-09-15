# SPEC-001 · QA portable, datos nativos y recuperación gráfica

Estado: **ready por etapas**. Prioridad P0. Requisitos QG-001/002/003/012. Dependencia: importación de v0.19. Los archivos nuevos citados a continuación son objetivos por implementar, no funciones ya presentes.

## Problema

Las pruebas actuales están ligadas a un navegador en `/usr/bin/chromium`, DISPLAY y carpetas de la versión de autoría. El almacenamiento se sustituye en pruebas, y la raíz Git anterior no corresponde al repositorio publicado. Los incidentes de pérdida de WebGL no cuentan aún con un lifecycle de recuperación general.

## Historias y aceptación

**REL-01 · Reproducción portable.** Dado un checkout limpio, cuando se seleccionan navegador, origen y salida mediante configuración, el runner ejecuta las aserciones actuales, escribe un manifiesto nuevo y devuelve error ante cualquier proceso fallido. No exige una ruta de usuario ni deduce baseline del primer commit.

**REL-02 · Evidencia fresca.** Dado un informe viejo que dice todo aprobado, cuando no se ejecuta su suite en el run actual, el gate lo rechaza. Un cambio de HTML durante el run también lo invalida. El resultado registra almacenamiento fixture/nativo y reloj controlado/continuo.

**REL-03 · Persistencia real.** Dado un origen HTTP local y un perfil de navegador aislado pero nativo, cuando se crean dos partidas con nombres, personaje, semilla e inventario distintos y se cierra y reabre el contexto, ambas reaparecen sin contaminación. Renombrar y borrar una no altera la otra ni resucita el espacio borrado.

**REL-04 · Conflictos.** Dadas dos pestañas con la misma revisión, cuando una guarda y la otra intenta escribir, la segunda no destruye silenciosamente la revisión nueva. Puede recargar o guardar una copia con un ID distinto. El test usa dos páginas reales, no sólo llamadas de la clase de almacenamiento.

**REL-05 · Cuota/datos inválidos.** Una escritura o importación rechazada deja intacta la versión anterior y ofrece exportación. No se borra automáticamente un catálogo corrupto. Probar la lógica existente con fallos inyectados y separar ese caso del navegador nativo.

**REL-06 · Contexto gráfico.** Dado el juego activo con una partida válida, cuando se provoca una pérdida de contexto soportada por el entorno de prueba, el dibujo se detiene y la UI comunica el estado. Restaurar reconstruye recursos sin duplicar simulación, inputs, actores o autoguardado. Si no es restaurable, ofrecer reanudación/exportación segura, no reiniciar silenciosamente.

**REL-07 · Recursos.** Un recorrido repetido de sectores mantiene los límites declarados y descarta GPU buffers fuera del vecindario. La memoria no crece por cada apertura de creador/selector. Medir, no inferir del HTML.

## Contratos

El modo fixture sigue disponible para regresión determinista. El modo nativo no instala un sustituto de localStorage. No modificar formato de partidas sólo para adaptar el harness. La recuperación gráfica es propietaria de recursos visuales, no de salud, munición o misiones.

## No objetivos

Nube, protección distribuida perfecta entre procesos, garantía universal para file://, portabilidad completa de todos los navegadores en un PR, nuevo motor o benchmark físico dentro de SwiftShader.

## Entrega

Runner/configuración documentados, suites nativas, lifecycle separado, regresión vigente, artefactos de CI y evidencia de limitaciones. REL-01/02 se entregan primero, REL-03/04 después y REL-06 en PR independiente. No marcar toda la spec aceptada por completar sólo el runner.
