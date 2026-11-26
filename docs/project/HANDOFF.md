# Continuación vigente · v0.20.25 · chaqueta LOD2 · refs #5

La chaqueta LOD2 comparte la malla intermedia existente, con pose/apariencia por
instancia y un solo propietario GPU. [Contrato, evidencia y coste](COLLAR-LOD.md).
No repetir el atlas de #63, la costura de #64 ni los experimentos de conectividad:
los últimos corrigieron dos píxeles pero no la cobertura completa muestreada.

La base #64 (`2b72a688`) aprobó sus tres workflows y nueve jobs. Esta unidad
mantiene master como destino y depende de #63/#64; ninguno se ha integrado ni
desplegado. La nueva CI se registra por su commit exacto en el PR.

**Siguiente paso concreto:** distinguir las limitaciones restantes de la piel
LOD2 y la cobertura fuente/LOD1 con los datos guardados. No llamar a las sondas
sin impacto 'sin intersección'. Comparar los pequeños márgenes negativos con
la geometría anterior y las cámaras de juego antes de cambiar la piel, el rig
u otra proporción. Las referencias completas de cuatro perfiles/tres poses,
los IDs de anclas y las mediciones están en la evidencia del contrato.

La [evidencia final](../../qa/collar-lod-v02025/README.md) conserva 42 vistas,
173 guardas y 110 criterios aprobados; comparación 304/304. Los cinco márgenes
negativos son menores de 0,2 mm: cuatro nuevos frente a la prenda anterior y
uno antes desconocido, sin puntos nuevos visibles en las cámaras revisadas.
Las 492 sondas sin impacto siguen desconocidas. No convertir el gate de
cobertura en una afirmación de cero colisiones.
También revisar las 190 combinaciones fuera del core LOD0/1 que pierden
cobertura al reutilizar LOD1, aunque la pérdida total frente a LOD0 baja de
1.365 a 841. Conservar IDs y cámaras; no aprobar sólo por el balance neto.

La política añade 2.181 triángulos por actor LOD2 y elimina 155.712 bytes de VBO,
un buffer de instancias, un VAO y la reducción anterior. Medir el coste real
con reparto en hardware físico; no extrapolar FPS desde SwiftShader. Siguen
pendientes arte global y adaptación de los modelos Higgsfield. #5/#6/#7 abiertos.

### Continuidad de los modelos Higgsfield

La unidad de autoría posterior al merge conserva una versión intermedia del
personaje y separa las ruedas del sedán. Para continuar el personaje, revisar
los puentes entre dedos con poses de flexión antes de transferir pesos del
rig de 49 huesos. Para el sedán, contrastar el habitáculo, los asientos y las
puertas con los puntos de acceso del vehículo nativo. Las fichas identifican
los archivos que se deben abrir y su procedencia. [Modelos y recetas](HIGGSFIELD-ASSETS.md).

## Registro anterior · v0.20.24

# Continuación vigente · v0.20.24 · continuidad cervical LOD2 · refs #5

La abertura posterior está corregida y verificada en la malla nativa y diez
poses cervicales preparadas. **No repetir ese diagnóstico ni el atlas de #63.**
[Contrato, reproducción, costes y límites](LOD-SEAM-CONTINUITY.md).

**Siguiente paso concreto:** resolver la intersección del cuello con la chaqueta
en LOD2. El diagnóstico separó ambas superficies: existen caras de prenda, pero
la piel queda por delante tras simplificar. En la vista posterior, píxel
(267,547), la chaqueta pasa de estar 28,52 mm delante en LOD0 a quedar 6,07 mm
detrás en LOD2; en perfil (447,548), de 43,85 mm delante a 10,44 mm detrás.
Reproducir en las cámaras fijadas antes de modificar la reducción; no tapar el
problema con color, culling ni caras inventadas. Conservar las pruebas de nuca.

Antes de integrar, revisar la nueva CI y la dependencia #63, cuyo HEAD `a72060b`
aprobó tres workflows/nueve jobs. Esta unidad se propone contra master para
mantener los gates; integrar primero #63 reduce el diff. No se ha desplegado.
La aceptación artística, adaptación de candidatos Higgsfield y evaluación en
hardware físico siguen pendientes. No cerrar los issues globales #5/#6/#7.

## Registro de la unidad anterior · atlas nativo

# Continuación vigente · atlas nativo v0.20.23 · refs #5

## Unidad actual

El atlas facial está integrado en la candidata del PR #63. Se ha adaptado
el shader cervical, la base tangente, la simplificación LOD y la exportación.
[Reproducción y límites](NATIVE-FACE-ATLAS.md). No repetir el diagnóstico ni
copiar los mapas anteriores sobre las nuevas UV.

**Siguiente paso:** revisar la candidata y la CI del HEAD exacto; después,
continuar la revisión artística del rostro, cuello y cabello y medir coste
en dispositivos físicos. Los candidatos Higgsfield aún requieren retopología,
rig/pivotes y adaptación al juego antes de sustituir recursos canónicos.
No cerrar los issues globales #5/#6/#7 por esta unidad técnica.

## Evidencia local de la candidata

Node **695/695**, benchmark **36/36**, primeros planos **32/32** y recuperación
WebGL **25/25**. [Resultados y hashes](NATIVE-FACE-ATLAS.md). La comparación
final confirma corregidos los parches angulares y el punto oscuro detectados
en las primeras candidatas. Persisten huecos LOD2 anteriores y queda revisión
artística. La CI del nuevo commit
se registra separadamente y no se ha desplegado la candidata.

## Ajuste del gate de autoría

El primer CI de `d85a1f8` aprobó el benchmark, pero autoría falló porque dos
aserciones exigían las UV defectuosas v1. [Registro y arreglo](NATIVE-FACE-ATLAS.md).
La integración de tangentes ahora pasa 5/5 para v2 y 5/5 para el export histórico;
conserva tolerancias y exige cero fallback en v2. El HTML mantiene su hash.
Comprobar la nueva CI del commit de corrección, no reutilizar el resultado anterior.

## Registro de etapas anteriores de #63

## Continuación: derivado UV reproyectado

Ya existe una [receta de UV y horneado](UV-REBAKE.md) con cero cartas colapsadas
en el derivado portable. Conserva geometría por esquina, rig y clips. No
rehacer el diagnóstico de 984 triángulos ni confundir el derivado con el
recurso canónico del runtime, que continúa intacto.

**Siguiente paso vigente:** corregir la transición de color del cuello en
materiales y adaptar pigmento/mezcla cervical del shader nativo para el nuevo
atlas, con comparación en las luces y poses del benchmark real. La reproyección
conserva la costura heredada; no la convierte en una superficie aceptada.
Revisar también el coste de tres mapas 2048² y las 29,016 esquinas de face
antes de integrar. La aceptación artística y rendimiento siguen pendientes.

Los comandos, resultados y reversión están en [UV-REBAKE](UV-REBAKE.md) y
su [plan](../../specs/002-character-benchmark/plan-uv-rebake.md).
Las notas siguientes describen la primera unidad de #63.

## Actualización · 25 noviembre 2026

Base master **f9454df7e3325a3cf4d516a0374c2ccb9565090c**, producto 0.20.22.
PR #61 ya integrado: no repetir escopeta/revólver. PR #62 sólo actualiza Pillow.
Los apartados inferiores conservan la entrega anterior como historia.

Trabajo actual: dos [modelos Higgsfield](HIGGSFIELD-ASSETS.md), rechazo de
GLB/manifiesto modificados durante la validación y diagnóstico UV por triángulo.
[Regresión de integridad](../../specs/002-character-benchmark/plan-validation-input-integrity.md),
[auditor UV y evidencia](../../specs/002-character-benchmark/plan-uv-audit.md).
Ver [STATE](STATE.md) para resultados locales. Runtime/build intactos.

**Primera tarea:** preparar receta de reparametrización y horneado del humano
canónico, usando los IDs del auditor: 981 triángulos en V=1 del GLB más tres
faciales, `1852`, `2200`, `5790`. No extender coordenadas a ciegas ni apagar
el normal map para ocultarlo. Comparar costura cervical, color y normales en
las luces/cámaras del benchmark y conservar rig/atributos.

Los nuevos candidatos requieren revisión de términos del proveedor y adaptación:
manos/topología/49 huesos para el personaje, piezas/pivotes para el coche;
ambos necesitan escala/ejes, LODs, proxies y pruebas en el renderer real.
El pipeline de tangentes puede repetirse sin nuevas generaciones de pago.

```sh
python3 tools/export_current_human.py --output artifacts/human-uv-next
node tools/qa/audit_uv.cjs artifacts/human-uv-next/dc-human-0.20.22-neutral.glb > artifacts/human-uv-next/uv-audit.json
node --test tests/glb-validation-contract.test.cjs tests/uv-audit.test.cjs
```

El auditor devuelve exit 1 para la deuda conocida; conservar su JSON.
Retirar las herramientas/tests/docs de esta unidad revierte sus efectos;
los modelos están separados y el HTML conserva su hash. #5/#6/#7 siguen
abiertos. No se requiere migración de partidas.

## Registro anterior a la integración de #61

## Base cerrada

Master **39b7647f1c763ab9e35e8c507723fc4cf5cfc57f**, árbol
**1820cda051434f5596c20c2b3c5fa9de2afc7661**, producto 0.20.21.
[#60](https://github.com/CripterHack/distrito-cero/pull/60) y su push están verificados.
No repetir pistola/escopeta, el shader de #59 ni los temporizadores de #58.

## Unidad presente

[Plan](../../specs/003-weapon-contact/plan-shotgun-revolver-handoff.md), CONTACT-04/05.
Habilita únicamente escopeta ↔ revólver en captureSwitch. Conserva cuerpo/manos,
pieza retornando, selector congelado y caché canónica, con una sustitución de
modelo y rechazo de un tercer modelo mostrado. Arco existente 0.12 m, 0.90 s
cosméticos. Sin otro solver, tracker o reloj. Acciones, munición, partidas,
longitudes, geometría, rig, pies y renderer no cambian.

Los tests comparten los barridos y helpers anteriores. La prueba dirigida sobre
la base dio cuatro fallos por captura/discontinuidad y una salvaguarda aprobada.
La misma selección tras la corrección dio cinco aprobadas. La primera tentativa
del archivo entero fue interrumpida por el límite del ejecutor y no se cuenta
como corrida completa. QA dio tres fallos por catálogo ausente y luego 22/22.

Sight añade cuatro rutas al catálogo existente: **148 checks = 56+44+48**,
28 intercambios de 61 estados más before. Conserva orden previo, resolución,
todas las capturas, cinco guardas, tres productores y límites de 1800 s y 40 min.
Base no aumenta: su PR previo consumió 1554.493 s. Comparar las 24 secuencias
anteriores con #60 y revisar cada secuencia nueva antes de integrar.

## Verificación y publicación

La base restaurada con **historial Git real** aprobó 658/658 Node. Suite completa
de candidata, contratos Python, autoría/build/export, navegador, CI y revisión
se registran con resultados reales en el PR enlazado desde
[#6](https://github.com/CripterHack/distrito-cero/issues/6). No inferir un merge de
esta nota. Revisión propia, no independiente. Verificar el push después del merge
por separado y no confundir HTTP local con aceptación del sitio público.

```sh
python3 build.py --check
node --test --test-concurrency=4 tests/*.test.cjs
python3 tests/qa_selection.test.py
python3 tests/qa_runner.test.py
python3 tests/ci_workflow.test.py
xvfb-run -a python3 -m tools.qa.run --suite sight --headed --timeout 1800
```

## Limpieza completada y pendientes

El usuario renovó la autorización para retirar ramas. Las 16 obsoletas y el
auxiliar de auditoría fueron retirados tras respaldo completo, restauración y
comprobación de SHA/protección/PRs. [Registro y recuperación](BRANCH-CLEANUP.md).
No volver a tratar esa limpieza como bloqueada. Las nuevas ramas de trabajo sólo
permanecen mientras sean activas. Nunca integrar helpers en producto/ascendencia.

#5 conserva UV/materiales/procedencia y arte global. #6 conserva otras parejas,
herramientas/pesados, anatomías/giros, cortes prioritarios y coste por actor/LOD.
#7 conserva recorrido/personas/hardware. No fabricar sus criterios. Revertir
esta unidad con su versión/build no migra ni borra partidas.

## Comprobación local de esta candidata

667/667 Node completos, 148/148 Python vigentes, autoría/build/export e invariancia
aprobados. 96 documentos sin enlaces locales rotos. El primer pase Python detectó
dos fixtures de conteos antiguos, que se corrigieron antes de repetir las quince
suites. El renderer y la CI siguen siendo gates separados.
