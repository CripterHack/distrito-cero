# Distrito Cero

Aventura criminal original de navegador con exploración, conducción y una ciudad procedural. **Versión jugable: v0.20.10 · Coherencia (`0.20.10`, prototipo).** JavaScript, WebGL2, Canvas 2D y Web Audio nativos. Un HTML autónomo, sin librerías externas, CDN, telemetría remota ni conexión obligatoria durante la partida.

El proyecto es un prototipo integrado en desarrollo. La dirección artística busca realismo, pero **no se presenta como un juego AAA terminado ni como fotorrealista**.

## Empezar

```sh
git clone git@github.com:CripterHack/distrito-cero.git
cd distrito-cero
python3 build.py
python3 -m http.server 8080 --bind 127.0.0.1
```

Abrir `http://127.0.0.1:8080`. También se puede abrir `index.html` directamente como archivo local, pero no se debe asumir que dos rutas `file://` comparten guardados. El servidor local es una comodidad de desarrollo, no un servicio obligatorio del juego. **Exportar las partidas JSON antes de cambiar de versión, ruta, navegador o dispositivo.**

No hace falta instalar paquetes para construir el HTML. Python 3.12 y Node 22 son los objetivos del entorno de integración continua. Las dependencias de `requirements-dev.txt` son exclusivamente de autoría y pruebas.

## Estado jugable

Campaña dirigida y exploración libre, tráfico y persecuciones, vehículos conducibles con daño, objetos destruibles, regiones urbanas/futuristas/retro/rurales, creador de personajes con once opciones de cabello y catálogo local de hasta doce partidas con nombres. Arsenal ficticio con Gauss, EMP y binoculares. Las secuencias de acceso distinguen vehículos vacíos y ocupados. El selector de equipo es translúcido sobre la escena pausada.

| Acción | Control |
| :--- | :--- |
| Caminar / conducir | WASD o flechas |
| Correr / agacharse | Shift / X |
| Entrar, salir o cancelar acceso | F |
| Interactuar | E |
| Selector de equipo | Tab |
| Usar / apuntar / recargar | J o clic izquierdo / Z o clic derecho / L |
| Gauss / EMP / binoculares | 9 / 0 / B |
| Rendición / atlas / foto / pausa | Mantener R / M / P / Esc |

Guía vigente: [v0.20](docs/v020/GUIA.md). El arsenal y sus animaciones son ficción de videojuego, no instrucciones de uso o fabricación de equipamiento real.

## Versión e integridad actual

La versión visible se genera desde [version.json](version.json). [build-info.json](build-info.json) contiene el hash exacto del HTML y sus fuentes. Inicio, pestaña y Pausa comparten esa identidad; Pausa muestra el build corto. No cambia el esquema de partidas. [Proceso de publicación](docs/project/RELEASES.md).

## Documentación vigente

**[Empieza aquí](docs/START-HERE.md)** · **[Estado real](docs/project/STATE.md)** · **[Plan de desarrollo](docs/project/ROADMAP.md)** · **[Trabajo siguiente](docs/project/HANDOFF.md)**

[Arquitectura](docs/project/ARCHITECTURE.md), [recursos](docs/project/ASSETS.md), [calidad y pruebas](docs/project/QUALITY.md), [método spec-game-development](docs/spec-game-development.md), [backlog](docs/project/BACKLOG.md), [riesgos y decisiones](docs/project/RISKS.md), [licencias pendientes](docs/project/LICENSING.md).

Los agentes deben leer [AGENTS.md](AGENTS.md) y la [constitución](.specify/memory/constitution.md) antes de implementar. Las especificaciones nuevas están en `specs/`. Las carpetas `docs/v*` y `qa/v*` son evidencia histórica, no el plan actual.

## Construir y comprobar

```sh
python3 build.py --check
python3 tests/release_build.test.py
node --test tests/*.test.cjs
python3 tools/export_contact.py
python3 tests/contact_exports.test.py
```

Desde un checkout limpio, `python3 build.py --check` y `git diff --exit-code -- assets/dc019-equipment.glb` comprueban que las salidas están sincronizadas. Después de modificar fuentes, una diferencia es esperable: revisar y versionar las salidas generadas correspondientes, no ignorarla.

La CI ejecuta construcción reproducible, lógica y exportación. La verificación WebGL usa un entorno aislado y publica sus informes como artefactos. Los resultados actuales se consultan en [Actions](https://github.com/CripterHack/distrito-cero/actions), no se deducen de una cifra histórica. [Protocolo de QA](docs/project/QA.md).

## Integridad de la publicación

Se importaron **730 archivos** del ZIP final de v0.19, con **729 huellas** verificadas. Commit original de importación: `23f9e9d031c7a0ad270cd74ce0805ea0dfc385da`.

HTML de esa base: `3aa9a27f4941ea1c701069c61db133ab3c93087e35d833d4921ba25b8a4b059f` (8,839,156 bytes). ZIP original: `307c8fd0d3093eb7d16a3468470a2dfd20ffa12a654ecbe306f07f8aea8a1241`.

`SOURCE-MANIFEST.json` se conserva como **manifiesto del paquete importado**, no como un inventario actualizado de esta documentación. Git registra los cambios posteriores. Las fuentes, recursos, pruebas y evidencias originales se conservan. La importación automatizada fue de una sola vez y su workflow se retiró después.

## Alcance y derechos

Se han comprobado persistencia HTTP nativa con reapertura y recuperación WebGL en Chromium. Siguen pendientes cobertura completa de situaciones emergentes, GPU física, Safari/Firefox, móviles y sesiones prolongadas. La recuperación no garantiza que el driver nunca pierda contexto. Los vídeos de inspección avanzan el tiempo de forma controlada: no prueban FPS reales.

No se añadió una licencia global al proyecto sin decisión de su titular. Las atribuciones de recursos de terceros se preservan en `assets/ATTRIBUTION-*.md`. Ver [estado de licencias](docs/project/LICENSING.md). No se incluyen archivos de fuentes tipográficas, secretos, partidas personales ni credenciales de desarrollo.
