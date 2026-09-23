# Estado real del proyecto

## Versión activa del árbol: v0.20.5 · Coherencia

Canal **prototype**, fecha 2026-09-23. Identidad en [version.json](../../version.json)
y [build-info.json](../../build-info.json). La publicación se verifica en Actions
y Pages, nunca por la existencia de este documento. Configuración de Pages sobre
master, licencia, permisos normales y esquemas de partidas sin cambios.

## Unidad actual: continuidad del apoyo dinámico

Base `bfa26cd629afbc5a4295d8afdbbf833cddd587c2`, PR #39 integrado. Verify
35870590860, exportación 35870591093, benchmark 35870591062 y Pages 35870589780
terminaron success. Estos resultados no se heredan como CI del nuevo cambio.

Se corrigen discontinuidades de presentación al pasar de pie plantado a balanceo
y al volver a apoyar. La memoria visual conserva y disipa el desfase del último
apoyo. Un muestreador compartido mantiene alcance durante el balanceo y anticipa
el siguiente contacto. La recuperación sólo suaviza la subida y nunca supera el
techo geométrico. No cambia posición física, velocidad, cámara o longitudes.

Siete regresiones nuevas, con RED observado. Suite local completa: **543/543 Node**,
sin skips, cancelaciones o todo, y **89 tests Python del core**. Autoría, build y
exportación del equipo aprobaron. Cuatro vídeos canónicos contienen 282 frames
verificados; 52 fueron revisados visualmente. Misma trayectoria física/cámara,
Storage fixture y GPU software. [Diseño, medidas y límites](SUPPORT-RELEASE.md).
El PR de esta unidad determina su CI e integración finales.

HTML nuevo: `4307c76139bc4f4b8178a16792ecb6c490bd1b0633d98a4a4a86336036cf3641`,
8,869,123 bytes. Fuente: `c24ebe1d3d15e9fd80f649c7ec70e9d0f5b57ab2eab618d9259f7ba203dd2e92`.
Malla humana y GLB de equipo permanecen intactos. La penetración de culata en
transiciones sigue pendiente de #6 y no se oculta con esta corrección de pies.

## Integraciones anteriores que no deben repetirse

| Unidad | Estado y alcance |
| :--- | :--- |
| PR #39, bfa26cd | v0.20.4 aplica la envolvente de marcha al alcance longitudinal del pie. Corrige el hundimiento cerca de reposo, no todos los bordes de apoyo. |
| PR #38, a7c13a8 | Derivado portable con tangentes MikkTSpace y política explícita para 984 triángulos con UV degeneradas. Original conservado. No repara las UV ni acredita arte. |
| PR #37, c49ed085 | Raíces de escena GLB corregidas y validadas. |
| PR #36, b96371e | Exportación humana actual aislada, children vacío y pesos cero corregidos en la salida. |
| PR #35, 4c61509 | Coordinación acotada de SMG, escopeta y sniper en 0.20.3. |
| PR #34, 6d1b756 | Fixture de apuntado coherente con el estado renderizado. #33 cerrada. |
| PR #30, d6da75a | Rifle neutral corregido. #29 cerrada. |
| PR #32, 37ab6f0 | Gates CI separados sin ocultar fallos. #31 cerrada. |

[Estado anterior completo](https://github.com/CripterHack/distrito-cero/blob/bfa26cd629afbc5a4295d8afdbbf833cddd587c2/docs/project/STATE.md)
conserva ejecuciones, hashes y fallos históricos. [Tangentes](PORTABLE-TANGENTS.md),
[exportación](CURRENT-HUMAN-EXPORT.md), [marcha lenta](GAIT-REST.md),
[rifle](RIFLE-COORDINATION.md) y [benchmark](BENCHMARK-AIM.md) mantienen sus contratos.
No convertir sus instrucciones históricas en trabajo sin implementar.

## Backlog vigente

| Issue | Pendiente real |
| :--- | :--- |
| #5 · Personaje patrón | Aprobación artística/procedencia global, materiales y UV degeneradas. La matriz técnica completa y las validaciones portables no sustituyen esa decisión. |
| #6 · Contactos y recargas | Penetración de culata/prenda durante guardia y recarga, revisión global de acciones/anatomías y coste por actor/LOD. El apoyo dinámico se verifica en su unidad propia. |
| #7 · Vertical slice | Escena, recorrido íntegro sin teletransportes, playtests y GPU física. Fixtures de campaña no acreditan estos criterios. |

#2/#3/#4, #19/#21/#23/#25/#27, #29/#31/#33 permanecen resueltas dentro de sus alcances.
No cerrar un issue global porque un subconjunto de tests apruebe.

## Sistemas e historia conservados

Campaña, creador, once peinados, doce partidas con nombres, arsenal, selector
translúcido, vehículos/ocupantes, policía, daños y regiones procedurales se conservan.
La memoria visual no entra al serializador. No se incorporan servicios remotos.
SOURCE-MANIFEST.json, docs/v019 y qa/v019 siguen siendo históricos.
[Handoff](HANDOFF.md), [QA](QA.md), [recursos](ASSETS.md) y
[fallos históricos](ACTIONS-RECOVERY.md). Revisión propia, no independiente.
