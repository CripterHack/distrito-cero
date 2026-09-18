# v0.20.1 · Coherencia · 2026-09-18

Parche parcial de #6 / #21: pistola y revólver colocan su montaje según el ojo articulado durante el apuntado, conservando las superficies relativas de manos y objeto. El retroceso se aplica alrededor de la empuñadura sobre la referencia estable. Recarga/equipamiento liberan la alineación gradualmente. Los límites de alcance tienen prioridad en poses extremas. Sin cambios de malla, pesos, esquemas o reglas de munición. Armas largas y ópticas mantienen su postura anterior.

La revisión final incluye el primer intervalo al equipar y apuntar: preparación visual gradual de armas cortas, sin retrasar el disparo o la transferencia de munición. En neutral, el máximo medido a 60 pasos/s pasa de 76.70 a 26.21 mm. Se añaden cuatro regresiones y dos comprobaciones del renderer.

[Plan y alcance](specs/003-weapon-contact/plan-sidearm-sight.md). La aceptación requiere pruebas y CI del commit exacto, no esta nota.

# v0.20 · Coherencia · 2026-09-16

Versión de producto 0.20.0, prototipo. Fuente canónica en `version.json` e identificación coherente en inicio, pestaña, pausa y `build-info.json`. Construcción determinista con `--check` no mutante. No se cambian esquemas ni claves de guardado.

Consolida los cambios integrados desde la publicación de v0.19: QA portable, persistencia HTTP nativa, recuperación WebGL y protección de generaciones retiradas, benchmark de personajes, pesos de mangas, codos ópticos, contacto de falanges y pulgares y apoyo entre manos en armas cortas. Añade el correctivo de contorno de la unión palma/pulgar recuperado de la rama pendiente.

La última corrección modifica sólo posición/normal de una zona de piel, hasta 4 mm, preservando el apoyo palmar medido, pesos, UV, topología y 49 huesos. Mantiene las reglas y animaciones existentes. Alineación ojo/mira, aprobación artística y vertical slice siguen abiertas en #5/#6/#7. [Guía](docs/v020/GUIA.md).

### Revisión de publicación de 0.20.0

Se fijan los saltos de línea de texto mediante `.gitattributes` y se comprueba el checkout con las tres políticas de `core.autocrlf`. Evita diferencias de huella debidas sólo a CRLF; medios binarios, contenido del juego y formato de partidas no cambian.

# v0.19 · Contacto articulado · resumen histórico

Montaje palmar del equipo, posturas coordinadas, índice independiente, recargas y selector translúcido. Base original importada en `23f9e9d`. La evidencia de esa entrega permanece en `docs/v019/` y `qa/v019/`; no se atribuye a v0.20.

# v0.18 · Manejo y contacto · resumen histórico

Orientación de muñecas, apoyos por familia, retroceso y manipulación de piezas visibles. Guía y límites originales en `docs/v018/`.

# v0.17 · Arsenal

Catálogo de catorce opciones, celdas y munición por partida, armas originales compartidas, poses de uso/recarga, Gauss cargable, EMP temporal y binoculares con zoom real y GPS. Pruebas actuales y límites en `docs/v017/VERIFICACION.md`. Se conservan personajes y perfiles de Rasgos v0.16.

# v0.16 · Rasgos

- Ajuste cervical corto con pivotes coherentes, sin comprimir el rostro.
- Giro deliberado distribuido parcialmente hacia el tórax para reducir torsión localizada.
- Once opciones de cabello con geometría/LOD compartidos y cejas separadas.
- Longitud cervical, volumen de pelo y vinculación de cejas editables y persistentes.
- Compatibilidad de perfiles anteriores y biblioteca de partidas preservada.
- Pruebas de CPU/GPU, geometría real, editor, catálogo, campaña y bucle continuo.

# v0.15 · Integración cervical

Nueva masa cervical en ancho y profundidad, perfiles distintos de nuca/garganta y transición submandibular gradual. Complexión vinculada al cuello sin alterar huesos o colisionadores, grosor independiente acotado y abertura de chaqueta/cierre sincronizados. Revisión de pesos para reducir compresión bajo el mentón en giro combinado. Normales del morph de cuerpo calculadas con Jacobiano completo. Misma topología, rig de 49 huesos, juego, creador y catálogo. Detalle y límites en `docs/v015/`.

# v0.14 · Equilibrio cervical

Corrección dirigida del abultamiento cervical inferior a la mandíbula, nuevas influencias regionales que mantienen rígido el mentón, normales continuas y transición de pigmento/rugosidad. Grosor de cuello y abertura de prenda sincronizados, con normal corregida por el Jacobiano del morph. Cuello y cabeza coordinados sin alterar objetivos de muñeca, pies ni reglas físicas. Dos estudios de revisión cervical en el creador. Caída del borde exterior del hombro moderada. Se conservan la topología y las otras partes, catálogo, campaña y mundo. Detalle, pruebas y limitaciones en `docs/v014/`.

# v0.13 · Movimiento orgánico

Apoyos posteriores a pose del torso, contacto talón/punta continuo, memoria visual acotada de pies, cadencia compartida por distancia real, brazos de carrera y respiración. Objetivos de volante alcanzables y perfiles de dedos por contexto. Superficies de prendas suavizadas sin inflación geométrica y normales de manos continuas. Microdetalle ligado al modelo con filtrado, ojos esféricos y mirada intermitente. Estudio con poses de conducción/alcance, enfoque de pies y cámara lenta exclusiva del editor. Se preservan creador, biblioteca de 12 historias y mundo. Detalle de límites y pruebas en docs/v013.

## Historial anterior

# v0.12 · Continuidad anatómica

* Cuello con base torácica y contorno cervical corregido. Abertura de la chaqueta y unión torso/mangas suavizadas.
* Muñecas/palmas más contenidas, uñas ajustadas al dorso real, detalle procedural de piel.
* Skinning por cuaterniones duales sobre el mismo rig de 49 huesos para todo el reparto.
* Grosor de cuello, inspección cercana, iluminación de estudio y comparación no destructiva en el creador.
* Búsqueda de partidas/personajes y orden por nombre, actividad o progreso. Catálogo y respaldo anteriores conservados.
* HTML y modelo GLB reproducibles, pruebas actualizadas y comparaciones del renderer.

# Cambios

## 0.11 · Identidad

- Editor inicial y edición desde Pausa con simulación de vista previa aislada y render WebGL real.
- Cuatro estilos base, nombres, complexión acotada, contorno facial, colores y cuatro variantes de pelo.
- Suavizado de perfil de prendas, volumen torácico/abdominal y collar. Rig y manos de v0.10 conservados.
- Aplicación de apariencia por actor mediante textura compartida, con sombras coherentes y LOD.
- Doce partidas con IDs únicos, nombres y revisiones, guardado activo y copias independientes.
- Importación no destructiva de JSON individual, grupo y versiones anteriores.
- Renombrado, exportación, respaldo completo y borrado confirmado.
- Detección de almacenamiento denegado/cuota/datos corruptos/revisiones obsoletas, sin borrado automático.
- Recarga confirmada tras conflicto, cancelación de borrador y reversión si falla el guardado de apariencia.
- Se conservan campaña, policía, territorio, daño e interacciones con conductores.

Los cambios anteriores están documentados en `docs/` y `assets/`. No se renombra un recurso histórico como si fuera nuevo.
