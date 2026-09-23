# Parche vigente: v0.20.4 · Coherencia

Inicio y Pausa muestran v0.20.4. El cuerpo ya no debe hundirse al terminar una
marcha lenta. Controles, campaña y partidas no cambian. Desde v0.20.3 las cuatro
familias largas usan el apoyo coordinado, con límites de revisión aún indicados
en [STATE](../project/STATE.md). Recargar el sitio conserva las partidas.

## Notas históricas de v0.20.1 y v0.20

# Actualización 0.20.1

El inicio y Pausa muestran **v0.20.1 · Coherencia** cuando se ejecuta el HTML de este parche. Pistola/revólver elevan y centran el objeto respecto del ojo durante el apuntado, sin alterar los controles. Usar Tab para equipar, Z para apuntar, J para disparar y L para recargar. La corrección no añade primera persona ni cambia las armas largas.

Los guardados del mismo origen siguen usando la misma clave. Recargar el sitio, sin borrar datos, permite ejecutar código nuevo tras su publicación. Exportar un respaldo sigue siendo prudente antes de cambiar de navegador u origen.

# Distrito Cero v0.20 · Coherencia

Versión de producto `0.20.0`, canal prototipo. Esta entrega consolida fiabilidad, contactos y la corrección de superficie palma/pulgar posterior a v0.19. No se anuncia fotorrealismo ni una beta terminada.

## Ver qué versión está abierta

El título de la pestaña, la etiqueta inferior del menú inicial y Pausa muestran v0.20. En Pausa se muestra también un identificador corto de build. `version.json` es la fuente de identidad. `build-info.json` identifica exactamente el HTML. Ambos se empaquetan durante la construcción: el juego no los descarga al ejecutar ni depende de red para consultar su versión.

Una pestaña ya abierta conserva su código hasta recargarse. Guarda o exporta antes de recargar. No borres datos del sitio para actualizar: en el mismo origen de Pages las partidas usan las mismas claves. Si cambias de navegador, dispositivo u origen, exporta e importa los JSON.

## Qué probar

Abre Equipamiento con **Tab**. Con fusil, subfusil o rifle de precisión, revisa la mano de apoyo. Usa **Z** para apuntar, **J** o clic izquierdo para usar y **L** para recargar. El contorno de la unión entre palma y pulgar tiene una reducción suave del volumen excesivo, sin desplazar toda la mano. Conserva los movimientos de dedos y pulgares y el apoyo entre manos de pistola/revólver.

**B** selecciona binoculares. **F** inicia entrada/salida/cancelación de vehículo. **R** sigue reservado a rendición policial. El catálogo, campaña, creador y controles no cambian. La [guía del arsenal](../v019/GUIA.md) conserva las instrucciones completas de los sistemas heredados y queda identificada como documentación de base.

## Guardados

La versión del producto no se escribe como versión del esquema. Se mantienen catálogo `distrito-cero:saves:v2`, perfiles/equipamiento versión 1 y exportación `distrito-cero-slot` versión 1. La prueba de compatibilidad utiliza un JSON sintético producido por el serializador del commit v0.19 `ef905ec`, no una partida personal.

## Construcción

```sh
python3 build.py
python3 build.py --check
```

El segundo comando no modifica ni repara archivos. Devuelve error cuando `index.html` o `build-info.json` no corresponden a las fuentes. El identificador no contiene rutas locales, hora del build o un commit futuro autorreferencial. Construir el mismo árbol produce los mismos bytes.

## Límites

La superficie corregida es local, hasta 4 mm en espacio de autoría. El rostro, los huesos, los pesos, el equipamiento y las reglas no se sustituyen. Las normales acompañan la forma nueva. No es autocolisión de todos los tejidos. Ojo/mira, fases intermedias, anatomía, cabello, materiales y la muestra jugable completa siguen pendientes.

Los informes CI diferencian fixtures gráficos, persistencia HTTP real y capturas preparadas. No representan FPS de GPU física. Véanse [estado](../project/STATE.md), [QA](../project/QA.md) y [superficie](../project/THENAR-SURFACE.md).
