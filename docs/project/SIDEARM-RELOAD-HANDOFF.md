# Salida de recarga entre armas cortas · candidata 0.20.12

Base `5c0248f6674abfb39a304a20d407f886fa3a7957`, PR #47 integrado, 0.20.11.
Continuación acotada de [SPEC-003](../../specs/003-weapon-contact/spec.md) e issue #6.
[Plan y registro](../../specs/003-weapon-contact/plan-sidearm-reload-handoff.md).

## Causa y cambio

La captura de #47 excluía explícitamente una recarga activa entre armas cortas.
Al cambiar de selección, la cancelación lógica retiraba inmediatamente la pose
de recarga y, en la pistola, el desplazamiento del cargador. La mano saltaba al
agarre siguiente. La captura y el retorno de piezas ya existían en el montaje
único para las armas largas. No se necesita otro solver.

Se elimina esa exclusión sólo entre pistola y revólver. La duración de sidearms
(0.90 s de simulación, sin cambios) prevalece sobre la duración general de salida
de recarga (0.60 s, conservada para las familias anteriores). La captura visible
anterior a cancelar inputs, o congelada por el selector, contiene sólo datos de
presentación. El cargador retorna mediante el arco existente antes de cambiar
de modelo a mitad de la entrega.

El cilindro actual del revólver pertenece a las piezas rígidas `body`. No existe
un canal animado `cylinder` en esta geometría. Se conserva su transformación
rígida sin inventar apertura, expulsión o reinserción física. El retorno con mano
libre es cosmético. Los targets palmares no son una aprobación artística de
contacto entre dedos y pieza durante todo el arco.

Selección y cancelación son inmediatas. No se transfieren rondas al cancelar ni
se duplican modelos. Disparo/nueva recarga prevalecen y restore descarta memoria
visual. Geometría, longitudes, anclas, física, cámara, disponibilidad, origen
lógico de disparo y partidas permanecen iguales.

## Regresiones y evidencia

Cuatro pruebas nuevas observaron RED en la base antes del cambio mínimo. Cubren
ambas direcciones, siete fases del temporizador y tres configuraciones de cuello,
agachado e inclinación: 42 casos con 72 pasos posteriores cada uno. Comprueban
palmas, longitudes, tres puntos de transformación de pieza, retorno al asiento,
selección/cancelación, munición, lectura pura y convergencia. También cubren
selector congelado, reselección, restore y prioridad de acciones.

El control anterior de exclusiones conserva otras familias y situaciones
indisponibles. Su cláusula de recarga de sidearms se sustituye explícitamente
por este contrato, no por un skip o umbral mayor. Criterios: <1e-5 m inicial,
<30 mm por paso a 60 Hz, <12 mm contra targets y longitudes invariantes.
La batería completa y revisión se registran en el PR del HEAD exacto.

`sight` conserva sus 32 comprobaciones y añade ocho: dos secuencias a 46% de
recarga con tecla real, 62 poses y nueve PNG por dirección. `reloadSwitchCases`
registra las piezas enviadas a `add`, un solo drawEquipment, transformaciones
iniciales y asiento antes del reemplazo. Contrato completo: 40 checks. Usa el
mismo renderer/cámara/escena, no módulos de juego reemplazados en memoria.

## Presupuesto de CI

El sight anterior necesitó 810.767 s de 900 y compartía graphics con ocho suites
más. La ampliación usa un shard sight independiente (1800 s por suite, 40 minutos
de job). Handoff conserva 1200 s y graphics 900 s. Los contratos Bash observaron
RED/GREEN y preservan unión normal/completa sin duplicados, fail-fast desactivado
y artefactos separados. HTTP y permisos no cambian. Los presupuestos del
laboratorio no demuestran FPS o coste por actor.

## Límites y reversión

No incluye familias cruzadas, pesados/herramientas, suavidad de acciones
prioritarias, todos los giros o anatomías. No demuestra colisión de toda la malla,
CCD, calidad artística, UV, hardware ni recorrido/playtest humano. #5/#6/#7
conservan sus criterios. Revertir fuentes/tests/versión/build y contrato de suite
juntos, sin migrar ni borrar partidas.
