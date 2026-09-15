# Procedencia de v0.10 · Constitución

## Reutilizado sin nuevas descargas de runtime

La cabeza MakeHuman HM08 y los mapas derivados de Aksel Skin, de Mindfront, conservan las fuentes y licencia CC0 documentadas en `ATTRIBUTION-v09.md`. El insumo compacto y las texturas permanecen incluidos. No se afirma autoría propia del rostro base ni de la piel original.

## Autoría nueva

`tools/body_authoring.py` y `tools/build_hero_v010.py` definen superficies originales paramétricas de torso vestido, mangas, pelvis, piernas, manos completas, uñas y calzado. La geometría corporal y las manos de este incremento no son un escaneo, un modelo completo MakeHuman ni un GLB de Higgsfield. `src/skin-rig.js` define el rig de 49 huesos y los perfiles de flexión.

Se consultaron metadatos de articulaciones de la malla HM08 mediante el sandbox remoto. La transferencia del subconjunto de mano no se completó ni se incorporó. No hay bytes truncados de esa tentativa en el modelo. Las manos finales proceden del generador local incluido.

La topología continua se hornea con marching cubes, luego se asignan pesos, normales y coordenadas y se cuantiza al formato del motor. Las dependencias de autoría no se distribuyen como bibliotecas de runtime.

El origen artístico histórico de los coches y recetas anteriores está documentado en los archivos previos. No se realizó una nueva generación visual con Higgsfield para representar esta entrega. Las imágenes de revisión son capturas del renderer WebGL del juego.

No se incluyen fuentes tipográficas, assets comprados ni materiales de terceros sin procedencia documentada. CC0 sólo describe los datos artísticos correspondientes, no cambia automáticamente la licencia del resto del proyecto.
