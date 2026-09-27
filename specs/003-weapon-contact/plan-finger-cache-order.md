# CONTACT-02/05 · Caché canónica independiente del orden

**Objetivo:** la misma recarga produce los mismos dedos y matrices aunque el
primer montaje de la pistola o rifle ocurra durante un cambio de equipo.
**Base:** PR #50 integrado, `7231aa51457539d2e5345f2d98ab470ded656fc0`.
**Especificación:** [SPEC-003](spec.md), CONTACT-02, CONTACT-04 y CONTACT-05.
**Ejecución:** secuencial con regresión antes del cambio y revisión propia.
**Tecnología:** JavaScript/WebGL2 nativos, Node 22 y QA Python/Playwright.

## Causa y contrato

`fitFingers` memoriza cuatro perfiles de autoría. `mount` conserva correctamente
la superficie/pivote del cargador anterior durante el handoff, pero usa esa
superficie transitoria para inicializar el ajuste del nuevo perfil. La caché
fría y la inicializada por otro actor pueden producir dedos distintos.

Separar exclusivamente la referencia local canónica del ajuste y la superficie
del objeto mostrado. Mantener `magazine.surface`, pivote, offset y rotación
capturados para el objeto anterior. Sin vaciar/precalentar la caché en runtime,
sin claves por actor/fotograma y sin cambiar solver, huesos, geometría, umbrales,
selección, recarga lógica, munición o partidas. El renderer sigue siendo lector.

## Unidad de implementación

Archivos: `src/weapon-handling.js`, `tests/finger-cache-order.test.cjs`,
identidad/build y documentación vigente. Reusar `tests/helpers/sidearm_sight.cjs`
y los observadores de superficies y montaje existentes. No crear otra matriz
visual equivalente. No extender rifle/revólver en esta unidad.

- [x] Crear procesos Node independientes con caché fría e inicializada. Primero
  rifle→pistola o pistola→rifle, libres y desde recarga, después recarga idéntica.
  Comparar ajustes, todas las matrices, palmas y transform del cargador.
- [x] Observar la regresión fallar en la base, no un error de carga del harness.
- [x] Separar el punto de autoría antes de aplicar el handoff. Usarlo sólo en
  `fitFingers`. Conservar las cuatro claves y la superficie capturada.
- [ ] Repetir regresión y suite Node completa. Comprobar memoria acotada,
  lecturas no mutantes, acciones inmediatas y conservación del primer frame.
- [ ] Actualizar versión de producto a 0.20.14 y regenerar HTML/build-info.
  Ejecutar contratos Python vigentes, autoría y exportación sin alterar assets.
- [ ] Verificar renderer con sight y superficies existentes, sin precalentarlas
  para ocultar el caso. Comparar con evidencia anterior y revisar imágenes.
- [ ] Publicar PR, verificar HEAD, revisar y fusionar sólo con gates aprobados.
  Registrar push/Pages por separado y retirar únicamente ramas concluidas.

## Focos de revisión

Caché fría, otro actor que inicializa primero, reversión/recarga durante cambio,
conservación de pieza visible y separación de gameplay. Los tests existentes
mantienen esos contratos de acciones/partidas/longitudes. Procesos nuevos, no
una API de reset añadida al juego, dan aislamiento real a la regresión.

## Reversión y límites

Revertir implementación, tests y versión/build juntos. Sin migración ni borrado
de partidas. Pruebas preparadas no son FPS físicos, aceptación artística global,
CCD ni cobertura de todas las herramientas. #5, #6 y #7 conservan sus criterios.
Resultados medidos, revisión visual y estado final se registran en el PR y
[HANDOFF](../../docs/project/HANDOFF.md), sin convertir planes en aprobaciones.
