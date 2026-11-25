# CHAR-06 · Integridad de entradas durante la validación

Refs #5, [SPEC-002](spec.md). Base: master `f9454df7e3325a3cf4d516a0374c2ccb9565090c`.

## Defecto y alcance

El validador lee el GLB y su manifiesto antes de esperar la respuesta asíncrona
de Khronos. Si otro proceso sustituye cualquiera de ellos durante esa espera,
puede producir un manifiesto de aceptación para bytes que ya no están presentes.
La comprobación inicial del hash no cubre esa sustitución.

Antes de aceptar, volver a cotejar los hashes del GLB y de los bytes exactos de
`source-manifest.json` contra las entradas capturadas. Conservar primero el
reporte completo de diagnóstico, incluso cuando se rechace la aceptación.
No cambia el esquema de reportes, la receta, el asset, el renderer ni el juego.

## Criterios y verificación

- Dadas entradas sin cambios, la CLI acepta y enlaza el reporte por su hash.
- Si cambia el GLB durante `validateBytes`, la CLI falla y no crea
  `validated-manifest.json`; conserva el reporte sobre los bytes capturados.
- Si cambia el manifiesto durante `validateBytes`, incluso sólo su formato,
  se obtiene el mismo rechazo y se conserva su hash original en el reporte.
- Una dependencia de prueba realiza las sustituciones de forma determinista.
  Comprueba la frontera asíncrona; no constituye validación Khronos de geometría.

Ejecutar `node --test tests/glb-validation-contract.test.cjs` primero con las
regresiones y después con el correctivo. La revisión/CI del conjunto siguen
siendo comprobaciones separadas. No acredita reparación UV, calidad artística
ni cierre de #5.

La ejecución inicial reprodujo dos fallos por aceptación indebida y cuatro
controles aprobados. Tras el cotejo final, las seis pruebas aprobaron; no hubo
omisiones ni cambios en los criterios de aceptación del reporte.

## Reversión y límite

Revertir esta unidad retira el cotejo adicional y sus regresiones, sin migrar
partidas ni modificar recursos. No bloquea escritores externos: un cambio
posterior al último cotejo todavía debe detectarse verificando los hashes al
consumir el artefacto.
