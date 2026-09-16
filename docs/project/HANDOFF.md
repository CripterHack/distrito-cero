# Handoff · oposición del pulgar

Base: master `71fd53aed765bdb1d450ecba274bd2fd5522026c`. Conserva mangas PR #12, codos ópticos PR #13, falanges PR #15, benchmark, recuperación gráfica y guardados nativos. #2/#3/#4 cerrados; #5/#6/#7 abiertos. Pages sigue publicando master.

## Unidad de contacto actual

Se incorpora oposición alrededor de una base metacarpal virtual, separada de la flexión de los tres segmentos existentes. No cambia malla, 49 huesos, pesos, anclas palmares o guardados. Sólo `skin-rig.js` y `weapon-handling.js` modifican el runtime, con HTML reconstruido. La búsqueda offline no se ejecuta durante la partida.

Leer [THUMB-CONTACTS.md](THUMB-CONTACTS.md) y [plan de unidad](../../specs/003-weapon-contact/plan-thumb-opposition.md). Hay once pruebas Node nuevas y una suite de quince checks con capturas. El benchmark de personajes y las regresiones de falanges, óptica, recuperación y datos nativos permanecen separados. Consultar el PR/CI para conocer los resultados efectivos, no deducirlos del documento.

## Próximo trabajo

#6: revisar contacto entre ambas manos en armas cortas y zonas mixtas palma/pulgar (el muestreo principal usa >=75% de influencia digital). Mantener el caso de oposición y las pruebas de no cruzar otros dedos antes de ampliar superficies o parámetros. Revisar fases intermedias, cambio de equipo y cancelaciones por familia; no declarar autocolisión general.

#5: usar la matriz para revisar proporciones, materiales, cabello y detalle visible de manos con decisión artística registrada. Esta corrección localizada no aprueba todo el humanoide.

#7: conserva gates de escena, mundo, recorrido íntegro, hardware y playtest. No cerrar por pruebas que preparan posiciones automáticamente.

## Entrada y cierre

```sh
python3 tools/rebind_garment.py --check
python3 build.py
node --test tests/*.test.cjs
python3 tools/export_contact.py
python3 tests/contact_exports.test.py
python3 -m tools.qa.run --suite thumbs --suite fingers --suite handling --suite optical --suite recovery
python3 -m tools.qa.run --suite characters
python3 -m tools.qa.run --suite native --origin http
```

Confirmar master/AGENTS y no sobreescribir ramas de otros. Usar rama por unidad y checks aprobados antes de integrar. Comprobar Pages contra el HTML de master. No confundir almacenamiento fixture con persistencia HTTP real ni medidas CPU/software con FPS de GPU física.
