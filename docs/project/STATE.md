# Estado real del proyecto

## Árbol de trabajo: candidata v0.20.19 · Coherencia · prototype

Identidad en[version.json](../../version.json) y[build-info.json](../../build-info.json).
Base remota integrada #56: **5ab52d79c517bee5d54e6aa286f94dae044e84f4**,
árbol 6391e911af488970f71f3f2313081bf38411658f, juego 0.20.18.
Su push 36469943251 aprobó siete jobs; seis artefactos descargados y contrastados
con305 WebGL y 80 HTTP. El pendiente operativo anterior ya fue comprobado.
[Cierre #56](https://github.com/CripterHack/distrito-cero/pull/56#issuecomment-5877275153).

## Unidad actual

Pistola ↔ SMG libre y desde recarga mantiene pose y pieza mostrada con captura,
montaje y retorno existentes. Conservar terceros modelos excluidos, caché
canónica, longitudes, acciones inmediatas, munición y partidas. No se modifica
geometría, rig, física o workflows. [Plan](../../specs/003-weapon-contact/plan-pistol-smg-handoff.md).

Regresión RED sobre base, corrección mínima y prueba de trayectoria:
45 pruebas dirigidas aprobadas después de rechazar el arco de 0.08 m a−7.772 mm de
chaqueta. Arco de 0.12 m medido, sin elevar tolerancia−2 mm. Las suites completas
y el renderer del HEAD son gates propios, no se deducen de este resultado.

Catálogo único:112 comprobaciones sight, veinte secuencias, tres particiones48 / 31 / 33.
Conserva94 checks anteriores,61 estados/caso, imágenes y cinco guardas en cada
partición. Sin nuevo runner ni elevar 1800 s por productor o 40 minutos por job. No implica
mejor FPS o menor cómputo real. La CI del PR mide la nueva distribución.

**Integración:** consultar el PR de la unidad en[issue #6](https://github.com/CripterHack/distrito-cero/issues/6).
Esta nota es anterior al cierre de CI. No presentar la candidata como integrada
sin comprobar PR/HEAD y el push por separado. [HANDOFF](HANDOFF.md),[QA](QA.md).

## Backlog

| Issue | Pendiente real |
| :--- | :--- |
| #5 | Arte global, fuentes/procedencia, materiales/UV y hardware |
| #6 | Cierre pistola/SMG, otras parejas, herramientas/pesados, cortes prioritarios, anatomías/giros y coste por actor/LOD |
| #7 | Recorrido íntegro, playtests humanos y hardware de referencia |

## Continuidad

#56 reforzó el verificador. #55 resolvió recarga SMG/revólver y #54 su cambio libre.
#53 y #52 cubrieron rifle/revólver, #51 caché, #50 particiones y #49 rifle/pistola.
Cada PR conserva evidencia propia. No repetir esos trabajos ni reetiquetar
el timeout histórico 36304175245. Campaña, creador, catálogo y vehículos intactos.

No se reintenta limpieza bloqueada ni se borran ramas. Helpers fuera del
producto, no features pendientes. La restauración local tiene historia
sintética, distinta de los padres remotos reales. No declarar revisión
independiente, GPU física, toda la malla/CCD o aceptación artística global.
