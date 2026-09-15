# Corrección de mangas y tórax durante el apuntado · issue #6

## Caso reproducido y causa

Base: `072750bc65d9ceb10ca536bc7f0c7b3146a5b055`, personaje v0.19. Caso del benchmark: `neutral--aim--neutral--front`, semilla 1337 y tiempo 1.25. La chaqueta formaba una membrana visible bajo el brazo de apoyo. Los contactos palmares correctos no demostraban una deformación correcta de la prenda.

La asignación de influencias anterior mezclaba brazos y torso principalmente por la coordenada transversal. En el muestreo de las mangas inferiores desconectadas había hasta **53.33% de influencia de pelvis/columna/tórax**. El tronco inferior también podía recibir hasta **19.61% de influencia del brazo**. Al resolver IK, esas superficies intentaban acompañar partes del cuerpo que no les correspondían.

## Cambio acotado

`tools/rebind_garment.py` reconstruye el reparto de pesos fuera del runtime. Suelda posiciones sólo para analizar adyacencia, identifica las tres superficies separadas bajo el arranque de la axila y fija mangas/tronco a sus grupos. Resuelve una transición armónica sobre la malla conectada del hombro, conservando los anclajes de cuello y capuchón superior. No altera posiciones, UV, normales, conectividad, articulaciones ni anclas de armas.

Las influencias longitudinales del brazo se conservan y renormalizan. La cuantización sigue siendo de cuatro IDs y cuatro pesos que suman exactamente 255. Los puños de manga comparten material con el pantalón, pero se identifican por zona **y por su pertenencia previa al brazo**. No se usa sólo el nombre del material para ligarlos al esqueleto.

El mismo asset se utiliza en protagonista, peatones y conductores. Los LOD se recalculan con el pipeline existente. El número de vértices del detalle máximo no cambia. El número de triángulos simplificados puede variar por el nuevo hueso dominante, por lo que el benchmark registra cada LOD. No hay un solver nuevo por vértice o por frame, física de tela ni una nueva librería durante la partida.

## Fuente y reconstrucción

`assets/garment-binding-source.json` guarda únicamente las influencias previas de chaqueta/pantalón y hashes de sus atributos. No duplica la geometría humana completa. Su origen es el asset SHA-256 `7dedf527bfe9e257c3067a4db063521e09a72d680ed2f8323fedd69a202ee5f4` de la base citada.

```sh
python3 tools/rebind_garment.py
python3 tools/rebind_garment.py --check
python3 tests/garment_binding.test.py
node --test tests/garment-binding.test.cjs
python3 build.py
```

La captura inicial de semillas se ejecuta una sola vez mediante `tools/capture_garment_binding_source.py`, exclusivamente sobre ese hash anterior. No ejecutarla sobre la versión corregida ni sobrescribir la semilla. La reconstrucción normal lee la semilla versionada y rechaza una geometría/UV/normal diferente hasta que se revise la receta. No se reescriben baselines ni informes históricos.

Asset corregido previsto y verificado localmente: `a4f5a6522f0012290bd2fca8d573ca5243388474f72fb026cf5766924e3c8b7d`. El HTML de publicación debe reconstruirse desde la rama actual, que también incluye recuperación WebGL. Las primeras inspecciones locales usaron la base visual original v0.19 con el mismo asset; no se presentan como validación del lifecycle posterior.

## Pruebas y hallazgos de desarrollo

Las tres regresiones nuevas fallaron antes del cambio: contaminación de manga, contaminación de tronco y distancia excesiva de la superficie a su brazo en una pose con pistola. Después de corregir el asset, el muestreo de pistola/fusil/Gauss/EMP/binoculares, agachado y fase de recarga conserva la manga a menos de 9 cm de los segmentos del brazo. Ese límite incluye el grosor y volumen de la prenda: **no es una tolerancia de separación palma/empuñadura**. El máximo local observado fue aproximadamente 6.02 cm.

Cinco tests Python comprueban reproducibilidad, contrato de huesos/atributos, integridad de pesos, preservación de partes ajenas y rechazo de cambios de geometría. La primera prueba visual de desarrollo detectó una selección demasiado amplia de puños que movía una zona del pantalón. Se corrigió el filtro semántico antes de publicar y se añadió una regresión específica. No se ocultan esos intentos fallidos ni se reutilizan como evidencia final.

La CI del PR debe revisar construcción, todas las pruebas Node, receta, benchmark de personajes, manejo, recuperación WebGL y guardados HTTP nativos. Las comparaciones son del motor real con parámetros equivalentes. El benchmark es de fotogramas preparados, no certifica continuidad completa, FPS físicos o ausencia universal de intersecciones.

## Alcance restante

Este cambio corrige la sujeción de la prenda al esqueleto, no reemplaza la anatomía ni implementa contacto físico de falanges. La forma del hombro, la axila superior, el pelo, el rostro y algunas poses extremas siguen necesitando pulido. #5 permanece abierto para aprobación artística y #6 para sus requisitos restantes. #7 no se resuelve con una corrección de asset.

Los GLB humanos anteriores siguen siendo exportaciones históricas, no se anuncian como modelos actualizados por este PR. El juego consume el asset corregido embebido en el HTML. Revertir el PR restaura los pesos anteriores sin migración de partidas.
