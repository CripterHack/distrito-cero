# Continuación vigente · materiales básicos · candidata 0.20.20

## Base integrada: no repetir #58

[PR #58](https://github.com/CripterHack/distrito-cero/pull/58) integrado en
**f65a9e6218e2c3b6b3bf3a2d55671c6591512627**, árbol
**99f6edda835f838c921faece5754aecd2c240aaa**, producto 0.20.19.
Su push Verify 36519887622, benchmark 36519887772 y Pages 36519886419
ya fueron comprobados. Los temporizadores y la verificación posterior no están
pendientes. El menor margen sight del push fue 94.764 s frente a 1800 s.

## Unidad actual

[Plan](../../specs/001-reliability/plan-static-material-program.md), REL-01/02/07,
issue #6. La descomposición sincronizada por malla sitúa el principal coste local
en las cajas estáticas de la ciudad, no en el avatar. Una sonda alternada del
mismo navegador conservó píxeles y simulación al especializar el fragment shader
para los materiales básicos. No se adoptaron cortes de luz, reordenamientos,
cambios de capturas ni simplificaciones del personaje.

El renderer conserva el shader general y añade una variante que elimina únicamente
ramas de materiales detallados que no pueden ocurrir en un lote comprobado.
`basicMaterialBatch` verifica IDs enteros 0–25 en los datos estáticos de subida.
Lotes dinámicos, deformados, mixtos o sin prueba explícita mantienen la ruta general.
No se infiere elegibilidad por el nombre de una malla. Geometría, orden, luces,
sombras, transparencia y todos los descartes alcanzables se mantienen.

Ambos programas reciben uniforms propios, también en la reflexión y en la capa
RealismRenderer, sin leer uniforms de vuelta del driver. El programa entrante se
restaura incluso ante una excepción de dibujo. El recurso adicional pertenece
al ledger y se libera con su generación. No hay otro solver, tracker o reloj.

## Validación y estado real

TDD dirigido: siete fallos por funcionalidad ausente entre diez pruebas iniciales.
Una regresión adicional detectó la exclusión independiente de metadatos crowd.
Tras implementar: trece pruebas nuevas y las nueve de lifecycle aprobadas.
El test de etiquetas de release detectó README/índice pendientes al subir versión,
que se actualizaron, sin debilitar el contrato.

La candidata cambia renderer y requiere versión/build 0.20.20, pero no cambia
acciones, munición, partidas, assets o rig. Mantiene **112 checks sight**, veinte
intercambios, 61 estados más before, 820×680 y todas las capturas/guardas.
Los workflows ordinarios no cambian: tres productores, 1800 s y 40 minutos/job.

La suite completa, sonda de ambas rutas de producción, CI del HEAD y revisión de
artefactos son gates separados. Consultar el PR vinculado desde
[issue #6](https://github.com/CripterHack/distrito-cero/issues/6) para sus resultados
reales y eventual integración. Esta nota no anticipa éxito de CI ni un merge.

```sh
python3 build.py --check
node --test tests/basic-material-program.test.cjs tests/render-lifecycle.test.cjs
node --test --test-concurrency=4 tests/*.test.cjs
python3 tests/release_build.test.py
python3 tests/release_checkout.test.py
xvfb-run -a python3 -m tools.qa.run --suite sight --headed --timeout 1800
```

## Después de verificar

Comparar los tiempos completos y datos/imágenes con #58, no sólo una sonda.
No convertir ahorro local en FPS ni en garantía de capacidad universal.
Después escoger otra pareja o coste por actor/LOD sin repetir pistola/SMG de #57.
#5 conserva arte/procedencia/UV. #6 mantiene otras parejas, herramientas/pesados,
anatomías/giros y cortes prioritarios. #7 conserva recorrido/personas/hardware.
Los tres issues permanecen abiertos.

Historia local sintética: publicar con padre remoto real y cotejar el árbol.
No reintentar limpieza bloqueada, borrar ramas, integrar helpers de transporte
o modificar manifiestos históricos. Reversión sin migrar partidas.
