# Tareas · SPEC-001

Todas pendientes. No marcar una tarea por haber escrito este documento.

## PR A · Runner portable

- [ ] A1. Crear rama desde master, ejecutar build/Node/export y registrar base.
- [ ] A2. Inventariar comandos, rutas y esquemas de los cinco informes vigentes.
- [ ] A3. Escribir tests fallidos para exit no cero, timeout, JSON ausente/viejo y HTML cambiado.
- [ ] A4. Implementar configuración y runner mínimo sin dependencia de Chromium en sus unit tests.
- [ ] A5. Adaptar manejo conservando las 51 aserciones y comparar el resultado.
- [ ] A6. Publicar artefactos fuera de qa histórico, documentar reproducción y revisar PR.

## PR B · Guardado nativo

- [ ] B1. Crear fixture de servidor local y perfil aislado sin sustituir localStorage.
- [ ] B2. Añadir test de dos partidas distintas, cierre/reapertura, renombrado/borrado y exportación.
- [ ] B3. Añadir conflicto entre dos páginas y verificación de copia/recarga segura.
- [ ] B4. Corregir sólo los defectos reproducidos, mantener importación antigua y pruebas de cuotas.
- [ ] B5. Registrar navegador y origen reales, límites de file:// y evidencia.

## PR C · Recuperación gráfica

- [ ] C1. Inventariar lifecycle de recursos y listeners por clase de renderer.
- [ ] C2. Añadir caso que falle ante pérdida/restauración controlada de contexto.
- [ ] C3. Implementar reconstrucción idempotente y UI sin reiniciar datos.
- [ ] C4. Verificar inputs, cargadores, ocupantes, partidas y ausencia de loops duplicados.
- [ ] C5. Probar fallback de restauración no disponible y reversión segura.

## PR D · Recursos y cierre

- [ ] D1. Ensayo de recorrido y reapertura repetida de interfaces con contador de recursos.
- [ ] D2. Ejecutar toda la batería de navegador vigente con informes nuevos.
- [ ] D3. Revisar requisitos REL-01–07 por separado y registrar cuáles quedan bloqueados.
- [ ] D4. Actualizar handoff, estado, plan y riesgos con commits y artefactos.

## Comandos de entrada vigentes

`python3 build.py`, `node --test tests/*.test.cjs`, `python3 tools/export_contact.py`, `python3 tests/contact_exports.test.py`.

Los comandos del runner propuesto se documentarán cuando exista. No se presentan como disponibles hoy.
