# Recursos de Continuidad anatómica v0.12

## Recursos anteriores conservados

La cabeza deriva del subconjunto MakeHuman HM08 con target adulto CC0 y los mapas de Aksel Skin por Mindfront, CC0. Los insumos compactos, huellas y fuentes están en `ATTRIBUTION-v09.md` y `anatomy-source/`. El trabajo original del cuerpo/manos y la convención del rig de 49 huesos está descrito en `ATTRIBUTION-v010.md`.

No se descargó un nuevo escaneo corporal ni un modelo nuevo de Higgsfield para v0.12. La referencia visual aportada por el usuario se utiliza para dirección de calidad, no como textura ni geometría ni imagen promocional del resultado. No se incorpora su archivo al paquete.

## Aportes originales v0.12

`build_hero_v012.py` y `body_authoring_v012.py`: transición cervical, abertura de cuello, suavizado de hombros/axilas, redistribución de pesos, palma y muñeca, uñas ajustadas sobre los triángulos de las manos. Poros, pliegues finos y rugosidad de manos/cuello en el shader son detalle original procedural, no mapas fotográficos nuevos.

`dual-quaternion.js` y la ruta del shader: implementación matemática original de mezcla de cuaterniones duales con corrección de hemisferio a partir de transformaciones rígidas. No se incorpora el código de otra librería. Referencia técnica: Ladislav Kavan et al., *Geometric Skinning with Approximate Dual Quaternion Blending* (2008), https://users.cs.utah.edu/~ladislav/kavan08geometric/kavan08geometric.html .

## Exportaciones

`dc012-human-continuity.glb` corresponde al personaje neutral de esta entrega. Incluye geometría, pesos, rig, tres mapas embebidos y siete estudios de pose/movimiento. La exportación glTF portátil no exige skinning DQ y puede verse distinta al flexionar en un visor lineal. Tampoco incorpora la totalidad de la apariencia del shader ni secuencias de vehículos.

Los archivos `dc010-*`, `dc09-*`, `hero-v010-baseline.js` y `higgsfield-*` son antecedentes, no recursos que el HTML descargue. `hero-native-report.json` es el informe actual. No se distribuyen fuentes tipográficas ni bibliotecas de ejecución.
