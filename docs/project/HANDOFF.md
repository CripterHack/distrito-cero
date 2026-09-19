# Handoff · v0.20.1 / verificación de recargas

Base de esta unidad: `3629d1876e160bd32c9e94eec70ce947043e7c66`, merge del PR #22. Producto **0.20.1 · Coherencia**, prototype. Leer [STATE](STATE.md), [alineación de armas cortas](SIDEARM-SIGHT.md) y [plan de la matriz de recargas](../../specs/003-weapon-contact/plan-reload-cancellation.md).

## Integración realizada

PR #22 quedó integrado por squash sobre master. HEAD revisado antes del merge: `87e3dd39b94066ece9003e310e8291966c722e20`. La CI `35388020900` aprobó 429 pruebas Node, 181 comprobaciones gráficas seleccionadas, guardados nativos y build/exportación. El benchmark `35388020903` también aprobó. No confundir la selección gráfica con `--suite all` ni estos resultados con una ejecución posterior de master.

La alineación de pistola/revólver utiliza el ojo articulado. Se conserva la prioridad del alcance, contactos y retroceso sobre referencia quieta. La transición de equipamiento incluye el primer fotograma: la regresión de revisión pasó de 76.70 a 26.21 mm máximos por paso neutral de 1/60. Preservar los cuatro tests de inicio de equipamiento y los 26 checks de sight.

HTML canónico del producto: `4a78bcca34cd40b2c406b0642362f30a6b71303d8a4a6ace659e0ba4afc9918d`, 8,862,957 bytes. Fuente: `dfb16e65c1a64d991f2bedfbecf0892d69c8b2110e4be1403e31d7af739c4fdb`. Los resultados de publicación se registran en #21. No cerrarla sólo porque #22 esté merged: comprobar CI de master y Pages. No borrar datos del sitio al actualizar.

## Unidad #23

`tests/reload-cancellation.test.cjs` amplía la cobertura de cancelación, cambio de equipo, serialización y cierre del selector sobre diez equipos recargables y siete puntos del temporizador real. La matriz contiene 490 combinaciones, agrupadas en 40 tests, más catálogo y control negativo. No inferir que estas pruebas pasan por estar escritas: comprobar la CI del HEAD exacto del PR de #23.

Contrato importante: `cancelEquipment` cancela inputs y conserva una recarga. `equipWeapon` con otro ID descarta esa recarga sin transferir munición. La restauración descarta acciones transitorias, mientras la UI cancela inputs al reanudar. El control negativo retira el bloqueo sólo en una instancia de test y exige detectar el disparo indebido. No modifica el runtime.

La unidad sólo añade pruebas/documentación. No cambiar versión, bundle, malla, pesos, huesos o reglas para aparentar otra entrega. Si una prueba revela un defecto, conservar la reproducción, revisar la causa y abrir el cambio de comportamiento explícito. No aumentar umbrales para ocultarlo.

## Puertas de integración

```sh
node --test tests/reload-cancellation.test.cjs
node --test tests/*.test.cjs
python3 tools/refine_thenar.py --check
python3 tools/rebind_garment.py --check
python3 build.py --check
python3 tests/release_build.test.py
python3 tests/release_checkout.test.py
python3 -m tools.qa.run --suite all
python3 -m tools.qa.run --suite all --origin http
```

Exigir la CI aplicable del HEAD exacto y revisar diff antes del merge autorizado. Documentar las suites realmente ejecutadas, los SHAs y las limitaciones. Después verificar el push de master. Conservar runs rojos históricos y fallos encontrados, no rebajar gates. Esta sesión utiliza GitHub Actions para la ejecución integral, no presenta una comprobación sintáctica local como prueba completa.

## Límites y continuidad

El adaptador UI del test no demuestra el reloj pausado real, Pointer Lock o inputs físicos del navegador. El roundtrip del serializador no reemplaza persistencia HTTP. La matriz por fases no representa cada fotograma, una secuencia gráfica completa o rendimiento de GPU física.

#5/#6/#7 permanecen abiertos por sus criterios generales. #5 conserva aprobación artística, materiales, pelo y variantes. #6 conserva coordinación de culata/hombro/mira en armas largas y revisión visual de transiciones/otras superficies. #7 requiere escena, recorrido íntegro y playtest. No deformar cara o alargar brazos para forzar contacto. Las capturas preparadas no completan la vertical slice ni acreditan FPS físicos.

Registrar el resultado definitivo de #23 en su issue y PR para que cualquier agente distinga pruebas pendientes, aprobadas e integradas sin inventar hashes autorreferenciales.
