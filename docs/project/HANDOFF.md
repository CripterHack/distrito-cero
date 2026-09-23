# Verificación local de familias largas: preparada para PR

Base remota `6d1b75637680386f2ba86453d1272b21ff53c6e4`, producto 0.20.3. 519 Node y 92 Python locales aprobados. La repetición gráfica aislada verificó 24 checks/48 PNG sobre el HTML nuevo, con revisión visual de las tres familias. Leer [plan y límites](../../specs/003-weapon-contact/plan-longarm-families.md) y [ADR 0004](../adr/0004-longarm-family-docks.md). Publicación y CI exacta todavía deben comprobarse en el PR. No cerrar #6 sólo por el éxito de esta unidad.

# Continuación actual · familias largas 0.20.3

Base remota `6d1b75637680386f2ba86453d1272b21ff53c6e4`. #29/#30 y #33/#34 ya están integrados. No repetir sus arreglos ni presentar Actions históricos fallidos como estado actual de master. Los tres jobs de Verify de la base `35663565966` aprobaron.

Se amplía el montaje existente a SMG, escopeta y sniper. Leer [ADR 0004](../adr/0004-longarm-family-docks.md) y [plan](../../specs/003-weapon-contact/plan-longarm-families.md). El rifle conserva su comportamiento y geometría. Las nuevas referencias/proxies se contrastan con bytes y triángulos reales. No hay otro solver ni cambios persistentes.

La prueba inicial reproduce las tres desalineaciones. Hay cobertura de 54 combinaciones centrales, ciclos nativos, equivariancia, geometría ajena intacta y controles negativos de superficie. El primer run gráfico perdió contexto antes de capturar y está separado de su repetición. La CI del nuevo HEAD y sus artefactos deben revisarse antes del merge autorizado. Registrar resultados nuevos, no copiar cifras históricas como actuales.

#5 sigue exigiendo revisión artística y procedencia de autoría. #7 sigue exigiendo recorrido sin teletransportes, playtest humano y GPU identificada. El cierre amplio de #6 requiere revisar todos sus criterios, no sólo una pose neutral. No fabricar aprobación artística, cinco participantes, FPS físicos ni cierre de issues por haber generado un plan.

Git local no resolvió GitHub. Snapshot recuperado de Pages de d6da75a y cinco blobs de #34 cotejados. El manifiesto local puede mantener commit=null. Los commits de publicación usan padres remotos reales y salidas reconstruidas/verificadas, nunca historia sintética.

## Registro anterior preservado

# Continuación actual: benchmark de rifle · #33

Base `d6da75a76201866fe7167fd0f8cbb46441c2c3c7`. PR #30 integrado, #29 cerrada y sus tres jobs posteriores de Verify `35653621273` aprobados. No hay un fallo pendiente de ese HEAD que deba reejecutarse.

[Correctivo del benchmark](BENCHMARK-AIM.md): la captura de apuntado asentaba aimWeight pero no rifleAim. Se corrige sólo el fixture y se rechaza la incoherencia con la fase del renderer. RED observado, 502/502 Node y 9/9 tests de matriz aprobados. Benchmark local `20260921T221156Z-44c19248a241`: 36 checks y 30 PNG cotejados, captura de apuntado revisada. El HTML 0.20.2 permanece intacto.

El PR de #33 determina su CI remota e integración. No confundir un resultado local con merge. Después de integrarlo, continuar #5/#6 desde la referencia corregida, sin repetir el diagnóstico de #29. #7 conserva sus gates. No cerrar aprobación artística, autocolisión, otras familias o GPU física por estas pruebas. Revisión propia, no independiente.

## Registro anterior de la corrección del rifle

# Handoff · v0.20.2 / rifle corregido, integración registrada en PR #30

Leer [STATE](STATE.md), [RIFLE-COORDINATION](RIFLE-COORDINATION.md) y [ADR 0003](../adr/0003-rifle-surface-dock.md). Base del cambio: PR #30, `0f01f574ef23817afd407e0cf2ed90fc7bd49540`. Master previo `37ab6f0`, con #31/#32 integrados y su CI/Pages aprobados. El estado de cierre, SHA integrado y CI posterior de esta unidad se consultan en #30, no se inventan en el documento antes del merge.

## No repetir el diagnóstico resuelto

El rifle ya no usa el desplazamiento de una articulación como superficie. La coordinación y dos cuboides cosméticos nuevos permiten la línea ocular sin forzar cabeza/hombros. El antiguo valor se conserva en `legacyStockError`. Las tolerancias no cambian. Los diez controles de superficies permanecen. Las cinco regresiones nuevas prueban referencias independientes, alcance, ciclo nativo y 18 poses. Localmente: 500/500 Node y 90 checks gráficos canónicos aprobados. El requisito que daba 238.64 mm ya pasa.

El HTML/GLB se regeneran, el recurso humano y partidas no cambian. No copiar perfiles A/B/C descartados. La decisión de autoría está documentada, no debe revertirse silenciosamente a referencias antiguas sólo para coincidir con un número histórico. No crear otro auditor equivalente.

## Antes de cualquier integración

Comprobar CI del HEAD exacto, artefactos y diff. La prueba del rifle debe permanecer dentro de `tests/*.test.cjs`, sin skip. Los workflows normales conservan ocho gates independientes y `contents: read`. Un build auxiliar en rama temporal no sustituye la CI completa de PR ni mueve master. Después del merge verificar el push y Pages separadamente. Conservar fallos históricos aunque una repetición apruebe.

## Siguiente trabajo del producto

#6 permanece abierta: extender una unidad equivalente a la siguiente familia larga reutilizando el observador, empezando por su evidencia de superficie, anatomía y ciclo. No aplicar automáticamente las medidas de rifle a SMG, escopeta o sniper. #5 requiere revisión artística/materiales/variantes. #7 requiere una escena y recorrido íntegro con playtest y hardware físico. El parche de rifle no cierra esos gates.

El ciclo actual está medido a 60 Hz y la matriz central cubre cuello/elevación/agachado. No deducir cobertura de todos los cuerpos, recoil extremo, colisiones emergentes, Safari/Firefox, móvil o FPS de GPU física. Evitar afirmaciones AAA/fotorrealistas.

## Historia preservada

[Cancelación](../../specs/003-weapon-contact/plan-reload-cancellation.md), [HTTP nativo](../../specs/003-weapon-contact/plan-native-reload.md), [auditor #27](../../specs/003-weapon-contact/plan-longarm-audit.md), [rechazos de superficie](../../specs/003-weapon-contact/stock-surface-rejection.md) y [CI](CI-GATES.md). La investigación inicial y los SHA anteriores permanecen en esos documentos, PRs y Git. No reescribir manifiestos históricos ni borrar datos del sitio.
