# Contrato de calidad y evaluación

## La meta no se mide con la etiqueta AAA

El objetivo es credibilidad visual, continuidad temporal, claridad de interacción y rendimiento consistente. Las pruebas de lógica demuestran propiedades limitadas; no certifican anatomía o diversión. Se evalúan por separado la imagen, el movimiento, la jugabilidad, los datos y el coste.

## Matriz visual obligatoria para personajes

Cámaras frontal, perfil, tres cuartos y posterior. Distancias: cuerpo en juego, busto de interacción y detalle en creador. Iluminación neutra, lateral y nocturna. Proporciones: neutral, delgada, robusta y extremos combinados permitidos. Peinados cortos y largos, ropa actual y estados sentados.

Poses: reposo, caminar, correr, frenar, giro, agachado, salto/aterrizaje, conducir, apuntar, recargar, extraer/entrar y giro/flexión cervical. Una captura aislada no puede aprobar el conjunto. Para cada defecto corregido conservar cámara, semilla, inputs, velocidad y calidad comparables.

## Criterios observables

| Dominio | Criterio de aceptación | Evidencia |
| :--- | :--- | :--- |
| Anatomía | La cabeza parece apoyada en el torso, sin cuello tubular, bulto cervical ni proporciones contradictorias entre presets | Vistas y poses equivalentes con decisión artística registrada |
| Malla y rig | Superficies sin grietas expuestas, normales válidas y huesos no alargados para ocultar alcance | Auditoría geométrica y vídeo de extremos |
| Manos/equipo | Palma y zonas de agarre acompañan la superficie, sin salto al cambiar fase | Puntos de contacto, silueta real y secuencia completa |
| Locomoción | Apoyos y cadencia responden al desplazamiento, sin patinaje evidente o pies flotantes en el escenario de prueba | Trayectorias, error medido y vídeo a velocidad real de simulación |
| Cabello | Nacimiento y volumen coherentes, sin cráneo atravesando ni contorno uniforme de casco | Primer plano y movimiento con presupuesto de overdraw |
| Materiales | Piel/tela/caucho/metal/vidrio se distinguen bajo la misma luz sin ruido especular dominante | Escena de materiales y revisión de espacios de color |
| Interacciones | Anticipación, contacto, acción y salida coherentes, con cancelación segura | Matriz de fases, inputs reales y rollback |
| Juego | Objetivo comprensible, control fiable, consecuencias legibles y más de una respuesta viable | Playtest registrado, no sólo tests de estado |
| Datos | No pérdida silenciosa, importación íntegra, reanudación real y mensajes claros | Origen nativo, cierre/reapertura y fallos inyectados |

Las tolerancias palmares actuales de 12–13 mm son límites de muestreo del prototipo. No son un objetivo artístico definitivo. Reducirlas donde el tamaño en pantalla lo exija y justificar cada criterio mediante medición real; no hacer pasar un contacto visual malo citando sólo su pivote.

## Presupuestos propuestos, todavía sin benchmark físico

| Perfil candidato | Resolución de referencia | Objetivo de diseño | Cómo se medirá |
| :--- | :--- | :--- | :--- |
| Escritorio equilibrado | 1920×1080 | Frame time p95 ≤16.7 ms, p99 ≤33.3 ms en recorrido controlado | Captura identificando CPU/GPU/navegador, escenas y ventana temporal |
| Portátil/móvil económico | 1280×720 interno, UI nativa | Frame time p95 ≤33.3 ms, p99 ≤50 ms | Dispositivo físico por seleccionar, límites térmicos y resolución registrados |
| Estudio de personaje | Viewport documentado | Sin bloqueo de inputs mientras cambia apariencia | Latencia observada y asignaciones por cambio |
| Streaming | Trayecto de 30 min | Cachés dentro de límites, sin crecimiento sostenido de recursos | Contadores CPU/GPU estimados y medidas de heap cuando disponibles |

Son **objetivos propuestos**, no resultados obtenidos ni compromisos para cualquier dispositivo. Los percentiles se calculan sobre tiempos de frame, no promediando FPS. Separar carga inicial, compilación de shaders y régimen estable. Las pruebas por software no aprueban estos objetivos.

Para el primer benchmark mantener los presupuestos actuales como línea de referencia. Definir VRAM/heap por perfil sólo después de disponer de medidas. No usar el tamaño comprimido del HTML como estimación de memoria de ejecución.

## Severidad de defectos

**P0:** pérdida/corrupción de datos, ejecución de contenido importado, crash o bloqueo irreversible. **P1:** misión imposible, control que no responde, colisión/captura injusta reproducible, cuello/mano que rompe claramente la lectura en cámara habitual. **P2:** intersección leve en pose rara, pop de LOD, desfase menor de material o ritmo. **P3:** detalles sin efecto apreciable en el alcance actual.

Un defecto visual repetido en cada conversación no debe recibir sólo otro ajuste a ojo. Crear caso fijo, referencia aprobada y causa localizada entre topología, pesos, proporciones, materiales y cámara.

## Evidencia de aprobación

Cada gate requiere una ficha con responsable/revisor, commit, hash de HTML, configuración, resultados y limitaciones. Una comparación no cambia la luz para favorecer una versión. Un vídeo debe indicar si el tiempo se avanzó de forma controlada. Una escena generada fuera del juego se rotula como referencia.

No afirmar recuperación de WebGL, persistencia nativa, mocap, física de tejidos o rendimiento hasta ejecutar el caso correspondiente. La palabra «accepted» en una spec exige enlaces a su evidencia, no un checklist marcado sin resultados.
