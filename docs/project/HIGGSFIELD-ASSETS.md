# Modelos Higgsfield · revisión de autoría · 25 noviembre 2026

Refs #5 y M2/M4. Solicitados por el titular en esta sesión. Se generaron dos
GLB mediante Higgsfield/Tripo, modelo `tripo_3d`, con geometría y texturas
detalladas, PBR y límite solicitado de 50,000 caras. Cotización: 12.5 créditos
por modelo, 25 en total; no es una auditoría de la facturación de la cuenta.
La primera petición de personaje fue rechazada antes de crear un job por
superar 1024 caracteres; sólo se repitió después de conocer ese rechazo.

[Manifiesto con prompts, parámetros, jobs y huellas](../../assets/higgsfield-20261125/manifest.json).
Los binarios y cuatro renders se entregan aparte, bajo
`artifacts/higgsfield-20261125/`, sin añadir binarios pesados al historial.
No son assets canónicos del runtime ni reemplazan las exportaciones históricas.

| Candidato | Triángulos | Mapas incrustados | Resultado |
| :--- | ---: | :--- | :--- |
| Personaje urbano con chaqueta | 47,321 | Color, normal y ORM, 4096² cada uno | Una malla sin rig |
| Sedán verde petróleo | 44,745 | Color, normal y ORM, 4096² cada uno | Una malla sin pivotes móviles |

## Derivados de autoría · 26 noviembre 2026

Se prepararon dos derivados desde los GLB con tangentes del paquete original.
El personaje intermedio conserva 28.391 triángulos y sus tres mapas. El sedán
mide 4,4 m, apoya las ruedas en el suelo y ofrece cuatro pivotes que se pueden
rotar por separado en el editor. Las pruebas, las medidas y los comandos están
en las fichas del [personaje](../../assets/higgsfield-20261125/character-lod-review.md)
y del [sedán](../../assets/higgsfield-20261125/sedan-review.md).

## Verificación y preparación de las fuentes

Los originales pasan Khronos glTF Validator 2.0.0-dev.3.10 con cero errores,
una advertencia de tangentes y cuatro hints de bufferView cada uno.
Se reutilizó `tools/export_human_tangents.cjs` y MikkTSpace 1.1.1 para crear
derivados separados: ambos pasan el validador completo con **cero errores y
cero advertencias**. El generador de tangentes cuenta cero triángulos UV
colapsados en ambos; no necesitó fallback. Se preservan originales y reportes.

Blender 4.3.2 importó los originales y produjo vistas opuestas con Cycles CPU,
24 muestras y resolución 1000². Revisión visual realizada sobre esas imágenes;
no es una prueba del renderer del juego, animación ni rendimiento.
El primer render falló porque Blender carece de OpenImageDenoise; se repitió
sin denoising, sin alterar los assets.

## Diferencias observadas y trabajo necesario

- Personaje: silueta, prendas y materiales legibles. La pose recibida está
  más próxima a T que a la A solicitada; manos, dedos y axilas requieren
  retopología y pruebas de deformación. Altura medida: 1.85 m frente a 1.80 m
  solicitados. Sin esqueleto, pesos, correctivos ni clips.
- Coche: carrocería y neumáticos definidos, pero cristal/interior y emblema
  frontal necesitan revisión de diseño. Longitud medida 4.025 m frente a 4.4 m
  solicitados. Ruedas, puertas y cuerpo llegan fusionados en una sola malla.
- Los pivotes están centrados; confirmar metros, Y-up y avance +Z al convertir.
  No asumir que `auto_size` satisface la escala solicitada o los ejes de ambos.
- Antes del runtime: revisar términos del proveedor aplicables a la cuenta,
  corregir topología y escala, vincular a los 49 huesos o pivotes existentes,
  generar LODs/proxies y convertir a buffers nativos incrustables. Medir costes
  y comparar en las cámaras reales. No introducir una descarga remota al jugar.

La generación fue autorizada; no se atribuye una licencia global ni una cesión
de derechos comerciales no comprobada. El objetivo AAA continúa siendo una
meta artística: estos modelos son insumos de autoría con integración pendiente.

## Reproducción de los derivados

Dentro del paquete de revisión, cada original tiene `source-manifest.json`.
Desde la raíz del repo, con los binarios en la ruta de artefactos:

```sh
npm install --prefix artifacts/gltf-tools --ignore-scripts --no-audit --no-fund --no-package-lock --save-exact mikktspace@1.1.1 gltf-validator@2.0.0-dev.3.10
node tools/export_human_tangents.cjs artifacts/higgsfield-20261125/dc-hf-character-urban-01 artifacts/higgsfield-20261125/character-rebuilt artifacts/gltf-tools/node_modules/mikktspace
node tools/qa/validate_glb.cjs artifacts/higgsfield-20261125/character-rebuilt artifacts/gltf-tools/node_modules/gltf-validator
```

Repetir con `dc-hf-vehicle-sedan-01` y un destino nuevo para el coche.
No se necesita una nueva generación de pago para repetir esta preparación.
Reversión: retirar únicamente los candidatos/documentación de esta unidad;
el HTML y las partidas no cambian.
