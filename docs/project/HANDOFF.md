# Continuación vigente · escopeta / revólver · candidata 0.20.22

## Base cerrada

Master **39b7647f1c763ab9e35e8c507723fc4cf5cfc57f**, árbol
**1820cda051434f5596c20c2b3c5fa9de2afc7661**, producto 0.20.21.
[#60](https://github.com/CripterHack/distrito-cero/pull/60) y su push están verificados.
No repetir pistola/escopeta, el shader de #59 ni los temporizadores de #58.

## Unidad presente

[Plan](../../specs/003-weapon-contact/plan-shotgun-revolver-handoff.md), CONTACT-04/05.
Habilita únicamente escopeta ↔ revólver en captureSwitch. Conserva cuerpo/manos,
pieza retornando, selector congelado y caché canónica, con una sustitución de
modelo y rechazo de un tercer modelo mostrado. Arco existente 0.12 m, 0.90 s
cosméticos. Sin otro solver, tracker o reloj. Acciones, munición, partidas,
longitudes, geometría, rig, pies y renderer no cambian.

Los tests comparten los barridos y helpers anteriores. La prueba dirigida sobre
la base dio cuatro fallos por captura/discontinuidad y una salvaguarda aprobada.
La misma selección tras la corrección dio cinco aprobadas. La primera tentativa
del archivo entero fue interrumpida por el límite del ejecutor y no se cuenta
como corrida completa. QA dio tres fallos por catálogo ausente y luego 22/22.

Sight añade cuatro rutas al catálogo existente: **148 checks = 56+44+48**,
28 intercambios de 61 estados más before. Conserva orden previo, resolución,
todas las capturas, cinco guardas, tres productores y límites de 1800 s y 40 min.
Base no aumenta: su PR previo consumió 1554.493 s. Comparar las 24 secuencias
anteriores con #60 y revisar cada secuencia nueva antes de integrar.

## Verificación y publicación

La base restaurada con **historial Git real** aprobó 658/658 Node. Suite completa
de candidata, contratos Python, autoría/build/export, navegador, CI y revisión
se registran con resultados reales en el PR enlazado desde
[#6](https://github.com/CripterHack/distrito-cero/issues/6). No inferir un merge de
esta nota. Revisión propia, no independiente. Verificar el push después del merge
por separado y no confundir HTTP local con aceptación del sitio público.

```sh
python3 build.py --check
node --test --test-concurrency=4 tests/*.test.cjs
python3 tests/qa_selection.test.py
python3 tests/qa_runner.test.py
python3 tests/ci_workflow.test.py
xvfb-run -a python3 -m tools.qa.run --suite sight --headed --timeout 1800
```

## Limpieza completada y pendientes

El usuario renovó la autorización para retirar ramas. Las 16 obsoletas y el
auxiliar de auditoría fueron retirados tras respaldo completo, restauración y
comprobación de SHA/protección/PRs. [Registro y recuperación](BRANCH-CLEANUP.md).
No volver a tratar esa limpieza como bloqueada. Las nuevas ramas de trabajo sólo
permanecen mientras sean activas. Nunca integrar helpers en producto/ascendencia.

#5 conserva UV/materiales/procedencia y arte global. #6 conserva otras parejas,
herramientas/pesados, anatomías/giros, cortes prioritarios y coste por actor/LOD.
#7 conserva recorrido/personas/hardware. No fabricar sus criterios. Revertir
esta unidad con su versión/build no migra ni borra partidas.

## Comprobación local de esta candidata

667/667 Node completos, 148/148 Python vigentes, autoría/build/export e invariancia
aprobados. 96 documentos sin enlaces locales rotos. El primer pase Python detectó
dos fixtures de conteos antiguos, que se corrigieron antes de repetir las quince
suites. El renderer y la CI siguen siendo gates separados.
