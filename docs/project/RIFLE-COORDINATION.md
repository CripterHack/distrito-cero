# Rifle · coordinación v0.20.2

Unidad #29 del PR #30. [Decisión de autoría y referencia](../adr/0003-rifle-surface-dock.md). [Estado](STATE.md). [QA general](QA.md). Los resultados remotos e integración final se registran en el PR sobre su HEAD exacto.

## Qué cambia

`weapon-handling.js` coordina ojo, prenda y marco del objeto sin duplicar el montaje. `skin-rig.js` reparte ajustes entre torso y clavículas. `equipment-geometry.js` reduce y baja la silueta de dos bloques cosméticos de culata. Las referencias de manos/miras/cargador permanecen. La anatomía del avatar no se remodela.

`rifleAim` es una presentación transitoria, inicializada al equipar. No modifica la intención de input o su contabilidad. La preparación visual y la liberación de apoyo durante recarga son continuas. La escena QA prepara también ese filtro cuando solicita una pose ya asentada, igual que preparaba `ready` y `aimWeight`. No reemplaza funciones del runtime.

El observador de rifle obtiene el triángulo de prenda de bytes y pesos reales, no de `mount.brace`. Mantiene la comparación antigua como `legacyStockError`. La galería identifica las dos referencias distintas entre familias. Los cuatro casos estáticos de rifle de la batería existente exigen criterios de pose y holgura, además de integridad de medición. Los ciclos intermedios no se confunden con apuntado ya asentado.

## Verificación local canónica

500 tests Node aprobados, cero fallidos, omitidos o cancelados. La aceptación original del PR permanece, más cinco pruebas nuevas. Se revisaron RED antes de implementar, los fallos intermedios de continuidad y sus correcciones. Las 18 combinaciones de cuello [-1,0,1], agachado [0,1] y elevación [-0.3,0,0.3] respetan ojo/apoyo/holgura. El ciclo nativo a 60 Hz comprueba cada paso de elevación, recarga y bajada contra 30 mm de desplazamiento palmar máximo, sin cambiar las pruebas anteriores de dedos.

Run gráfico `20260921T200921Z-9bf157915e17`, Chromium del sistema, Xvfb y GPU software. Longarms 24, handling 51, thumbs 15: 90 checks aprobados, sin errores/peticiones externos en sus informes. Longarms conserva 48 PNG, 72 poses numéricas y 240 muestras de ciclo. Los 48 hashes se cotejaron y se revisaron frontal, tres cuartos, agachado, elevaciones y secuencia. El commit del manifiesto local es null porque el árbol se recuperó de Pages, no se fabricó un checkout Git.

| Pose renderizada | Error ocular mm | Apoyo/prenda mm | Holgura cara mm | Holgura chaqueta mm |
| :--- | ---: | ---: | ---: | ---: |
| Neutral | <0.001 | 10.00 | 6.99 | 1.37 |
| Agachado | <0.001 | 10.00 | 1.21 | 4.61 |
| Arriba, cuello largo | <0.001 | 10.00 | -0.67 | 3.92 |
| Abajo, cuello corto | <0.001 | 28.00 | 31.81 | 1.08 |

Negativo significa penetración muestreada. -0.67 mm sigue dentro de 2 mm, no es ausencia absoluta de intersecciones. La distancia antigua en neutral es 190.98 mm y se conserva visible: no afirmar que el nuevo apoyo coincide con el antiguo pivote. Precisión aritmética del modelo no es precisión física humana. El diseño todavía es de un prototipo.

HTML: `acf4f05ccbb4a1a68008bd57876b9e7839628b4127a686715802ec47c7130be8`, 8,865,702 bytes. Fuente: `897aa398ccd20013100a81ea90e6d62018d475408cb45900c3b11970ef1b0530`. GLB: `b8536e990e251b63ba4fcd2c5fcf220d0088654c80f8a241bef594a7e110825c`. Recurso humano intacto.

## Reproducción

```sh
python3 build.py --check
node --test tests/*.test.cjs
python3 tests/release_build.test.py
python3 tools/export_contact.py
python3 tests/contact_exports.test.py
xvfb-run -a python3 -m tools.qa.run --suite longarms --suite handling --suite thumbs --headed
```

Ejecutar también el resto de Python vigente, el benchmark y las suites WebGL/HTTP de CI antes de integrar. No usar los resultados de v0.20.1 como aprobación del nuevo HTML.

## Publicación y fallos conservados

Git del laboratorio no resolvió GitHub. Se reconstruyeron las salidas en una rama temporal usando un parche sobre el padre remoto real y un manifiesto de 18 blobs esperados. El job sólo crea objetos de contenido, no modifica refs ni PRs ni publica Pages. Tiene `contents: write` limitado a esa rama/job para almacenar blobs. Los workflows normales de la aplicación conservan `contents: read`. El helper temporal no se integra al producto.

El primer intento gráfico local fue interrumpido por el presupuesto de una llamada concurrente. Se repitió en una ejecución aislada y se conserva el intento fallido. El primer build remoto auxiliar `35649868299` coincidió en todos los hashes y pasó Node, pero falló correctamente por STATE con versión vieja. Se actualizó el documento y se repitieron los mismos gates, sin omitir la prueba.

Las variantes exploratorias con módulos sustituidos y las antiguas A/B/C no son evidencia canónica y siguen descartadas. No se afirma FPS físico, validación universal de navegadores, colisión de triángulos completa o aprobación artística independiente.
