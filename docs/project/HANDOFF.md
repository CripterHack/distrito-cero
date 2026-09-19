# Handoff · v0.20.1 / auditor cooperativo CONTACT-03

**Base remota:** `fecf117385941dabd4e22f13c04d45d4032fb042`, PR #26 integrado y #25 cerrada. Producto **0.20.1 · Coherencia**, canal prototype. Leer [STATE](STATE.md), [QA](QA.md), [hallazgos de armas largas](LONGARM-CONTACT.md) y [plan #27](../../specs/003-weapon-contact/plan-longarm-audit.md).

## Reanudación de la unidad anterior

La CI de master [35428128166](https://github.com/CripterHack/distrito-cero/actions/runs/35428128166), el benchmark [35428128169](https://github.com/CripterHack/distrito-cero/actions/runs/35428128169) y Pages [35428127755](https://github.com/CripterHack/distrito-cero/actions/runs/35428127755) terminaron `success`. Sus resultados se consultaron al iniciar #27, separados de la CI previa del PR.

La suite HTTP `reload` conserva sus 31 checks y 27 escenarios con RAF/inputs/Storage de producción. No repetir #25 ni tratarla como pendiente. El primer timeout de 900 s y el bloqueo HTTP local siguen documentados en el [plan nativo](../../specs/003-weapon-contact/plan-native-reload.md). La revisión posterior utilizó 1,800 s y un diario parcial que nunca sustituye al informe final.

## Unidad actual #27

Nuevo auditor QA de `smg`, `rifle`, `shotgun` y `sniper`. `tools/qa/longarm_contact.js` mide el ojo, eje de mira verificado contra geometría, culata visible, referencia articulada del hombro, palmas y longitudes entre articulaciones distintas. No usa la mira de pistola para armas largas. La escena del navegador consume la paleta realmente dibujada.

Contrato `longarms`: 24 checks de integridad, 48 capturas, matriz numérica de 72 poses y 240 muestras del ciclo. **No cambia ni aprueba la postura del juego.** `screening.status=needs-coordination` permanece visible aunque el proceso de medición apruebe. El desajuste neutral observado sigue entre 205.53 y 238.64 mm. Una traslación al ojo aumenta la separación de culata a 209.63–242.56 mm. El contrafactual es algebraico, no una corrección implementada.

Trece pruebas Node y cuatro Python de galería añaden controles negativos. `qa_selection.test.py` exige origen fixture, nunca HTTP. La CI incorpora la suite sin retirar los checks anteriores. La ejecución local headless no ofreció WebGL2 y quedó fallida. La ejecución headed/Xvfb produjo la galería con 24/24 checks; cada repetición y la CI deben consultarse por su propio manifiesto. El PR asociado a #27 determina el resultado de integración, no la existencia de este archivo.

## Qué se conserva

HTML SHA-256 `4a78bcca34cd40b2c406b0642362f30a6b71303d8a4a6ace659e0ba4afc9918d`, 8,862,957 bytes. Fuente `dfb16e65c1a64d991f2bedfbecf0892d69c8b2110e4be1403e31d7af739c4fdb`. No hay cambios de runtime, mallas, rig, inventario, guardados, permisos o versión. No borrar datos del sitio.

La copia local es el artefacto Pages del SHA canónico. Su historia Git de ejecución es sintética y no se publica. Los commits remotos parten del SHA real. Los resultados de fixture no se etiquetan como persistencia HTTP o rendimiento físico.

## Puertas de verificación

```sh
python3 build.py --check
node --test tests/*.test.cjs
python3 tests/longarm_gallery.test.py
python3 tests/qa_selection.test.py
python3 tests/reload_contract.test.py
python3 tools/export_contact.py
python3 tests/contact_exports.test.py
xvfb-run -a python3 -m tools.qa.run --suite longarms --suite sight --suite handling --suite characters --headed
```

Ejecutar también autoría, build, runner y suites vigentes según [QA](QA.md). Exigir CI del HEAD exacto, revisión del diff y capturas antes del merge autorizado. El push posterior a master y Pages son verificaciones independientes. No publicar un snapshot local ni declarar artística una aprobación de checks.

## Siguiente acción concreta

Tras integrar #27, no añadir otra auditoría equivalente. Reutilizar las referencias para una corrección acotada de rifle neutral que coordine cabeza, hombro, culata y alcance sin deformar cara o alargar brazos. El detalle está en [LONGARM-CONTACT](LONGARM-CONTACT.md#siguiente-unidad-sin-repetir-este-diagnóstico). Preservar recargas, continuidad, dedos, palmas, óptica y todos los formatos. La referencia del hombro no sustituye la revisión de la superficie real de la prenda.

#5 necesita aprobación artística/materiales/variantes. #6 sigue pendiente de coordinación y revisión de superficies/movimiento. #7 necesita escena y recorrido íntegro sin teletransportes, además de playtest y GPU física. No cerrar esos gates por el éxito de la suite diagnóstica.
