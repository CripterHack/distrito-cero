# Auditoría de coordenadas UV · CHAR-05/06 · issue #5

Estado: herramienta de diagnóstico implementada; parametrización y revisión
artística pendientes. Base inspeccionada: `f9454df7e3325a3cf4d516a0374c2ccb9565090c`,
producto 0.20.22. No modifica recursos ni el runtime.

## Problema y contrato

El [adaptador de tangentes](../../docs/project/PORTABLE-TANGENTS.md) cuenta 984
triángulos UV degenerados, pero no identifica sus índices ni distingue una carta
colapsada de un triángulo geométricamente colapsado. Cero errores del validador
glTF no demuestra que exista una parametrización invertible para esos mapas.

`tools/qa/audit_uv.cjs` lee un GLB local y emite JSON determinista con su SHA-256,
mesh/primitiva/material, sets UV usados por las cinco referencias de textura PBR
básicas, roles compartidos, índices originales de triángulo y límites espaciales
y UV del conjunto afectado. Cuenta V constante y V en el borde 0/1, y mantiene
la degeneración geométrica de las primitivas texturizadas auditadas en una lista
separada, sin atribuir cobertura a las omitidas. Los totales únicos de triángulo
no duplican una superficie que usa más de un set UV; `degenerateUvTriangleCharts`
cuenta las ocurrencias por carta.

- Given una carta válida o reflejada, When se audita, Then devuelve `passed`.
- Given determinante UV exactamente cero, Then devuelve `blocked` y exit 1,
  conservando los IDs de todos los triángulos afectados.
- Given bytes no finitos, índices inválidos o layouts no soportados, Then falla
  con exit 2; no convierte una entrada inválida en aprobación.
- Given una malla sin mapas básicos, Then la registra como omitida; si ninguna
  carta aplica, devuelve `not-applicable`, distinto de una carta aprobada.
- Given cualquier auditoría, Then los bytes, atributos, materiales y fuentes
  originales permanecen idénticos. No genera otro modelo ni repara UV.

Soporta listas de triángulos indexadas/no indexadas, posiciones float32, UV
float32 o enteros uint8/uint16 normalizados, offsets y strides válidos. Rechaza
morphs, compresión, sparse, extensiones de material/accessor y transformaciones
de textura. Es un gate parcial de autoría, no un reemplazo del validador glTF.
La clasificación geométrica es informativa: no redefine el gate UV ni declara
aprobación de anatomía, materiales, normal maps, rendimiento o arte.

## Ejecución y evidencia

```sh
python3 tools/export_current_human.py --output artifacts/uv-audit/current
node tools/qa/audit_uv.cjs artifacts/uv-audit/current/dc-human-0.20.22-neutral.glb > artifacts/uv-audit/current/uv-audit.json
node --test tests/uv-audit.test.cjs
```

El segundo comando devuelve **1 intencionadamente** para este recurso. No se
añade como gate ordinario de CI que finja aprobar deuda conocida. El reporte
JSON continúa disponible aunque falle el gate. Las rutas de salida son locales
y no se versionan nuevos GLB ni capturas históricas.

RED: siete pruebas fallaron ante la herramienta ausente, registro local
`artifacts/uv-audit/red.tap`. GREEN final: diez pruebas del auditor y nueve del
adaptador de tangentes aprobadas (19/19), sin omitidos,
incluyendo cartas reflejadas, degeneración UV/geométrica separada, mezclas,
sets/roles compartidos, UV normalizados intercalados, entradas corruptas y
CLI con hash y no mutación. La revisión independiente detectó que normalizar
uint16 antes del determinante podía ocultar una carta collineal por redondeo;
la regresión usa [1,1006, 2,1007, 3,1008] y el cálculo ahora conserva enteros
hasta clasificar el triángulo. También rechaza referencias de textura ausentes.
Node 24.22.3; Python de exportación 3.12.14.

La exportación actual generada para esta unidad tiene SHA-256
`53d9ced1f2f6e4dc161214af06cc35ff9e252221afea11ca732306a0d7ee2ee7`.
Resultado: mesh 3 `face`, primitiva 0, material 3, 9,672 triángulos;
**984 UV degenerados, ninguno geométricamente degenerado**, 981 en V=1 del
GLB. Los tres restantes son los triángulos `1852`, `2200`, `5790`; por tanto
no todos los degenerados pertenecen al cuello. Trece primitivas sin mapas
se registran como omitidas, no como cartas verificadas.

La receta histórica `tools/build_hero_v012.py` genera V=(y−1.52)/0.28 para cara
y extensión cervical; el empaquetado uint16 limita ese resultado a [0,1].
La exportación invierte V y lleva ese borde a 1. La prueba independiente de la
fuente confirma 981 triángulos en V=0 y tres caras collineales de V constante.
Reparametrizar y volver a hornear mapas requiere una unidad artística propia:
extender coordenadas sin rehacer el atlas no constituye una reparación válida.

Los dos GLB nuevos de Higgsfield también fueron auditados sin modificar sus
bytes: personaje (`e7d41d6ea3245dc78a88865d2228a90979cc62ced65ca3712085a28f2ef9c7fd`,
47,321 triángulos) y sedán
(`d5af7354a1fdd16e88b7b0eb28029e44d6d6a4f147f49a4a9650333962dbdc9b`,
44,745 triángulos). Ambos tienen una carta auditada, cero triángulos UV o
geométricamente degenerados y exit 0. Los JSON se conservan localmente bajo
`artifacts/uv-audit/higgsfield-character.json` y `higgsfield-sedan.json`.
Es evidencia de parametrización estructural, no integración en juego ni
aprobación artística.

## Reversión y siguiente paso

Retirar la herramienta, sus tests y este plan revierte íntegramente la unidad;
no cambia partidas, rig, fuentes humanas ni GLB históricos. Usar los IDs del
reporte para preparar una receta de UV/horneado revisable y comparar materiales
en las luces del benchmark. #5 permanece abierto; no se reclama reparación UV,
aceptación artística ni calidad AAA.
