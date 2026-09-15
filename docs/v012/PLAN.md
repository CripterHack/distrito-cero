# Distrito Cero v0.12 · Continuidad anatómica

## Base y autorización
Continuación solicitada de v0.11. No rehacer ni eliminar el creador inicial o el catálogo de 12 partidas. La imagen aportada es referencia de detalle, no un modelo descargable ni una prueba del renderer. Las afirmaciones de acabado se basarán en capturas del juego.

## Incremento verificable
1. Superficies: cuello continuo hasta la base torácica, inserciones suavizadas, hombros sin uniones duras y pliegues más contenidos. Manos con mejor muñeca, almohadilla palmar, lectura dorsal y uñas.
2. Deformación: dual quaternions sobre los mismos 49 huesos, matrices de simulación conservadas, CPU y shader con referencia matemática equivalente. Mezcla con corrección de hemisferio, sin nuevas bibliotecas de runtime. Probar volumen de torsión y rigidez de una influencia.
3. Editor: grosor acotado del cuello, inspección de cuello/manos, iluminación y comparación no destructiva con el borrador inicial. Perfiles antiguos sin parámetro nuevo deben importar con valor neutro.
4. Partidas: búsqueda por nombre/personaje y orden por actividad, nombre o progreso sobre el catálogo existente. No introducir un segundo backend ni mutar datos al ordenar.
5. Regresión: lógica heredada, editor y persistencia, extracción/conducción/cruce, capturas iguales antes/después. Sin promesas de FPS sobre SwiftShader.

## Criterios
HTML reconstruible offline. Pesos válidos y coherencia de color/sombra. Comparación mantiene cámara/luz/pose. Suelas y puntos de muñeca conservados. Rechazo de parámetros inválidos sin escritura. Aplicar/cancelar apariencia no cruza espacios. Conservación de campaña, ocupación y mundo procedural.

## Límites de esta entrega
No escaneo corporal, simulación muscular ni tela física. Dual quaternion conserva volumen de torsión pero puede generar abultamientos y no evita toda intersección. Los contactos de dedos siguen siendo objetivos aproximados. La referencia artística no se presentará como resultado alcanzado.

## Referencia técnica
Kavan et al. Geometric Skinning with Approximate Dual Quaternion Blending (2008), página de los autores: https://users.cs.utah.edu/~ladislav/kavan08geometric/kavan08geometric.html . Implementación matemática original local, sin copiar código con licencia externa.

## Cierre de implementación

Las cinco unidades quedaron integradas en el HTML v0.12. El caso de prueba de contorno cervical detectó y corrigió un pico de la geometría heredada, y la prueba de uñas forzó el ajuste sobre la superficie real. No se sustituyó la malla de cabeza completa, no se añadieron nuevos estilos de prendas ni miniaturas de guardados. Las mejoras de catálogo de esta unidad son búsqueda y ordenación.

Resultado comprobado: 207 pruebas de lógica, 155 comprobaciones de navegador y 21 de geometría/exportación. La lectura independiente, las huellas y la reconstrucción exacta están en `qa/v012/release-report.json`. Limitaciones en `VERIFICACION.md`.
