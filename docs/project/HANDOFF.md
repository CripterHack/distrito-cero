# Handoff · v0.20.1 / rifle neutral en RED

**Base remota:** `32a8cca590b83a5b2a1b3efabad5723d3c9d6757`, PR #28 integrado y #27 cerrada. **Trabajo actual:** `fix/029-rifle-coordination`, issue #29, requisito pendiente de #6. Producto **0.20.1 · Coherencia**, canal prototype. Leer [STATE](STATE.md), [QA](QA.md), [auditor y límites](LONGARM-CONTACT.md) y [plan #29](../../specs/003-weapon-contact/plan-rifle-coordination.md).

## Lo que ya se integró

El PR #28 fue revisado sobre HEAD `6d2effd65868a921422cbe9099c5c633f474f07d`. Verify `35457549479` y benchmark `35457549514` terminaron success. Se descargó y cotejó el artefacto WebGL `10589016422`, SHA-256 `d1d7c2de18bc2eb0b648c8a4fd9933519a4597bce4bf63ebd0a3bc89603047b0`: nueve suites, 205 checks, 133 PNG, cero errores/peticiones. Se comprobaron los 48 hashes del auditor y se revisaron poses y ciclos. No había hilos pendientes ni solicitudes de cambios. Revisión propia, no independiente.

Después del squash terminaron `success` [Verify 35623114643](https://github.com/CripterHack/distrito-cero/actions/runs/35623114643), [benchmark 35623114699](https://github.com/CripterHack/distrito-cero/actions/runs/35623114699) y [Pages 35623112646](https://github.com/CripterHack/distrito-cero/actions/runs/35623112646). El artefacto Pages `10649968865` contiene el HTML canónico. Esto verifica el artefacto y el despliegue, no una nueva consulta HTTP a la URL pública.

El auditor tiene 24 checks de integridad, 48 capturas, 72 poses numéricas y 240 muestras de ciclo. **No corrige ni aprueba las posturas.** `needs-coordination` sigue visible. #25/#26 también están cerradas: no repetir la cobertura HTTP de recarga ni tratarla como pendiente. Sus fallos históricos y sus verificaciones propias se conservan en [plan nativo](../../specs/003-weapon-contact/plan-native-reload.md) y [plan #27](../../specs/003-weapon-contact/plan-longarm-audit.md).

## Punto exacto para continuar

`tests/rifle-coordination.test.cjs` reutiliza el auditor existente. Está dentro de `tests/*.test.cjs`, sin skip ni selectores que escondan el fallo. La base pasa 484 Node; con la nueva aceptación, el resultado completo es **484 aprobadas y una fallida de 485**. Falla `rifle neutral coordinates the mesh eye and stock without stretching arms`, con `eye/sight: 0.238643317922643 m`. No integrar esta rama en RED.

Se probaron dos variantes temporales sobre el renderer, no dentro del producto. Aunque bajaron el error ocular a 0.1569 y 2.7697 mm, se rechazaron por la elevación/inclinación de hombro y cabeza. Las recetas y límites están en el plan. No copiar esos perfiles como una solución aprobada ni llamar QA canónica a una captura con módulos sustituidos en memoria.

La proyección del montaje dentro del alcance de ambas manos es parte del problema: mover sólo cabeza/hombro dominante puede dejar fuera de alcance al brazo de apoyo y desplazar otra vez la culata. Retomar desde la prueba fallida y coordinar ambos hombros, cabeza y montaje, revisando además la superficie de la chaqueta. El punto heredado del hombro no representa toda la prenda. No construir otra matriz diagnóstica equivalente ni cambiar referencias/umbrales sin un contrato explícito y comparación conservada.

## Qué permanece intacto

No hay corrección de producción aceptada en #29. Se conservan `src/`, HTML, assets, rig, reglas, partidas, permisos, workflows y versión. HTML SHA-256 `4a78bcca34cd40b2c406b0642362f30a6b71303d8a4a6ace659e0ba4afc9918d`, 8,862,957 bytes. Fuente `dfb16e65c1a64d991f2bedfbecf0892d69c8b2110e4be1403e31d7af739c4fdb`. No borrar datos del sitio.

La copia local procede del ZIP Pages `10649968865`, SHA-256 `d14dbc643645e4121f757a6a958fd432510de98885efa3821deb41e22c0394c7`. Git remoto no resolvió DNS. Los commits del conector parten de padres remotos reales, nunca de historia sintética del laboratorio. Fixture y GPU software no equivalen a persistencia HTTP o rendimiento físico.

## Verificación al retomar

```sh
# RED conocido: no esconder este requisito para integrar la rama.
node --test tests/rifle-coordination.test.cjs
node --test tests/*.test.cjs
# El producto canónico permanece reproducible.
python3 build.py --check
```

Después de una corrección real, ejecutar autoría, build/export, Python vigente, Node completo, suites gráficas y HTTP según [QA](QA.md). Revisar preparación, recarga/cancelación, agachado, pitch, cuello, movimiento y otros equipos. Exigir capturas del runtime canónico nuevo, CI del HEAD exacto y revisión del diff antes del merge autorizado. Master y Pages se verifican por separado.

#5 necesita aprobación artística/materiales/variantes. #6 continúa abierta por coordinación, superficies y movimiento. #7 necesita escena/recorrido íntegro, playtest y GPU física. Ni el auditor aprobado ni una variante que sólo satisface distancias cierran esos gates.
