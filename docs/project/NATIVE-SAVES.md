# Guardados nativos · issue #3

`python3 -m tools.qa.run --suite native --origin http --headed --output artifacts/native-unique` ejecuta un origen HTTP local ligado a 127.0.0.1 y un perfil persistente temporal de Chromium. No utiliza perfiles o partidas personales, credenciales ni un sustituto de Web Storage. Para Linux sin pantalla, anteponer `xvfb-run -a`.

La prueba crea dos personajes/partidas mediante el creador real, prepara dinero, misión e inventario para distinguirlas, guarda, cierra Chromium y reabre el mismo perfil. Comprueba IDs, contenido, renombrado, borrado, importación/exportación y conflictos entre dos páginas reales. Las descargas JSON son del navegador. Los informes y capturas salen del harness, no de los directorios históricos.

El renderer se aparca después de iniciar WebGL y cargar sus materiales para que una medición de datos no dependa del rendimiento de SwiftShader. La UI y las rutas reales de guardado siguen ejecutándose. No se presenta como benchmark visual, como garantía universal para file:// o como prueba de todos los navegadores.

La CI tiene un job separado `Native saved games and tabs`. El runner exige explícitamente `nativeStorage: true` para el contrato HTTP y no mezcla `--suite all` con fixtures de otro origen. El resultado debe leerse en los artefactos nuevos del run actual: la existencia del script no demuestra que haya aprobado.

No se cambia el esquema de partidas ni el HTML público en esta unidad. Fallos de cuota/permisos inyectados siguen perteneciendo a las pruebas de catálogo existentes y se distinguen de la persistencia nativa.
