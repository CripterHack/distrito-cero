# Continuación vigente · pistola ↔ escopeta · candidata 0.20.21

## Base integrada: no repetir #59

[PR #59](https://github.com/CripterHack/distrito-cero/pull/59) está integrado en
**bb2412283e55d77d92dadc703d62ea89c69709c2**, árbol
**ffc69b9b88c7b76d10ea335ad3454a0808c7e62a**, producto 0.20.20.
Verify posterior **36656252962** aprobó sus siete jobs. El artefacto de Pages
36656252463 conserva el HTML exacto. La copia de 958 archivos reprodujo ese árbol
y pasó build y **649/649 Node**. No repetir la variante de materiales estáticos,
los temporizadores de #58 ni las transiciones de #57 y anteriores.

Se cotejaron digest/CRC, informes y 180 hashes de las tres particiones sight:
112 checks, veinte secuencias y cinco guardas por partición. Tiempos internos
registrados en timing.elapsedSeconds: 723.218527 / 1169.413280 / 950.100918 s.
Son tiempos diagnósticos del productor, no el tiempo total del runner, FPS ni
una comparación controlada de rendimiento entre máquinas. El cierre operativo
real de #59 se mantiene en su PR.

## Unidad actual

[Plan](../../specs/003-weapon-contact/plan-pistol-shotgun-handoff.md), SPEC-003
CONTACT-04/05, issue #6. Ampliación acotada **pistola ↔ escopeta**, libre y desde
recarga. Reutiliza captureSwitch, presentación, retorno de pieza, 0.90 s cosméticos
y caché canónica. Rechaza terceros modelos mostrados. Conserva acciones inmediatas,
munición, partidas, rig, longitudes, geometría y memoria del actor. No cambia
el shader o renderer de #59.

## Regresiones y alcance comprobado

RED sobre la base: 27 tests dirigidos, veinte aprobados y siete fallos por salto
inicial o captura ausente. Ejemplos Node: palma izquierda 222.268 mm en
pistola→escopeta y 550.606 mm en la inversa. No confundir estos fixtures con
el diagnóstico del navegador ni con FPS. Primer intento interrumpido por la
herramienta conservado aparte, no contado como prueba aprobada.

GREEN dirigido: **34/34** (27 cross-family y siete sidearm). Diez rutas dirigidas,
ocho estados y cuatro configuraciones: 320 selecciones. La nueva pareja mantiene
máximo palmar preparado 27.366 / 25.895 mm y un solo reemplazo de modelo.
La cohorte de culata cubre **760 poses** de las rutas admitidas, mínimo conjunto
−0.353 mm dentro del criterio original de −2 mm. No certifica toda la malla/CCD.

QA de selección: tres fallos RED, después **21/21**. Catálogo único ampliado a
**24 intercambios, 130 checks = 56+36+38**, preservando el orden de los veinte casos
previos. El observador mide la culata y cargador de la escopeta realmente mostrada.
61 estados más before, 820×680, capturas y cinco guardas. Sin nuevos runners ni
incrementar 1800 s/productor o 40 minutos/job.

## Verificación pendiente de cierre

La suite completa de candidata terminó **658/658 Node**, sin fallos, omisiones o
cancelaciones. Build, autoría, exportación de equipo e invariancia y 95 documentos
sin enlaces rotos verificados. Los contratos Python, renderer real, CI del HEAD,
artefactos e imágenes son gates separados, sin anticipar merge o publicación. Leer el PR de esta unidad desde
[issue #6](https://github.com/CripterHack/distrito-cero/issues/6) para estado real.
Las sondas de sólo los cuatro casos nuevos se identifican como diagnóstico, nunca
como una partición completa de CI. Revisión propia, no independiente.

```sh
python3 build.py --check
node --test tests/cross-family-handoff.test.cjs tests/sidearm-handoff.test.cjs
node --test --test-concurrency=4 tests/*.test.cjs
python3 tests/qa_selection.test.py
python3 tests/qa_runner.test.py
python3 tests/ci_workflow.test.py
xvfb-run -a python3 -m tools.qa.run --suite sight --headed --timeout 1800
```

## Continuidad y límites

Primero cerrar esta unidad por HEAD exacto y comprobar su push por separado.
Después elegir otra pareja excluida o coste por actor/LOD con reproducción y RED.
#5 conserva arte/procedencia/UV. #6 mantiene otras parejas, herramientas/pesados,
anatomías/giros y cortes prioritarios. #7 conserva recorrido/personas/hardware.
Los tres issues permanecen abiertos. No atribuir GPU física o aceptación artística.

Historia local sintética: publicar con padre remoto real y cotejar el árbol.
No reintentar limpieza bloqueada, borrar ramas, integrar helpers de transporte
o modificar manifiestos históricos. Reversión conjunta con versión/build sin
migrar ni borrar partidas.
