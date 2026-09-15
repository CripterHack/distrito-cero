# Handoff · unión de mangas y torso durante el apuntado

## Base y continuidad

Se trabajó desde master `072750bc65d9ceb10ca536bc7f0c7b3146a5b055`. #2, #3 y #4 están cerrados por sus gates de QA portable, guardado HTTP nativo y recuperación WebGL. PR #11 añadió el benchmark; #5 sigue abierto por revisión artística y otros criterios. GitHub Pages publica desde master, sin cambio de configuración.

## Unidad actual de #6

La superficie de mangas desconectadas recibía hasta 53.33% de influencia del torso y el tronco inferior hasta 19.61% de los brazos. Corregidos los pesos en autoría mediante adyacencia y transición armónica, sin cambiar el esqueleto, geometría, normales, UVs, anclas de equipo, física o formato de partidas.

Leer [GARMENT-BINDING.md](GARMENT-BINDING.md) y [plan de la unidad](../../specs/003-weapon-contact/plan-sleeves.md). Asset resultante: `a4f5a6522f0012290bd2fca8d573ca5243388474f72fb026cf5766924e3c8b7d`. HTML reconstruido sobre el runtime con recuperación: `47cbc618241b3419e300d76480176f77287ca80ee449edf14c78d1af4f32e875`, 8,851,413 bytes.

Tres regresiones Node reprodujeron el defecto y pasaron después. Cinco tests Python verifican receta, integridad y separación de puños/pantalones. El workflow de autoría se ejecutó una sola vez en la rama y se retiró del árbol final. La CI permanente comprueba `--check` y la suite Python. Consultar el PR/Actions para los resultados gráficos del commit exacto, no considerar la presencia de un test como pase.

## Verificación y publicación

Antes de integrar: build reproducible, todas las pruebas Node, receta de pesos, benchmark de personajes, manejo, recuperación y guardados nativos. Las primeras comparaciones locales utilizaron la base visual v0.19 antes del lifecycle, con los mismos assets y poses. La CI captura el HTML actual con recuperación. Mantener diferenciadas las evidencias y sus hashes.

Revisar frente/perfil del fusil, fase de recarga, agachado, pistola, Gauss, binoculares y reposo. No aprobar toda la anatomía por desaparecer la membrana de la chaqueta. Los GLB humanos anteriores son exportaciones históricas, no incluyen automáticamente estos pesos.

## Trabajo que sigue

#6: ampliar la regresión de superficie a la axila superior, hombro y todo el ciclo de apuntado/recarga. Después abordar contactos de falanges y coordinación de ojo/mira con el montaje único existente. No cambiar pesos y puntos de agarre simultáneamente sin medir qué defecto corresponde a cada uno. La corrección presente no cierra la issue completa.

#5: registrar revisión artística de proporciones, siluetas, manos/cabello y autoría. No marcar `art-review.json` como aprobado por tests numéricos.

#7: vertical slice pendiente, con gates de mundo/escena, recorrido íntegro, hardware y playtest. No cerrar por añadir documentación o mover al jugador por script entre objetivos.

## Comandos

```sh
python3 tools/rebind_garment.py --check
python3 tests/garment_binding.test.py
python3 build.py
node --test tests/*.test.cjs
python3 -m tools.qa.run --suite characters --suite handling --suite recovery
python3 -m tools.qa.run --suite native --origin http
```

Ejecutar además exportación y tests de harness/contratos según QA.md. Partir siempre de HEAD remoto actualizado. Preservar SOURCE-MANIFEST y qa histórico. Actualizar documentación/issue con evidencia real, integrar con checks aprobados y confirmar que Pages sirve el hash correspondiente.
