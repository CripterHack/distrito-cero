# Limpieza de ramas y recuperación · 23 de septiembre de 2026

## Resultado verificado

Se revisaron las 32 ramas originales, se integró el PR #40 como
`86952732d7231312bf305c362d6b07af5257a08b` y se retiraron las otras 31 referencias.
No se reescribió `master`, no se borraron archivos del producto ni se cerraron
issues por razones administrativas. #5, #6 y #7 conservan sus requisitos.

[Manifiesto de las 31 ramas](archives/2026-09-23-branches.json): nombre, SHA exacto,
criterio y evidencia por rama. Contiene 25 ramas integradas, cinco ramas auxiliares
retiradas y una rama de un PR cerrado y duplicado. El PR #14 **no** se declara
fusionado: su implementación y pruebas coinciden con el PR #13. Sus diferencias
documentales y el orden/nombre de pasos CI quedan conservados en el respaldo.

Para merges squash se cotejó el árbol con el commit aceptado, no sólo ascendencia.
Los payloads de reconstrucción de rifle, familias y marcha coinciden respectivamente
con 18 blobs, 20 hashes y 13 hashes de sus revisiones aceptadas. Los otros dos
helpers tienen el mismo árbol que su base. No hay funcionalidad única que rescatar
mediante otro PR. Los helpers de reconstrucción no deben entrar en `master`.

La operación [35899815008](https://github.com/CripterHack/distrito-cero/actions/runs/35899815008)
aprobó: borrado atómico, dry-run y leases por SHA exacto. Rechaza cabezas movidas,
ramas protegidas o usadas por un PR abierto. Se verificó que las 31 ramas
seleccionadas desaparecieron y `master` siguió en `8695273`.

Después de esa operación quedaron `master` y la rama temporal de auditoría.
La rama de este PR documental y la de auditoría se retiran al finalizar su
integración. Su resultado final se registra en el PR, no se anticipa aquí.

## Respaldo independiente de las ramas

[Auditoría y bundle completo](https://github.com/CripterHack/distrito-cero/actions/runs/35898765986/artifacts/10767817631).
Archivo de la conversación: `distrito-cero-respaldo-ramas-20260923.zip`.
Incluye historial Git real autocontenido, `snapshot.json`, metadatos de PRs e
instrucciones de recuperación. El bundle se verificó en Actions y después mediante
clonado local y `git fsck --full`. Contiene las 32 ramas originales y la primera
revisión de la rama auxiliar. No es una historia creada a partir de Pages.

ZIP SHA-256: `3009f808ca98af9538ef81e51d0e840d61f5c8752f8f5f128caa55b1c6a7e75d`.
Bundle SHA-256: `b4b433c190f59ae08091d53f551f10ee7bde3258064d9b5a259167c8c07e630f`.
Bundle: 72,421,586 bytes. Retención del artefacto: hasta el 22 de diciembre de 2026.
La copia descargable de la conversación se entrega también para conservación
externa. No depender de que GitHub retenga indefinidamente un commit sin referencia.
El archivo `open-issues.json` de ese job no es un inventario completo de issues:
el token de auditoría estaba limitado a contenido y PRs. El backlog se consulta
directamente con el conector y en [STATE](STATE.md).

Tras descomprimir en una carpeta de respaldo, para inspeccionar sin escribir en GitHub:

```sh
sha256sum distrito-cero-before-cleanup.bundle
git clone distrito-cero-before-cleanup.bundle restored
cd restored
git fsck --full
git branch -a
```

Para recuperar una rama concreta, usar el nombre y SHA del manifiesto con
`git switch -c <rama-recuperada> <sha>`. Revisar antes de añadir un remoto de escritura.
No restaurar todas las ramas por defecto, ni sobrescribir `master`.

## Continuidad y política

`master` es la única rama permanente. Crear ramas pequeñas sólo para trabajo activo,
desde la versión actual, y retirarlas tras verificar integración y ausencia de
trabajo único. Los agentes empiezan por [HANDOFF](HANDOFF.md), no por listar todas
las ramas, abrir galerías históricas o reinterpretar planes ya integrados.

La limpieza no cambia controles de acceso del repositorio, workflows normales,
versión 0.20.5, fuentes, HTML, assets ni partidas. El job de eliminación utilizó
permiso de contenido limitado a su ejecución y fuera del árbol del producto.
Revisión propia, no independiente. Restaurar referencias no necesita migrar partidas.
