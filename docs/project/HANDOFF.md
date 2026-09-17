# Handoff · v0.20.1 / referencia ocular de armas cortas

Base: `687ead2` (v0.20.0). Unidad actual: #21, PR por crear/verificar. Producto del árbol: **0.20.1 · Coherencia**, prototype. Leer [SIDEARM-SIGHT](SIDEARM-SIGHT.md), [STATE](STATE.md) y [plan](../../specs/003-weapon-contact/plan-sidearm-sight.md).

## Cambio actual

Pistola/revólver colocan el montaje según el ojo articulado usando la paleta ya evaluada. Alineación progresiva y retroceso sobre referencia quieta alrededor de la empuñadura. El alcance tiene prioridad. Sin cambios de malla/pesos/huesos, reglas o claves de guardado. Preservar mangas, dedos, pulgares, apoyo entre manos y contorno de v0.20.

Dos pruebas originales de mira fallaron en la base. Un candidato de retroceso hacía bajar el objeto y fue descartado con una regresión. Se añaden doce tests Node y suite `sight` de 24 checks, con pruebas gráficas separadas de las HTTP nativas. No confundir la postura heredada de equipar con el coste temporal del nuevo correctivo.

## Puertas antes de integrar

```sh
python3 tools/refine_thenar.py --check
python3 tools/rebind_garment.py --check
python3 build.py --check
python3 tests/release_build.test.py
python3 tests/release_checkout.test.py
node --test tests/*.test.cjs
python3 -m tools.qa.run --suite all
python3 -m tools.qa.run --suite all --origin http
```

Revisar diff y CI del HEAD exacto. El usuario autorizó merge si la revisión y pruebas aplicables aprueban. Después verificar CI del push y Pages contra build-info, versión visible y guardados. Cerrar #21 sólo tras validar su alcance. Documentar resultados en el issue para no inventar un commit autorreferencial.

## Continuidad

#19 se cerró tras publicar v0.20 por #20. #2/#3/#4 conservan alcance cerrado; #5/#6/#7 siguen abiertos. El ajuste actual no resuelve armas largas: la culata a hombro y la mira necesitan un contrato conjunto de postura, no mover las manos hasta forzar el ojo. Preparar casos de cuello/torso/alcance y revisar sin deformar la cara.

#5 conserva aprobación artística completa, materiales, pelo y variantes. #7 conserva escena, recorrido íntegro y playtest. Las capturas preparadas no los satisfacen. Gráficos por software y perfiles de prueba no acreditan FPS físicos ni usan partidas del usuario. No borrar runs rojos históricos o relajar gates.
