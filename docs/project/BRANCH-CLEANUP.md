# Ramas: limpieza vigente y recuperación

## Limpieza autorizada y completada en la continuación actual

Con master **39b7647f1c763ab9e35e8c507723fc4cf5cfc57f** se auditaron las 16 ramas
secundarias: nueve commits ya ancestros de master y siete auxiliares de transporte
con productos integrados. No había ramas protegidas ni PRs abiertos afectados.
La autorización renovada del usuario sustituye las notas antiguas de no reintento.

[Auditoría 36802284648](https://github.com/CripterHack/distrito-cero/actions/runs/36802284648)
y [retiro 36802528301](https://github.com/CripterHack/distrito-cero/actions/runs/36802528301)
terminaron correctamente. El segundo job creó y publicó un bundle autónomo,
restauró un mirror y comprobó fsck y cada ref antes de efectuar bajas atómicas
con lease del SHA esperado. Master no cambió. También retiró su propio auxiliar:
**17 bajas, de las cuales 16 eran ramas antiguas**. Sólo master quedó en remoto.
Ningún helper entró en el producto o su ascendencia.

Artefacto previo a las bajas: **11135907780**, `branch-retirement-backup-36802528301`,
ZIP SHA-256 `4a0c91bb7c59e28556d6e26623f9ca15922837361e7bb90e022bdbb6847afb5a`.
Resultado: **11135697974**, `branch-retirement-result-36802528301`, SHA-256
`f8cb277649d78176c27106e78aac023da37672a6c33ee1576b996795739e82dc`.
Los artefactos tienen retención de 30 días. La copia de conversación
`distrito-cero-respaldo-ramas-retiradas.zip` conserva el bundle y plan completo.
No depender sólo de la retención temporal de Actions.

Para recuperar en un directorio nuevo, extraer el ZIP y ejecutar:

```sh
git clone --mirror repository.bundle distrito-cero-recuperado.git
git --git-dir=distrito-cero-recuperado.git fsck --full
```

El plan JSON enumera nombres, SHAs, protección y contenido único. Recuperar una
rama sólo cuando sea necesaria, nunca volver a subir en bloque todos los helpers.
Las nuevas unidades parten de master actualizado y retiran su rama al cerrar.
Esta limpieza no completa los criterios globales de #5, #6 o #7.

## Registro histórico

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


## PR #49 · retirada verificada el 27 de septiembre de 2026

Merge `0fa83b9e024819821e135a9de540a3f897bc9c78`. La operación
[36304799177](https://github.com/CripterHack/distrito-cero/actions/runs/36304799177)
retiró atómicamente sólo `fix/006-cross-family-handoff` en `a946fd5` y el
helper `build/006-cross-family-0213` en `9754afe`, con leases de SHA exacto,
sin PRs abiertos o ramas protegidas y tras subir un respaldo autocontenido.
No cambia master ni equivale a aprobación de la ejecución sight del push.

Artefacto `10926822359`, `pr49-backup-36304799177`, disponible hasta el
26 de diciembre de 2026 según GitHub. Bundle `distrito-cero-pr49-before-retirement.bundle`,
75,511,375 bytes, SHA-256 `dbf01324c22784e94ee712c9d6e3ec8a56f3a1f04bb8d9ed9bbb10c96815f72d`.
Descargado, cotejado y restaurado en un repositorio vacío. `git fsck --full`,
árbol y HTML verificados; el helper no pertenece a la ascendencia de master.
Refs `refs/backup/pr49/0`, `/1`, `/2`: master, feature y helper respectivamente.
Recibo de retirada `10926353809`. El [PR](https://github.com/CripterHack/distrito-cero/pull/49#issuecomment-5854096986)
conserva los hashes de los ZIP, detalle y comprobaciones. Crear nuevas ramas
sólo para trabajo activo posterior, no restaurar éstas como tareas pendientes.
