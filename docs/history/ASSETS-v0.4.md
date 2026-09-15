# Procedencia del coupé y límites de integración

Modelo original creado mediante el conector autenticado Higgsfield 3D Jutsu, con operaciones de Blender. No se importaron modelos de catálogos de terceros.

- Proyecto: `b423a0c7-1fe4-4a56-a0bd-4cd654a18258`
- Nombre: Distrito Cero · Vehículo modular v0.4
- Operación de modelado: `dc04-coupe-modular-01`
- Revisión comprometida: `2`
- Motor de autoría reportado: Blender 5.2.0 LTS
- 154 objetos de malla con nombres de carrocería, cristales, ruedas, puertas, luces e interior
- Metros, Blender Z hacia arriba y frente hacia -Y, exportación glTF Y arriba y frente +Z

## Recursos originales opcionales

Proyecto editable del propietario:
https://higgsfield.ai/3d-jutsu/b423a0c7-1fe4-4a56-a0bd-4cd654a18258

GLB completo y render de referencia, exportados y subidos desde Higgsfield:
https://d2ol7oe51mr4n9.cloudfront.net/user_3Icvp3WfrHKY6QGnlXqcYgbAGfb/947db9f1-dd49-43c9-a954-af1c4c8f6dc4.zip

Render original:
https://d2ol7oe51mr4n9.cloudfront.net/user_3Icvp3WfrHKY6QGnlXqcYgbAGfb/5d14ec09-2304-4005-a328-52b59314fa23.png

El ZIP original contiene `coupe.glb` y `coupe.png`. La escena editable Blender está en el proyecto, no dentro del ZIP local de código. Esos recursos NO se solicitan durante el juego.

## Lo realmente integrado

`higgsfield-body.json` contiene `BODY_shell` y cuatro paneles `GLASS_*` extraídos del GLB exportado. Coordenadas y normales cuantizadas con unidad 0.001, índices completos, transformaciones ya aplicadas e identidad comprobada. Carrocería: 812 triángulos. Cristales: 8. Total importado: 820 triángulos.

El conversor `tools/convert_vehicle.py` valida los datos y genera `src/vehicle-asset.js`: posiciones, normales y UV intercaladas, expandidas para dibujo instanciado. No hay un cargador glTF general ni una dependencia de Draco, Meshopt o KTX. No acepta libremente cualquier GLB.

Las demás piezas del coupé del runtime son aproximaciones procedurales. La apertura de puertas, ruedas y suspensión se anima a partir del estado del juego, no reproduciendo los clips de Blender. Un modelo de referencia offline no prueba por sí mismo el acabado del juego: las capturas de `qa/v04/` pertenecen al renderer real.

El render de referencia se inspeccionó a resolución reducida. El modelo integrado y el shader de daño se revisaron en capturas de juego y en el render continuo.
