# Spec-game-development · método del proyecto

## Qué significa aquí

En este repositorio, **spec-game-development** nombra la adaptación local de desarrollo guiado por especificaciones a un videojuego sistémico. No se identifica como una certificación externa ni como un paquete instalado. Toma la separación intención → especificación → plan → tareas → implementación de [GitHub Spec Kit](https://github.github.com/spec-kit/) y añade dirección artística, pruebas de juego, presupuestos de rendimiento y evidencia del motor real.

El objetivo no es producir documentos por volumen. Es evitar los ciclos de correcciones visuales aisladas que cambian una proporción, rompen otra y carecen de una referencia estable. Un requisito conecta una necesidad del jugador con una decisión, un cambio y una prueba.

## Unidad de trabajo

Cada capacidad pertenece a `specs/NNN-nombre/`. Su especificación define el problema, usuarios, resultado observable, no objetivos, restricciones y escenarios de aceptación. `plan.md` define los módulos, contratos, alternativas rechazadas, fases y reversión. `tasks.md` enumera unidades verificables. `evidence.md` registra comandos, hashes, capturas, entorno y límites reales. No declarar terminada una capacidad sólo por crear estos archivos.

Las especificaciones complejas pueden separar investigación, implementación y evaluación. No escribir código hipotético enorme dentro del documento: explicar la interfaz y el comportamiento suficiente para que una implementación distinta también pueda verificarse.

## Flujo obligatorio

1. **Inspeccionar.** Leer el estado, la fuente y la evidencia actual. Reproducir el defecto cuando exista. Anotar el hash del juego y el entorno.
2. **Especificar.** Definir qué debe percibir el jugador y qué queda fuera. Convertir objetivos como «realista» en escenas, poses, escalas y criterios comparables.
3. **Aclarar decisiones.** Resolver cambios de motor, arte de pago, licencia, servicios y targets físicos. Las decisiones artísticas inciertas se registran como propuestas, no como verdades anatómicas universales.
4. **Planificar.** Seleccionar el menor cambio compatible con el contrato. Identificar assets, rig, shader, simulación, UI y guardado afectados. Definir rollback.
5. **Dividir.** Tareas pequeñas por resultado, no por cien archivos simultáneos. Cada una produce código, prueba y evidencia revisable.
6. **Implementar con regresión.** Escribir primero el caso que revela el fallo. Cambiar una causa a la vez, ejecutar las pruebas y revisar escenas reales. No aumentar un umbral para esconder un problema.
7. **Validar el juego.** Lógica, geometría, integración visual, inputs reales, continuidad temporal, memoria y partidas anteriores. Añadir playtest humano para ritmo, legibilidad y control.
8. **Revisar y publicar.** PR con relación requisito → archivo → prueba → evidencia. Integrar sólo el alcance verificado. Actualizar estado y handoff.

## Estados y puertas

`proposed` → `ready` → `in-progress` → `verification` → `accepted`. `blocked` requiere motivo y acción concreta. `superseded` requiere enlace al reemplazo. Una propuesta puede estar documentada y no autorizada para compras o cambios de producto.

**Definition of Ready:** intención clara, dependencia satisfecha, contrato conocido, criterio verificable, coste y riesgo acotados. **Definition of Done:** implementación y salidas coherentes, pruebas aplicables, revisión visual cuando corresponda, compatibilidad y reversión, documentación actualizada y límites explícitos.

## Evidencia que sí cuenta

Una captura muestra un instante, no continuidad. Un vídeo generado o un render de Blender puede servir como referencia artística, nunca como prueba del runtime. Un clip con tiempo controlado no demuestra FPS. Una prueba con localStorage sustituido no demuestra persistencia nativa. Una consulta a coordenadas remotas no equivale a conducir toda la distancia.

Los informes nuevos deben incluir commit, SHA-256 del HTML, versiones de herramientas, resolución, calidad, semilla, cámara/pose y modo de almacenamiento. Mantener separados los resultados heredados y los actuales. Si falta hardware, registrar «pendiente» en lugar de extrapolar resultados de SwiftShader.

## Trabajo multiagente

Un agente coordinador asigna una especificación y archivos de propiedad a cada rama. Separar anatomía, contactos, QA y documentación cuando sean independientes. Rig, renderer y esquema de guardado requieren contratos antes del paralelismo. Ningún agente elimina cambios de otro sin revisión.

El revisor comprueba requisitos y regresiones, no sólo estilo de código. La integración usa master actualizado y commits no destructivos. Si no hay subagentes disponibles, ejecutar las tareas secuencialmente y registrar una revisión local sin presentarla como revisión independiente.

## Plantilla y ejemplo

Usar [plantilla de feature](../specs/templates/feature.md). El primer trabajo listo es [001 · Fiabilidad](../specs/001-reliability/spec.md), seguido por el [benchmark de personajes](../specs/002-character-benchmark/spec.md). La [constitución](../.specify/memory/constitution.md) conserva las restricciones del producto.

No se han instalado comandos slash de Spec Kit, ni se asume que existen en cualquier agente. Los Markdown son utilizables directamente y pueden integrarse en una herramienta después, sin convertirse en dependencia del juego.
