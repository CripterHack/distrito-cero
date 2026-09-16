# Handoff · contacto digital con equipo

Base de esta unidad: master `f9998523492bf29ff276cf85c3f282d32163821a`. Preserva mangas de PR #12, codos ópticos de PR #13, benchmark, recuperación y guardados nativos. #2/#3/#4 cerrados; #5/#6/#7 permanecen abiertos. Pages publica master y no se modifica su configuración.

## Unidad actual

Tres pruebas de superficie reprodujeron dedos dentro de los objetos, aunque la palma alcanzara su ancla. Se añadió un ajuste de cuatro perfiles compartidos de falanges no pulgares, sin cambiar malla, pesos, huesos, anclas, física o formato de guardados. La recarga abre y recupera las falanges gradualmente; una prueba nativa a 1/60 s descubrió y corrigió un tirón visual.

Leer [FINGER-CONTACTS.md](FINGER-CONTACTS.md) y el [plan](../../specs/003-weapon-contact/plan-finger-contacts.md). La unidad añade 14 tests Node y una suite de 15 checks / 12 capturas. Consultar PR/Actions para el resultado del commit exacto; no atribuir capturas locales antiguas a la CI nueva.

## Siguiente corrección

#6: oposición del pulgar y transición de su base a la palma. Una exploración de rotaciones no logró una solución convincente, así que el pulgar sigue sin modificarse. Reproducir mediante superficie/topología/pesos, conservando los cuatro dedos ya corregidos, los codos y la continuidad de recarga. Después revisar contacto mano-mano y ojo/mira.

#5: registrar revisión artística de proporciones, materiales y cabello con la matriz existente y recursos de procedencia verificable. No convertir una única imagen en aprobación general.

#7: recorrido completo, entorno/mundo y playtests conservan sus requisitos; no cerrar por un plan o por mover automáticamente al jugador entre objetivos.

## Verificación

```sh
python3 tools/rebind_garment.py --check
python3 tests/garment_binding.test.py
python3 build.py
node --test tests/*.test.cjs
python3 tools/export_contact.py
python3 tests/contact_exports.test.py
python3 -m tools.qa.run --suite fingers --suite handling --suite optical --suite recovery
python3 -m tools.qa.run --suite characters
python3 -m tools.qa.run --suite native --origin http
```

Confirmar HEAD remoto, AGENTS, hashes y checks antes de integrar. Verificar Pages después. No escribir sobre evidencia histórica. Las pruebas gráficas usan fixture de almacenamiento y no son FPS físicos. La prueba HTTP nativa es independiente.
