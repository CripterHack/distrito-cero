# Salida de recarga entre pistola y revólver

**Base:** master `5c0248f6674abfb39a304a20d407f886fa3a7957`, producto 0.20.11.
**Spec:** [SPEC-003](spec.md), CONTACT-04/05, issue #6.
**Ejecución:** superpowers:executing-plans, secuencial, revisión propia.

## Contrato y diseño

Extender el montaje de #47 a ambos sentidos durante recarga activa. Conservar
selección/cancelación inmediatas, disponibilidad, munición, prioridad de acciones,
longitudes, geometría y partidas. Capturar la pose que realmente presenta la UI.
El cargador de pistola reutiliza el retorno cosmético existente. El cilindro del
revólver conserva su geometría/transformación actual, sin fabricar una apertura o
reinserción mecánica. Mostrar un solo modelo. No añadir solver, tracker o reloj.

Aceptar salto inicial <1e-5 m, paso palmar <30 mm a 60 Hz, contactos a los targets
<12 mm y longitudes invariantes. El cargador anterior debe estar asentado antes
del cambio de modelo. Una mano libre durante la transición no es un contacto
físico de reinserción. No se certifican CCD, toda la malla, arte o GPU física.

## Tareas verificables

1. Añadir regresiones para dos direcciones × siete fases, pieza visible, selector,
   reselección, restore y prioridad real. Observar RED antes de cambiar runtime.
2. Reutilizar captureSwitch/present y duración de sidearms. Ajustar sólo si la
   medición lo exige. Reemplazar explícitamente la antigua exclusión de recarga
   por el contrato nuevo, sin omitir la prueba o aumentar umbrales.
3. Reutilizar la suite sight y sus cámaras, conservar 32 checks anteriores,
   añadir dos secuencias de recarga con tecla real y referencia antes/inicio/final.
   Separar sight del resto de gráficos sólo si el presupuesto de CI lo requiere,
   con prueba de unión íntegra sin solapamiento. No aumentar permisos de producto.
4. Regenerar versión/build, ejecutar Node y Python completos y navegador afectado.
   Actualizar STATE/HANDOFF/QA y registrar fallos, límites y evidencia nueva.
5. Publicar PR desde esta base, revisar HEAD/artefactos y merge sólo con CI verde.
   Verificar master/Pages y retirar únicamente ramas concluidas con respaldo.

## Registro

La base tiene el mismo árbol aprobado de #47: 590 Node y 106 Python comprobados
en esta sesión. PR #47 integrado con revisión 5312681262. Se conserva su timeout
local histórico; la CI remota exacta aprobó 243 WebGL y 80 HTTP.

Cuatro tests observaron RED. El cambio de dos expresiones en captureSwitch lleva
a GREEN la matriz dirigida. La exclusión de recarga se sustituye por el contrato
explícito. Tres configuraciones × siete fases × dos direcciones: 42 casos con
72 pasos cada uno. Los contratos de workflow observaron tres fallos por shard
ausente y sight falló por 32 != 40 antes del cambio; ambos vuelven a aprobar.
Decisión: el cilindro sigue como parte rígida body pues no existe canal animado
cylinder en la geometría actual. No atribuirle reinserción física.
