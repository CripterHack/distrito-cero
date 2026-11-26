# Residente del Mercado · v0.20.29 · refs #5

Un residente de chaqueta espera junto a la marquesina y recorre un tramo de la acera del taller. El jugador puede seguirlo, verlo volver y tocar el claxon desde un vehículo cercano. Permite revisar en movimiento el personaje creado para Distrito Cero con Higgsfield/Tripo. La ficha del original conserva el job, el prompt y las huellas. [Procedencia](../../assets/higgsfield-20261125/manifest.json).

## Recorrido y criterios

| Situación | Resultado observable |
| --- | --- |
| Llegar a la marquesina (154,5; 130) | Un civil espera o camina por la acera a un metro del centro de la parada. |
| Seguirlo hacia la esquina | Recorre 19 m a 1,35 m/s. En los extremos espera 2,4 s y gira para volver. |
| Tocar el claxon cerca del residente | Acelera a 3,78 m/s por la misma acera. Mantiene el modelo, alterna los pies y vuelve a caminar al calmarse. |
| Alejarse y volver | El residente sigue en el barrio. El reparto mantiene sus 72 plazas y las partidas anteriores se pueden abrir. |
| Acercar o retirar la cámara | Se alternan las dos mallas con histéresis. En calidad equilibrada pasa a detalle alto a menos de 12,8 m y baja al sobrepasar los 19,2 m. |

[Integración y reversión](plan.md) · [Tareas verificadas](tasks.md) · [Huellas y pruebas](evidence.md).

## Lectura nocturna en la parada

El difusor situado bajo la cubierta de cada marquesina usa la lista de luces puntuales existente. Su cono apunta hacia abajo y se extingue a 4 m. En el menú de pausa, el control de luz permite comparar los extremos de día y noche. En la cámara preparada desde la calzada, el contraste mediano entre la chaqueta y el fondo pasó de 20,29 a 39,15 niveles de luminancia sobre 255 por la noche. En el taller, a la misma hora, ningún píxel cambió más de cuatro niveles por canal. El montaje sigue visible durante el día. [Comparación en la calzada](../../qa/mercado-luz/README.md).

## Apoyo del jugador

Al llegar a pie desde el taller, el avatar pisaba visualmente a 0,015 m en un bordillo de 0,150 m. La presentación consulta las mismas superficies de la manzana que se dibujan en WebGL2, suaviza el cambio de altura en 36 cm y coloca la sombra sobre el plano superior. En el mismo instante y con la misma cámara, la suela llega a 0,150 m y la sombra a 0,153 m. La altura del salto sigue siendo relativa al suelo para el rig. [Regresiones de superficie y acceso](../../tests/player-surface.test.cjs).

## Mallas y presupuesto

| Recurso | Presupuesto en esta candidata |
| --- | ---: |
| Malla cercana / lejana | 9.773 / 5.331 triángulos |
| Módulo embebido con mallas, atlas y animaciones | 716.567 bytes |
| Atlas PBR WebP | 131.180 bytes |
| Atributos de las dos mallas en GPU | 2.899.968 bytes |
| Textura RGBA8 de 512 × 1536 con dos niveles adicionales de mipmap | 4.128.768 bytes |

Las posiciones y las UV conservan precisión de 32 bits para mantener las pequeñas superficies de los dedos. La conversión protege la separación del índice y los pliegues de ambas rodillas. La instancia aprovecha una fila de la textura de poses del reparto y ocupa un dibujo de color y otro de sombras si la pasada está activa. Los tamaños de GPU describen los buffers y los niveles de imagen, antes de la gestión interna del controlador. Falta el perfilado temporal en hardware físico.

## Reconstrucción

Se requieren Blender 4.3.2 con SciPy y NumPy, Node, Python con Pillow y meshoptimizer 0.23.0 para autoría. `MESHOPTIMIZER` apunta al directorio local del paquete. `ORIGINAL` es el GLB del personaje con índices articulados, SHA-256 `9b74d3e839623de66f5ccffb822cd74dad85f4afa0dd6d18a333c911095c06e7`. Para obtener y revisar los tres ciclos se puede usar la [receta del modelo portátil](../../assets/higgsfield-20261125/body-motion.md).

```sh
mkdir -p artifacts/reparto
blender -b -t 2 --python-exit-code 1 -P tools/rig_higgsfield_character.py -- "$ORIGINAL" artifacts/reparto/modelo
cmp artifacts/reparto/modelo/character-walk.glb assets/higgsfield-20261125/character-walk.glb
node tools/prepare_market_ped.cjs "$MESHOPTIMIZER" artifacts/reparto/market-ped-data.js
cmp artifacts/reparto/market-ped-data.js src/market-ped-data.js
python3 build.py --check
node --test tests/market-*.test.cjs
```
