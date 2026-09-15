# Identidad · v0.11

## Objetivo
Continuar Constitución v0.10 sin reconstruir el juego. Crear una selección inicial con vista previa WebGL y aspecto persistente, doce partidas independientes con nombre, y un refinamiento de prendas/cabello/cuerpo visible en todos los actores.

## Contratos
JavaScript/WebGL2 nativos, un HTML offline. La apariencia pertenece a la simulación. La UI edita un borrador: cancelar no cambia la partida. Cada slot tiene id y revisión únicos, no se identifica por nombre. Importar crea una nueva partida, nunca sobreescribe otra. Datos inválidos, almacenamiento bloqueado, cuota llena o una revisión ajena deben mostrar error sin destruir el estado anterior. La importación antigua mantiene mundo, progreso, vehículo y ocupación.

## Implementación
1. [x] Tests fallidos de apariencia validada y partidas independientes.
2. [x] `appearance.js`: presets, parámetros acotados, colores, perfil por actor y extensión serializable.
3. [x] `save-store.js`: catálogo versionado, CRUD, copia, exportación, migración no destructiva, revisiones.
4. [x] Refinamiento geométrico reproducible sobre v0.10. Morfología de volumen antes del skinning, peinados y colores por actor en textura compartida. No cambiar colisionadores o IK por personalizar.
5. [x] `identity-ui.js`: editor inicial, vista previa viva, cancelar, edición desde pausa, biblioteca y mensajes de guardado.
6. [x] Aceptación en navegador: dos personajes/partidas, renombrado/copia/importación, rehidratación mediante fixture de almacenamiento explícito, rechazo de cuota/datos, entradas de teclado/táctil, fotogramas del renderer y regresión de campaña/vehículos/sectores.
7. [x] Construir, comprobar integridad, documentación con límites y entregar archivos.

## Límites explícitos
No se promete acabado AAA. Variantes de una familia de malla, no personas escaneadas independientes. Complexión ajusta volumen, no estatura ni longitud ósea para preservar los contactos. Peinados derivados del groom existente. Partidas locales, no nube. Máximo 12 slots, sujeto a cuota real. No se garantiza compartir almacenamiento entre archivos file:// distintos. Los efectos gráficos específicos del motor no equivalen a un GLB genérico.

## Ajustes de aceptación
Se intentó navegar por HTTPS local interceptado, pero el laboratorio devolvió ERR_BLOCKED_BY_ADMINISTRATOR. Se probaron lecturas/escrituras con contrato localStorage inyectado. No se afirma persistencia nativa. Se añadió una regresión de recarga tras conflicto que falló antes de corregir la rama de reanudación.
