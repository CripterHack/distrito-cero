# Constitución de Distrito Cero

Versión documental 1.0. Base de producto v0.19. Alcance: decisiones de continuidad y contrato de calidad del proyecto. No es un estándar externo ni instala Spec Kit.

## I. Intención jugable antes que expansión

La experiencia combina historia dirigida, conducción, exploración y consecuencias sistémicas legibles. Un sistema se incorpora por el valor que aporta al jugador, no por aumentar una lista de funcionalidades. Se prioriza una muestra jugable de alta calidad antes de multiplicar regiones o equipamiento.

## II. Continuidad y propiedad del estado

Conservar campaña, guardados, creador, ocupación, arsenal y territorio. La simulación posee el estado persistente. Presentación, audio, cámara y UI lo consumen mediante contratos explícitos. Las mejoras visuales no pueden modificar reglas o datos silenciosamente.

## III. Runtime y distribución

JavaScript/WebGL2/Canvas/Web Audio nativos y entrega HTML autónoma. Cero librerías externas y solicitudes de red obligatorias durante la partida. Las herramientas de desarrollo no son dependencias del juego. Cualquier cambio de motor, formato de entrega o servicio remoto necesita una decisión arquitectónica aprobada.

## IV. Especificación comprobable

Toda feature tiene identificador, intención, no objetivos, criterios Given/When/Then, contratos, presupuesto y evidencia exigida. El recorrido es especificar, planificar, dividir tareas, implementar, verificar, revisar y registrar. Las pruebas visuales y playtests complementan, no reemplazan, las pruebas de lógica.

## V. Integridad de datos

Nunca sobrescribir por nombre, borrar un catálogo corrupto automáticamente o confundir una sesión volátil con un guardado satisfactorio. Las migraciones son explícitas, probadas, idempotentes y reversibles mediante exportación. No se añaden servicios de nube por defecto.

## VI. Calidad artística y rendimiento independientes

Un recuento de pruebas, polígonos o huesos no demuestra realismo. Se requieren proporciones coherentes, siluetas, superficies, contactos y continuidad temporal en cámaras de juego. Cada mejora declara su coste de CPU/GPU/memoria. Los objetivos de frame time son hipótesis hasta medirlos en hardware identificado.

## VII. Reproducibilidad y procedencia

Conservar fuentes de autoría disponibles, conversiones, versiones de herramientas, licencias y hashes. Un GLB portable puede diferir del renderer DQ y debe indicarse. No distribuir assets de permiso incierto ni atribuir como propia la autoría de terceros. No fabricar historial o resultados de QA.

## VIII. Seguridad, accesibilidad y autonomía responsable

Inputs sin acciones accidentales detrás de diálogos, límites de recursos, importación no ejecutable, recuperación segura y controles accesibles. Sin telemetría remota no consentida ni gasto real automático. La violencia pertenece al mundo ficticio del juego y no se transforma en instrucciones prácticas del mundo real.

## IX. Control de cambios

Ramas por unidad de trabajo desde master, commits legibles, PR con evidencias y rollback. Ninguna reescritura masiva sin demostrar su beneficio frente a una migración incremental. Ninguna subida de umbrales sólo para ocultar una regresión. Las excepciones necesitan un ADR, responsable y condición de revisión.

## X. Definición de terminado

Requisito implementado, pruebas aplicables aprobadas, antes/después comparable cuando proceda, partida anterior conservada, presupuesto medido o declarado pendiente, documentación y handoff actualizados. Un plan escrito no equivale a una feature terminada. Una CI aprobada no equivale a calidad AAA.
