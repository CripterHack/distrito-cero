# Riesgos, decisiones y acciones manuales

| Riesgo | Señal actual | Mitigación y puerta |
| :--- | :--- | :--- |
| Calidad que oscila entre iteraciones | Varias revisiones cervicales sin referencia estable | Escena patrón y aceptación de forma antes de modificar materiales o cámara |
| Confundir más detalle con realismo | Alto coste geométrico con manos/cabello aún estilizados | Evaluar silueta, contactos, superficie y movimiento por separado |
| Pérdida de datos local | Pruebas previas usan almacenamiento sustituido | Origen nativo, reapertura, migración y conflictos reales |
| Contexto gráfico perdido | Incidentes SwiftShader documentados | Lifecycle explícito, diagnóstico y caso de recuperación, no reintento ciego |
| Fragilidad de capas | Clase pública reemplazada por varias extensiones | Contratos y tests de orden antes de refactorizar |
| Crecimiento de repositorio | Baselines y evidencia histórica preservados | No nuevas duplicaciones masivas, política de releases/LFS por ADR |
| QA dependiente del laboratorio | Rutas absolutas, DISPLAY fijo, auditor que asume otro historial | Harness configurable y evidencia por ejecución |
| Deriva de alcance | Personajes, armas y mundo amplían coste simultáneamente | Máximo dos frentes de contratos independientes, vertical slice primero |
| Assets de permiso insuficiente | No hay licencia global decidida | Titular decide licencia, preservar atribuciones y revisar nuevos insumos |
| Promesa de rendimiento no fundada | No benchmark físico disponible | Perf targets como hipótesis, hardware documentado antes de aprobar |

## Decisiones de esta publicación

Se conserva master, el runtime nativo, el HTML autónomo y el juego v0.19 sin cambios. Se importan todos los archivos originales. El workflow de importación se retira tras usarse. La CI ordinaria es de lectura de repositorio y publica informes, no despliega.

La carpeta `.specify` contiene una constitución local. No implica instalación de un framework ni cambia los comandos del entorno del usuario. Los PRs y CODEOWNERS facilitan revisión, pero **no activan por sí mismos protecciones de rama**.

## Pendientes reservados al titular

**Licencia y contribuciones:** elegir términos globales de código y arte propio antes de promocionar una licencia abierta o comercial específica.

**Hardware:** confirmar los dispositivos de referencia para presupuestos y facilitar pruebas físicas. La RTX/Mac/otros equipos no se asumen disponibles a este agente.

**Recursos de pago:** aprobar presupuesto y permisos de cualquier asset, mocap, sonido o servicio. No se hicieron compras.

**Configuración GitHub:** valorar reglas de master y checks obligatorios tras confirmar nombres estables de CI. No activar políticas administrativas silenciosamente.

**Distribución:** aprobar hosting, dominio y release público jugable antes de desplegar. El repositorio público fue solicitado; una publicación web o monetización no se deduce automáticamente de ello.

Estas decisiones no bloquean escribir specs, mejorar QA o trabajar con los assets ya autorizados. No se solicita al usuario repetir acciones que ya se ejecutaron con herramientas.
