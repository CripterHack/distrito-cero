# Handoff · continuidad del hombro en observación óptica

## Base preservada

Unidad iniciada desde master `ac3cf5b3ef78e42f50eee173a8200b9e3d2e4286` (PR #12). Mantiene la corrección topológica de mangas, el benchmark PR #11, recuperación WebGL y guardados nativos. #2/#3/#4 cerrados. #5/#6/#7 continúan abiertos por sus criterios restantes. Pages sirve master, sin cambio de configuración.

## Corrección actual de #6

La revisión del ciclo de hombro localizó una inversión brusca de codos en los binoculares, especialmente agachado. Las anclas palmares seguían correctas pero la referencia genérica de flexión casi se alineaba en sentido opuesto al eje hombro-muñeca. Se añadieron referencias propias del perfil óptico y una subida/bajada más gradual, sin cambiar malla, pesos, huesos, anclas de instrumentos, zoom ni guardados.

Leer [OPTICAL-SHOULDERS.md](OPTICAL-SHOULDERS.md) y [plan de la unidad](../../specs/003-weapon-contact/plan-optical-shoulders.md). Ocho pruebas Node cubren la trayectoria y 284 posiciones de superficie por pose. Seis reproducen fallos con las fuentes anteriores. La nueva suite optical tiene 14 checks y 13 capturas del renderer real, con tiempo preparado y almacenamiento fixture.

HTML resultante: `fe47dfa3ef9b2bff6d415b6f6fb0b64e0d0b0c0df7193b135c59e4fc3fe7b93b`, 8,851,747 bytes. Asset humano sin cambios: `a4f5a6522f0012290bd2fca8d573ca5243388474f72fb026cf5766924e3c8b7d`. No confundir estas huellas con la base visual local usada para comparaciones, que no incluía la capa posterior de recuperación. La prueba remota y la CI sí incluyen el runtime actual.

## Verificación y continuidad

La comprobación Node local completa tiene 354 tests en esta unidad. El proceso de publicación debe confirmar el run del PR, no sólo esa cifra: build/export/receta, manejo, optical, recuperación, benchmark de personajes y persistencia HTTP nativa. La suite optical no demuestra almacenamiento nativo o FPS físicos. Consultar PR/Actions para resultados del commit exacto.

El workflow de construcción de una sola vez se retira del árbol final. La CI habitual conserva permisos de lectura y añade optical al conjunto rápido. No se modifica SOURCE-MANIFEST ni qa histórico.

## Siguiente unidad

#6: continuar con los contactos de falanges y las fases de manipulación/recarga por familia usando el montaje único. Registrar una penetración o separación concreta antes de cambiar manos o anclas. Mantener los casos nuevos de continuidad de codo y superficie para no recuperar inversiones al ajustar el agarre. La forma de hombro/axila aún es simplificada y no está aprobada como hiperrealista.

#5: registrar la decisión artística sobre proporciones, materiales, pelo y autoría usando la matriz. Las pruebas numéricas no sustituyen la aprobación visual. No convertir un nuevo ajuste aislado de cuello en referencia general sin la matriz.

#7: sigue pendiente la vertical slice con gates de entorno, mundo, recorrido completo, hardware y playtest. No cerrar sólo por escribir otra propuesta o mover al personaje automáticamente a objetivos.

## Entrada y comandos

```sh
python3 tools/rebind_garment.py --check
python3 tests/garment_binding.test.py
python3 build.py
node --test tests/*.test.cjs
python3 -m tools.qa.run --suite characters --suite handling --suite optical --suite recovery --headed
python3 -m tools.qa.run --suite native --origin http --headed
```

Revisar siempre HEAD remoto, AGENTS y resultados actuales antes de crear rama. Mantener exportación y tests del harness. Integrar sólo con checks aprobados, comprobar Pages contra master y actualizar el issue con alcance real, sin cerrarlo prematuramente.
