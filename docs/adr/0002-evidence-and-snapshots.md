# ADR-0002 · Evidencia histórica inmutable y QA por ejecución

Estado: accepted para la publicación del repositorio.

## Contexto

El ZIP original incluye informes y un SOURCE-MANIFEST, y varios auditores asumen una historia Git temporal. Reemplazar sus hashes al escribir documentación ocultaría el origen. Ejecutar tests encima de qa/v019 mezclaría resultados nuevos y antiguos.

## Decisión

Conservar SOURCE-MANIFEST como manifiesto de la instantánea original y el commit de importación como base verificable. Git registra cambios posteriores. La CI trabaja en una copia aislada y publica sólo resultados nuevos bajo un artefacto asociado al commit/run. No deducir baseline del primer commit del repositorio.

## Consecuencias

Los antiguos auditores no se usan como gate genérico hasta adaptarlos. Las verificaciones nuevas identifican exactamente qué pruebas se ejecutaron y qué modo de almacenamiento/render se usó. Documentación actual y evidencia original pueden tener diferentes fechas y funciones sin contradicción.
