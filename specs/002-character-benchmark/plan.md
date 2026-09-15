# Plan de ejecución · personaje patrón

Estado: primera unidad técnica implementada, aceptación artística pendiente. Spec: [SPEC-002](spec.md).

## A · Referencia reproducible

Matriz declarativa versionada en tests, generador Python validado, preparación JS exclusiva de QA y captura Playwright del renderer original. El smoke cubre cada eje sin afirmar la cobertura cartesiana. La matriz full está disponible por separado para no convertir cada PR en cientos de renders obligatorios.

Pruebas antes de implementación: contrato inválido, parámetros fuera de rango, independencia de casos, rutas de galería, aprobación vacía, mediciones reales y LOD. Ningún nuevo script entra en el bundle del juego.

## B · Revisión artística, siguiente gate

Comparar frontal/perfil/tres cuartos/posterior bajo tres luces. Revisar cuatro proporciones, doce poses y peinados. Separar la medición del rig de la silueta. Registrar los problemas por ID de caso y decidir qué proporciones se aceptan como base, sin declarar hiperrealismo.

El hallazgo de chaqueta al apuntar enlaza con SPEC-003: crear primero una regresión de deformación/superficie que falle en la base. Revisar pesos, anclas y postura completa, no aumentar sólo la tolerancia de muñeca.

## C · Autoría y correcciones

Tras el gate B, editar topología/pesos/materiales mediante sus fuentes y regeneradores. Cada corrección se compara contra las mismas cámaras y conserva datos/rig o incorpora una migración explícita. Incluir contactos de manos, hombro y cuello en poses sentadas y de equipo.

## D · Cierre

Ejecutar regresiones de personajes, gameplay, guardados y recuperación. Registrar coste real por LOD, permisos y validación de intercambio. No cerrar #5 sólo por aprobar el smoke técnico; no cerrar #6 por una imagen más favorecedora. Reversión de la unidad A: retirar los archivos QA/workflow, sin migración ni alteración de partidas.
