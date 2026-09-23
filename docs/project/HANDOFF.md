# Continuación actual · tangentes del GLB portable

Base `c49ed085fe3270c42b284867575c5abc2251fa69`, PR #37 integrado. Verify
35855788180, exportación 35855788346 y Pages 35855786623 terminaron success.
Los PRs #35/#36/#37 ya están en master. No repetir los arreglos del rifle,
las otras familias, el benchmark, children vacío, pesos cero o raíces de escena.

## Unidad actual de CHAR-06

[Variante con tangentes](PORTABLE-TANGENTS.md),
[plan](../../specs/002-character-benchmark/plan-portable-tangents.md).
Se genera un derivado separado con MikkTSpace 1.1.1 y una política explícita para
984 triángulos con UV colapsadas. Se preservan original, atributos por esquina,
buffers anteriores, clips y reportes completos. No se afirma reparación de UV
o equivalencia visual portable. No cambia src, HTML, assets históricos, versión
0.20.3, partidas o permisos.

RED observado y GREEN local: 531 Node, 14 Python de exportación, nueve contratos
del adaptador y cinco integraciones reales. Khronos derivado: cero errores y
advertencias, 20 informativos conservados. El workflow human-export instala sólo
herramientas de autoría fijadas y valida original/derivado separadamente. El PR
registra CI y artefactos del HEAD exacto antes de integrar. Master y Pages se
comprueban después, no se deducen de esta nota.

La rama auxiliar de adquisición de dependencias usa sólo lectura y nunca se
integra. La copia local procede del ZIP Pages de c49ed085, SHA-256
`6c79f561e87611bedc2418d306d899d23a4d9c2105f2c7894a32e74e14f20dd2`.
Git no resolvió DNS. No fabricar historial del snapshot. Una ejecución Node se
interrumpió y otra observó los nuevos tests en RED. Sólo la repetición completa
aprobada cuenta como GREEN. Revisión propia, no independiente.

## Pendientes que no se cierran con este cambio

#5 conserva aprobación artística y procedencia/licencia global. La geometría
portable requiere revisión visual y las UV degeneradas no están reparadas.
#6 conserva vídeo continuo y coste por actor/LOD además de superficies/acciones.
#7 conserva escena, recorrido íntegro, playtest humano y GPU física. No fabricar
participantes, FPS o aprobación artística para cerrar esos alcances.

El siguiente agente debe consultar el PR de esta unidad antes de repetirla.
[Estado](STATE.md), [exportación](CURRENT-HUMAN-EXPORT.md), [QA](QA.md),
[rifle](RIFLE-COORDINATION.md), [familias](../../specs/003-weapon-contact/plan-longarm-families.md).
El [handoff previo completo](https://github.com/CripterHack/distrito-cero/blob/c49ed085fe3270c42b284867575c5abc2251fa69/docs/project/HANDOFF.md)
conserva las ejecuciones, fallos y límites de los PRs #35/#36/#37. No tratar sus
instrucciones históricas como tareas sin implementar.

Ramas por unidad y padres remotos reales. Merge sólo tras CI y revisión del HEAD
exacto. Revertir tangentes retira derivador/tests/pasos adicionales, sin migrar
partidas ni tocar los GLB históricos.
