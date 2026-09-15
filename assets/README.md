# Recursos actuales · v0.12 Continuidad anatómica

La malla actual se genera con `python tools/build_hero_v012.py`, se empaqueta con `python build.py` y se exporta con `python tools/export_continuity_glb.py`. El HTML contiene sus propios buffers y mapas. No carga un GLB remoto ni necesita los archivos externos para jugar.

`dc012-human-continuity.glb`: personaje neutral actual, 13 grupos de material, 49 huesos y siete estudios procedurales. Apariencia portable aproximada. La deformación glTF estándar puede diferir de los cuaterniones duales del juego.

`hero-native-report.json`: informe geométrico actual. `anatomy-source/`: insumos anteriores de cabeza y piel con licencias y huellas conservadas.

Ver **ATTRIBUTION-v012.md**, **ATTRIBUTION-v09.md** y **ATTRIBUTION-v010.md**. Las exportaciones de versiones anteriores y las referencias de autoría Higgsfield permanecen identificadas como históricas. No se distribuyen archivos de fuentes tipográficas.
