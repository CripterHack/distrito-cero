# Continuación vigente · 0.20.18 y aceptación estricta de QA

## Producto integrado, no repetir

[PR #55](https://github.com/CripterHack/distrito-cero/pull/55) está integrado en
**cf7327750edd0c50dfda5f227345d80ac7ca74fb**, árbol
**56929d6acd902b1ce288f7929e24f357edb05006**, producto **0.20.18**.
SMG ↔ revólver desde recarga activa, selector congelado y pieza retornando
conserva pose y pieza. Mantiene el rechazo del tercer objeto mostrado, retorno
cosmético de 0.90 s, arco medido de 0.12 m y acciones reales inmediatas.
No tratar ese cambio ni #53/#54, caché #51 o particiones #50 como ausentes.

## Cierre posterior a #55 comprobado

Verify **36451732544** aprobó siete jobs sobre el merge real. Se descargaron
sus seis artefactos y se verificaron hash de ZIP, commit, HTML y resultados:
**305 WebGL y 80 HTTP**, sin sumar informes duplicados. Sight conserva **94
nombres únicos**, dieciséis secuencias de 61 estados y cinco guardas por
partición, contadas sólo una vez. Sus 144 capturas de intercambio tienen
hash verificado. Revisadas las 18 capturas nuevas de recarga SMG/revólver.

Ambas rutas nuevas tienen salto inicial de palmas, pieza y matrices **cero**.
Máximos palmares por paso preparado: **8.066/17.390 mm**. Los productores
sight tardaron **1295.000 / 1438.198 / 1177.252 s**, bajo 1800 s cada uno.
No son FPS, hardware físico, toda la malla/CCD ni reinserción mecánica certificada.

Benchmark **36451732780**: 36 checks. Exportación **36451732722**: original
0 errores/1 advertencia conocida y derivado 0 errores/0 advertencias, fuentes
por hash e informes completos contrastados. Pages **36451731177** publicó el
HTML exacto **cc313e22ad17b155f403c4ade3b965892631a07d2658a1dd9e6afb8555fd3cbb**,
8,878,050 bytes. Se verificaron artefacto y despliegue, no HTTP público.
La copia de la base repitió **623/623 Node** y build --check.

## Unidad de QA de este árbol

[Plan REL-01/02](../../specs/001-reliability/plan-sight-evidence-gates.md).
El runner anterior podía aceptar exit 0 con `comparisonOnly: true` o con
checks aprobados y guardas fallidas/ausentes. La regresión con procesos reales
reprodujo 30 fallos de aserción en diez métodos. El arreglo rechaza informes
comparativos y valida partición, checks con nombres únicos y las cinco guardas
exactas, compartidas con el productor. Base las exige dentro de checks.

Los informes reales de #55 pasan el contrato reforzado. Esto no convierte los
fixtures de regresión en pruebas del juego ni invalida su evidencia verificada.
No cambia runtime, HTML, versión, cobertura, tolerancias, CI ni presupuesto.
Consultar el PR vinculado en [issue #6](https://github.com/CripterHack/distrito-cero/issues/6)
para la integración y CI de esta unidad de QA, distintas del cierre de #55.

```sh
python3 build.py --check
python3 tests/qa_runner.test.py
python3 tests/qa_selection.test.py
python3 tests/ci_workflow.test.py
node --test --test-concurrency=4 tests/*.test.cjs
xvfb-run -a python3 -m tools.qa.run --suite sight --headed --timeout 1800
```

## Siguiente trabajo real

Cerrar primero el gate de QA del HEAD exacto. Después reproducir un cruce aún
excluido, por ejemplo pistola/SMG, con los observadores existentes antes de
habilitarlo. No extrapolar el arco de otra pareja. Quedan herramientas/pesados,
cortes visuales prioritarios, giros/anatomías y coste por actor/LOD en #6.
#5 mantiene arte/procedencia/materiales/UV y #7 recorrido, personas y hardware.
No cerrar issues globales por conteos ni presentar revisión propia como independiente.

## Recuperación

No reintentar la limpieza bloqueada ni borrar ramas. Los helpers anteriores
no pertenecen al producto. La unidad de QA se revierte sin migrar partidas ni
cambiar el juego. Una restauración local desde archivos es un snapshot con
historial sintético: sólo su árbol es comparable; no es historial Git remoto.
