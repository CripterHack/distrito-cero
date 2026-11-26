# Seguimiento de la implementación

| Trabajo | Criterio de verificación | Referencia |
| --- | --- | --- |
| Asignar un residente permanente a la acera | A través de un viaje y una carga sigue habiendo 72 peatones. El civil camina, gira y corre al tocar el claxon. | [Simulación](../../tests/market-resident.test.cjs) |
| Distribuir los pesos de las rodillas | Comparación con v0.20.28 y búsqueda de cruces en 129 fases por acción de ambas piernas. | [Mediciones y comparación](../../qa/higgsfield-knee/README.md) |
| Adaptar el modelo al renderizador | Derivar dos mallas, materiales y curvas desde el GLB. Conservar la geometría de los dedos y comprobar las rodillas con las matrices que usa la GPU. | [Receta y pruebas](../../assets/higgsfield-20261125/peaton-mercado.md) |
| Verificar el movimiento en la calle | Medir la superficie visible con y sin la instancia, comprobar la acción elegida tras el claxon y repetir al fallar la carga de la textura. | [Captura del residente](../../tools/qa/capture_market_pedestrian.py) |
| Iluminar la parada de noche | Comparar la chaqueta con el mismo fondo en los extremos del control de luz. Mantener el taller como control exterior. | [Pruebas de la marquesina](../../tests/mercado-landmarks.test.cjs) |
