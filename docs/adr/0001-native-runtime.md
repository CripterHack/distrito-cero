# ADR-0001 · Conservar runtime nativo y HTML autónomo

Estado: accepted como continuidad de la restricción explícita del usuario. No es una decisión nueva de cambiar de motor.

## Contexto

La v0.19 integra numerosas capacidades y se construye en un HTML offline. Sustituir la base por un motor externo alteraría el requisito original y podría perder reglas, datos y regresiones. El objetivo artístico más alto no elimina por sí mismo esa restricción.

## Decisión

Conservar WebGL2/JS/Canvas/Web Audio nativos. Permitir herramientas de autoría y QA como dependencias de desarrollo documentadas. GLB como intercambio de assets, no obligación de añadir un cargador externo al juego. Mejorar arquitectura por fronteras y medición, no por reescritura general.

## Consecuencias

El equipo mantiene responsabilidad sobre renderer, skinning, lifecycle y herramientas. Hay más trabajo propio y se debe priorizar una vertical slice. Un modo opcional de assets separados o un motor alternativo requiere propuesta comparativa, prueba de viabilidad, presupuesto y aprobación explícita. No se presenta como ya autorizado.
