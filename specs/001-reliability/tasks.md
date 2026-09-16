# Tareas · SPEC-001

Estado reconciliado en v0.20 con las implementaciones de PR #8, #9, #10 y #17. Las marcas se refieren al alcance entregado, no a cobertura universal de hardware. El ensayo prolongado de recursos sigue pendiente.

## PR A · Runner portable

- [x] A1. Crear rama desde master, ejecutar build/Node/export y registrar base.
- [x] A2. Inventariar comandos, rutas y esquemas de los cinco informes vigentes.
- [x] A3. Escribir tests fallidos para exit no cero, timeout, JSON ausente/viejo y HTML cambiado.
- [x] A4. Implementar configuración y runner mínimo sin dependencia de Chromium en sus unit tests.
- [x] A5. Adaptar manejo conservando las 51 aserciones y comparar el resultado.
- [x] A6. Publicar artefactos fuera de qa histórico, documentar reproducción y revisar PR.

## PR B · Guardado nativo

- [x] B1. Crear fixture de servidor local y perfil aislado sin sustituir localStorage.
- [x] B2. Añadir test de dos partidas distintas, cierre/reapertura, renombrado/borrado y exportación.
- [x] B3. Añadir conflicto entre dos páginas y verificación de copia/recarga segura.
- [x] B4. Corregir sólo los defectos reproducidos, mantener importación antigua y pruebas de cuotas.
- [x] B5. Registrar navegador y origen reales, límites de file:// y evidencia.

## PR C · Recuperación gráfica

- [x] C1. Inventariar lifecycle de recursos y listeners por clase de renderer.
- [x] C2. Añadir caso que falle ante pérdida/restauración controlada de contexto.
- [x] C3. Implementar reconstrucción idempotente y UI sin reiniciar datos.
- [x] C4. Verificar inputs, cargadores, ocupantes, partidas y ausencia de loops duplicados.
- [x] C5. Probar fallback de restauración no disponible y reversión segura.

## PR D · Recursos y cierre

- [ ] D1. Ensayo de recorrido y reapertura repetida de interfaces con contador de recursos.
- [x] D2. Ejecutar toda la batería de navegador vigente con informes nuevos.
- [ ] D3. Revisar requisitos REL-01–07 por separado y registrar cuáles quedan bloqueados.
- [x] D4. Actualizar handoff, estado, plan y riesgos con commits y artefactos.

## Comandos de entrada vigentes

`python3 build.py`, `node --test tests/*.test.cjs`, `python3 tools/export_contact.py`, `python3 tests/contact_exports.test.py`.

`python3 -m tools.qa.run --suite all` ya es ejecutable y conserva evidencia por run. Para los casos nativos, `--suite native --origin http`. En v0.20 también existe `--suite release --origin http`.

REL-01/02: PR #8, REL-03/04: PR #9. REL-05 conserva validación, cuota y corrupción en tests de almacenamiento con fallos inyectados; no implica agotar cuotas físicas de todos los navegadores. REL-06: PR #10 y guardas #17. REL-07 y D1 (sesiones prolongadas y memoria) no están aceptados globalmente. Ver `docs/project/QA.md` y Actions para el hash actual.
