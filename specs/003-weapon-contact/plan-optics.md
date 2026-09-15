# Unidad CONTACT-03/05/06 · plano de codos y transición óptica

Base: `ac3cf5b`. Issue #6 permanece abierto para requisitos adicionales. No es una remodelación ni la aceptación artística de SPEC-002.

## Resultado buscado

Al subir y bajar binoculares, de pie o agachado, las manos mantienen su apoyo y los codos no invierten bruscamente su plano de flexión. El hombro y la chaqueta acompañan una trayectoria continua. El equipamiento restante conserva sus contratos.

## Secuencia ejecutada

1. Recuperar fuentes no publicadas sin borrar el trabajo anterior y comparar con master.
2. Reproducir seis fallos entre ocho nuevas pruebas sobre el código anterior.
3. Localizar la referencia de codo casi colineal con el eje hombro-muñeca y la elevación visual demasiado rápida.
4. Introducir referencias específicas en el perfil de binoculares y amortiguación visual limitada a esa familia.
5. Conservar longitudes, palmas, orientación, inventario y tiempos de armas de fuego.
6. Revisar la superficie superior de hombros/chaqueta, no sólo pivotes, y la secuencia de levantar/bajar completa en pasos de simulación.
7. Ejecutar integración WebGL, receta de mangas, build/export y regresión de datos. Publicar sólo tras CI y revisión del diff.

## Criterios de esta unidad

Ocho pruebas Node y catorce comprobaciones de navegador con contrato explícito. Codos bajo muñecas en la observación central muestreada, proyección estable en el barrido de ángulos, contacto palmar conservado, sin estiramiento óseo ni escritura de datos desde el muestreo. Recarga de fusil e inventario sin cambios. Comparar cámaras equivalentes de frente y perfil.

Los límites de desplazamiento por paso se refieren a incrementos y tiempos fijados por la prueba. No utilizarlos como definición general de realismo ni como equivalentes de FPS. El archivo de evidencia debe indicar almacenamiento fixture, reloj controlado y ausencia de GPU física.

## Fuera de alcance y reversión

Falanges contra geometría, autocolisión de brazo/ropa, ojos alineados exactamente al ocular, captura de movimiento, revisión completa de todas las armas y vertical slice. Reversión mediante commit sin migración. La receta de pesos de la entrega anterior debe seguir generando los mismos bytes.
