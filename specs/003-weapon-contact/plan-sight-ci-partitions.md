# Sight CI partitions · implementación y validación

> Continuación inline de SPEC-003. Revisión propia, no independiente.

**Objetivo:** resolver el timeout real de QA sin reducir cobertura ni modificar
el juego. Base master `0fa83b9`, producto 0.20.13, PR #49 integrado.
**Especificación:** [SPEC-003](spec.md), [QA](../../docs/project/QA.md).
**Arquitectura:** un único productor con selección cerrada `all`, `base` o
`cross-family`. Dos suites concretas en el registro, alias `sight` que expande
y deduplica. CI ejecuta las particiones en runners separados. No crear otro
renderer, solver, tracker o matriz de casos. Python, Playwright y WebGL existentes.

## Evidencia y límites

Push Verify `36304175245`: sight detenido a 1800.008 s / exit 124. Sólo emitió
44 PASS, sin informe completo. El PR previo había terminado en 1785.964 s.
No es prueba de un fallo geométrico ni justificación para dar por pasados los
checks que faltan. El artefacto fallido `10926778997` permanece disponible.

El límite sigue en 1800 s por partición y 40 minutos por job. El máximo
agregado permitido de tiempo de runners es mayor. Este reparto no prueba
menos coste total de CPU/GPU, mejor FPS ni hardware físico.

## Entregables y pruebas

1. `tools/qa/sight_contract.py`: un catálogo inmutable de ocho intercambios,
   mismo orden, ambas direcciones, libre y recarga 0.46. Base 40 y cruce 18.
   `sight_cases(partition)` rechaza valores desconocidos.
2. `tests/sidearm_sight_browser.py`: conservar todos los cuerpos de medición,
   61 estados por intercambio, imágenes y umbrales. `--partition` inválido
   falla antes de importar navegador o crear salidas. Mapas/selector/cierre de inputs/errores/catálogo
   se verifican en cada partición tras su propia última secuencia; no contar los requisitos compartidos dos veces.
3. `tools/qa/run.py`: suites con nombres e informes distintos. `--suite sight`
   ejecuta ambas; alias combinado con nombres explícitos no repite trabajo.
   `all` incluye cada suite concreta una vez; native/HTTP sigue separado.
4. `.github/workflows/ci.yml`: selección explícita en cuatro grupos gráficos,
   sin solapamiento, ni checks quitados, ni permisos ampliados. Artefactos
   propios y fallos independientes. No cambiar renderer, browser o resolución.
5. `tests/qa_selection.test.py` y `tests/ci_workflow.test.py`: unión exacta,
   cobertura fija 40+18, comandos, deduplicación, rechazo, layout y presupuestos.
   Revisar diff completo, documentos y reversión de QA sin tocar partidas.

## Ejecución

- [x] Reproducir el defecto mediante la evidencia completa del job fallido.
- [x] RED: seis fallos de selección y cuatro de workflow sobre la base.
- [x] GREEN inicial: 17 pruebas de selección y nueve de workflow.
- [x] Revisión detectó guardas de selector faltantes tras el último rifle.
  Tres regresiones nuevas fallaron antes de corregir. Las cinco guardas se
  ejecutan en ambas particiones, sin aumentar el conteo 40+18.
- [x] Iteración inicial local: 601 Node, 125 Python y cruce 18/18 en 631.214 s.
  Esta corrida gráfica precede la corrección de guardas y no se atribuye a ella.
- [ ] Node completo, Python vigente, build/export/inmutabilidad.
- [ ] CI del HEAD exacto, sin exigir exportación humana omitida por filtros
  legítimos cuando no cambia su código/entradas. Benchmark conserva su filtro.
- [ ] Cotejar unión de 58 nombres, ocho secuencias completas y capturas con la
  evidencia aceptada de #49. Revisar imágenes actuales y no sólo números.
- [ ] Merge condicionado a los gates y comprobación posterior separada.

Los estados de CI posteriores pertenecen al PR y sus artefactos exactos, no
se deducen de esta lista. Los intentos locales incompletos o fallidos se
registran, nunca se suman a resultados aprobados. #5/#6/#7 siguen globalmente abiertos.
