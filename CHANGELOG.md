# v0.20.22 · Coherencia · 2026-10-01

Escopeta ↔ revólver conserva pose y pieza durante cambio libre y cancelación de
recarga, incluido selector congelado y reselección durante retorno. Reutiliza el
sistema existente, sin cambiar munición, partidas, geometría, rig ni el renderer.
No retrasa disparo, selección o nueva recarga. La cobertura del productor existente
incorpora cuatro secuencias, sin aumentar timeouts ni añadir runners.

[Plan y límites](specs/003-weapon-contact/plan-shotgun-revolver-handoff.md).
Se retiraron las ramas históricas auditadas con autorización renovada del usuario
y respaldo completo restaurado. [Recuperación](docs/project/BRANCH-CLEANUP.md).
La integración y la evidencia final se consultan en el PR vinculado desde #6.

# v0.20.21 · Coherencia · 2026-09-30

Pistola ↔ escopeta conserva pose y pieza mostradas en cambio libre y desde
recarga, incluida vista congelada y reselección. Reutiliza la transición existente
sin retrasar acciones, modificar munición, partidas, geometría o rig.
No altera la optimización gráfica de #59.

Regresiones de ocho estados y cuatro configuraciones, caché fría/inicializada y
cuatro secuencias adicionales en el renderer existente. Conserva los veinte casos
anteriores y sus guardas. [Plan](specs/003-weapon-contact/plan-pistol-shotgun-handoff.md).
CI e integración se registran en el PR correspondiente, no se anticipan aquí.

# v0.20.20 · Coherencia · 2026-09-29

Variante del fragment shader para lotes estáticos con materiales básicos comprobados.
Conserva la ruta general para personajes, datos dinámicos, mixtos o desconocidos.
Elimina trabajo de materiales detallados imposible en esos lotes, sin quitar
geometría, reducir resolución o cambiar iluminación, sombras o capturas.
No cambia controles, campaña, munición, assets, rig ni partidas.

Trece regresiones nuevas cubren clasificación, selección, uniforms y recursos.
Las sondas controladas son evidencia local, no FPS ni una aprobación anticipada
de las suites completas. [Plan](specs/001-reliability/plan-static-material-program.md).
El estado real de CI, revisión e integración está en el PR vinculado desde #6.

# v0.20.19 · Coherencia · 2026-09-28

Pistola ↔ SMG conserva pose y pieza mostradas en cambio libre y desde recarga,
selector congelado y retorno. Reutiliza captura/montaje de0.90 s y caché canónica,
sin alterar acciones lógicas, munición, geometría, rig o partidas.

El arco de 0.08 m falló a −7.772 mm en chaqueta. Se verifica 0.12 m sólo para esta
pareja, manteniendo la tolerancia de 2 mm. Los bucles existentes suman64 casos
dirigidos y152 poses de culata. Se mantienen exclusiones de terceros modelos.
El catálogo gráfico pasa de 94 a 112 checks, veinte secuencias distribuidas entre
los mismos tres jobs (48 + 31 + 33), sin elevar límites ni quitar guardas.
[Plan](specs/003-weapon-contact/plan-pistol-smg-handoff.md). Consultar el PR
vinculado en #6 para CI, revisión e integración reales, no inferirlas del conteo.

# v0.20.18 · Coherencia · 2026-09-28

SMG ↔ revólver desde recarga conserva pose y pieza visibles usando captura,
montaje y retorno existentes. Mantiene acciones lógicas inmediatas, munición,
partidas, caché canónica y rechazo de terceros modelos todavía mostrados.

Las regresiones existentes cubren fases activas, selector congelado, retorno,
reselección y caché fría/inicializada. Sight conserva sus 84 checks y añade diez,
en el tercer job existente: 40 +26 +28. No modifica los workflows, los límites
de tiempo, la geometría ni las tolerancias. La transición es cosmética, no una
recarga mecánica certificada. [Plan y criterios](specs/003-weapon-contact/plan-smg-revolver-reload.md).
La evidencia de CI e integración del HEAD está en el PR vinculado desde #6.

# v0.20.17 · Coherencia · 2026-09-28

SMG ↔ revólver libre conserva la pose mostrada usando captura/montaje existentes.
Mantiene acciones lógicas inmediatas y excluye recargas activas, piezas retornando
y terceros modelos mostrados para esta nueva pareja. El arco de 0.08 m fue
rechazado por penetración muestreada de 4.068 mm en chaqueta. Se adopta 0.12 m
sólo tras verificar la geometría de SMG, conservando el límite de 2 mm.

El catálogo gráfico único añade dos casos y ocho checks a la capacidad del job
existente sight-revolver-reload: 40 + 26 + 18 = 84, catorce secuencias. No agrega
jobs ni eleva límites o tolerancias. [Plan](specs/003-weapon-contact/plan-smg-revolver-free.md).
Integración/CI y verificación posterior se registran en el PR del HEAD exacto.

# v0.20.16 · Coherencia · 2026-09-27

Rifle ↔ revólver desde recarga reutiliza la captura de pose y pieza visible,
el retorno cosmético de 0.90 s y la caché canónica existente. Conserva selección,
cancelaciones, munición, partidas y prioridad inmediata de disparo/nueva recarga.
Mantiene excluido un tercer modelo mostrado ajeno a la pareja.

La regresión existente cubre 128 casos dirigidos y 304 poses de culata, siete
fases de recarga, selector congelado, reselección de pieza retornando y caché
fría/inicializada. Sight conserva los 66 checks anteriores y añade diez en
una partición disjunta: 40 + 26 + 10, doce secuencias de 61 estados cada una.
Las cinco guardas compartidas siguen siendo bloqueantes y se cuentan una vez.
Sin cambios de rig, geometría, solver, tiempos lógicos o guardados. Se mantienen
1800 s por productor y 40 minutos por job, con mayor presupuesto agregado de
runners. [Plan y límites](specs/003-weapon-contact/plan-rifle-revolver-reload.md).
Verificación remota e integración pendientes al escribir esta candidata.

# v0.20.15 · Coherencia · 2026-09-27

Intercambio **libre rifle ↔ revólver**, conservando la pose mostrada, las
palmas, coordinación corporal y dedos. Reutiliza el montaje de 0.90 s y el
arco frontal existente, medido para esta pareja sin relajar la tolerancia.
Selección, cancelaciones y acciones reales inmediatas. Recarga activa,
devolución de pieza pendiente y otro modelo mostrado quedan excluidos.

Tres tests Node adicionales y extensión de los observadores existentes,
selector congelado, reversión antes/después del reemplazo, marcha, prioridad
y persistencia. Sight conserva sus 58 checks y añade ocho: 40 base + 26 cruces,
diez secuencias, 61 estados por intercambio. No cambia workflows, presupuesto,
geometría, rig, munición ni partidas. [Plan y límites](specs/003-weapon-contact/plan-rifle-revolver-free.md).
Resultados completos e integración: [HANDOFF](docs/project/HANDOFF.md) y PR
del HEAD exacto. Una candidata no implica CI ni publicación aprobadas.

# v0.20.14 · Coherencia · 2026-09-27

El ajuste canónico de los dedos deja de depender del primer equipo mostrado.
Durante rifle ↔ pistola se conserva el cargador anterior, pero su superficie
transitoria ya no inicializa el perfil de la nueva arma. Misma caché de cuatro
entradas, sin precalentamiento, nuevas claves o cambios de geometría, gameplay,
munición, huesos, acciones prioritarias o partidas.

Cuatro regresiones comparan procesos fríos e inicializados, ambas direcciones,
libre/recarga y dos configuraciones. Se comparan ajustes, matrices completas,
palmas y piezas. [Plan y límites](specs/003-weapon-contact/plan-finger-cache-order.md).
Estado de verificación e integración: [HANDOFF](docs/project/HANDOFF.md).

## QA integrada de 0.20.13

PR #50 (`7231aa5`) distribuyó sight en 40 + 18 comprobaciones. Su PR y su
push aprobaron, incluidas ambas particiones, benchmark y Pages. El timeout
anterior de #49 permanece como fallo histórico. No volver a implementar #50.

# v0.20.13 · Coherencia · 2026-09-27

Primer cruce rifle ↔ pistola, libre y desde recarga: continuidad de la pose
visible, coordinación corporal, dedos y cargador anterior. Arco cosmético de
0.90 s con 4 cm frontales adicionales sólo en esta pareja, tras reproducir una
penetración muestreada de chaqueta. No se relajan umbrales ni se cambian piezas,
huesos, controles, disponibilidad, munición, cámara, física o partidas.

Siete regresiones dirigidas; sight conserva sus 40 checks y añade 18 mediante
cuatro secuencias con tecla real. Otros cruces y criterios globales permanecen
pendientes. [Contrato y límites](docs/project/CROSS-FAMILY-HANDOFF.md).
Verificación completa e integración: consultar el PR del HEAD exacto.

# v0.20.4 · Coherencia · 2026-09-23

La excursión longitudinal de los pies se atenúa al acercarse al reposo, como su
elevación e inclinación. Evita la caída brusca del cuerpo al frenar a velocidad
baja, sin cambiar simulación, longitudes óseas, controles o datos persistentes.
Pruebas de fase/velocidad, trayectoria normal sin cambios y parada nativa.
La revisión de superficies de equipo sigue separada. [Detalle](docs/project/GAIT-REST.md).

## Historial conservado

# v0.20.1 · Coherencia · 2026-09-18

## 0.20.3 · Familias largas

Coordinación ocular, apoyo de prenda y filtro de presentación para SMG, escopeta y sniper. Geometría de culata por familia, validación de superficies ampliada y transiciones continuas. Rifle, recurso humano, munición y partidas conservados. Validación final del HEAD e integración registradas en su PR.

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
