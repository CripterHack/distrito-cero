# Entrega de equipo con contexto de marcha

> Ejecución secuencial con superpowers:executing-plans. Revisión propia, no independiente.

**Objetivo:** conservar la pose efectivamente presentada al seleccionar otra familia durante marcha, conforme a CONTACT-05 de [SPEC-003](spec.md).
**Base:** master `6dd7a01b29d3007377ccfe0d316cecf4235cc270`, 0.20.9.
**Arquitectura:** la UI obtiene el actor del MotionTracker ya usado por el renderer y lo pasa explícitamente como argumento opcional de equipWeapon/captureSwitch. Sólo la instantánea de presentación lo consume. El montaje de gameplay nunca recibe este contexto. No duplicar tracker, solver o reloj.
**Alternativas descartadas:** guardar una pose desde drawEquipment en la simulación introduce escritura de gameplay desde renderer. Crear un segundo MotionTracker deriva en memorias distintas. Mover el seguimiento completo al tick modifica toda la marcha fuera del alcance. El argumento explícito preserva responsabilidad y compatibilidad de llamadas sin contexto.

## Contratos

- Selection/cancelación/disparo/recarga y disponibilidad siguen inmediatos.
- Misma instancia de seguimiento para dibujar, congelar selector y capturar el cambio. Reset explícito al cambiar de simulación y fallback sin tracker/estudio.
- Desplazamiento inicial palmar <1e-5 m. Huesos y anclas sin cambios. Sin alteración de memoria de pies, munición, cámara o persistencia.
- No afirmar cobertura de toda anatomía, colisión continua, hardware físico o arte global. No cambiar tolerancias para esconder errores.

## Tareas

- [x] Repetir baseline completo y fallo de 92.172 mm con pruebas nuevas y navegador canónico.
- [x] Pasar actor opcional a captureSwitch desde equipWeapon. Centralizar sólo la lectura de actor del renderer y enlazar la UI antes de cancelar inputs.
- [x] GREEN de regresiones por familias, reload, aislamiento/escena, lectura no mutante y gameplay independiente. Node y Python vigentes completos.
- [ ] Evidencia antes/después en mismo renderer, con teclado y marcha nativa. Extender la suite existente sin repetir otra matriz equivalente.
- [ ] Version/build/documentación coherentes. Publicar commits separados de producto y documentación desde base remota, revisar CI exacta antes de merge. Verificar master/Pages aparte.

**Reversión:** revertir fuentes/pruebas/build/version de esta unidad. Sin migración ni borrado de partidas. #5/#6/#7 mantienen criterios globales.

## Registro de ejecución

Base: build inmutable y 576 Node aprobados. Las siete regresiones observaron RED; cuatro identificaron el salto de ~92.17 mm. La captura de navegador original terminó sin errores. Primer GREEN 7/7.

Ruling: separar handoff del resto de gráficos en CI, manteniendo la selección completa desde el registro y 40 minutos por shard. La evidencia previa dejó sólo 28.576 s de margen de suite, insuficiente para añadir 62 observaciones. Se conservan todos los casos, HTTP y umbrales. Dos tests de la selección del workflow observaron RED/GREEN.

GREEN completo: 583 Node, 103 Python. Comparación canónica: 92.171838 mm → 0 mm, cuatro PNG. Capturas revisadas, sin errores ni peticiones. La CI ampliada sigue pendiente de publicación.
