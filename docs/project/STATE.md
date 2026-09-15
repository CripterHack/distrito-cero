# Estado real del proyecto

## Identidad de la base

- Juego: Distrito Cero v0.19 · Contacto articulado.
- Repositorio: CripterHack/distrito-cero, rama predeterminada master, público al iniciar la publicación. No se cambió su visibilidad.
- Importación íntegra: `23f9e9d031c7a0ad270cd74ce0805ea0dfc385da`.
- Archivo original: 80,607,113 bytes, SHA-256 `307c8fd0d3093eb7d16a3468470a2dfd20ffa12a654ecbe306f07f8aea8a1241`.
- HTML reconstruido: 8,839,156 bytes, SHA-256 `3aa9a27f4941ea1c701069c61db133ab3c93087e35d833d4921ba25b8a4b059f`.

Se importaron 730 archivos: 38 en src, 48 en assets, 141 en tests, 70 en tools, 55 en docs, 371 en qa y siete archivos raíz. El manifiesto original cubre 729 porque no incluye su propia huella. La revisión documental posterior no modifica el juego ni inventa una v0.20.

## Madurez

**Prototipo integrado con regresión extensa, no producción ni calidad AAA demostrada.** Hay bastante funcionalidad y una deuda importante de autoría artística, portabilidad de pruebas, robustez gráfica y comportamiento emergente. La evidencia automatizada no sustituye la evaluación visual o la experiencia de personas jugando.

| Sistema | Implementado | Brecha prioritaria |
| :--- | :--- | :--- |
| Personajes | Familia corporal, cara con mapas, 49 huesos, DQ, LOD, once opciones de cabello | Diversidad anatómica real, materiales, expresiones, correcciones de poses extremas |
| Armas y herramientas | Catálogo, Gauss, EMP, óptica, inventario, recargas y contactos palmares | Contacto digital preciso, alineación ojo/mira, autointersecciones, variantes de recarga |
| Vehículos | Conducción, daño por zonas, conductores y acceso ocupado/vacío | Contactos más ricos, reacción física, navegación de tráfico y recuperación segura |
| Mundo | Sectores deterministas, regiones, props, atlas, entregas | Relieve transitable, vías orgánicas, streaming asíncrono, densidad y composición |
| NPC/policía | Reacciones y persecución, pérdida de contacto, captura y rendición | Decisiones sociales más profundas y navegación robusta. No existe combate armado autónomo |
| Historia | Campaña y actividades integradas | Una muestra narrativa completa pulida, dirección, sonido y ritmo |
| Identidad y datos | Creador, hasta doce espacios por ID, nombres, copias, JSON y conflictos | Pruebas de persistencia nativa y concurrencia real, recuperación y experiencia de cuotas |
| Plataforma | HTML offline, teclado/ratón/táctil, controles de calidad | GPU física, Safari/Firefox, gamepad, sesiones largas, pérdida/restauración de WebGL |

## Qué se ha comprobado en esta publicación

El ZIP se verificó contra sus 729 hashes sin discrepancias. La construcción local generó exactamente el HTML entregado. Las 328 pruebas Node se ejecutaron de nuevo localmente y en el workflow de importación, ambas con cero fallos. El workflow importó todos los archivos mediante un commit fast-forward, sin forzar la rama.

La evidencia distribuida de v0.19 documenta 271 aserciones de navegador y una prueba GLB. **Es evidencia histórica incluida, no una reejecución completa durante la publicación.** Las nuevas ejecuciones de CI tienen sus propios run IDs y artefactos. Consultar Actions para su resultado, no inferirlo de este documento.

## Hallazgos documentales y técnicos

`assets/README.md` aún describía v0.12 como actual. Se reemplaza por un índice que distingue datos canónicos, generadores y exportaciones históricas. Los scripts de auditoría de entregas antiguas asumen una historia Git temporal que no existe en este repositorio nuevo: no son una puerta universal de CI.

El build concatena 36 JS en un orden significativo. Las capas extienden clases y reasignan `D.World`, `D.Simulation`, `D.Renderer` y `D.App`. Esta dependencia se debe hacer explícita antes de reorganizar archivos.

La mayor pieza de fuente es `hero-asset.js`, de unos 8.18 MB, con datos geométricos embebidos. No confundir ese archivo con el coste de todo el juego ni editar sus buffers manualmente. Se conservan varias bases y GLB históricos porque sostienen reconstrucciones y comparaciones.

## No demostrado

No hay certificación AAA, benchmark en hardware del usuario, física completa de tejidos, mecánica real de armas, red multijugador, persistencia nativa después de cerrar el navegador ni recuperación general de contexto WebGL. No se ha elegido una licencia global ni se ha desplegado el juego desde este repositorio.
