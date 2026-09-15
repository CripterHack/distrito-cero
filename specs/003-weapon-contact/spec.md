# SPEC-003 · Contactos, animación de equipo y transiciones

Estado: **proposed**. Prioridad P1. Dependencia: rig/referencias del benchmark CHAR. Relación QG-005/010. Todo el equipamiento es ficción del juego.

## Objetivo

Que las manos, brazos, torso y herramientas funcionen como un conjunto perceptible, sin manos flotantes, huesos estirados ni cambios instantáneos al usar, recargar o cancelar. Conservar tiempos, inventario y reglas de la v0.19 salvo cambios de diseño explícitamente aprobados.

## Base existente

Un montaje genera referencias de arma, palmas, muñecas, culata, cargador y boca. Hay manos diferenciadas, IK con orientación, piezas de recarga e inercia. Las pruebas actuales son de contactos muestreados, no colisión por cada falange. No partir de cero ni añadir otro montaje paralelo.

## Requisitos

**CONTACT-01:** definir proxies simples y anclas para superficies dominantes, soporte y manipulación. La muñeca se deriva del contacto de la palma; conservar simetría/equivariancia al girar al actor. En las familias y poses acordadas no hay separación visible de palma o atraviesos significativos del agarre.

**CONTACT-02:** agregar un ajuste acotado de falanges a proxies para los equipos donde sea perceptible. Mantener longitudes y rangos, impedir cierres invertidos y diferenciar pulgar/índice del resto. El runtime puede usar solver local limitado y correctivos, no exige física completa.

**CONTACT-03:** el hombro, culata, ojo y mira son restricciones cooperativas. Priorizar postura alcanzable, continuidad y campo visual. Rechazar una solución que alinee un pivote pero deforme cara/codo o penetre ampliamente el torso. Validar niveles de apuntado, agachado y giro.

**CONTACT-04:** cada secuencia tiene anticipación, contacto, acción, liberación y recuperación. Revisar aproximación/extracción/inserción/asentamiento/retorno de recarga. Cancelar o pausar desde cualquiera de esas fases conserva munición y no deja una pieza duplicada.

**CONTACT-05:** combinar locomoción, retroceso y arma sin dos fuentes de estado. Cambio de equipo y carga de partida comienzan en la misma postura que el primer frame. Reanudar el selector no restituye el trigger cancelado.

**CONTACT-06:** binoculares alcanzan una referencia ocular coherente y ambas palmas. No deformar cuello o cara para compensar un instrumento mal escalado. Cuerpo a cuerpo y lanzables tienen trayectorias propias, con feedback legible.

## Matriz y pruebas

Trece equipos, neutral/agachado, guardia/apuntado, tres elevaciones, movimiento/frenada y fases de recarga. Muestrear manos completas y no sólo muñecas cuando se evalúa contacto. Medir desplazamiento de frame a frame y revisar vídeo de juego, además de fotogramas preparados.

Mantener los casos de Gauss cancelado, EMP temporal, óptica ocluida, fuga de clics tras diálogos, cadencia y reposición. No permitir que el solver visual toque salud, munición o alertas policiales.

## Archivos afectados

`weapon-handling.js`, `skin-rig.js`, `equipment-geometry.js`, `equipment-renderer.js`, `equipment-simulation.js` sólo si hay una transición de estado requerida, `equipment-ui.js` para feedback/inspección, y tests de manejo/superficie. Los proxies son datos de juego, no especificaciones de fabricación.

## No objetivos

Balística real, ingeniería de armamento, disparos desde vehículos, NPCs con combate autónomo o recargas mecánicas detalladas de todas las familias en un mismo PR. Esas capacidades necesitarían specs aparte.

## Gate

Evidencia antes/después bajo los mismos parámetros, no nuevas poses favorecedoras aisladas. La aceptación exige continuidad visual y regresión de datos, presupuesto de solver por actor/LOD y documentación de las limitaciones restantes.
