# Continuación vigente · autoría y validación · refs #5

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
