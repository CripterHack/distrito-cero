# Inventario y política de recursos

## Categorías

**Canónico del runtime:** `src/hero-asset.js`, `src/human-materials.js`, `src/hair-geometry.js`, `src/vehicle-asset.js` y las recetas de `visual-geometry.js` / `equipment-geometry.js`. El build incorpora sus datos o código dentro del HTML.

**Insumos conservados:** `assets/anatomy-source/`, `assets/hero-v010-baseline.js`, `hero-v012-baseline.js`, `hero-v013-baseline.js`, `hero-v014-baseline.js`. No borrar por considerarlos duplicados sin reconstruir las recetas que los consumen.

**Intercambio/exportación:** los GLB `dc09-*` a `dc019-*` son exportaciones de versiones concretas. `assets/dc019-equipment.glb` corresponde al equipamiento actual. `assets/dc016-human-traits.glb` conserva el humano neutral exportado en v0.16, no las poses de manejo añadidas después. No existe una exportación universal de todo el creador.

**Comparación:** `assets/baseline-v018.html` es sólo referencia de QA, no dependencia de la partida. `qa/v*/` conserva capturas, clips, informes y fallos documentados.

## Procedencia

Cabeza y mapas anteriores remiten a MakeHuman HM08 y Aksel Skin, con atribuciones y huellas en `assets/ATTRIBUTION-v09.md`. El resto de la anatomía y las recetas procedurales tienen el historial descrito por versión. No se añaden permisos nuevos durante esta publicación. Un asset artístico es dato, no una librería de runtime.

## Pipeline requerido para nuevos recursos

Referencia autorizada → modelo de autoría → topología y UV → materiales → rig/weights → poses correctivas → LOD → proxies y anclas → GLB validado → conversión controlada → integración real → medición → evidencia comparable.

Cada asset debe tener ID estable, autor, procedencia, licencia, modificación, huella de origen, unidades/ejes, presupuesto por LOD, versión del rig, mapas y reglas de colisión. Registrar qué función está sólo en runtime y qué viaja en la exportación.

La convención actual es Y-up, metros y +Z adelante. En Blender revisar conversión desde Z-up, transforms aplicadas, inverse binds, nombres y pivotes. Validar PNG/WebP y la interpretación de albedo frente a mapas lineales. No utilizar mapas de color como mapas de normales por apariencia.

## Presupuestos de trabajo

La base tiene 49 huesos y humano/peinado de detalle alto por debajo de 100,000 triángulos según la entrega de Rasgos. El kit actual de armas tiene 9,888 triángulos en trece equipos. Son referencias de coste, no reglas universales ni garantía de rendimiento. La decisión sobre resolución y geometría se toma por tamaño en pantalla, número simultáneo y frame time, no por perseguir una cifra de polígonos.

No añadir decodificadores de compresión externos al HTML sin una decisión aprobada. La optimización de autoría puede producir buffers nativos listos para usar. Medir overdraw de pelo, slots de material, draw calls, texturas compartidas y coste del skinning.

## Almacenamiento del repositorio

Se conserva íntegra la primera importación, incluidos recursos históricos. Ningún archivo individual del paquete supera 9 MB aproximadamente. No se activó Git LFS ni se contrataron servicios. Para crecimiento posterior, proponer LFS o releases para binarios pesados con una decisión de cuota, coste y reproducibilidad. No versionar secuencias de frames sin comprimir ni nuevas copias del juego completo en cada PR.

Referencias técnicas: [glTF 2.0](https://registry.khronos.org/glTF/specs/2.0/glTF-2.0.html), [validador Khronos](https://github.com/KhronosGroup/glTF-Validator), [archivos grandes en GitHub](https://docs.github.com/en/repositories/working-with-files/managing-large-files/about-large-files-on-github).

## Correctivo canónico de la almohadilla de la mano

`tools/refine_thenar.py` y `assets/thenar-contour-source.json` producen un correctivo local de posición/normal del recurso humano. No alteran sus pesos ni su rig. Ejecutar `--check` junto al rebinding de prendas para verificar autoría. Ver [THENAR-SURFACE.md](THENAR-SURFACE.md). Las exportaciones humanas antiguas permanecen históricas y no reciben silenciosamente esta modificación.
