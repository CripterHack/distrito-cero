# Coordinación de familias largas Implementation Plan

> **For agentic workers:** Use superpowers:executing-plans. Continuación autónoma solicitada, revisión propia, sin atribuir subagentes.

**Goal:** Resolver CONTACT-03 en SMG, escopeta y sniper reutilizando la coordinación del rifle.

**Architecture:** Parametrizar el montaje existente por perfil y verificar por separado mira, apoyo de prenda, geometría y superficies. Conservar el comportamiento y las medidas del rifle. No crear otro solver ni corregir el cuerpo para compensar el objeto.

**Tech Stack:** JavaScript nativo, WebGL2, Node 22 y Python/Playwright sólo para desarrollo.

**Spec:** [SPEC-003](spec.md), [ADR 0003](../../docs/adr/0003-rifle-surface-dock.md).

## Global Constraints

Montaje único, recurso humano y 49 huesos inmutables, formatos persistentes sin cambios. Ojo <10 mm, apoyo <30 mm, palmas <12 mm, variación ósea <1e-6 m y penetración muestreada <=2 mm. No retirar aceptación para conseguir verde.

## Review Focus

La mira tubular de sniper no puede usar la pendiente de miras abiertas. Escopeta conserva su apoyo inferior y recarga por puerto. Cambios de equipo y primer frame deben iniciar filtro transitorio correcto. Las muestras de recarga no deben presentar saltos o duplicar munición. Las superficies deben usar geometría real, no la referencia vieja del hombro.

## Tareas

- [x] Recuperar master `6d1b756` por contenido, verificar build y reproducir tres fallos de alineación en fuentes anteriores.
- [x] Añadir parámetros de mira/culata por familia en el montaje existente. Extender filtro transitorio y coordinación sin cambiar rifle.
- [x] Verificar geometría revisada de cada culata y adaptar el auditor de superficies existente con controles negativos por familia.
- [x] Comprobar matriz central, transformaciones del actor, contactos, continuidad de recarga, aislamiento de otras familias y datos persistentes.
- [ ] Regenerar HTML/GLB, ejecutar suites completas aplicables y revisar capturas reales comparables antes/después.
- [ ] Publicar PR con documentación/evidencia, comprobar CI exacta antes del merge y verificar master/Pages por separado.

## Reversión y límites

Revertir fuentes y salidas conjuntamente, sin migración ni borrado de partidas. No cerrar #5 o #7 por una corrección de contactos. El cierre completo de #6 requiere todos sus criterios, no sólo estos tres casos.

## Verificación de la implementación local

519/519 Node aprobadas, sin tests omitidos, cancelados o todo. Diecisiete regresiones nuevas, incluidas 54 combinaciones centrales y ciclos a 60 Hz. Los tres casos iniciales fallaban por la separación ocular antes de modificar producción. 92 tests Python ejecutados y aprobados, incluidos nueve de matriz. La prueba de estructura de CI no se incluyó localmente porque el snapshot de Pages no contiene `.github`; el checkout remoto conserva y ejecuta sus seis pruebas. Autoría, build inmutable y exportación aprobados.

La primera ejecución gráfica perdió el contexto antes de capturar una pose. Se conserva como fallida. La repetición aislada `20260923T091215Z-7495c370563d` aprobó 24 checks, 48 PNG con hashes cotejados, 72 poses numéricas y 240 muestras de ciclo, sin errores/peticiones. Usa Chromium del sistema, Xvfb y GPU software, no hardware físico. Commit local null porque la copia proviene de Pages.

Se revisaron las cinco vistas estáticas y siete muestras de elevación/bajada de cada una de las tres familias. La comparación neutral usa las cámaras existentes del artefacto de #34, cuyo digest fue comprobado. El apuntado está más alto y alineado, conservando apoyo de manos y una inclinación moderada. Vestuario y objetos siguen siendo geometría de prototipo, sin aprobación artística global. Las imágenes no representan una comprobación de todos los fotogramas o autocolisión completa.

Neutral: ojo <0.001 mm numérico, apoyo/prenda 10.00 mm en las tres familias. Holgura facial mínima 6.99 mm en SMG/escopeta y 9.43 mm en sniper. Holgura de chaqueta 1.37 mm. Los límites de 2 mm de penetración muestreada y 30 mm de apoyo permanecen, no se exige ausencia matemática absoluta de intersecciones. La distancia antigua permanece visible.

Después de esa ejecución sólo se corrigieron el encabezado y `gateKind` del informe gráfico para identificar su aceptación estática ampliada. Sus aserciones, fuentes de producto y capturas no cambiaron. La CI del PR debe verificar el archivo final completo. No se hereda una aprobación remota de la ejecución local.
