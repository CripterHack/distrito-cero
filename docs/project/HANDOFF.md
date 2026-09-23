# Continuación vigente · v0.20.6, guardia y recarga

## Base y unidad actual

Base remota `02e3a140baa8994a02fbcb5943b9a4c8258915df`, producto publicado 0.20.5.
Su Verify 35903012951 terminó con los tres jobs aprobados. PRs #40/#41 integrados
y limpieza completada: no repetirlos ni restaurar ramas antiguas.

El parche local 0.20.6 se aplica en esta continuación a una rama nueva desde esa
base. El PR de esta unidad registra HEAD, CI, revisión, merge y publicación finales.
La documentación por sí sola no acredita integración ni despliegue.

[STOCK-TRANSITIONS](STOCK-TRANSITIONS.md) define la corrección acotada de #6:
culata delante de la misma superficie de chaqueta durante guardia y recarga,
arco exterior hacia el apuntado, y preparación compartida de torso y objeto.
No cambian mallas, longitudes, anclas palmares, cámara, física, munición o partidas.
El origen y el recorrido visual del equipo sí cambian.

## Verificación y procedencia

Diez de once regresiones volvieron a fallar con el código original. Repetición
local nueva: **554/554 Node**, sin omisiones, y seis archivos de producto idénticos
al manifiesto del parche. Reconstrucción remota 35916388833: mismo build y
554 Node, con objetos de contenido comprobados. No sustituye la CI del PR.

El bundle de esa reconstrucción contiene el historial Git auténtico del master
actual. El parche completo se aplicó con su verificador, desde el commit exacto,
y se cotejaron sus once archivos. No se fabrica historia a partir de Pages.
La herramienta temporal y su permiso de almacenamiento de objetos no pertenecen
al árbol ni al historial de la rama de producto y se retiran al terminar.

La evidencia gráfica previa del parche conserva 141 checks, 80 comparativas y
las limitaciones de los escenarios preparados. No se etiqueta como ejecución
nueva ni como hardware físico. Las suites HTTP y exportación humana del nuevo
HEAD son controles separados, exigidos antes del merge.

## Siguiente trabajo real

**Desenvainado inicial con ready < 1.** La nueva reproducción nativa confirma
penetración de chaqueta de hasta 23.70 mm al equipar, alrededor del décimo paso
a 60 Hz. El parche no la resuelve: la aceptación actual empieza con ready=1.
Retomar el recorrido inicial con `stock_clearance.js`, `longarm_contact.js` y
las pruebas existentes. Conservar contactos, continuidad, alcance y estado.
No crear otra matriz o solver paralelo ni relajar el límite de 2 mm.

#5 conserva arte, materiales/UV y procedencia global. #6 mantiene además revisión
amplia de acciones/anatomías y coste por actor/LOD. #7 conserva recorrido íntegro,
playtests humanos y hardware. No inventar aprobación ni cerrar por recuentos.

## Comprobaciones y ramas

```sh
node --test tests/stock-transition-clearance.test.cjs
node --test tests/*.test.cjs
python3 build.py --check
python3 tests/release_build.test.py
```

Añadir los controles de [QA](QA.md), artefactos del HEAD exacto y revisión gráfica.
Verificar master/Pages por separado. [Política y respaldo](BRANCH-CLEANUP.md):
master es la única rama permanente. Retirar las ramas de esta unidad sólo después
de verificar su integración o de conservar su trabajo. No modificar permisos
normales ni licencia. Reversión sin migraciones ni borrado de partidas.

[Handoff anterior](https://github.com/CripterHack/distrito-cero/blob/02e3a140baa8994a02fbcb5943b9a4c8258915df/docs/project/HANDOFF.md)
conserva la limpieza y el apoyo dinámico. Revisión propia, no independiente.
