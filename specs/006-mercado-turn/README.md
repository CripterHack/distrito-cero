# Media vuelta del residente del Mercado · v0.20.30

Al llegar a la marquesina o a la esquina, el residente debe cambiar de dirección recolocando cada pie y trasladando el peso al otro. En v0.20.29 cambiaba la orientación de toda la instancia mientras reproducía el reposo. El punto donde apoyar cada suela debe poder comprobarse en el mundo y en ambos niveles de detalle.

| Escena | Criterio |
| --- | --- |
| Llegada a cualquiera de los dos extremos | Una media vuelta completa dentro de la parada de 2,4 s. El origen del actor permanece en su acera. |
| Pasos de giro | Cada pie se despega y vuelve a apoyar. El otro sostiene el cuerpo sin barrer el suelo. Comprobar el desplazamiento horizontal de las suelas y la altura respecto al pavimento. |
| Claxon durante el giro | Se conserva la fase y el residente acelera la salida hacia el tramo disponible. |
| Reproducir el GLB fuera del juego | La cuarta acción se puede seleccionar por separado y mantiene su orientación final en la última clave. |

La malla de referencia proviene de la generación de Higgsfield ya integrada. [Procedencia](../../assets/higgsfield-20261125/manifest.json) · [Residente y recorrido anteriores](../005-mercado-character/README.md).

## Reproducir la animación

En el juego, acercarse al Taller del Mercado (168, 96) y seguir al residente de chaqueta entre Z = 130 y Z = 149. En cada extremo, espera 0,5 s antes de empezar la media vuelta. Recoloca los pies durante 1,4 s y permanece 0,5 s en la nueva dirección antes de caminar. Si oye el claxon durante el giro, aumenta la cadencia desde la fase actual.

En un visor glTF, abrir el [GLB](../../assets/higgsfield-20261125/character-walk.glb), seleccionar **Giro** y desactivar la repetición. La última clave deja al residente de espaldas a su orientación inicial. En la escena editable de Blender, la acción empieza en el fotograma 226. [Integración y reversión](plan.md).

## Reproducir el recurso de calle

Con Node, Python, Pillow y meshoptimizer 0.23.0 en autoría, ejecutar los siguientes comandos desde la raíz. `MESHOPTIMIZER` es la ruta al paquete instalado.

```sh
mkdir -p artifacts/giro
node tools/prepare_market_ped.cjs "$MESHOPTIMIZER" artifacts/giro/market-ped-data.js
cmp artifacts/giro/market-ped-data.js src/market-ped-data.js
python3 build.py --check
node --test tests/market-*.test.cjs
```

El módulo de calle ocupa 749.331 bytes, 32.764 más que el anterior. Las mallas tienen 9.773 y 5.331 triángulos. Comparten atlas, rig y pistas. El HTML autónomo ocupa 11.548.017 bytes.

[Comparación del calzado en el juego](../../qa/market-turn-v02030/README.md) · [Escena editable y cámaras](../../assets/higgsfield-20261125/giro-estudio.md) · [Mediciones y huellas](evidence.md).
