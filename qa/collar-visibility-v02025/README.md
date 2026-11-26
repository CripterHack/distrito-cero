# Visibilidad de la deuda del cuello · v0.20.25

Diagnóstico offline de los datos completos preservados del PR #65. No cambia
el runtime ni genera capturas nuevas. [Resumen, IDs y procedencia](summary.json).

Las 190 combinaciones que perdieron cobertura normal fuera del núcleo LOD0/1
corresponden a 54 triángulos fuente. En las cámaras de primer plano conservadas,
76 centros de píxel posteriores y 8 de perfil cambian de chaqueta a piel. Son
combinaciones condición-píxel muestreadas, no el área total del defecto. El borde
lateral del escote conserva una deuda visible al forzar LOD2 a 0,85 m.

Un ejemplo verificable es `neutral/idle`, ancla `9216`: píxel posterior
**(263,524)** y perfil **(406,533)**. Los rayos atraviesan chaqueta antes de la
política y alcanzan primero piel después. Los PNG originales y sus valores RGB
están identificados por hash en el resumen. No es el parche anterior de
(267,547), ya corregido. [Antes/después posterior](../collar-lod-v02025/README.md).

Las 492 sondas UNKNOWN corresponden a 44 triángulos en el borde inferior de la
piel. La ausencia de impacto de su rayo normal no demuestra un agujero. Sus
rayos de cámara alcanzan piel o chaqueta; algunos alcanzan otra zona de la piel.
Se conservan como desconocidas. En las tres cámaras de cuerpo completo guardadas
—posterior, frontal y perfil a 3,3 m— la chaqueta ocluye las 682 combinaciones.
Ninguna de esas direcciones muestreadas termina en fondo entre ambas superficies;
esto no certifica cobertura global ni incluye cabello o escenario.

## Escala y límites

La proyección exacta de cada triángulo fuente y el rayo del centro de píxel se
conservan separadamente. Los escenarios analíticos de juego usan FOV `π·0,36`,
las escalas de resolución y el umbral de retención LOD2 reales. La selección LOD
usa distancia al jugador, no a la cámara. Las cifras de píxeles por metro se
rotulan **estimaciones transversales en eje**, nunca cotas globales: perspectiva,
inclinación, desplazamiento local y encuadre importan. El modo foto puede cambiar
la distancia; no se extrapola visibilidad de calle desde este primer plano.

## Reproducción

Requiere NumPy y el paquete de evidencia completo de v0.20.25. Las rutas bajo
`artifacts/` son datos preservados del paquete, no dependencias del juego.
El comando rechaza hashes distintos, cohortes alteradas y salidas existentes.

```sh
python3 tools/qa/project_collar_visibility.py \
  --before-report artifacts/collar-lod/before-final/report.json \
  --after-report artifacts/collar-lod/after-final/report.json \
  --clearance-report artifacts/collar-lod/skin-clearance-after-final.json \
  --coverage-report artifacts/collar-lod/fullsource-coverage-final.json \
  --output artifacts/collar-followup/reproduction.json
python3 tests/collar_visibility.test.py
```

Cinco pruebas analíticas aprobadas: profundidad proyectiva, punto detrás de la
cámara, diferencia entre rayo continuo y centro de píxel, sonda ausente con
prenda presente y cambio del orden de superficies. La primera corrida detectó
dos errores al normalizar coordenadas enteras; se corrigieron usando Float64.
No es aceptación artística, prueba de colisión completa, nueva geometría ni FPS.
