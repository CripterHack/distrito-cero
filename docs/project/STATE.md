# Estado real del proyecto

## Versión activa del árbol: v0.20 · Coherencia

Producto `0.20.0`, canal **prototype**, fecha declarada 2026-09-16. Identidad canónica en [version.json](../../version.json); hash y tamaño exactos del HTML en [build-info.json](../../build-info.json). Guía vigente en [v020](../v020/GUIA.md). La publicación de un commit se confirma en Actions y comparando Pages, no por la existencia de este documento.

GitHub Pages sigue configurado sobre master. No se cambia esa configuración, la licencia ni los esquemas de datos. Una pestaña abierta necesita recarga para ejecutar código nuevo, sin borrar datos del sitio.

| Issue | Estado y alcance |
| :--- | :--- |
| #2 · QA portable | Cerrado por PR #8. Copias aisladas, informes frescos y diagnóstico. |
| #3 · Guardados nativos | Cerrado por PR #9. Persistencia HTTP, reapertura y conflictos reales. |
| #4 · Recuperación WebGL | Cerrado por PR #10. PR #17 protege generaciones retiradas. No garantiza que un driver no vuelva a reiniciarse. |
| #5 · Personaje patrón | Benchmark #11 integrado. Aprobación artística y otros gates pendientes. |
| #6 · Contactos/recargas | Mangas #12, óptica #13, falanges #15, oposición #16 y ambas manos #18. Esta entrega añade contorno palma/pulgar. Alineación ojo/mira y fases intermedias pendientes. |
| #7 · Vertical slice | Pendiente de escena, recorrido íntegro y evaluación de juego/hardware. |
| #19 · Publicación v0.20 | Verificar build, identidad visible, compatibilidad y publicación del commit exacto. No cierra #5/#6/#7. |

## Cambio de esta entrega

Se recuperó el trabajo sin PR de `fix/006-palm-webbing` (`91ba765`) sobre `ef905ec`. La zona compartida entre palma y pulgar penetraba apoyos que las pruebas digitales no cubrían. El correctivo reduce suavemente hasta 4 mm de profundidad en 1,166 posiciones de piel. Mantiene el parche palmar medido, pesos, UV, topología, 49 huesos, uñas y otros buffers. [Detalle](THENAR-SURFACE.md).

El build genera la identidad de inicio, pestaña, pausa e interacciones, y `DC.BuildInfo`. `build-info.json` identifica las fuentes y el HTML. `python3 build.py --check` detecta salidas ausentes o diferentes sin modificarlas. [Publicación](RELEASES.md).

## Sistemas conservados

Campaña, creador, once estilos de cabello, catálogo de hasta doce partidas con nombres, equipamiento, selector translúcido, vehículos/ocupantes, policía, daños y regiones procedurales. No se añade combate autónomo nuevo, simulación de tejidos, terreno avanzado o una vertical slice completa.

El recurso humano tiene SHA-256 `522a9a24e2cc70857a3ec5c18bf9c2126c7b59d9ce8e4c5601c3b8be2c911b54`. El kit GLB de equipamiento conserva sus bytes. Los GLB humanos anteriores son exportaciones históricas, no modelos nuevos de v0.20.

## Evidencia y límites

Los proxies gráficos no son autocolisión completa. Tiempo/cámara preparados no demuestran FPS. El benchmark smoke tiene 30 capturas/36 comprobaciones; la matriz completa requiere su propio informe. La prueba de versión importa por HTTP nativo un JSON sintético producido por el serializador de v0.19. Los guardados nativos se verifican por separado de los fixtures gráficos.

Antes de esta unidad, la CI de master `35057506852` sobre `ef905ec`, el benchmark y Pages terminaron en success. Los cinco fallos históricos permanecen documentados en [ACTIONS-RECOVERY.md](ACTIONS-RECOVERY.md). Cada commit nuevo exige sus propias ejecuciones.

## Historia preservada

Base importada v0.19: `23f9e9d`, 730 archivos y 729 huellas. HTML original `3aa9a27f4941ea1c701069c61db133ab3c93087e35d833d4921ba25b8a4b059f`. `SOURCE-MANIFEST.json`, `docs/v019/` y `qa/v019/` conservan su función histórica. No se actualizan para simular resultados actuales.

Runtime nativo, 38 fuentes JS con orden significativo y un HTML autónomo. Sin validación universal de GPU física, Safari/Firefox, móviles, tejidos, multijugador o fotorrealismo. [Handoff](HANDOFF.md), [QA](QA.md), [recursos](ASSETS.md).
